from sqlalchemy.orm import Session
from app.models import Batch, Proposal, Version, PipelineLog, BatchStatus, ProposalStatus, Skill, ProposerProfile
from typing import Tuple, List
from app.schemas import VersionResponse

def release_version(db: Session, batch_id: str) -> Tuple[Version, str]:
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise ValueError("Batch not found")
        
    audit_results = batch.audit_results
    proposals = batch.proposals
    
    if len(audit_results) < len(proposals) and len(proposals) > 0:
        raise ValueError("Audit not completed for all proposals in batch")
        
    if not batch.resulting_version_id:
        raise ValueError("No merge candidate version found in batch")
        
    quarantined = [p for p in proposals if p.status == ProposalStatus.QUARANTINED]
    clean = [p for p in proposals if p.status not in (ProposalStatus.QUARANTINED, ProposalStatus.REJECTED)]
    
    if len(quarantined) == len(proposals) and len(proposals) > 0:
        return None, "All proposals quarantined. Cannot release."
        
    merge_candidate = db.query(Version).filter(Version.id == batch.resulting_version_id).first()
        
    if len(quarantined) > 0 and len(clean) > 0:
        # Re-run merge synthesis with only clean proposals
        from app.services.clustering import cluster_proposals
        from app.services.weighting import rank_clusters, resolve_conflicts
        from app.services.merge import synthesize_merge
        from app.config import settings

        current_content = merge_candidate.parent_version.content if merge_candidate.parent_version else ""
        clusters = cluster_proposals(clean, settings.similarity_threshold)
        ranked = rank_clusters(clusters, current_content)
        resolved = resolve_conflicts(ranked)
        merged_content = synthesize_merge(current_content, resolved, batch.skill.name)

        new_version = Version(
            skill_id=batch.skill_id,
            parent_version_id=merge_candidate.parent_version_id,
            content=merged_content,
            merge_batch_id=batch.id
        )
        db.add(new_version)
        db.flush()
        merge_candidate = new_version
        
    skill = db.query(Skill).filter(Skill.id == batch.skill_id).first()
    skill.current_version_id = merge_candidate.id
    
    batch.status = BatchStatus.COMPLETED
    batch.resulting_version_id = merge_candidate.id
    
    from app.services.trust import compute_trust_score
    from datetime import datetime

    for p in clean:
        p.status = ProposalStatus.MERGED
        proposer = p.proposer
        if proposer:
            history = list(proposer.contribution_history or [])
            history.append({
                "skill_id": batch.skill_id,
                "proposal_id": p.id,
                "outcome": "merged",
                "timestamp": str(batch.window_start)
            })
            proposer.contribution_history = history
            proposer.trust_score = compute_trust_score(proposer)
            proposer.trust_score_updated_at = datetime.utcnow()
            db.add(proposer)
            
    log = PipelineLog(
        batch_id=batch.id,
        stage="release",
        event_type="version_released",
        payload={
            "version_id": merge_candidate.id,
            "skill_id": skill.id,
            "clean_count": len(clean),
            "quarantined_count": len(quarantined)
        }
    )
    db.add(log)
    db.commit()
    
    return merge_candidate, "Version released successfully."

def get_version_lineage(db: Session, version_id: str) -> List[VersionResponse]:
    lineage = []
    current_id = version_id
    while current_id:
        v = db.query(Version).filter(Version.id == current_id).first()
        if not v:
            break
        lineage.append(v)
        current_id = v.parent_version_id
        
    return [VersionResponse.model_validate(v) for v in reversed(lineage)]
