"""
SQLAlchemy ORM models — the canonical data model for the entire system.

Tables:
  skills             — normalized skill records
  versions           — immutable content snapshots (append-only lineage)
  proposals          — diffs / issue reports against a live version
  batches            — processing windows that group proposals
  audit_results      — per-proposal security audit verdicts
  proposer_profiles  — trust-relevant identity data
  usage_events       — logged skill-usage events (training data)
  pipeline_logs      — raw logs of every scoring/merge decision (future model training)

Circular FK handling:
  Skill.current_version_id → Version.id  (use_alter for deferred FK)
  Version.merge_batch_id   → Batch.id    (use_alter for deferred FK)
"""

from datetime import datetime
from uuid import uuid4
import enum

from sqlalchemy import (
    Column, String, Text, Float, Integer, DateTime,
    Enum, JSON, ForeignKey, Boolean, Index,
)
from sqlalchemy.orm import relationship, DeclarativeBase


def _uuid() -> str:
    return str(uuid4())


# ═══════════════════════════════════════════════════════════════════════════
# Base
# ═══════════════════════════════════════════════════════════════════════════

class Base(DeclarativeBase):
    pass


# ═══════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════

class ProposalStatus(str, enum.Enum):
    PENDING     = "pending"
    MERGED      = "merged"
    QUARANTINED = "quarantined"
    REJECTED    = "rejected"


class ProposalType(str, enum.Enum):
    MODIFICATION = "modification"
    ISSUE_REPORT = "issue_report"


class BatchStatus(str, enum.Enum):
    ACCUMULATING = "accumulating"
    PROCESSING   = "processing"
    COMPLETED    = "completed"
    FAILED       = "failed"


class RiskVerdict(str, enum.Enum):
    CLEAN      = "clean"
    SUSPICIOUS = "suspicious"


# ═══════════════════════════════════════════════════════════════════════════
# Skill
# ═══════════════════════════════════════════════════════════════════════════

class Skill(Base):
    __tablename__ = "skills"

    id                  = Column(String, primary_key=True, default=_uuid)
    name                = Column(String(256), nullable=False, index=True)
    description         = Column(Text, default="")
    category            = Column(String(128), nullable=False, index=True)
    current_version_id  = Column(
        String,
        ForeignKey("versions.id", use_alter=True, name="fk_skill_current_version"),
        nullable=True,
    )
    source_repos        = Column(JSON, default=list)
    trigger_conditions  = Column(Text, default="")
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    current_version = relationship(
        "Version", foreign_keys=[current_version_id], post_update=True,
    )
    versions     = relationship("Version",  foreign_keys="Version.skill_id",    back_populates="skill", order_by="Version.created_at")
    proposals    = relationship("Proposal", back_populates="skill",             order_by="Proposal.submitted_at")
    usage_events = relationship("UsageEvent", back_populates="skill")
    batches      = relationship("Batch",    back_populates="skill",             order_by="Batch.created_at")


# ═══════════════════════════════════════════════════════════════════════════
# Version  (immutable — append-only lineage)
# ═══════════════════════════════════════════════════════════════════════════

class Version(Base):
    __tablename__ = "versions"

    id                = Column(String, primary_key=True, default=_uuid)
    skill_id          = Column(String, ForeignKey("skills.id"), nullable=False, index=True)
    parent_version_id = Column(String, ForeignKey("versions.id"), nullable=True)
    content           = Column(Text, nullable=False)
    created_at        = Column(DateTime, default=datetime.utcnow)
    merge_batch_id    = Column(
        String,
        ForeignKey("batches.id", use_alter=True, name="fk_version_merge_batch"),
        nullable=True,
    )

    # relationships
    skill          = relationship("Skill",   foreign_keys=[skill_id], back_populates="versions")
    parent_version = relationship("Version", remote_side=[id], foreign_keys=[parent_version_id])
    merge_batch    = relationship("Batch",   foreign_keys=[merge_batch_id])


# ═══════════════════════════════════════════════════════════════════════════
# Proposal
# ═══════════════════════════════════════════════════════════════════════════

class Proposal(Base):
    __tablename__ = "proposals"

    id                = Column(String, primary_key=True, default=_uuid)
    skill_id          = Column(String, ForeignKey("skills.id"), nullable=False, index=True)
    target_version_id = Column(String, ForeignKey("versions.id"), nullable=False)
    batch_id          = Column(String, ForeignKey("batches.id"), nullable=True, index=True)

    # Proposer identity & trust features (snapshotted at submission time)
    proposer_id               = Column(String, ForeignKey("proposer_profiles.id"), nullable=False, index=True)
    proposer_trust_snapshot    = Column(JSON, default=dict)   # raw feature dict logged for future model training

    # Content
    proposal_type     = Column(Enum(ProposalType), nullable=False, default=ProposalType.MODIFICATION)
    diff_content      = Column(Text, default="")              # unified diff
    proposed_content  = Column(Text, default="")              # full replacement text (for modifications)
    issue_text        = Column(Text, default="")              # free-text (for issue reports)

    # Status
    status            = Column(Enum(ProposalStatus), nullable=False, default=ProposalStatus.PENDING)
    submitted_at      = Column(DateTime, default=datetime.utcnow)

    # relationships
    skill          = relationship("Skill",   back_populates="proposals")
    target_version = relationship("Version", foreign_keys=[target_version_id])
    proposer       = relationship("ProposerProfile", back_populates="proposals")
    audit_result   = relationship("AuditResult", back_populates="proposal", uselist=False)


