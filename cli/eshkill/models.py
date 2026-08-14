"""
Data models and schemas for eshkill.
Supports both standard Python dataclasses for zero-dependency operation and Pydantic if available.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


@dataclass
class SkillSummary:
    id: str
    name: str
    title: str
    category: str
    subcategory: str
    version: str
    tags: List[str] = field(default_factory=list)
    trust_rating: float = 0.90
    estimated_tokens: int = 1000
    description: str = ""
    trigger_patterns: List[str] = field(default_factory=list)
    relative_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillSummary':
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            title=data.get("title", data.get("name", "")),
            category=data.get("category", ""),
            subcategory=data.get("subcategory", ""),
            version=data.get("version", "1.0.0"),
            tags=list(data.get("tags", [])),
            trust_rating=float(data.get("trust_rating", 0.9)),
            estimated_tokens=int(data.get("estimated_tokens", 1000)),
            description=data.get("description", ""),
            trigger_patterns=list(data.get("trigger_patterns", [])),
            relative_path=data.get("relative_path", "")
        )


@dataclass
class SkillDetail(SkillSummary):
    content: str = ""
    raw_frontmatter: Dict[str, Any] = field(default_factory=dict)
    source_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillDetail':
        summary = SkillSummary.from_dict(data)
        return cls(
            id=summary.id,
            name=summary.name,
            title=summary.title,
            category=summary.category,
            subcategory=summary.subcategory,
            version=summary.version,
            tags=summary.tags,
            trust_rating=summary.trust_rating,
            estimated_tokens=summary.estimated_tokens,
            description=summary.description,
            trigger_patterns=summary.trigger_patterns,
            relative_path=summary.relative_path,
            content=data.get("content", ""),
            raw_frontmatter=data.get("raw_frontmatter", {}),
            source_url=data.get("source_url", "")
        )


@dataclass
class SearchResult:
    skill: SkillSummary
    score: float
    matched_triggers: List[str] = field(default_factory=list)
    matched_tags: List[str] = field(default_factory=list)
    match_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.skill.id,
            "name": self.skill.name,
            "title": self.skill.title,
            "category": self.skill.category,
            "subcategory": self.skill.subcategory,
            "version": self.skill.version,
            "score": round(self.score, 4),
            "trust_rating": self.skill.trust_rating,
            "estimated_tokens": self.skill.estimated_tokens,
            "description": self.skill.description,
            "matched_triggers": self.matched_triggers,
            "matched_tags": self.matched_tags,
            "match_reasons": self.match_reasons
        }


@dataclass
class VaultIndex:
    version: str
    vault_name: str
    total_skills: int
    categories: Dict[str, Dict[str, List[str]]]
    skills: List[SkillSummary]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "vault_name": self.vault_name,
            "total_skills": self.total_skills,
            "categories": self.categories,
            "skills": [s.to_dict() for s in self.skills]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VaultIndex':
        skills = [
            SkillSummary.from_dict(s)
            for s in data.get("skills", [])
        ]
        return cls(
            version=data.get("version", "1.0.0"),
            vault_name=data.get("vault_name", "Public Agentic Skill Vault"),
            total_skills=len(skills),
            categories=data.get("categories", {}),
            skills=skills
        )


@dataclass
class RoutingDecision:
    prompt: str
    detected_stack: List[str]
    detected_intents: List[str]
    selected_skills: List[SkillDetail]
    match_scores: Dict[str, float]
    routing_reasons: List[str]
    unified_payload: str
    total_estimated_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "detected_stack": self.detected_stack,
            "detected_intents": self.detected_intents,
            "selected_skills": [s.to_dict() for s in self.selected_skills],
            "match_scores": self.match_scores,
            "routing_reasons": self.routing_reasons,
            "unified_payload": self.unified_payload,
            "total_estimated_tokens": self.total_estimated_tokens
        }


@dataclass
class InstallResult:
    success: bool
    skill_id: str
    mode: str  # 'workspace' | 'global' | 'temp'
    target_path: str
    message: str
    ephemeral_content: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProposalPayload:
    skill_id: str
    proposer_id: str
    proposal_type: str = "modification"  # 'modification' | 'issue_report' | 'new_skill'
    proposed_content: Optional[str] = None
    diff_text: Optional[str] = None
    reason: str = ""
    author_github: Optional[str] = None
    is_agent: bool = False
    tags: List[str] = field(default_factory=list)
    agent_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProposalResult:
    success: bool
    message: str
    proposal_id: Optional[str] = None
    status: str = "pending"
    pr_url: Optional[str] = None
    patch_file: Optional[str] = None
    is_agent: bool = False
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# MCP (Model Context Protocol) Schemas
@dataclass
class MCPToolCall:
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPToolResult:
    content: List[Dict[str, Any]]
    is_error: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "isError": self.is_error
        }
