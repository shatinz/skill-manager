"""
Argus: The Multi-Repository Skill Search Engine & Proxy for AI Agents.
"""

from .models import (
    SkillSource,
    SkillPackage,
    GoalAnalysis,
    SkillGoalMatch,
    ArgusBundle,
    SourceType,
    SkillFormat
)
from .proxy import ArgusProxy
from .engine import GoalAnalyzer, ArgusSearchIndex
from .ranker import GoalAwareRanker
from .sources import SourceManager

__version__ = "1.0.0"
__all__ = [
    "ArgusProxy",
    "SourceManager",
    "GoalAnalyzer",
    "GoalAwareRanker",
    "ArgusSearchIndex",
    "SkillSource",
    "SkillPackage",
    "GoalAnalysis",
    "SkillGoalMatch",
    "ArgusBundle",
    "SourceType",
    "SkillFormat"
]