# ═══════════════════════════════════════════════════════════════════════════
# Batch
# ═══════════════════════════════════════════════════════════════════════════

class Batch(Base):
    __tablename__ = "batches"

    id                   = Column(String, primary_key=True, default=_uuid)
    skill_id             = Column(String, ForeignKey("skills.id"), nullable=False, index=True)
    window_start         = Column(DateTime, nullable=False)
    window_end           = Column(DateTime, nullable=True)
    status               = Column(Enum(BatchStatus), nullable=False, default=BatchStatus.ACCUMULATING)
    resulting_version_id = Column(String, ForeignKey("versions.id"), nullable=True)
    merge_log            = Column(JSON, default=dict)      # full scoring/clustering/merge log → training data
    created_at           = Column(DateTime, default=datetime.utcnow)

    # relationships
    skill             = relationship("Skill",    back_populates="batches")
    resulting_version = relationship("Version",  foreign_keys=[resulting_version_id])
    proposals         = relationship("Proposal", backref="batch", foreign_keys="Proposal.batch_id")
    audit_results     = relationship("AuditResult", back_populates="batch")


# ═══════════════════════════════════════════════════════════════════════════
# AuditResult
# ═══════════════════════════════════════════════════════════════════════════

class AuditResult(Base):
    __tablename__ = "audit_results"

    id                       = Column(String, primary_key=True, default=_uuid)
    proposal_id              = Column(String, ForeignKey("proposals.id"), nullable=False, unique=True)
    batch_id                 = Column(String, ForeignKey("batches.id"), nullable=False, index=True)
    static_analysis_flags    = Column(JSON, default=list)
    semantic_diff_risk_score = Column(Float, default=0.0)
    sandbox_canary_results   = Column(JSON, default=dict)
    sybil_flags              = Column(JSON, default=list)
    risk_verdict             = Column(Enum(RiskVerdict), nullable=False, default=RiskVerdict.CLEAN)
    review_notes             = Column(Text, default="")
    created_at               = Column(DateTime, default=datetime.utcnow)

    # relationships
    proposal = relationship("Proposal", back_populates="audit_result")
    batch    = relationship("Batch",    back_populates="audit_results")


# ═══════════════════════════════════════════════════════════════════════════
# ProposerProfile
# ═══════════════════════════════════════════════════════════════════════════

class ProposerProfile(Base):
    __tablename__ = "proposer_profiles"

    id                     = Column(String, primary_key=True)  # e.g. github username or generated id
    display_name           = Column(String(256), default="")
    account_created_at     = Column(DateTime, nullable=False)
    project_stars          = Column(Integer, default=0)
    contribution_history   = Column(JSON, default=list)        # [{skill_id, proposal_id, outcome, timestamp}]
    trust_score            = Column(Float, default=0.0)
    trust_score_updated_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    proposals = relationship("Proposal", back_populates="proposer")


# ═══════════════════════════════════════════════════════════════════════════
# UsageEvent  (Stage B — logged usage for training data)
# ═══════════════════════════════════════════════════════════════════════════

class UsageEvent(Base):
    __tablename__ = "usage_events"

    id         = Column(String, primary_key=True, default=_uuid)
    skill_id   = Column(String, ForeignKey("skills.id"), nullable=False, index=True)
    version_id = Column(String, ForeignKey("versions.id"), nullable=False)
    user_id    = Column(String, nullable=False)
    used_at    = Column(DateTime, default=datetime.utcnow)

    # relationships
    skill   = relationship("Skill", back_populates="usage_events")
    version = relationship("Version")


# ═══════════════════════════════════════════════════════════════════════════
# PipelineLog  (generous logging for future model training)
# ═══════════════════════════════════════════════════════════════════════════

class PipelineLog(Base):
    __tablename__ = "pipeline_logs"

    id         = Column(String, primary_key=True, default=_uuid)
    batch_id   = Column(String, ForeignKey("batches.id"), nullable=True, index=True)
    stage      = Column(String(64), nullable=False, index=True)   # e.g. "clustering", "weighting", "merge", "audit"
    event_type = Column(String(64), nullable=False)                # e.g. "cluster_formed", "score_computed", "merge_output"
    payload    = Column(JSON, default=dict)                        # arbitrary structured data
    created_at = Column(DateTime, default=datetime.utcnow)
