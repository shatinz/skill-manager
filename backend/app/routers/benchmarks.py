"""
Router: Real-World Execution Benchmarks & Task-Aware Empirical Skill Ranking
Provides evidence telemetry recording, skill benchmark aggregation, and autonomous task matching.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models import Skill, Version, ExecutionEvidence, ExecutionOutcome
from app.schemas import (
    ExecutionEvidenceCreate,
    ExecutionEvidenceResponse,
    SkillBenchmarkSummary,
    TaskRankRequest,
    TaskRankResponse,
    TaskRankResult
)

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.post("/evidence", response_model=ExecutionEvidenceResponse)
def record_execution_evidence(payload: ExecutionEvidenceCreate, db: Session = Depends(get_db)):
    """
    Record real-world agent execution evidence on a project task.
    Enables empirical performance tracking rather than arbitrary star counts.
    """
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        # Check by name
        skill = db.query(Skill).filter(Skill.name.ilike(f"%{payload.skill_id}%")).first()
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill '{payload.skill_id}' not found")

    version_id = payload.version_id or skill.current_version_id
    version_tag = payload.skill_version_tag
    if not version_tag and skill.current_version:
        version_tag = f"v{skill.current_version.id[:8]}"

    # Validate outcome enum
    outcome_str = payload.outcome.lower()
    try:
        outcome_enum = ExecutionOutcome(outcome_str)
    except ValueError:
        outcome_enum = ExecutionOutcome.SUCCESS

    evidence = ExecutionEvidence(
        skill_id=skill.id,
        version_id=version_id,
        skill_version_tag=version_tag or "1.0.0",
        repository_name=payload.repository_name,
        repository_url=payload.repository_url,
        ecosystem=payload.ecosystem or "",
        task_description=payload.task_description,
        task_category=payload.task_category or "",
        outcome=outcome_enum,
        duration_seconds=payload.duration_seconds,
        model_name=payload.model_name,
        cost_usd=payload.cost_usd,
        tokens_used=payload.tokens_used,
        agent_id=payload.agent_id,
        is_agent=payload.is_agent,
        execution_logs=payload.execution_logs,
        feedback_notes=payload.feedback_notes,
        metadata_json=payload.metadata_json or {}
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


@router.get("/skills/{skill_id}", response_model=SkillBenchmarkSummary)
def get_skill_benchmarks(skill_id: str, db: Session = Depends(get_db)):
    """
    Get aggregated real-world performance benchmarks for a given skill.
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        skill = db.query(Skill).filter(Skill.name.ilike(f"%{skill_id}%")).first()
        if not skill:
            raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")

    evidences = db.query(ExecutionEvidence).filter(ExecutionEvidence.skill_id == skill.id).order_by(desc(ExecutionEvidence.created_at)).all()
    
    total_runs = len(evidences)
    successful_runs = sum(1 for e in evidences if e.outcome == ExecutionOutcome.SUCCESS)
    success_rate = (successful_runs / total_runs) if total_runs > 0 else 1.0
    avg_duration = (sum(e.duration_seconds for e in evidences) / total_runs) if total_runs > 0 else 0.0
    avg_cost = (sum(e.cost_usd for e in evidences) / total_runs) if total_runs > 0 else 0.0
    
    models = list(set(e.model_name for e in evidences if e.model_name))
    repos = list(set(e.repository_name for e in evidences if e.repository_name))

    return SkillBenchmarkSummary(
        skill_id=skill.id,
        skill_name=skill.name,
        total_runs=total_runs,
        successful_runs=successful_runs,
        success_rate=round(success_rate, 4),
        avg_duration_seconds=round(avg_duration, 2),
        avg_cost_usd=round(avg_cost, 4),
        models_tested=models,
        repositories_tested=repos[:10],
        recent_evidences=evidences[:10]
    )


@router.get("/recent", response_model=List[ExecutionEvidenceResponse])
def get_recent_evidence_ledger(limit: int = Query(default=20, le=100), db: Session = Depends(get_db)):
    """
    List the most recent execution evidence records across all projects and agents.
    """
    evidences = db.query(ExecutionEvidence).order_by(desc(ExecutionEvidence.created_at)).limit(limit).all()
    return evidences


