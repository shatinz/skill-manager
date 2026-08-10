from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import Proposal, ProposalStatus, Batch, BatchStatus
from app.schemas import AuditReviewAction, DashboardStats, ProposalResponse, VersionResponse
from app.services.audit import audit_batch
from app.services.release import release_version, get_version_lineage

router = APIRouter(tags=["audit"])

@router.post("/batch/{batch_id}/audit")
def run_audit(batch_id: str, db: Session = Depends(get_db)):
    try:
        summary = audit_batch(db, batch_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch/{batch_id}/release")
def release_batch(batch_id: str, db: Session = Depends(get_db)):
    try:
        version, message = release_version(db, batch_id)
        if version is None:
            return {"version_id": None, "message": message}
        return {"version_id": version.id, "message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/quarantined", response_model=List[ProposalResponse])
def get_quarantined(db: Session = Depends(get_db)):
    proposals = db.query(Proposal).filter(Proposal.status == ProposalStatus.QUARANTINED).all()
    return proposals

@router.post("/proposal/{proposal_id}/review")
def review_proposal(proposal_id: str, action: AuditReviewAction, db: Session = Depends(get_db)):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
        
    if action.action == "approve":
        proposal.status = ProposalStatus.PENDING
    else:
        proposal.status = ProposalStatus.REJECTED
        
    db.commit()
    return {"status": proposal.status.value, "proposal_id": proposal.id}

@router.post("/pipeline/{skill_id}/run-full")
def run_full_pipeline(skill_id: str, db: Session = Depends(get_db)):
    """Convenience endpoint: close batch → process → audit → release, all in one call."""
    from app.services.batch import force_close_batch, close_and_process_batch

    # Step 1: Close the current batch and process (clustering, weighting, merge)
    batch = db.query(Batch).filter(
        Batch.skill_id == skill_id,
        Batch.status == BatchStatus.ACCUMULATING
    ).first()
    if not batch:
        raise HTTPException(status_code=404, detail="No accumulating batch found for this skill")

    # Check it has proposals
    pending_count = db.query(Proposal).filter(
        Proposal.batch_id == batch.id,
        Proposal.status == ProposalStatus.PENDING
    ).count()
    if pending_count == 0:
        raise HTTPException(status_code=400, detail="Batch has no pending proposals to process")

    batch_id = batch.id
    try:
        process_result = close_and_process_batch(db, batch_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    # Step 2: Audit
    audit_summary = audit_batch(db, batch_id)

    # Step 3: Release
    version, rel_message = release_version(db, batch_id)

    return {
        "batch_id": batch_id,
        "process_result": {
            "status": process_result.status,
            "merge_candidate_version_id": process_result.merge_candidate_version_id,
            "message": process_result.message,
        },
        "audit_summary": audit_summary,
        "release_message": rel_message,
        "version_id": version.id if version else None
    }
    
@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    from app.models import Skill, Version, UsageEvent
    from sqlalchemy import func
    
    total_skills = db.query(Skill).count()
    total_versions = db.query(Version).count()
    total_proposals = db.query(Proposal).count()
    total_usage = db.query(UsageEvent).count()
    pending = db.query(Proposal).filter(Proposal.status == ProposalStatus.PENDING).count()
    quarantined = db.query(Proposal).filter(Proposal.status == ProposalStatus.QUARANTINED).count()
    
    cats = db.query(Skill.category, func.count(Skill.id)).group_by(Skill.category).all()
    categories = {c[0]: c[1] for c in cats}
    
    return DashboardStats(
        total_skills=total_skills,
        total_versions=total_versions,
        total_proposals=total_proposals,
        total_usage_events=total_usage,
        pending_proposals=pending,
        quarantined_proposals=quarantined,
        categories=categories
    )

@router.get("/version/{version_id}/lineage", response_model=List[VersionResponse])
def get_lineage(version_id: str, db: Session = Depends(get_db)):
    return get_version_lineage(db, version_id)
