"""
Configuration — all tunable parameters in one place.

Every knob the spec mentions (batch window, trust weights, audit thresholds,
LLM provider) lives here so nothing is hardcoded in service logic.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Central configuration, overridable via env vars or .env file."""

    # ── Database ────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./skill_manager.db"

    # ── Batch Processing (Stage C) ──────────────────────────────────────
    batch_window_hours: float = 24.0          # close batch after this many hours
    batch_min_proposals: int = 1              # min proposals before a batch *can* close
    batch_max_proposals: int = 100            # force-close at this count

    # ── Trust Score Weights (Stage D input) ─────────────────────────────
    #    Raw formula (v1):
    #      trust = w_age * log(1+age_days) / log(1+365)
    #            + w_stars * log(1+stars) / log(1+10000)
    #            + w_accepted * min(prior_accepted / 20, 1.0)
    trust_account_age_weight: float = 0.25
    trust_project_stars_weight: float = 0.25
    trust_prior_accepted_weight: float = 0.50
    trust_age_baseline_days: int = 365        # "fully mature" account age
    trust_stars_baseline: int = 10000         # "fully proven" star count
    trust_accepted_baseline: int = 20         # "fully established" accepted count

    # ── Nonlinear Scoring (Stage D) ─────────────────────────────────────
    #    cluster_weight = sum(trust_i) * (1 + ln(cluster_size) * redundancy_mult)
    #    effective_weight = cluster_weight * (1 - disruptiveness * dampen(avg_trust))
    #    dampen(t) = high_dampener if t >= threshold else low_dampener
    redundancy_trust_multiplier: float = 1.5
    disruptiveness_low_trust_dampener: float = 0.7   # strong dampening
    disruptiveness_high_trust_dampener: float = 0.2   # mild dampening
    disruptiveness_trust_threshold: float = 0.5

    # ── Security Audit (Stage E) ────────────────────────────────────────
    audit_risk_threshold: float = 0.7         # above → suspicious
    sybil_account_age_threshold_days: int = 30
    sybil_timing_cluster_window_minutes: int = 60
    sybil_min_cluster_size: int = 2           # need ≥2 new accounts within window

    # ── LLM ─────────────────────────────────────────────────────────────
    llm_provider: str = "mock"                # "openai" | "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"

    # ── Vector / Similarity ─────────────────────────────────────────────
    similarity_threshold: float = 0.6         # cosine-sim above this → "redundant"

    # ── Server ──────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["*"]

    model_config = {"env_file": ".env", "env_prefix": "SKM_"}


settings = Settings()
