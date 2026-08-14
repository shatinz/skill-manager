"""
Vault connector for eshkill.
Handles on-demand loading of skill manifests and markdown from local paths, GitHub raw URLs, or local cache with TTL.
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
DEFAULT_CACHE_DIR = os.path.expanduser("~/.cache/eshkill")
FALLBACK_CACHE_DIR = os.path.expanduser("~/.cache/askill")
DEFAULT_REMOTE_RAW_BASE = os.environ.get(
    "SKILL_VAULT_URL",
    "https://raw.githubusercontent.com/shatinz/skills-and-rules/main/skills-vault"
)

# Skill ID and Name aliases for backwards and cross-version compatibility
SKILL_ALIASES = {
    "fastapi-rest-craft": "fastapi-production-craft",
    "coding.api-design.fastapi-rest-craft": "web-frameworks.python-api.fastapi-production-craft",
    "react-performance-audit": "nextjs-15-app-router",
    "coding.frontend-engineering.react-performance-audit": "web-frameworks.react-fullstack.nextjs-15-app-router",
    "tailwind-design-system": "tailwind-v4-tokens",
    "coding.frontend-engineering.tailwind-design-system": "ui-design-antislop.styling-tokens.tailwind-v4-tokens",
    "docker-multi-stage-build": "docker-multi-stage-distroless",
    "devops-cloud.ci-cd.docker-multi-stage-build": "devops-cloud-serverless.containerization.docker-multi-stage-distroless",
    "prisma-orm-patterns": "prisma-orm-mastery",
    "coding.database-architecture.prisma-orm-patterns": "databases-storage.orm-data-access.prisma-orm-mastery",
    "duckdb-fast-analytics": "duckdb-polars-analytics",
    "data-ai-engineering.data-pipelines.duckdb-fast-analytics": "databases-storage.olap-embedded.duckdb-polars-analytics",
    "dry-solid-refactor": "dry-solid-clean-architecture",
    "coding.refactoring-clean-code.dry-solid-refactor": "clean-architecture-refactoring.principles-patterns.dry-solid-clean-architecture",
    "input-sanitization-guard": "input-sanitization-xss-defense",
    "security-compliance.code-hardening.input-sanitization-guard": "security-sast-hardening.web-defense.input-sanitization-xss-defense",
    "secret-leak-detector": "secret-leak-precommit-guard",
    "testing-quality.security-sast.secret-leak-detector": "security-sast-hardening.secrets-management.secret-leak-precommit-guard",
    "adr-writer-reviewer": "adr-architecture-decision-records",
    "documentation-communication.architecture-decision-records.adr-writer-reviewer": "clean-architecture-refactoring.architectural-docs.adr-architecture-decision-records",
    "coding.database-architecture.postgres-query-tuning": "databases-storage.relational-sql.postgres-query-tuning",
    "testing-quality.unit-integration.pytest-mocking-mastery": "testing-qa-automation.unit-integration-python.pytest-mocking-mastery",
    "testing-quality.unit-integration.playwright-e2e-automation": "testing-qa-automation.e2e-testing.playwright-e2e-automation",
    "testing-quality.security-sast.owasp-top10-scanner": "security-sast-hardening.application-security.owasp-top10-scanner",
    "devops-cloud.ci-cd.github-actions-matrix-ci": "devops-cloud-serverless.ci-cd.github-actions-matrix-ci",
    "devops-cloud.infrastructure-as-code.terraform-aws-modules": "devops-cloud-serverless.iac-cloud.terraform-aws-modules",
    "devops-cloud.observability.prometheus-grafana-telemetry": "devops-cloud-serverless.observability.prometheus-grafana-telemetry",
    "data-ai-engineering.llm-rag.rag-chunking-hybrid-search": "ai-llm-agents.rag-retrieval.rag-chunking-hybrid-search",
    "data-ai-engineering.llm-rag.prompt-engineering-distiller": "ai-llm-agents.prompt-craft.prompt-engineering-distiller",
    "security-compliance.code-hardening.jwt-oauth2-secureshop": "security-sast-hardening.auth-security.jwt-oauth2-secureshop",
    "coding.refactoring-clean-code.legacy-code-modernizer": "clean-architecture-refactoring.code-modernization.legacy-code-modernizer",
    "documentation-communication.api-docs.openapi-swagger-generator": "web-frameworks.python-api.fastapi-production-craft"
}


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
            except Exception:
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

        # Check fallback cache dir
        fallback_file = os.path.join(FALLBACK_CACHE_DIR, "vault.json")
        if not force_refresh and self._is_cache_valid(fallback_file):
            try:
                with open(fallback_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._index = VaultIndex.from_dict(data)
                return self._index
            except Exception:
                pass

        # 3. Remote URL fetch
        remote_url = f"{DEFAULT_REMOTE_RAW_BASE}/vault.json"
        try:
            req = urllib.request.Request(remote_url, headers={"User-Agent": "eshkill-cli/1.1"})
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
            if os.path.exists(fallback_file):
                with open(fallback_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._index = VaultIndex.from_dict(data)
                return self._index
            raise RuntimeError(
                f"Could not load skill vault index from local or remote source: {e}"
            )

    def list_skills(self) -> List[SkillSummary]:
        """Convenience accessor returning all indexed skills."""
        return self.load_index().skills

    def get_skill(self, skill_id_or_name: str) -> SkillDetail:
        index = self.load_index()

        # Check alias table first
        resolved_key = SKILL_ALIASES.get(skill_id_or_name, skill_id_or_name)

        # Match by ID or exact name or suffix
        target_summary: Optional[SkillSummary] = None
        for s in index.skills:
            if (s.id == resolved_key or
                s.name == resolved_key or
                s.id.endswith(f".{resolved_key}") or
                s.id == skill_id_or_name or
                s.name == skill_id_or_name or
                s.id.endswith(f".{skill_id_or_name}")):
                target_summary = s
                break

        if not target_summary:
            # Match by case-insensitive or hyphenated
            target_lower = resolved_key.lower().replace("_", "-")
            for s in index.skills:
                if (s.id.lower() == target_lower or
                    s.name.lower() == target_lower or
                    s.id.lower().endswith(f".{target_lower}")):
                    target_summary = s
                    break

        if not target_summary:
            # Fuzzy match top 1
            for s in index.skills:
                if (target_lower in s.name.lower() or
                    target_lower in s.id.lower() or
                    skill_id_or_name.lower() in s.name.lower()):
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
                    req = urllib.request.Request(remote_skill_url, headers={"User-Agent": "eshkill-cli/1.1"})
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
