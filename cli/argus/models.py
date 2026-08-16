"""
Argus Data Models.
Defines core data structures for Multi-Repository Skill Proxying,
Goal-Aware Semantic Matching, Format Normalization, and Compatibility Evaluation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Set, Optional, Any
import time


class SourceType(str, Enum):
    LOCAL_DIR = "local_dir"
    GIT_REPO = "git_repo"
    HTTP_REGISTRY = "http_registry"
    ANTIGRAVITY_SYSTEM = "antigravity_system"
    CURSOR_RULES = "cursor_rules"
    CLAUDE_PROMPTS = "claude_prompts"
    MCP_REGISTRY = "mcp_registry"
    BUILTIN_VAULT = "builtin_vault"


class SkillFormat(str, Enum):
    ANTIGRAVITY_SKILL = "antigravity_skill"      # SKILL.md with YAML frontmatter + scripts + refs
    CURSOR_MDC = "cursor_mdc"                    # .cursor/rules/*.mdc or .cursorrules
    ANTHROPIC_CLAUDE = "anthropic_claude"        # XML/Markdown prompt / skill
    OPENAI_GPT = "openai_gpt"                    # Instructions / Tool schema
    COPILOT_INSTRUCTION = "copilot_instruction"  # .github/copilot-instructions.md
    GENERIC_MARKDOWN = "generic_markdown"        # Markdown guide / cheat-sheet
    MCP_TOOLSET = "mcp_toolset"                  # MCP tool definitions


@dataclass
class SkillSource:
    id: str
    name: str
    source_type: SourceType
    location: str  # Path or URL
    enabled: bool = True
    priority: int = 100  # Higher = preferred
    trust_score: float = 1.0  # 0.0 - 1.0
    branch: Optional[str] = None
    last_synced: Optional[float] = None
    skill_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source_type": self.source_type.value if isinstance(self.source_type, SourceType) else self.source_type,
            "location": self.location,
            "enabled": self.enabled,
            "priority": self.priority,
            "trust_score": self.trust_score,
            "branch": self.branch,
            "last_synced": self.last_synced,
            "skill_count": self.skill_count,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillSource":
        stype = data.get("source_type", SourceType.LOCAL_DIR.value)
        if isinstance(stype, str):
            try:
                stype = SourceType(stype)
            except ValueError:
                stype = SourceType.LOCAL_DIR
        return cls(
            id=data["id"],
            name=data["name"],
            source_type=stype,
            location=data["location"],
            enabled=data.get("enabled", True),
            priority=data.get("priority", 100),
            trust_score=data.get("trust_score", 1.0),
            branch=data.get("branch"),
            last_synced=data.get("last_synced"),
            skill_count=data.get("skill_count", 0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SkillPackage:
    id: str  # e.g. "threejs-scene-craft"
    source_id: str  # ID of the repo / vault source
    name: str
    format: SkillFormat
    description: str
    category: str
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = "community"
    capabilities: List[str] = field(default_factory=list)
    compatible_frameworks: List[str] = field(default_factory=list)  # e.g. ["react", "vite", "nextjs", "threejs"]
    conflicts_with: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    actionability_score: float = 0.9  # How concrete/runnable code vs docs
    file_path: Optional[str] = None
    raw_content: Optional[str] = None
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def qualified_id(self) -> str:
        """Fully qualified ID including source, e.g. 'antigravity:3d-graphics/img2threejs'"""
        return f"{self.source_id}:{self.id}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "qualified_id": self.qualified_id,
            "source_id": self.source_id,
            "name": self.name,
            "format": self.format.value if isinstance(self.format, SkillFormat) else self.format,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "version": self.version,
            "author": self.author,
            "capabilities": self.capabilities,
            "compatible_frameworks": self.compatible_frameworks,
            "conflicts_with": self.conflicts_with,
            "required_tools": self.required_tools,
            "actionability_score": self.actionability_score,
            "file_path": self.file_path,
            "token_count": self.token_count,
            "metadata": self.metadata,
        }


@dataclass
class GoalAnalysis:
    """Deconstructed user prompt goal."""
    raw_prompt: str
    primary_goal: str
    deliverable_type: str  # e.g. "3d_web_application", "rest_api", "agent_workflow", "fullstack_dashboard"
    target_domains: List[str] = field(default_factory=list)  # e.g. ["3d-graphics", "web-frontend", "animation"]
    detected_frameworks: List[str] = field(default_factory=list)  # e.g. ["threejs", "react", "tailwind"]
    inferred_needs: List[str] = field(default_factory=list)  # e.g. ["canvas_host", "3d_mesh_loader", "responsive_controls"]
    complexity_level: str = "intermediate"  # simple, intermediate, complex
    constraints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_prompt": self.raw_prompt,
            "primary_goal": self.primary_goal,
            "deliverable_type": self.deliverable_type,
            "target_domains": self.target_domains,
            "detected_frameworks": self.detected_frameworks,
            "inferred_needs": self.inferred_needs,
            "complexity_level": self.complexity_level,
            "constraints": self.constraints,
        }


@dataclass
class SkillGoalMatch:
    """Ranked skill match for a specific user goal."""
    skill: SkillPackage
    goal_relevancy_score: float  # 0.0 - 1.0 (How directly it satisfies the prompt's goal)
    capability_fit_score: float  # 0.0 - 1.0 (Actionable implementation vs passive info)
    compatibility_score: float   # 0.0 - 1.0 (Synergy with stack & other recommended skills)
    provenance_trust_score: float  # 0.0 - 1.0 (Source reputation & quality)
    composite_rank_score: float    # Combined weighted score
    goal_role: str                 # e.g. "Primary 3D Engine", "UI Canvas Host", "Styling & Responsive Shell"
    goal_alignment_reason: str     # Explanation of why this skill fits the user prompt's goal
    synergy_skills: List[str] = field(default_factory=list)
    confidence: str = "high"       # high, medium, low

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill": self.skill.to_dict(),
            "goal_relevancy_score": round(self.goal_relevancy_score, 4),
            "capability_fit_score": round(self.capability_fit_score, 4),
            "compatibility_score": round(self.compatibility_score, 4),
            "provenance_trust_score": round(self.provenance_trust_score, 4),
            "composite_rank_score": round(self.composite_rank_score, 4),
            "goal_role": self.goal_role,
            "goal_alignment_reason": self.goal_alignment_reason,
            "synergy_skills": self.synergy_skills,
            "confidence": self.confidence,
        }


@dataclass
class ArgusBundle:
    """Complete goal-oriented skill bundle crafted for an AI Agent."""
    prompt: str
    goal_analysis: GoalAnalysis
    selected_matches: List[SkillGoalMatch]
    sources_queried: List[str]
    total_skills_evaluated: int
    compiled_agent_instructions: str
    framework_stack: List[str]
    warnings_or_conflicts: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "goal_analysis": self.goal_analysis.to_dict(),
            "selected_matches": [m.to_dict() for m in self.selected_matches],
            "sources_queried": self.sources_queried,
            "total_skills_evaluated": self.total_skills_evaluated,
            "framework_stack": self.framework_stack,
            "warnings_or_conflicts": self.warnings_or_conflicts,
            "compiled_agent_instructions_len": len(self.compiled_agent_instructions),
            "created_at": self.created_at,
        }
