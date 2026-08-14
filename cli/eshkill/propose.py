"""
Contribution and PR proposal module for eshkill.
Enables autonomous agents and human developers to propose updates, bugfixes, and enhancements to living skills.
"""

import os
import difflib
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
from .models import ProposalPayload, ProposalResult
from .vault import VaultConnector

DEFAULT_SKILL_MANAGER_API = os.environ.get("SKILL_MANAGER_API_URL", "http://localhost:8000/api")


class ProposalManager:
    def __init__(self, vault_connector: Optional[VaultConnector] = None, api_url: str = DEFAULT_SKILL_MANAGER_API):
        self.vault = vault_connector or VaultConnector()
        self.api_url = api_url.rstrip("/")

    def generate_diff(self, original_content: str, proposed_content: str, filename: str = "SKILL.md") -> str:
        orig_lines = original_content.splitlines(keepends=True)
        prop_lines = proposed_content.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            prop_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}"
        )
        return "".join(diff)

    def submit_proposal(
        self,
        skill_id: str,
        proposer_id: str,
        proposal_type: str = "modification",
        proposed_content: Optional[str] = None,
        file_path: Optional[str] = None,
        reason: str = "",
        author_github: Optional[str] = None,
        output_patch: Optional[str] = None,
        is_agent: bool = False,
        tags: Optional[list] = None,
        agent_metadata: Optional[Dict[str, Any]] = None
    ) -> ProposalResult:
        try:
            skill = self.vault.get_skill(skill_id)
        except KeyError as e:
            return ProposalResult(success=False, message=str(e))

        # Resolve proposed content from file if given
        content = proposed_content
        if file_path and os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        if not content:
            return ProposalResult(
                success=False,
                message="No proposed content or file path was provided for modification."
            )

        # Compute diff
        diff_text = self.generate_diff(skill.content, content, filename=f"{skill.name}/SKILL.md")

        # Save local patch if requested
        saved_patch_file = None
        if output_patch:
            with open(output_patch, "w", encoding="utf-8") as f:
                f.write(diff_text)
            saved_patch_file = output_patch

        # Automatic agent tagging
        is_agent_final = is_agent or proposer_id.startswith("agent:") or proposer_id.startswith("bot:")
        tags_final = list(tags) if tags else []
        if is_agent_final:
            if "autonomous_agent" not in tags_final:
                tags_final.insert(0, "autonomous_agent")
            if "ai_generated" not in tags_final:
                tags_final.append("ai_generated")
        else:
            if "human" not in tags_final:
                tags_final.append("human")

        # Try submitting to local/remote Unified Skill Manager API if available
        api_endpoint = f"{self.api_url}/proposals/skills/{skill.id}/proposals"
        payload = {
            "proposer_id": proposer_id,
            "proposal_type": proposal_type,
            "proposed_content": content,
            "issue_text": reason or f"Proposed update to {skill.name}",
            "is_agent": is_agent_final,
            "tags": tags_final,
            "agent_metadata": agent_metadata or {}
        }

        try:
            req = urllib.request.Request(
                api_endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "eshkill-cli/1.1"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                return ProposalResult(
                    success=True,
                    message=f"Proposal submitted directly to Skill Manager pipeline for skill '{skill.name}'.",
                    proposal_id=resp_data.get("id"),
                    status=resp_data.get("status", "pending"),
                    patch_file=saved_patch_file,
                    is_agent=resp_data.get("is_agent", is_agent_final),
                    tags=resp_data.get("tags", tags_final)
                )
        except Exception:
            # Fallback to generating GitHub PR template instructions
            agent_badge = "🤖 AUTONOMOUS AGENT" if is_agent_final else "👤 HUMAN CONTRIBUTOR"
            pr_title = f"fix({skill.category}/{skill.name}): {reason[:60] if reason else 'update skill guidelines'}"
            pr_body = f"""### 🚀 Proposed Update for `{skill.id}` [{agent_badge}]

**Proposer**: `{proposer_id}` ({'Autonomous AI Agent' if is_agent_final else 'Human'})
**Tags**: `{', '.join(tags_final)}`
**Reason**: {reason or 'Continuous agent performance improvement based on live execution feedback.'}

#### 📋 Unified Diff:
```diff
{diff_text}
```

---
*Generated autonomously by `eshkill propose`*
"""
            return ProposalResult(
                success=True,
                message=(
                    f"Created proposal diff for skill '{skill.name}'.\n"
                    f"Unified Skill Manager API was offline/unreachable, generated GitHub PR template payload."
                ),
                status="ready_for_pr",
                patch_file=saved_patch_file,
                is_agent=is_agent_final,
                tags=tags_final
            )

    def auto_propose_from_feedback(
        self,
        skill_id: str,
        execution_feedback: str,
        suggested_modifications: str,
        agent_id: str = "agent:autonomous-worker",
        reason: str = "Autonomous refinement based on task execution feedback and error recovery",
        agent_model: str = "claude-3-5-sonnet"
    ) -> ProposalResult:
        """
        Autonomous Agent Self-Improvement Protocol:
        Takes runtime execution feedback or test results, applies suggested improvements
        to the target skill, and automatically submits the proposal tagged as an autonomous agent.
        """
        try:
            skill = self.vault.get_skill(skill_id)
        except KeyError as e:
            return ProposalResult(success=False, message=str(e))

        agent_metadata = {
            "agent_id": agent_id,
            "agent_model": agent_model,
            "execution_feedback": execution_feedback,
            "timestamp": str(os.environ.get("TIMESTAMP", ""))
        }

        # If suggested_modifications contains the full replacement or instructions append
        proposed_content = suggested_modifications
        if not proposed_content.startswith("#") and not proposed_content.startswith("---"):
            # It's an append or patch instruction, synthesize into current content
            proposed_content = f"{skill.content.rstrip()}\n\n## 🛠️ Autonomous Agent Update ({reason})\n{suggested_modifications.strip()}\n"

        return self.submit_proposal(
            skill_id=skill_id,
            proposer_id=agent_id,
            proposal_type="modification",
            proposed_content=proposed_content,
            reason=f"[Autonomous Agent] {reason}",
            is_agent=True,
            tags=["autonomous_agent", "ai_generated", "self_healing", "runtime_feedback"],
            agent_metadata=agent_metadata
        )
