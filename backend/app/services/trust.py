import math
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import ProposerProfile
from app.config import settings

def compute_trust_score(profile: ProposerProfile) -> float:
    now = datetime.utcnow()
    age_days = (now - profile.account_created_at).days
    age_days = max(0, age_days)

    w_age = settings.trust_account_age_weight
    w_stars = settings.trust_project_stars_weight
    w_accepted = settings.trust_prior_accepted_weight

    age_score = math.log(1 + age_days) / math.log(1 + settings.trust_age_baseline_days)
    age_score = min(age_score, 1.0)

    stars = max(0, profile.project_stars)
    stars_score = math.log(1 + stars) / math.log(1 + settings.trust_stars_baseline)
    stars_score = min(stars_score, 1.0)

    # count prior accepted/merged proposals
    prior = 0
    if profile.contribution_history:
        for contrib in profile.contribution_history:
            if contrib.get("outcome") in ("accepted", "merged"):
                prior += 1
    
    accepted_score = min(prior / settings.trust_accepted_baseline, 1.0)

    trust = (w_age * age_score) + (w_stars * stars_score) + (w_accepted * accepted_score)
    return max(0.0, min(trust, 1.0))

def snapshot_trust_features(profile: ProposerProfile) -> dict:
    now = datetime.utcnow()
    age_days = max(0, (now - profile.account_created_at).days)
    prior = sum(1 for c in profile.contribution_history if c.get("outcome") in ("accepted", "merged")) if profile.contribution_history else 0

    return {
        "account_age_days": age_days,
        "project_stars": profile.project_stars,
        "prior_accepted": prior,
        "computed_score": compute_trust_score(profile)
    }

def update_trust_score(db: Session, proposer_id: str) -> float:
    profile = db.query(ProposerProfile).filter(ProposerProfile.id == proposer_id).first()
    if not profile:
        return 0.0
    
    score = compute_trust_score(profile)
    profile.trust_score = score
    profile.trust_score_updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return score
