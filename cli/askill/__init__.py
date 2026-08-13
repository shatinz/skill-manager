"""
askill — Backwards compatibility wrapper for eshkill.
"""

from eshkill import (
    Eshkill,
    VaultConnector,
    SmartSkillSearch,
    AgentFormatter,
    MCPServer,
    AutoRouter,
    SkillInstaller,
    ProposalManager,
    run_server,
    SkillSummary,
    SkillDetail,
    SearchResult,
    VaultIndex,
    RoutingDecision,
    InstallResult,
    ProposalPayload,
    ProposalResult,
    __version__,
    __author__
)

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
    "__version__"
]
