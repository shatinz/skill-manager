"""
Skill Installer module for eshkill.
Enables instant installation of skills into local workspace (.agents/skills/<id>/SKILL.md),
global user configuration (~/.gemini/config/skills/ or ~/.eshkill/skills/), or ephemeral temp buffers.
"""

import os
import json
import tempfile
from typing import Optional, List, Dict, Any
from .models import InstallResult, SkillDetail
from .vault import VaultConnector

WORKSPACE_SKILLS_REL_PATH = os.path.join(".agents", "skills")
GLOBAL_GEMINI_SKILLS_PATH = os.path.expanduser("~/.gemini/config/skills")
GLOBAL_ESHKILL_SKILLS_PATH = os.path.expanduser("~/.eshkill/skills")
TEMP_SKILLS_DIR = os.path.join(tempfile.gettempdir(), "eshkill_skills")


class SkillInstaller:
    def __init__(self, vault_connector: Optional[VaultConnector] = None):
        self.vault = vault_connector or VaultConnector()

    def install(
        self,
        skill_id_or_name: str,
        mode: str = "workspace",
        workspace_dir: Optional[str] = None,
        custom_path: Optional[str] = None
    ) -> InstallResult:
        """
        Installs a skill to workspace, global, or temp directory.

        Modes:
          - 'workspace': <workspace>/.agents/skills/<skill_id>/SKILL.md
          - 'global': ~/.gemini/config/skills/<skill_id>/SKILL.md and ~/.eshkill/skills/
          - 'temp': /tmp/eshkill_skills/<skill_id>/SKILL.md (ephemeral)
        """
        try:
            skill = self.vault.get_skill(skill_id_or_name)
        except KeyError as e:
            return InstallResult(
                success=False,
                skill_id=skill_id_or_name,
                mode=mode,
                target_path="",
                message=str(e)
            )

        mode_clean = mode.lower().strip()
        workspace_root = os.path.abspath(workspace_dir) if workspace_dir else os.getcwd()

        if custom_path:
            target_file = os.path.abspath(custom_path)
            target_dir = os.path.dirname(target_file)
        elif mode_clean == "global":
            # Primary global location
            target_dir = os.path.join(GLOBAL_GEMINI_SKILLS_PATH, skill.id)
            target_file = os.path.join(target_dir, "SKILL.md")
            # Also mirror to ~/.eshkill/skills
            alt_dir = os.path.join(GLOBAL_ESHKILL_SKILLS_PATH, skill.id)
            os.makedirs(alt_dir, exist_ok=True)
            with open(os.path.join(alt_dir, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write(skill.content)
        elif mode_clean in ("temp", "ephemeral"):
            target_dir = os.path.join(TEMP_SKILLS_DIR, skill.id)
            target_file = os.path.join(target_dir, "SKILL.md")
        elif mode_clean in ("cursor", "cursorrules"):
            # Write to .cursor/rules/<skill_id>.mdc
            target_dir = os.path.join(workspace_root, ".cursor", "rules")
            target_file = os.path.join(target_dir, f"{skill.name}.mdc")
            os.makedirs(target_dir, exist_ok=True)
            cursor_mdc_content = f"""---
description: {skill.description}
globs: *
---
# {skill.title}

{skill.content.strip()}
"""
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(cursor_mdc_content)
            return InstallResult(
                success=True,
                skill_id=skill.id,
                mode="cursor",
                target_path=target_file,
                message=f"Successfully installed Cursor rule '{skill.id}' into {target_file}"
            )
        elif mode_clean in ("windsurf", "windsurfrules"):
            target_dir = workspace_root
            target_file = os.path.join(workspace_root, ".windsurfrules")
            os.makedirs(target_dir, exist_ok=True)
            entry = f"\n\n# --- Skill: {skill.title} ({skill.id}) ---\n{skill.content.strip()}\n"
            with open(target_file, "a", encoding="utf-8") as f:
                f.write(entry)
            return InstallResult(
                success=True,
                skill_id=skill.id,
                mode="windsurf",
                target_path=target_file,
                message=f"Successfully appended skill '{skill.id}' into {target_file}"
            )
        elif mode_clean in ("copilot", "copilot-instructions"):
            target_dir = os.path.join(workspace_root, ".github")
            target_file = os.path.join(target_dir, "copilot-instructions.md")
            os.makedirs(target_dir, exist_ok=True)
            entry = f"\n\n# {skill.title} (`{skill.id}`)\n{skill.content.strip()}\n"
            with open(target_file, "a", encoding="utf-8") as f:
                f.write(entry)
            return InstallResult(
                success=True,
                skill_id=skill.id,
                mode="copilot",
                target_path=target_file,
                message=f"Successfully appended skill '{skill.id}' into {target_file}"
            )
        elif mode_clean in ("claude", "claude.md"):
            target_dir = workspace_root
            target_file = os.path.join(workspace_root, "CLAUDE.md")
            entry = f"\n\n# {skill.title} (`{skill.id}`)\n{skill.content.strip()}\n"
            with open(target_file, "a", encoding="utf-8") as f:
                f.write(entry)
            return InstallResult(
                success=True,
                skill_id=skill.id,
                mode="claude",
                target_path=target_file,
                message=f"Successfully appended skill '{skill.id}' into {target_file}"
            )
        elif mode_clean in ("all-ide", "all"):
            # Install to workspace .agents/skills, cursor .mdc, windsurfrules, and copilot-instructions
            self.install(skill.id, mode="workspace", workspace_dir=workspace_root)
            self.install(skill.id, mode="cursor", workspace_dir=workspace_root)
            self.install(skill.id, mode="windsurf", workspace_dir=workspace_root)
            self.install(skill.id, mode="copilot", workspace_dir=workspace_root)
            self.install(skill.id, mode="claude", workspace_dir=workspace_root)
            return InstallResult(
                success=True,
                skill_id=skill.id,
                mode="all-ide",
                target_path=workspace_root,
                message=f"Successfully installed skill '{skill.id}' into all IDE formats (.agents, .cursor, .windsurf, .github/copilot, CLAUDE.md)"
            )
        else:
            # Default: workspace (.agents/skills/<id>/SKILL.md)
            mode_clean = "workspace"
            target_dir = os.path.join(workspace_root, WORKSPACE_SKILLS_REL_PATH, skill.id)
            target_file = os.path.join(target_dir, "SKILL.md")

        try:
            os.makedirs(target_dir, exist_ok=True)

            # Write SKILL.md
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(skill.content)

            # Write metadata.json alongside SKILL.md
            metadata_file = os.path.join(target_dir, "metadata.json")
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(skill.to_dict(), f, indent=2)

            return InstallResult(
                success=True,
                skill_id=skill.id,
                mode=mode_clean,
                target_path=target_file,
                message=f"Successfully installed skill '{skill.id}' into {target_file}",
                ephemeral_content=skill.content if mode_clean in ("temp", "ephemeral") else None
            )
        except Exception as e:
            return InstallResult(
                success=False,
                skill_id=skill.id,
                mode=mode_clean,
                target_path=target_file if 'target_file' in locals() else "",
                message=f"Failed to install skill '{skill.id}': {e}"
            )

    def install_stack(
        self,
        decision_or_prompt: Any,
        mode: str = "all-ide",
        workspace_dir: Optional[str] = None
    ) -> List[InstallResult]:
        """Installs all skills from a RoutingDecision or prompt into the workspace."""
        if isinstance(decision_or_prompt, str):
            from .router import AutoRouter
            router = AutoRouter(self.vault)
            decision = router.route(decision_or_prompt)
        else:
            decision = decision_or_prompt

        results = []
        for skill in decision.selected_skills:
            res = self.install(skill.id, mode=mode, workspace_dir=workspace_dir)
            results.append(res)
        return results

    def uninstall(
        self,
        skill_id_or_name: str,
        mode: str = "workspace",
        workspace_dir: Optional[str] = None
    ) -> bool:
        """Removes an installed skill."""
        workspace_root = os.path.abspath(workspace_dir) if workspace_dir else os.getcwd()
        mode_clean = mode.lower().strip()

        if mode_clean == "global":
            target_dirs = [
                os.path.join(GLOBAL_GEMINI_SKILLS_PATH, skill_id_or_name),
                os.path.join(GLOBAL_ESHKILL_SKILLS_PATH, skill_id_or_name)
            ]
        elif mode_clean in ("temp", "ephemeral"):
            target_dirs = [os.path.join(TEMP_SKILLS_DIR, skill_id_or_name)]
        else:
            target_dirs = [os.path.join(workspace_root, WORKSPACE_SKILLS_REL_PATH, skill_id_or_name)]

        removed = False
        for d in target_dirs:
            if os.path.exists(d):
                for fname in os.listdir(d):
                    try:
                        os.remove(os.path.join(d, fname))
                    except Exception:
                        pass
                try:
                    os.rmdir(d)
                    removed = True
                except Exception:
                    pass
        return removed

    def list_installed(
        self,
        mode: str = "workspace",
        workspace_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists installed skills in the specified target scope."""
        workspace_root = os.path.abspath(workspace_dir) if workspace_dir else os.getcwd()
        mode_clean = mode.lower().strip()

        if mode_clean == "global":
            search_dirs = [GLOBAL_GEMINI_SKILLS_PATH, GLOBAL_ESHKILL_SKILLS_PATH]
        elif mode_clean in ("temp", "ephemeral"):
            search_dirs = [TEMP_SKILLS_DIR]
        else:
            search_dirs = [os.path.join(workspace_root, WORKSPACE_SKILLS_REL_PATH)]

        installed = []
        seen = set()
        for root in search_dirs:
            if not os.path.exists(root):
                continue
            for entry in os.listdir(root):
                entry_path = os.path.join(root, entry)
                if os.path.isdir(entry_path) and entry not in seen:
                    skill_file = os.path.join(entry_path, "SKILL.md")
                    meta_file = os.path.join(entry_path, "metadata.json")
                    if os.path.exists(skill_file):
                        seen.add(entry)
                        meta_data = {}
                        if os.path.exists(meta_file):
                            try:
                                with open(meta_file, "r", encoding="utf-8") as f:
                                    meta_data = json.load(f)
                            except Exception:
                                pass
                        installed.append({
                            "id": entry,
                            "path": skill_file,
                            "scope": mode_clean,
                            "metadata": meta_data
                        })
        return installed
