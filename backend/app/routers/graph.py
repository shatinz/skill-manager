"""
Neural Graph & Ecosystem Topology Router.
Produces graph nodes and edges representing the live ecosystem:
- Skills (hub nodes)
- Versions (lineage nodes linked by parent-child synapses)
- Proposers (trust agent nodes with energy scores)
- Proposals (in-flight signals or quarantined pods)
- Pipeline Cortex Stages (processing cores)
- Batches (accumulation clusters)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import Skill, Version, Proposal, Batch, ProposerProfile, AuditResult, ProposalStatus

router = APIRouter(prefix="/graph", tags=["Neural Graph"])


@router.get("/neural-data")
def get_neural_graph_data(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    versions = db.query(Version).all()
    proposals = db.query(Proposal).all()
    proposers = db.query(ProposerProfile).all()
    batches = db.query(Batch).all()
    audit_results = db.query(AuditResult).all()

    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []

    # 1. Pipeline Stages (Central Neural Cortex Hubs)
    pipeline_stages = [
        {"id": "cortex_ingest", "name": "Stage A: Ingestion", "type": "cortex", "group": "pipeline", "color": "#00d4ff", "size": 22, "desc": "AST parsing & vector deduplication", "x_hint": -400, "y_hint": -150},
        {"id": "cortex_feedback", "name": "Stage B: Telemetry & Feedback", "type": "cortex", "group": "pipeline", "color": "#38bdf8", "size": 22, "desc": "Usage events & proposal capture", "x_hint": -200, "y_hint": -150},
        {"id": "cortex_batch", "name": "Stage C: Batch Accumulation", "type": "cortex", "group": "pipeline", "color": "#818cf8", "size": 24, "desc": "Window accumulation & clustering", "x_hint": 0, "y_hint": -150},
        {"id": "cortex_weight", "name": "Stage D: Nonlinear Merge", "type": "cortex", "group": "pipeline", "color": "#a855f7", "size": 28, "desc": "Redundancy bonus & disruptiveness dampening", "x_hint": 200, "y_hint": -150},
        {"id": "cortex_audit", "name": "Stage E: Security Sentinel", "type": "cortex", "group": "pipeline", "color": "#f43f5e", "size": 26, "desc": "Static analysis, sandbox canary & sybil heuristics", "x_hint": 400, "y_hint": -150},
        {"id": "cortex_release", "name": "Stage F: Version Release", "type": "cortex", "group": "pipeline", "color": "#10b981", "size": 24, "desc": "Append-only immutable lineage release", "x_hint": 600, "y_hint": -150},
    ]

    for stage in pipeline_stages:
        nodes.append(stage)

    # Pipeline backbone links
    for i in range(len(pipeline_stages) - 1):
        links.append({
            "source": pipeline_stages[i]["id"],
            "target": pipeline_stages[i + 1]["id"],
            "type": "cortex_flow",
            "color": "#818cf8",
            "value": 3,
            "animated": True
        })

    # 2. Proposer Nodes (Trust Agents)
    for p in proposers:
        trust = p.trust_score or 0.0
        color = "#10b981" if trust >= 0.7 else ("#f59e0b" if trust >= 0.3 else "#ec4899")
        nodes.append({
            "id": f"proposer_{p.id}",
            "name": p.display_name or p.id,
            "type": "proposer",
            "group": "proposer",
            "trust": round(trust, 3),
            "stars": p.project_stars,
            "color": color,
            "size": 16 + int(trust * 10),
            "desc": f"Trust Score: {trust:.2f} | Stars: {p.project_stars}",
            "raw_id": p.id
        })
        # Link proposer to feedback stage
        links.append({
            "source": f"proposer_{p.id}",
            "target": "cortex_feedback",
            "type": "trust_link",
            "color": color,
            "value": 1.5,
            "animated": False
        })

    # Category color palette
    cat_colors = {
        "code-generation": "#00d4ff",
        "testing": "#10b981",
        "devops": "#8b5cf6",
        "data-analysis": "#f59e0b",
        "security": "#ef4444",
        "refactoring": "#ec4899",
        "documentation": "#06b6d4",
        "debugging": "#f97316"
    }

    # 3. Skill Nodes (Hubs)
    skill_map = {}
    for s in skills:
        skill_color = cat_colors.get(s.category, "#3b82f6")
        node_id = f"skill_{s.id}"
        skill_map[s.id] = node_id
        nodes.append({
            "id": node_id,
            "name": s.name,
            "type": "skill",
            "group": "skill",
            "category": s.category,
            "current_version_id": s.current_version_id,
            "color": skill_color,
            "size": 22,
            "desc": f"Category: {s.category} | {s.description[:80]}...",
            "raw_id": s.id
        })

        # Link skill to Ingestion and Release cortex
        links.append({
            "source": "cortex_ingest",
            "target": node_id,
            "type": "ingest_link",
            "color": "#00d4ff",
            "value": 1,
            "animated": False
        })

    # 4. Version Nodes (Lineage chain)
    version_map = {}
    for v in versions:
        v_node_id = f"version_{v.id}"
        version_map[v.id] = v_node_id
        is_live = any(s.current_version_id == v.id for s in skills)
        nodes.append({
            "id": v_node_id,
            "name": f"v:{v.id[:8]}",
            "type": "version",
            "group": "version",
            "is_live": is_live,
            "skill_id": v.skill_id,
            "color": "#10b981" if is_live else "#64748b",
            "size": 14 if is_live else 10,
            "desc": f"{'🌟 LIVE VERSION' if is_live else 'Historical Snapshot'} | Created: {v.created_at}",
            "raw_id": v.id
        })

        # Link version to its parent skill
        if v.skill_id in skill_map:
            links.append({
                "source": skill_map[v.skill_id],
                "target": v_node_id,
                "type": "skill_version_link",
                "color": "#10b981" if is_live else "#475569",
                "value": 2 if is_live else 1,
                "animated": is_live
            })

        # Link version to parent version (Lineage synapse)
        if v.parent_version_id and v.parent_version_id in version_map:
            links.append({
                "source": version_map[v.parent_version_id],
                "target": v_node_id,
                "type": "lineage_synapse",
                "color": "#a855f7",
                "value": 2.5,
                "animated": True
            })

    # 5. Proposal & Quarantine Nodes
    for p in proposals:
        p_node_id = f"proposal_{p.id}"
        is_quarantined = (p.status == ProposalStatus.QUARANTINED)
        is_merged = (p.status == ProposalStatus.MERGED)
        
        p_color = "#ef4444" if is_quarantined else ("#10b981" if is_merged else "#f59e0b")
        nodes.append({
            "id": p_node_id,
            "name": f"prop:{p.proposal_type[:4]}_{p.id[:6]}",
            "type": "quarantined" if is_quarantined else "proposal",
            "group": "proposal",
            "status": p.status.value if hasattr(p.status, "value") else str(p.status),
            "proposer_id": p.proposer_id,
            "color": p_color,
            "size": 12,
            "desc": f"Status: {p.status} | By: {p.proposer_id}",
            "raw_id": p.id
        })

        # Link proposer to proposal
        if f"proposer_{p.proposer_id}" in [n["id"] for n in nodes]:
            links.append({
                "source": f"proposer_{p.proposer_id}",
                "target": p_node_id,
                "type": "proposer_proposal_link",
                "color": p_color,
                "value": 1,
                "animated": False
            })

        # If quarantined, link to Security cortex node
        if is_quarantined:
            links.append({
                "source": p_node_id,
                "target": "cortex_audit",
                "type": "quarantine_beam",
                "color": "#ef4444",
                "value": 2.5,
                "animated": True
            })
        elif p.skill_id in skill_map:
            links.append({
                "source": p_node_id,
                "target": skill_map[p.skill_id],
                "type": "proposal_target_link",
                "color": p_color,
                "value": 1,
                "animated": False
            })

    return {
        "nodes": nodes,
        "links": links,
        "meta": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "skills_count": len(skills),
            "versions_count": len(versions),
            "proposals_count": len(proposals),
            "proposers_count": len(proposers),
        }
    }
