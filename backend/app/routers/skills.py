from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Skill, Version, UsageEvent
from app.schemas import SkillListResponse, SkillDetail, VersionResponse, UsageCreate, UsageResponse

router = APIRouter(prefix="/skills", tags=["skills"])

@router.get("/", response_model=SkillListResponse)
def list_skills(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    if search:
        search_term = f"%{search}%"
        query = query.filter(Skill.name.ilike(search_term) | Skill.description.ilike(search_term))
    
    skills = query.all()
    total = len(skills)
    
    from sqlalchemy import func
    cat_counts = db.query(Skill.category, func.count(Skill.id)).group_by(Skill.category).all()
    categories = [{"category": c[0], "count": c[1]} for c in cat_counts]

    return {
        "skills": skills,
        "total": total,
        "categories": categories
    }

@router.get("/categories/list", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Skill.category).distinct().all()
    return [c[0] for c in cats]

@router.get("/{skill_id}", response_model=SkillDetail)
def get_skill(skill_id: str, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    version_count = db.query(Version).filter(Version.skill_id == skill_id).count()
    usage_count = db.query(UsageEvent).filter(UsageEvent.skill_id == skill_id).count()
    
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "category": skill.category,
        "current_version_id": skill.current_version_id,
        "source_repos": skill.source_repos,
        "trigger_conditions": skill.trigger_conditions,
        "created_at": skill.created_at,
        "updated_at": skill.updated_at,
        "current_version": skill.current_version,
        "version_count": version_count,
        "usage_count": usage_count
    }

@router.get("/{skill_id}/versions", response_model=List[VersionResponse])
def list_versions(skill_id: str, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    versions = db.query(Version).filter(Version.skill_id == skill_id).order_by(Version.created_at.desc()).all()
    return versions

@router.post("/{skill_id}/use", response_model=UsageResponse)
def log_usage(skill_id: str, usage: UsageCreate, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    if not skill.current_version_id:
        raise HTTPException(status_code=400, detail="Skill has no current version")
        
    usage_event = UsageEvent(
        skill_id=skill_id,
        version_id=skill.current_version_id,
        user_id=usage.user_id
    )
    db.add(usage_event)
    db.commit()
    db.refresh(usage_event)
    return usage_event
