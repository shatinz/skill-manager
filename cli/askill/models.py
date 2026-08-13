"""
Data models and schemas for askill.
Supports both Pydantic (if available) and standard Python dataclasses for zero-dependency operation.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

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

@dataclass
class SkillDetail(SkillSummary):
    content: str = ""
    raw_frontmatter: Dict[str, Any] = field(default_factory=dict)
    source_url: str = ""

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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VaultIndex':
        skills = [
            SkillSummary(
                id=s.get("id", ""),
                name=s.get("name", ""),
                title=s.get("title", s.get("name", "")),
                category=s.get("category", ""),
                subcategory=s.get("subcategory", ""),
                version=s.get("version", "1.0.0"),
                tags=s.get("tags", []),
                trust_rating=float(s.get("trust_rating", 0.9)),
                estimated_tokens=int(s.get("estimated_tokens", 1000)),
                description=s.get("description", ""),
                trigger_patterns=s.get("trigger_patterns", []),
                relative_path=s.get("relative_path", "")
            )
            for s in data.get("skills", [])
        ]
        return cls(
            version=data.get("version", "1.0.0"),
            vault_name=data.get("vault_name", "Public Skill Vault"),
            total_skills=len(skills),
            categories=data.get("categories", {}),
            skills=skills
        )

@dataclass
class ProposalPayload:
    skill_id: str
    proposer_id: str
    proposal_type: str  # 'modification' | 'issue_report' | 'new_skill'
    proposed_content: Optional[str] = None
    diff_text: Optional[str] = None
    reason: str = ""
    author_github: Optional[str] = None

@dataclass
class ProposalResult:
    success: bool
    message: str
    proposal_id: Optional[str] = None
    status: str = "pending"
    pr_url: Optional[str] = None
    patch_file: Optional[str] = None