@router.post("/rank", response_model=TaskRankResponse)
def rank_skills_for_task(payload: TaskRankRequest, db: Session = Depends(get_db)):
    """
    Autonomous Task-Aware Empirical Skill Ranking Engine.
    Given a task description, repository context, and target model,
    ranks skills by real-world execution success, speed, cost, and relevance.
    """
    query_text = f"{payload.task} {payload.repository_context or ''} {payload.ecosystem or ''}".lower()
    skills = db.query(Skill).all()

    scored_candidates = []

    for skill in skills:
        # 1. Text Relevance Score
        skill_blob = f"{skill.name} {skill.description} {skill.category} {skill.trigger_conditions}".lower()
        query_words = [w for w in query_text.split() if len(w) > 2]
        match_count = sum(1 for w in query_words if w in skill_blob)
        relevance_score = match_count / max(1, len(query_words))

        # 2. Real-World Execution Evidence Telemetry
        evidences = db.query(ExecutionEvidence).filter(ExecutionEvidence.skill_id == skill.id).all()
        evidence_count = len(evidences)
        
        if evidence_count > 0:
            succ_count = sum(1 for e in evidences if e.outcome == ExecutionOutcome.SUCCESS)
            success_rate = succ_count / evidence_count
            avg_dur = sum(e.duration_seconds for e in evidences) / evidence_count
            avg_cost = sum(e.cost_usd for e in evidences) / evidence_count
            
            # Model compatibility bonus
            model_match = any(e.model_name.lower() == (payload.model or "").lower() and e.outcome == ExecutionOutcome.SUCCESS for e in evidences)
            model_bonus = 0.15 if model_match else 0.0

            # Repo context match bonus
            repo_match = any((payload.repository_context or "").lower() in e.repository_name.lower() for e in evidences)
            repo_bonus = 0.20 if repo_match else 0.0
            
            # Duration & cost efficiency penalties / bonuses
            dur_score = max(0.0, 1.0 - (avg_dur / 600.0))  # within 10 min
            cost_score = max(0.0, 1.0 - (avg_cost / 2.0))   # within $2.00
            
            empirical_score = (
                0.35 * relevance_score +
                0.35 * success_rate +
                0.10 * dur_score +
                0.10 * cost_score +
                model_bonus +
                repo_bonus
            )
        else:
            # Baseline when no empirical evidence recorded yet
            success_rate = 0.85
            avg_dur = 120.0
            avg_cost = 0.10
            empirical_score = 0.70 * relevance_score + 0.20

        # Best matching evidence
        best_ev = evidences[0] if evidences else None

        content_snippet = ""
        version_tag = "1.0.0"
        if skill.current_version:
            version_tag = f"v{skill.current_version.id[:8]}"
            content_snippet = skill.current_version.content[:350] + "..."

        reasoning = (
            f"Ranked based on {evidence_count} real-world execution runs (Success Rate: {int(success_rate*100)}%, "
            f"Avg MTTR: {round(avg_dur/60, 1)} min, Avg Cost: ${round(avg_cost, 2)})."
        )

        scored_candidates.append(
            TaskRankResult(
                skill_id=skill.id,
                skill_name=skill.name,
                category=skill.category,
                empirical_rank_score=round(empirical_score, 4),
                success_rate=round(success_rate, 4),
                avg_duration_seconds=round(avg_dur, 1),
                avg_cost_usd=round(avg_cost, 4),
                evidence_count=evidence_count,
                best_matching_evidence=best_ev,
                recommended_version=version_tag,
                content_snippet=content_snippet,
                reasoning=reasoning
            )
        )

    # Sort descending by empirical rank score
    scored_candidates.sort(key=lambda x: x.empirical_rank_score, reverse=True)
    top_results = scored_candidates[:payload.max_results]

    return TaskRankResponse(
        query_task=payload.task,
        repository_context=payload.repository_context,
        top_skill=top_results[0] if top_results else None,
        ranked_skills=top_results,
        total_candidates_evaluated=len(skills)
    )
