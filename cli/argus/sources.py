"""
Argus Source Manager.
Manages multi-repository skill sources, handles discovery, syncing,
multi-format normalization (Antigravity SKILL.md, Cursor rules, Claude prompts, Git repos, MCP),
and content retrieval.
"""

import os
import re
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Set
from .models import SkillSource, SkillPackage, SourceType, SkillFormat
from .remote import RemoteRepoScanner, is_remote_location, parse_git_url


DEFAULT_SOURCES = [
    SkillSource(
        id="builtin-vault",
        name="Argus Standard Skill Vault",
        source_type=SourceType.BUILTIN_VAULT,
        location=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "skills-vault")),
        enabled=True,
        priority=100,
        trust_score=1.0,
        metadata={"description": "High-craft standard skills catalog"}
    ),
    SkillSource(
        id="antigravity-system",
        name="Antigravity Global & Builtin Skills",
        source_type=SourceType.ANTIGRAVITY_SYSTEM,
        location=os.path.expanduser("~/.gemini/config/skills"),
        enabled=True,
        priority=95,
        trust_score=0.98,
        metadata={"description": "User installed Antigravity agent skills"}
    ),
    SkillSource(
        id="skills-and-rules-repo",
        name="GitHub Skills & Rules Knowledge Base",
        source_type=SourceType.GIT_REPO,
        location="https://github.com/shatinz/skills-and-rules",
        enabled=True,
        priority=90,
        trust_score=0.95,
        branch="main",
        metadata={"description": "Remote public skills & rules upstream"}
    ),
    SkillSource(
        id="cursor-workspace-rules",
        name="Cursor Rules & MDCs",
        source_type=SourceType.CURSOR_RULES,
        location=".cursor/rules",
        enabled=True,
        priority=80,
        trust_score=0.90,
        metadata={"description": "Workspace cursorrules and MDC rules"}
    )
]


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse YAML-style frontmatter from markdown content."""
    meta = {}
    body = content
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            for line in fm_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    # Strip quotes
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    # List format parsing [a, b, c]
                    if val.startswith("[") and val.endswith("]"):
                        items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                        meta[key] = items
                    else:
                        meta[key] = val
    return meta, body


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class SourceManager:
    """Manages skill repositories, local vaults, and remote source registries."""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.argus")
        self.cache_dir = os.path.join(self.config_dir, "cache")
        self.sources_file = os.path.join(self.config_dir, "sources.json")
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.remote_scanner = RemoteRepoScanner(self.cache_dir)
        self.sources: Dict[str, SkillSource] = {}
        self._load_sources()

    def _load_sources(self):
        if os.path.exists(self.sources_file):
            try:
                with open(self.sources_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("sources", []):
                        src = SkillSource.from_dict(item)
                        self.sources[src.id] = src
            except Exception:
                self._init_default_sources()
        else:
            self._init_default_sources()

    def _init_default_sources(self):
        self.sources.clear()
        for src in DEFAULT_SOURCES:
            self.sources[src.id] = src
        self.save_sources()

    def save_sources(self):
        data = {
            "sources": [s.to_dict() for s in self.sources.values()]
        }
        with open(self.sources_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def list_sources(self) -> List[SkillSource]:
        return list(self.sources.values())

    def get_source(self, source_id: str) -> Optional[SkillSource]:
        return self.sources.get(source_id)

    def add_source(
        self,
        id: str,
        name: str,
        source_type: SourceType,
        location: str,
        priority: int = 100,
        trust_score: float = 1.0,
        branch: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SkillSource:
        # Auto-detect git_repo if remote URL provided
        if source_type == SourceType.LOCAL_DIR and is_remote_location(location):
            source_type = SourceType.GIT_REPO

        src = SkillSource(
            id=id,
            name=name,
            source_type=source_type,
            location=location,
            enabled=True,
            priority=priority,
            trust_score=trust_score,
            branch=branch,
            metadata=metadata or {}
        )
        self.sources[id] = src
        self.save_sources()
        return src

    def remove_source(self, source_id: str) -> bool:
        if source_id in self.sources:
            del self.sources[source_id]
            self.save_sources()
            return True
        return False

    def toggle_source(self, source_id: str, enabled: bool) -> bool:
        if source_id in self.sources:
            self.sources[source_id].enabled = enabled
            self.save_sources()
            return True
        return False

    def sync_source(self, source_id: str) -> Tuple[bool, str, int]:
        """Sync or index a remote or local source without full repository download."""
        src = self.get_source(source_id)
        if not src:
            return False, f"Source '{source_id}' not found", 0

        if src.is_remote or src.source_type in (SourceType.GIT_REPO, SourceType.HTTP_REGISTRY) or is_remote_location(src.location):
            try:
                packages = self.remote_scanner.scan_remote_source(
                    source=src,
                    parse_frontmatter_func=parse_frontmatter,
                    infer_capabilities_func=self._infer_capabilities,
                    infer_frameworks_func=self._infer_frameworks,
                    estimate_tokens_func=estimate_tokens,
                    force_refresh=True
                )
                
                # If remote network yielded nothing (e.g. offline sandbox), check scratch fallback
                if not packages:
                    scratch_alt = os.path.expanduser("~/.gemini/antigravity/scratch/skills-and-rules")
                    if os.path.exists(scratch_alt):
                        packages = self._scan_directory(scratch_alt, src)

                src.skill_count = len(packages)
                import time
                src.last_synced = time.time()
                self.save_sources()
                return True, f"Successfully indexed remote repository '{src.name}' ({len(packages)} skills found via zero-clone discovery)", len(packages)
            except Exception as e:
                # If remote fails, try checking if a local clone exists in scratch
                scratch_alt = os.path.expanduser("~/.gemini/antigravity/scratch/skills-and-rules")
                if os.path.exists(scratch_alt):
                    packages = self._scan_directory(scratch_alt, src)
                    src.skill_count = len(packages)
                    self.save_sources()
                    return True, f"Synced from local mirror '{scratch_alt}' ({len(packages)} skills)", len(packages)
                return False, f"Failed to sync remote source {src.location}: {str(e)}", 0

        elif src.source_type in (SourceType.LOCAL_DIR, SourceType.ANTIGRAVITY_SYSTEM, SourceType.BUILTIN_VAULT, SourceType.CURSOR_RULES):
            resolved_path = os.path.expanduser(src.location)
            if not os.path.isabs(resolved_path):
                resolved_path = os.path.abspath(resolved_path)
            
            packages = self.scan_source_skills(src)
            src.skill_count = len(packages)
            self.save_sources()
            return True, f"Scanned local source '{src.name}' ({len(packages)} skills found)", len(packages)

        return True, f"Source '{src.name}' is up to date", src.skill_count

    def scan_source_skills(self, source: SkillSource) -> List[SkillPackage]:
        """Scan all skills available in a given source, normalizing formats."""
        if not source.enabled:
            return []

        if source.is_remote or source.source_type in (SourceType.GIT_REPO, SourceType.HTTP_REGISTRY) or is_remote_location(source.location):
            packages = self.remote_scanner.scan_remote_source(
                source=source,
                parse_frontmatter_func=parse_frontmatter,
                infer_capabilities_func=self._infer_capabilities,
                infer_frameworks_func=self._infer_frameworks,
                estimate_tokens_func=estimate_tokens,
                force_refresh=False
            )
            if packages:
                return packages

            # Fallback to local scratch clone if offline or uninitialized
            scratch_path = os.path.expanduser("~/.gemini/antigravity/scratch/skills-and-rules")
            if os.path.exists(scratch_path):
                return self._scan_directory(scratch_path, source)
            return []

        resolved_path = os.path.expanduser(source.location)
        if not os.path.isabs(resolved_path):
            resolved_path = os.path.abspath(resolved_path)

        if not os.path.exists(resolved_path):
            return []

        return self._scan_directory(resolved_path, source)

    def _scan_directory(self, root_dir: str, source: SkillSource) -> List[SkillPackage]:
        packages: List[SkillPackage] = []
        if not os.path.exists(root_dir):
            return packages

        for root, dirs, files in os.walk(root_dir):
            # Skip git / node_modules / cache
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", ".venv", "dist", "build")]

            # 1. Antigravity Skill Format: SKILL.md
            if "SKILL.md" in files:
                skill_file = os.path.join(root, "SKILL.md")
                pkg = self._parse_antigravity_skill(skill_file, source)
                if pkg:
                    packages.append(pkg)
                continue

            # 2. Cursor MDC / Rules
            for f in files:
                if f.endswith(".mdc") or f == ".cursorrules":
                    rule_file = os.path.join(root, f)
                    pkg = self._parse_cursor_rule(rule_file, source)
                    if pkg:
                        packages.append(pkg)
                elif f.endswith(".md") and f not in ("README.md", "CHANGELOG.md", "LICENSE.md", "CONTRIBUTING.md"):
                    # Check if standalone skill markdown or rule file
                    doc_file = os.path.join(root, f)
                    pkg = self._parse_generic_markdown_skill(doc_file, source)
                    if pkg:
                        packages.append(pkg)

        return packages

    def _parse_antigravity_skill(self, file_path: str, source: SkillSource) -> Optional[SkillPackage]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            meta, body = parse_frontmatter(content)
            folder_name = os.path.basename(os.path.dirname(file_path))
            skill_name = meta.get("name", folder_name)
            description = meta.get("description", "")
            
            if not description:
                # Extract first paragraph
                lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#")]
                description = lines[0] if lines else skill_name

            category = meta.get("category", "")
            if not category:
                parent = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
                category = parent if parent and parent not in ("skills", "vault", "skills-vault") else "general"

            tags = meta.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]

            # Infer capabilities & frameworks from content and metadata
            caps = meta.get("capabilities", [])
            if not caps:
                caps = self._infer_capabilities(skill_name, description, body)

            frameworks = meta.get("frameworks", meta.get("compatible_frameworks", []))
            if not frameworks:
                frameworks = self._infer_frameworks(skill_name, description, body)

            return SkillPackage(
                id=skill_name,
                source_id=source.id,
                name=skill_name,
                format=SkillFormat.ANTIGRAVITY_SKILL,
                description=description,
                category=category,
                tags=tags,
                version=str(meta.get("version", "1.0.0")),
                author=meta.get("author", "community"),
                capabilities=caps,
                compatible_frameworks=frameworks,
                actionability_score=0.95 if ("```" in body or "## Instructions" in body) else 0.8,
                file_path=file_path,
                raw_content=content,
                token_count=estimate_tokens(content),
                metadata=meta
            )
        except Exception:
            return None

    def _parse_cursor_rule(self, file_path: str, source: SkillSource) -> Optional[SkillPackage]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            meta, body = parse_frontmatter(content)
            rule_name = os.path.splitext(os.path.basename(file_path))[0]
            description = meta.get("description", "")
            if not description:
                lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#")]
                description = lines[0] if lines else f"Cursor rule: {rule_name}"

            return SkillPackage(
                id=f"cursor-{rule_name}",
                source_id=source.id,
                name=rule_name,
                format=SkillFormat.CURSOR_MDC,
                description=description,
                category="cursor-rules",
                tags=["cursor", "editor-rule"] + (meta.get("globs", []) if isinstance(meta.get("globs"), list) else []),
                capabilities=self._infer_capabilities(rule_name, description, body),
                compatible_frameworks=self._infer_frameworks(rule_name, description, body),
                actionability_score=0.88,
                file_path=file_path,
                raw_content=content,
                token_count=estimate_tokens(content),
                metadata=meta
            )
        except Exception:
            return None

    def _parse_generic_markdown_skill(self, file_path: str, source: SkillSource) -> Optional[SkillPackage]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if len(content.strip()) < 50:
                return None

            meta, body = parse_frontmatter(content)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Find first heading
            heading = base_name
            for line in content.splitlines():
                if line.startswith("# "):
                    heading = line[2:].strip()
                    break

            description = meta.get("description", "")
            if not description:
                for line in body.splitlines():
                    if line.strip() and not line.startswith("#"):
                        description = line.strip()
                        break
            if not description:
                description = f"Skill guideline: {heading}"

            return SkillPackage(
                id=base_name,
                source_id=source.id,
                name=heading,
                format=SkillFormat.GENERIC_MARKDOWN,
                description=description,
                category=os.path.basename(os.path.dirname(file_path)),
                tags=[base_name.lower()],
                capabilities=self._infer_capabilities(heading, description, body),
                compatible_frameworks=self._infer_frameworks(heading, description, body),
                actionability_score=0.75,
                file_path=file_path,
                raw_content=content,
                token_count=estimate_tokens(content),
                metadata=meta
            )
        except Exception:
            return None

    def _infer_capabilities(self, name: str, desc: str, body: str) -> List[str]:
        caps: Set[str] = set()
        text = f"{name} {desc} {body[:500]}".lower()

        cap_keywords = {
            "3d_rendering": ["three.js", "threejs", "webgl", "canvas", "3d", "spline", "r3f", "mesh", "shader"],
            "frontend_ui": ["react", "vue", "svelte", "nextjs", "vite", "component", "tailwind", "html", "css"],
            "api_backend": ["fastapi", "rest", "api", "endpoint", "express", "hono", "backend", "crud"],
            "database_sql": ["postgres", "postgresql", "sql", "sqlite", "supabase", "query", "database", "orm", "prisma"],
            "ai_agents": ["agent", "llm", "prompt", "rag", "embedding", "langgraph", "mcp", "tool"],
            "devops_deploy": ["docker", "container", "ci/cd", "kubernetes", "vercel", "deploy", "aws", "terraform"],
            "security_hardening": ["security", "auth", "sast", "jwt", "owasp", "sanitization", "xss", "cve"],
            "testing_qa": ["test", "pytest", "playwright", "vitest", "jest", "mock", "fixture"]
        }

        for cap, terms in cap_keywords.items():
            if any(term in text for term in terms):
                caps.add(cap)

        return list(caps)

    def _infer_frameworks(self, name: str, desc: str, body: str) -> List[str]:
        frameworks: Set[str] = set()
        text = f"{name} {desc} {body[:500]}".lower()

        known = [
            "threejs", "react", "nextjs", "vite", "vue", "svelte", "tailwind",
            "fastapi", "python", "typescript", "javascript", "supabase",
            "postgres", "docker", "hono", "prisma", "drizzle", "playwright"
        ]

        for k in known:
            if re.search(rf"\b{k}\b", text):
                frameworks.add(k)

        return list(frameworks)

    def fetch_skill_content(self, source_id: str, skill_id: str) -> Optional[str]:
        """Retrieve full markdown content for a skill by source and ID."""
        src = self.get_source(source_id)
        if not src:
            return None

        packages = self.scan_source_skills(src)
        for pkg in packages:
            if pkg.id == skill_id or pkg.name == skill_id or pkg.qualified_id == skill_id:
                if pkg.raw_content:
                    return pkg.raw_content
                if src.is_remote or pkg.remote_url:
                    content = self.remote_scanner.fetch_skill_raw_content(src, pkg)
                    if content:
                        pkg.raw_content = content
                        return content
                if pkg.file_path and os.path.exists(pkg.file_path):
                    with open(pkg.file_path, "r", encoding="utf-8") as f:
                        return f.read()
        return None

