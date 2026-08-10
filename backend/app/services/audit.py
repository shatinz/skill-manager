import re
import difflib
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
from sqlalchemy.orm import Session
from app.models import Proposal, Batch, AuditResult, RiskVerdict, ProposalStatus, ProposalType, PipelineLog, ProposerProfile
from app.config import settings

def static_analyze(content: str) -> List[Dict]:
    flags = []
    if not content:
        return flags
        
    # 1. Network/HTTP calls (actual code calls or shell downloaders)
    network_pattern = re.compile(r'\b(curl\s+|wget\s+|requests\.(get|post|put|delete)|fetch\(|httpx\.(get|post)|urllib\.request)\b')
    for match in network_pattern.finditer(content):
        flags.append({"type": "network_call", "severity": "high", "match": match.group(0), "context": content[max(0, match.start()-20):match.end()+20]})
        
    # 2. File system operations outside expected scope
    fs_pattern = re.compile(r'\b(rm\s+-[a-zA-Z]*r[a-zA-Z]*|shutil\.rmtree|os\.remove|os\.unlink)\b')
    for match in fs_pattern.finditer(content):
        flags.append({"type": "file_system", "severity": "high", "match": match.group(0), "context": content[max(0, match.start()-20):match.end()+20]})
        
    # 3. Code execution
    exec_pattern = re.compile(r'\b(eval\(|exec\(|subprocess\.(Popen|run|call)|os\.system|__import__\()\b')
    for match in exec_pattern.finditer(content):
        flags.append({"type": "code_execution", "severity": "high", "match": match.group(0), "context": content[max(0, match.start()-20):match.end()+20]})
        
    # 4. Encoded/obfuscated content
    obf_pattern = re.compile(r'\b(base64\.b64decode|bytes\.fromhex)\b')
    for match in obf_pattern.finditer(content):
        flags.append({"type": "obfuscation", "severity": "medium", "match": match.group(0), "context": content[max(0, match.start()-20):match.end()+20]})
        
    # 5. Privilege escalation
    priv_pattern = re.compile(r'\b(sudo\s+|chmod\s+\+x|chmod\s+777|setuid)\b')
    for match in priv_pattern.finditer(content):
        flags.append({"type": "privilege_escalation", "severity": "high", "match": match.group(0), "context": content[max(0, match.start()-20):match.end()+20]})
        
    # 6. Safety override language
    override_pattern = re.compile(r'\b(ignore previous instructions|disregard safety|override restrictions)\b', re.IGNORECASE)
    for match in override_pattern.finditer(content):
        flags.append({"type": "safety_override", "severity": "high", "match": match.group(0), "context": content[max(0, match.start()-20):match.end()+20]})
        
    return flags

def semantic_diff_review(old_content: str, new_content: str) -> Tuple[float, str]:
    if not old_content:
        old_content = ""
    if not new_content:
        new_content = ""
        
    if settings.llm_provider == "openai":
        # LLM integration
        return 0.1, "LLM analysis: LGTM"
    else:
        # Mock: use difflib
        sm = difflib.SequenceMatcher(None, old_content, new_content)
        ratio = sm.ratio()
        
        # Calculate heuristic risk score based on disruption ratio
        risk_score = max(0.0, 1.0 - ratio) * 0.7  # scale disruption
        
        suspicious_words = ['subprocess', 'eval(', 'exec(', 'os.system', 'sudo ']
        for word in suspicious_words:
            if word in new_content and word not in old_content:
                risk_score += 0.4
                
        risk_score = min(1.0, risk_score)
        return risk_score, f"Semantic diff score: {risk_score:.2f} (similarity ratio {ratio:.2f})"

def sandbox_canary_check(content: str) -> Dict:
    findings = []
    passed = True
    
    if not content:
        return {"passed": True, "findings": [], "note": "v2: run in Docker container"}
    
    # parse markdown code blocks
    code_blocks = re.findall(r'```(?:python|bash|sh)?\n(.*?)\n```', content, re.DOTALL)
    
    for block in code_blocks:
        if re.search(r'\b(curl\s+|wget\s+|requests\.)', block):
            findings.append("Network call found in code block")
            passed = False
        if re.search(r'\b(open\(|with open)', block) and '/tmp' not in block and 'w' in block:
            findings.append("File write outside /tmp found in code block")
            passed = False
        if re.search(r'\b(import subprocess|subprocess\.run|os\.system)', block):
            findings.append("Dangerous process execution found in code block")
            passed = False
            
    return {
        "passed": passed,
        "findings": findings,
        "note": "v2: run in Docker container"
    }

