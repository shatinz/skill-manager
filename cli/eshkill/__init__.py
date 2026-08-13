"""
eshkill — The Package Manager & Smart Search Engine for AI Agent Skills.
Connecting autonomous AI agents, Cursor, Claude, Antigravity, and vibe coders
to modular, community-driven skill capabilities.
"""

__version__ = "1.1.0"
__author__ = "Unified Agentic Skill Manager Team"

from typing import Optional, List, Dict, Any

from .models import (
    SkillSummary,
    SkillDetail,
    SearchResult,
    VaultIndex,
    RoutingDecision,
    InstallResult,
    ProposalPayload,
    ProposalResult,
    MCPToolCall,
    MCPToolResult
)
from .vault import VaultConnector
from .search import SmartSkillSearch
from .agent import AgentFormatter
from .router import AutoRouter
from .installer import SkillInstaller
from .propose import ProposalManager
from .mcp import MCPServer
from .server import run_server


class Eshkill:
    """Unified high-level facade for the eshkill skill ecosystem."""

    def __init__(self, source: Optional[str] = None):
        self.vault = VaultConnector(vault_path_or_url=source)
        self.search_engine = SmartSkillSearch(self.vault.load_index())
        self.router = AutoRouter(self.vault)
        self.installer = SkillInstaller(self.vault)
        self.proposer = ProposalManager(self.vault)
        self.formatter = AgentFormatter()

    def search(self, query: str, category: Optional[str] = None, subcategory: Optional[str] = None, tag: Optional[str] = None, top_k: int = 5) -> List[SearchResult]:
        """Search skills by query, intent, or tags."""
        return self.search_engine.search(query=query, category=category, subcategory=subcategory, tag=tag, top_k=top_k)

    def route(self, prompt: str, max_skills: int = 3) -> RoutingDecision:
        """Autonomous vibe-coding router: detects stack and orchestrates top complementary skills."""
        return self.router.route(prompt=prompt, max_skills=max_skills)

    def match(self, task: str) -> Optional[SearchResult]:
        """Find the single best matching skill for a task."""
        return self.search_engine.find_best_match(task)

    def get(self, skill_id_or_name: str) -> SkillDetail:
        """Fetch skill markdown and metadata on-demand."""
        return self.vault.get_skill(skill_id_or_name)

    def install(self, skill_id_or_name: str, mode: str = "workspace", workspace_dir: Optional[str] = None) -> InstallResult:
        """Install skill to local workspace, global config, or temp directory."""
        return self.installer.install(skill_id_or_name=skill_id_or_name, mode=mode, workspace_dir=workspace_dir)

    def propose(self, skill_id: str, proposed_content: str, reason: str = "", proposer_id: str = "agent_client") -> ProposalResult:
        """Propose an update or bugfix to an existing skill."""
        return self.proposer.submit_proposal(skill_id=skill_id, proposed_content=proposed_content, reason=reason, proposer_id=proposer_id)

    def categories(self) -> Dict[str, Dict[str, List[str]]]:
        """List all category trees."""
        return self.vault.list_categories()


__all__ = [
    "Eshkill",
    "VaultConnector",
    "SmartSkillSearch",
    "AgentFormatter",
    "MCPServer",
    "AutoRouter",
    "SkillInstaller",
    "ProposalManager",
    "run_server",
    "SkillSummary",
    "SkillDetail",
    "SearchResult",
    "VaultIndex",
    "RoutingDecision",
    "InstallResult",
    "ProposalPayload",
    "ProposalResult",
    "MCPToolCall",
    "MCPToolResult",
    "__version__"
]
