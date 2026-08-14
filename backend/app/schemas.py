"""
Pydantic schemas — request/response contracts for the API layer.

Naming convention:
  *Create   — POST request body
  *Update   — PATCH request body
  *Response — serialized API response
  *Detail   — response with nested relations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# Proposer
# ═══════════════════════════════════════════════════════════════════════════

class ProposerCreate(BaseModel):
    id: str
    display_name: str = ""
    is_agent: bool = False
    account_created_at: datetime
    project_stars: int = 0
    contribution_history: List[Dict[str, Any]] = []


class ProposerResponse(BaseModel):
    id: str
    display_name: str
    is_agent: bool = False
    account_created_at: datetime
    project_stars: int
    trust_score: float
    trust_score_updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════
# Version
# ═══════════════════════════════════════════════════════════════════════════

class VersionResponse(BaseModel):
    id: str
    skill_id: str
    parent_version_id: Optional[str] = None
    content: str
    created_at: datetime
    merge_batch_id: Optional[str] = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════
# Skill
# ═══════════════════════════════════════════════════════════════════════════

class SkillCreate(BaseModel):
    name: str
    description: str = ""
    category: str
    content: str                                    # initial version content
    source_repos: List[str] = []
    trigger_conditions: str = ""


class SkillResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    current_version_id: Optional[str] = None
    source_repos: List[str]
    trigger_conditions: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SkillDetail(SkillResponse):
    current_version: Optional[VersionResponse] = None
    version_count: int = 0
    usage_count: int = 0


class SkillListResponse(BaseModel):
    skills: List[SkillResponse]
    total: int
    categories: List[Dict[str, Any]]


# ═══════════════════════════════════════════════════════════════════════════
# Usage
# ═══════════════════════════════════════════════════════════════════════════

class UsageCreate(BaseModel):
    user_id: str


class UsageResponse(BaseModel):
    id: str
    skill_id: str
    version_id: str
    user_id: str
    used_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════
# Proposal
# ═══════════════════════════════════════════════════════════════════════════

class ProposalCreate(BaseModel):
    proposer_id: str
    proposal_type: str = "modification"             # "modification" | "issue_report"
    proposed_content: str = ""                       # full replacement (modification)
    diff_content: str = ""                           # unified diff (optional)
    issue_text: str = ""                             # free text (issue_report)
    is_agent: bool = False                           # True if submitted autonomously by AI agent
    tags: List[str] = []                             # e.g. ["autonomous_agent", "ai_generated"]
    agent_metadata: Dict[str, Any] = {}              # agent model, execution logs, feedback


class ProposalResponse(BaseModel):
    id: str
    skill_id: str
    target_version_id: str
    batch_id: Optional[str] = None
    proposer_id: str
    proposer_trust_snapshot: Dict[str, Any]
    is_agent: bool = False
    tags: List[str] = []
    agent_metadata: Dict[str, Any] = {}
    proposal_type: str
    diff_content: str
    proposed_content: str
    issue_text: str
    status: str
    submitted_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════
# Batch
# ═══════════════════════════════════════════════════════════════════════════

class BatchResponse(BaseModel):
    id: str
    skill_id: str
    window_start: datetime
    window_end: Optional[datetime] = None
    status: str
    resulting_version_id: Optional[str] = None
    merge_log: Dict[str, Any]
    proposal_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchDetailResponse(BatchResponse):
    proposals: List[ProposalResponse] = []
    audit_results: List["AuditResultResponse"] = []


# ═══════════════════════════════════════════════════════════════════════════
# Audit
# ═══════════════════════════════════════════════════════════════════════════

class AuditResultResponse(BaseModel):
    id: str
    proposal_id: str
    batch_id: str
    static_analysis_flags: List[Dict[str, Any]]
    semantic_diff_risk_score: float
    sandbox_canary_results: Dict[str, Any]
    sybil_flags: List[Dict[str, Any]]
    risk_verdict: str
    review_notes: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditReviewAction(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    reviewer_notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# Pipeline / Processing
# ═══════════════════════════════════════════════════════════════════════════

class BatchProcessRequest(BaseModel):
    """Manually trigger batch close + processing for a skill."""
    skill_id: str


class BatchProcessResponse(BaseModel):
    batch_id: str
    status: str
    merge_candidate_version_id: Optional[str] = None
    audit_summary: Dict[str, Any] = {}
    message: str = ""


class PipelineLogResponse(BaseModel):
    id: str
    batch_id: Optional[str]
    stage: str
    event_type: str
    payload: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════════
# Ingestion
# ═══════════════════════════════════════════════════════════════════════════

class IngestRequest(BaseModel):
    repo_url: str                                    # GitHub repo URL
    category: str = "general"


class IngestResponse(BaseModel):
    skill_id: str
    name: str
    category: str
    version_id: str
    message: str


class SeedResponse(BaseModel):
    skills_created: int
    skills: List[SkillResponse]


# ═══════════════════════════════════════════════════════════════════════════
# Stats / Dashboard
# ═══════════════════════════════════════════════════════════════════════════

class DashboardStats(BaseModel):
    total_skills: int
    total_versions: int
    total_proposals: int
    total_usage_events: int
    pending_proposals: int
    quarantined_proposals: int
    categories: Dict[str, int]                       # category → skill count


# ═══════════════════════════════════════════════════════════════════════════
# Execution Evidence & Real-World Benchmarks
# ═══════════════════════════════════════════════════════════════════════════

class ExecutionEvidenceCreate(BaseModel):
    skill_id: str
    version_id: Optional[str] = None
    skill_version_tag: str = "1.0.0"
    repository_name: str                             # e.g. "Rust compiler plugin"
    repository_url: Optional[str] = None
    ecosystem: Optional[str] = None                  # e.g. "rust", "python", "typescript"
    task_description: str                            # e.g. "Fix CI"
    task_category: Optional[str] = None
    outcome: str = "success"                         # success, failure, partial, timeout
    duration_seconds: float = 0.0                    # e.g. 180.0 (3 min)
    model_name: str = "GPT-5"
    cost_usd: float = 0.0                            # e.g. 0.19
    tokens_used: int = 0
    agent_id: str = "agent:autonomous-worker"
    is_agent: bool = True
    execution_logs: str = ""
    feedback_notes: str = ""
    metadata_json: Dict[str, Any] = {}


class ExecutionEvidenceResponse(BaseModel):
    id: str
    skill_id: str
    version_id: Optional[str] = None
    skill_version_tag: str
    repository_name: str
    repository_url: Optional[str] = None
    ecosystem: Optional[str] = None
    task_description: str
    task_category: Optional[str] = None
    outcome: str
    duration_seconds: float
    model_name: str
    cost_usd: float
    tokens_used: int
    agent_id: str
    is_agent: bool
    execution_logs: str
    feedback_notes: str
    metadata_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class SkillBenchmarkSummary(BaseModel):
    skill_id: str
    skill_name: str
    total_runs: int
    successful_runs: int
    success_rate: float                              # 0.0 to 1.0 (e.g. 0.96)
    avg_duration_seconds: float
    avg_cost_usd: float
    models_tested: List[str]
    repositories_tested: List[str]
    recent_evidences: List[ExecutionEvidenceResponse]


class TaskRankRequest(BaseModel):
    task: str                                        # e.g. "Fix CI on rust compiler plugin"
    repository_context: Optional[str] = None         # e.g. "Rust compiler plugin"
    ecosystem: Optional[str] = None                  # e.g. "rust"
    model: Optional[str] = None                      # e.g. "GPT-5"
    max_results: int = 3


class TaskRankResult(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    empirical_rank_score: float                      # Composite score (0.0 to 1.0)
    success_rate: float
    avg_duration_seconds: float
    avg_cost_usd: float
    evidence_count: int
    best_matching_evidence: Optional[ExecutionEvidenceResponse] = None
    recommended_version: str
    content_snippet: str
    reasoning: str


class TaskRankResponse(BaseModel):
    query_task: str
    repository_context: Optional[str] = None
    top_skill: Optional[TaskRankResult] = None
    ranked_skills: List[TaskRankResult]
    total_candidates_evaluated: int