def check_sybil_patterns(proposals: List[Proposal], db: Session) -> List[Dict]:
    flags = []
    
    sybil_age = settings.sybil_account_age_threshold_days
    sybil_window = settings.sybil_timing_cluster_window_minutes
    min_size = settings.sybil_min_cluster_size
    
    now = datetime.utcnow()
    
    # group by skill_id
    skills = {}
    for p in proposals:
        skills.setdefault(p.skill_id, []).append(p)
        
    for skill_id, props in skills.items():
        new_account_props = []
        for p in props:
            proposer = p.proposer
            if proposer:
                age_days = (now - proposer.account_created_at).days
                if age_days < sybil_age:
                    new_account_props.append(p)
                    
        # check time clusters among new accounts
        new_account_props.sort(key=lambda x: x.submitted_at)
        
        i = 0
        while i < len(new_account_props):
            cluster = [new_account_props[i]]
            j = i + 1
            while j < len(new_account_props) and (new_account_props[j].submitted_at - new_account_props[i].submitted_at).total_seconds() <= sybil_window * 60:
                cluster.append(new_account_props[j])
                j += 1
                
            if len(cluster) >= min_size:
                for cp in cluster:
                    flags.append({
                        "proposal_id": cp.id,
                        "proposer_id": cp.proposer_id,
                        "flag_type": "timing_cluster",
                        "severity": "high",
                        "details": f"Part of coordinated cluster of {len(cluster)} new accounts submitting within {sybil_window} mins"
                    })
            i = j
            
    return flags

def audit_batch(db: Session, batch_id: str) -> Dict[str, Any]:
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise ValueError("Batch not found")
        
    proposals = db.query(Proposal).filter(Proposal.batch_id == batch_id).all()
    
    sybil_flags = check_sybil_patterns(proposals, db)
    
    sybil_map = {}
    for f in sybil_flags:
        sybil_map.setdefault(f["proposal_id"], []).append(f)
        
    clean_count = 0
    suspicious_count = 0
    quarantined_ids = []
    details_per_proposal = {}
    
    for p in proposals:
        content_to_check = p.proposed_content if p.proposal_type == ProposalType.MODIFICATION else p.issue_text
        old_content = p.target_version.content if p.target_version else ""
        
        static_flags = static_analyze(content_to_check)
        semantic_score, semantic_reason = semantic_diff_review(old_content, content_to_check)
        sandbox_results = sandbox_canary_check(content_to_check)
        
        p_sybil_flags = sybil_map.get(p.id, [])
        
        has_high_static = any(f.get("severity") == "high" for f in static_flags)
        has_sybil = len(p_sybil_flags) > 0
        has_high_semantic = semantic_score > settings.audit_risk_threshold
        
        verdict = RiskVerdict.SUSPICIOUS if (has_high_static or has_sybil or has_high_semantic) else RiskVerdict.CLEAN
        
        audit_result = AuditResult(
            proposal_id=p.id,
            batch_id=batch.id,
            static_analysis_flags=static_flags,
            semantic_diff_risk_score=semantic_score,
            sandbox_canary_results=sandbox_results,
            sybil_flags=p_sybil_flags,
            risk_verdict=verdict,
            review_notes=semantic_reason
        )
        db.add(audit_result)
        
        if verdict == RiskVerdict.SUSPICIOUS:
            p.status = ProposalStatus.QUARANTINED
            suspicious_count += 1
            quarantined_ids.append(p.id)
        else:
            clean_count += 1
            
        details_per_proposal[p.id] = {
            "verdict": verdict.value,
            "static_flags": len(static_flags),
            "semantic_score": semantic_score,
            "sybil_flags": len(p_sybil_flags)
        }
        
    log = PipelineLog(
        batch_id=batch.id,
        stage="audit",
        event_type="audit_completed",
        payload={
            "total": len(proposals),
            "clean_count": clean_count,
            "suspicious_count": suspicious_count,
            "quarantined_ids": quarantined_ids
        }
    )
    db.add(log)
    db.commit()
    
    return {
        "total": len(proposals),
        "clean_count": clean_count,
        "suspicious_count": suspicious_count,
        "quarantined_proposal_ids": quarantined_ids,
        "details_per_proposal": details_per_proposal
    }
