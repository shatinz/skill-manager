from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Batch, Proposal, PipelineLog
from app.schemas import BatchProcessRequest, BatchProcessResponse, BatchDetailResponse, BatchResponse, PipelineLogResponse
from app.services.batch import close_and_process_batch, force_close_batch

router = APIRouter(prefix="/batches", tags=["batches"])

@router.post("/process", response_model=BatchProcessResponse)
def process_batch(request: BatchProcessRequest, db: Session = Depends(get_db)):
    batch_id = force_close_batch(db, request.skill_id)
    return close_and_process_batch(db, batch_id)

@router.get("/skill/{skill_id}")
def list_batches(skill_id: str, db: Session = Depends(get_db)):
    batches = db.query(Batch).filter(Batch.skill_id == skill_id).order_by(Batch.created_at.desc()).all()
    result = []
    for b in batches:
        count = db.query(Proposal).filter(Proposal.batch_id == b.id).count()
        result.append({
            "id": b.id,
            "skill_id": b.skill_id,
            "window_start": b.window_start,
            "window_end": b.window_end,
            "status": b.status.value if b.status else "unknown",
            "resulting_version_id": b.resulting_version_id,
            "merge_log": b.merge_log or {},
            "proposal_count": count,
            "created_at": b.created_at,
        })
    return result

@router.get("/{batch_id}")
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    count = db.query(Proposal).filter(Proposal.batch_id == batch.id).count()
    proposals = db.query(Proposal).filter(Proposal.batch_id == batch.id).all()
    return {
        "id": batch.id,
        "skill_id": batch.skill_id,
        "window_start": batch.window_start,
        "window_end": batch.window_end,
        "status": batch.status.value if batch.status else "unknown",
        "resulting_version_id": batch.resulting_version_id,
        "merge_log": batch.merge_log or {},
        "proposal_count": count,
        "created_at": batch.created_at,
        "proposals": proposals,
        "audit_results": batch.audit_results or [],
    }

@router.get("/{batch_id}/logs", response_model=List[PipelineLogResponse])
def get_batch_logs(batch_id: str, db: Session = Depends(get_db)):
    logs = db.query(PipelineLog).filter(PipelineLog.batch_id == batch_id).all()
    return logs
