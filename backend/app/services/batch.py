from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Batch, BatchStatus, Proposal, ProposalStatus, Version, PipelineLog
from app.config import settings
from app.services import clustering, weighting, merge
from app.schemas import BatchProcessResponse

def get_or_create_batch(db: Session, skill_id: str) -> Batch:
    """Find the current ACCUMULATING batch for a skill, or create one."""
    batch = db.query(Batch).filter(
        Batch.skill_id == skill_id,
        Batch.status == BatchStatus.ACCUMULATING
    ).first()
    
    if not batch:
        batch = Batch(
            skill_id=skill_id,
            window_start=datetime.utcnow()
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
    return batch

def check_batch_ready(db: Session, batch: Batch) -> bool:
    """True if window expired OR max proposals reached."""
    proposal_count = db.query(Proposal).filter(
        Proposal.batch_id == batch.id,
        Proposal.status == ProposalStatus.PENDING
    ).count()
    
    if proposal_count >= settings.batch_max_proposals:
        return True
        
    time_elapsed = datetime.utcnow() - batch.window_start
    if time_elapsed.total_seconds() >= settings.batch_window_hours * 3600:
        if proposal_count >= settings.batch_min_proposals:
            return True
            
    return False

def close_and_process_batch(db: Session, batch_id: str) -> BatchProcessResponse:
    """THE main pipeline orchestrator for processing a batch of proposals."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise ValueError("Batch not found")
        
    # 1. Close the batch window
    batch.status = BatchStatus.PROCESSING
    batch.window_end = datetime.utcnow()
    db.commit()
    
    # 2. Fetch all PENDING proposals in the batch
    proposals = db.query(Proposal).filter(
        Proposal.batch_id == batch.id,
        Proposal.status == ProposalStatus.PENDING
    ).all()
    
    if not proposals:
        batch.status = BatchStatus.COMPLETED
        db.commit()
        return BatchProcessResponse(
            batch_id=batch.id,
            status=batch.status.value,
            message="No pending proposals to process"
        )
        
    skill = batch.skill
    current_version = skill.current_version
    current_content = current_version.content if current_version else ""
    
    # 3. Call clustering.cluster_proposals
    clusters = clustering.cluster_proposals(proposals, settings.similarity_threshold)
    db.add(PipelineLog(batch_id=batch.id, stage="clustering", event_type="cluster_formed", payload={"cluster_count": len(clusters)}))
    
    # 4. Call weighting.rank_clusters + resolve_conflicts
    ranked = weighting.rank_clusters(clusters, current_content)
    resolved = weighting.resolve_conflicts(ranked)
    
    db.add(PipelineLog(batch_id=batch.id, stage="weighting", event_type="score_computed", payload={"ranked_count": len(ranked), "resolved_count": len(resolved)}))
    
    # 5. Call merge.synthesize_merge
    merged_content = merge.synthesize_merge(current_content, resolved, skill.name)
    
    db.add(PipelineLog(batch_id=batch.id, stage="merge", event_type="merge_output", payload={"content_length": len(merged_content)}))
    
    # 6. Create a new Version with the merge output
    new_version = Version(
        skill_id=skill.id,
        parent_version_id=current_version.id if current_version else None,
        content=merged_content,
        merge_batch_id=batch.id
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    
    # Update batch
    batch.resulting_version_id = new_version.id
    batch.merge_log = {
        "resolved_clusters": [
            {
                "centroid_text": c[0].centroid_text,
                "weight": c[1].effective_weight,
                "reasoning": c[1].reasoning,
                "proposals_count": c[0].cluster_size
            }
            for c in resolved
        ]
    }
    db.commit()
    
    return BatchProcessResponse(
        batch_id=batch.id,
        status=batch.status.value,
        merge_candidate_version_id=new_version.id,
        message="Batch processed and candidate version created for audit"
    )

def force_close_batch(db: Session, skill_id: str) -> str:
    """Manually close the current batch and trigger processing."""
    batch = get_or_create_batch(db, skill_id)
    batch.window_end = datetime.utcnow()
    db.commit()
    return batch.id
