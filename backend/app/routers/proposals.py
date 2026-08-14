from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import difflib
from datetime import datetime

from app.database import get_db
from app.models import Skill, Version, Proposal, Batch, BatchStatus, ProposerProfile
from app.schemas import ProposalCreate, ProposalResponse
from app.services.trust import snapshot_trust_features

router = APIRouter(tags=["proposals"])

@router.post("/skills/{skill_id}/proposals", response_model=ProposalResponse)
def submit_proposal(skill_id: str, proposal: ProposalCreate, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    # Determine autonomous agent status
    is_agent = (
        proposal.is_agent
        or proposal.proposer_id.startswith("agent:")
        or proposal.proposer_id.startswith("bot:")
        or "autonomous_agent" in proposal.tags
        or "ai_generated" in proposal.tags
    )

    # Process and guarantee standard tags
    tags = list(proposal.tags)
    if is_agent:
        if "autonomous_agent" not in tags:
            tags.insert(0, "autonomous_agent")
        if "ai_generated" not in tags:
            tags.append("ai_generated")
    else:
        if "human" not in tags:
            tags.append("human")

    # Find or auto-register proposer profile
    proposer = db.query(ProposerProfile).filter(ProposerProfile.id == proposal.proposer_id).first()
    if not proposer:
        if is_agent:
            # Auto-register autonomous agent profile
            proposer = ProposerProfile(
                id=proposal.proposer_id,
                display_name=proposal.proposer_id.replace("agent:", "Autonomous Agent: "),
                is_agent=True,
                account_created_at=datetime.utcnow(),
                project_stars=10,
                trust_score=0.5,
                contribution_history=[]
            )
            db.add(proposer)
            db.flush()
        else:
            # Auto-register human proposer profile for frictionless community proposals
            proposer = ProposerProfile(
                id=proposal.proposer_id,
                display_name=proposal.proposer_id,
                is_agent=False,
                account_created_at=datetime.utcnow(),
                project_stars=0,
                trust_score=0.2,
                contribution_history=[]
            )
            db.add(proposer)
            db.flush()

    target_version_id = skill.current_version_id
    if not target_version_id:
        raise HTTPException(status_code=400, detail="Skill has no active version")

    target_version = db.query(Version).filter(Version.id == target_version_id).first()

    # snapshot trust
    trust_snapshot = snapshot_trust_features(proposer)
    
    # Compute diff if modification and not provided
    diff_content = proposal.diff_content
    if proposal.proposal_type == "modification" and not diff_content and proposal.proposed_content:
        original_lines = target_version.content.splitlines()
        proposed_lines = proposal.proposed_content.splitlines()
        diff = difflib.unified_diff(
            original_lines, proposed_lines, 
            fromfile='current_version', tofile='proposed_version', lineterm=''
        )
        diff_content = '\n'.join(list(diff))

    # Find or create accumulating batch
    batch = db.query(Batch).filter(
        Batch.skill_id == skill_id, 
        Batch.status == BatchStatus.ACCUMULATING
    ).first()
    
    if not batch:
        batch = Batch(
            skill_id=skill_id,
            window_start=datetime.utcnow(),
            status=BatchStatus.ACCUMULATING
        )
        db.add(batch)
        db.flush()

    new_proposal = Proposal(
        skill_id=skill_id,
        target_version_id=target_version_id,
        batch_id=batch.id,
        proposer_id=proposer.id,
        proposer_trust_snapshot=trust_snapshot,
        is_agent=is_agent,
        tags=tags,
        agent_metadata=proposal.agent_metadata,
        proposal_type=proposal.proposal_type,
        diff_content=diff_content,
        proposed_content=proposal.proposed_content,
        issue_text=proposal.issue_text
    )
    db.add(new_proposal)
    db.commit()
    db.refresh(new_proposal)
    
    return new_proposal

@router.get("/skills/{skill_id}/proposals", response_model=List[ProposalResponse])
def list_proposals(
    skill_id: str, 
    status: Optional[str] = None,
    is_agent: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Proposal).filter(Proposal.skill_id == skill_id)
    if status:
        query = query.filter(Proposal.status == status)
    if is_agent is not None:
        query = query.filter(Proposal.is_agent == is_agent)
    return query.all()

@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal
