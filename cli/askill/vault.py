"""
Vault connector for askill.
Handles on-demand loading of skill manifests and markdown from local paths, GitHub raw URLs, or local cache.
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from .models import VaultIndex, SkillSummary, SkillDetail

DEFAULT_LOCAL_VAULT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "skills-vault")
)
DEFAULT_CACHE_DIR = os.path.expanduser("~/.cache/askill")
DEFAULT_REMOTE_RAW_BASE = os.environ.get(
    "SKILL_VAULT_URL",
    "https://raw.githubusercontent.com/shatinz/skills-and-rules/main/skills-vault"
)

class VaultConnector:
    def __init__(self, vault_path_or_url: Optional[str] = None, cache_ttl_seconds: int = 3600):
        self.custom_source = vault_path_or_url or os.environ.get("SKILL_VAULT_SOURCE")
        self.cache_ttl = cache_ttl_seconds
        self.cache_dir = DEFAULT_CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        self._index: Optional[VaultIndex] = None

    def _get_cache_path(self, filename: str) -> str:
        safe_name = filename.replace("/", "_").replace("\\", "_")
        return os.path.join(self.cache_dir, safe_name)

    def _is_cache_valid(self, cache_file: str) -> bool:
        if not os.path.exists(cache_file):
            return False
        age = time.time() - os.path.getmtime(cache_file)
        return age < self.cache_ttl

    def load_index(self, force_refresh: bool = False) -> VaultIndex:
        if self._index and not force_refresh:
            return self._index

        cache_file = self._get_cache_path("vault.json")

        # 1. Local filesystem path if exists
        local_candidates = [
            self.custom_source if self.custom_source and os.path.exists(self.custom_source) else None,
            os.path.join(DEFAULT_LOCAL_VAULT, "vault.json") if os.path.exists(os.path.join(DEFAULT_LOCAL_VAULT, "vault.json")) else None,
        ]
        
        for candidate in filter(None, local_candidates):
            try:
                target_json = candidate if candidate.endswith(".json") else os.path.join(candidate, "vault.json")
                if os.path.exists(target_json):
                    with open(target_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self._index = VaultIndex.from_dict(data)
                    return self._index
            except Exception as e:
                pass

        # 2. Check local disk cache
        if not force_refresh and self._is_cache_valid(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._index = VaultIndex.from_dict(data)
                return self._index
            except Exception:
                pass

        # 3. Remote URL fetch
        remote_url = f"{DEFAULT_REMOTE_RAW_BASE}/vault.json"
        try:
            req = urllib.request.Request(remote_url, headers={"User-Agent": "askill-cli/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode("utf-8")
                data = json.loads(content)
                with open(cache_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self._index = VaultIndex.from_dict(data)
                return self._index
        except Exception as e:
            # Fallback to expired cache if available
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._index = VaultIndex.from_dict(data)
                return self._index
            raise RuntimeError(
                f"Could not load skill vault index from local or remote source: {e}"
            )

    def get_skill(self, skill_id_or_name: str) -> SkillDetail:
        index = self.load_index()
        
        # Match by ID or exact name or suffix
        target_summary: Optional[SkillSummary] = None
        for s in index.skills:
            if (s.id == skill_id_or_name or 
                s.name == skill_id_or_name or 
                s.id.endswith(f".{skill_id_or_name}")):
                target_summary = s
                break

        if not target_summary:
            # Fuzzy match top 1
            for s in index.skills:
                if skill_id_or_name.lower() in s.name.lower() or skill_id_or_name.lower() in s.id.lower():
                    target_summary = s
                    break

        if not target_summary:
            raise KeyError(f"Skill '{skill_id_or_name}' not found in vault.")

        # Resolve content
        content = ""
        source_url = ""

        # 1. Local path check
        local_skill_path = os.path.join(DEFAULT_LOCAL_VAULT, target_summary.relative_path)
        if os.path.exists(local_skill_path):
            with open(local_skill_path, "r", encoding="utf-8") as f:
                content = f.read()
            source_url = f"file://{local_skill_path}"
        else:
            # 2. Check Cache
            cache_file = self._get_cache_path(f"{target_summary.id}.md")
            if self._is_cache_valid(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    content = f.read()
                source_url = f"cache://{cache_file}"
            else:
                # 3. Remote URL
                remote_skill_url = f"{DEFAULT_REMOTE_RAW_BASE}/{target_summary.relative_path}"
                try:
                    req = urllib.request.Request(remote_skill_url, headers={"User-Agent": "askill-cli/1.0"})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        content = response.read().decode("utf-8")
                        with open(cache_file, "w", encoding="utf-8") as f:
                            f.write(content)
                        source_url = remote_skill_url
                except Exception as e:
                    if os.path.exists(cache_file):
                        with open(cache_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        source_url = f"cache://{cache_file}"
                    else:
                        raise RuntimeError(f"Failed to fetch skill content for {target_summary.id}: {e}")

        # Strip frontmatter if needed for pure body
        raw_fm = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()

        return SkillDetail(
            id=target_summary.id,
            name=target_summary.name,
            title=target_summary.title,
            category=target_summary.category,
            subcategory=target_summary.subcategory,
            version=target_summary.version,
            tags=target_summary.tags,
            trust_rating=target_summary.trust_rating,
            estimated_tokens=target_summary.estimated_tokens,
            description=target_summary.description,
            trigger_patterns=target_summary.trigger_patterns,
            relative_path=target_summary.relative_path,
            content=body,
            raw_frontmatter=raw_fm,
            source_url=source_url
        )

    def list_categories(self) -> Dict[str, Dict[str, List[str]]]:
        index = self.load_index()
        return index.categories
