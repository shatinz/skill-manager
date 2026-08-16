"""
Argus Remote Repository Client & Sparse Skill Scanner.
Enables searching and proxying remote GitHub / Git repositories without downloading
or cloning the full repository onto the local machine.

Techniques:
1. GitHub Git Trees API + Raw Content Stream (Zero disk, only skill metadata/blobs)
2. In-Memory Streaming Tarball Extraction (Discards non-skill files on the fly)
3. Git Sparse Filter Clone (--filter=blob:none + sparse-checkout)
4. Fast JSON metadata cache for offline & instant cross-repo BM25 search
"""

import os
import re
import json
import time
import tarfile
import urllib.request
import urllib.error
import subprocess
from typing import List, Dict, Optional, Tuple, Any, Set
from .models import SkillSource, SkillPackage, SkillFormat, SourceType


# Regex patterns to detect skill and rule files in remote repository trees
SKILL_FILE_PATTERNS = [
    r"(^|/)SKILL\.md$",
    r"\.mdc$",
    r"(^|/)\.cursorrules$",
    r"(^|/)copilot-instructions\.md$",
    r"^(skills|rules|prompts|vault)/.*\.md$",
    r"^skills-vault/.*\.md$",
]

IGNORE_NAMES = {
    "readme.md", "changelog.md", "license.md", "contributing.md",
    "code_of_conduct.md", "security.md", "todo.md"
}


def parse_git_url(url: str) -> Dict[str, Optional[str]]:
    """
    Parse remote git repository URLs into provider, owner, repo, and default branch.
    Handles HTTPS, SSH, and shorthand URLs.
    """
    clean_url = url.strip()
    
    # GitHub HTTPS: https://github.com/owner/repo or https://github.com/owner/repo.git
    gh_match = re.match(r"^https?://(?:www\.)?github\.com/([^/]+)/([^/#]+)(?:/(?:tree|blob)/([^/#]+))?(?:\.git)?/?$", clean_url)
    if gh_match:
        owner = gh_match.group(1)
        repo = gh_match.group(2).removesuffix(".git")
        branch = gh_match.group(3)
        return {
            "provider": "github",
            "owner": owner,
            "repo": repo,
            "branch": branch or "main",
            "clean_url": f"https://github.com/{owner}/{repo}"
        }

    # GitHub SSH: git@github.com:owner/repo.git
    ssh_match = re.match(r"^git@github\.com:([^/]+)/([^/#]+?)(?:\.git)?$", clean_url)
    if ssh_match:
        owner = ssh_match.group(1)
        repo = ssh_match.group(2)
        return {
            "provider": "github",
            "owner": owner,
            "repo": repo,
            "branch": "main",
            "clean_url": f"https://github.com/{owner}/{repo}"
        }

    # GitLab HTTPS
    gl_match = re.match(r"^https?://(?:www\.)?gitlab\.com/([^/]+)/([^/#]+)(?:\.git)?/?$", clean_url)
    if gl_match:
        owner = gl_match.group(1)
        repo = gl_match.group(2).removesuffix(".git")
        return {
            "provider": "gitlab",
            "owner": owner,
            "repo": repo,
            "branch": "main",
            "clean_url": f"https://gitlab.com/{owner}/{repo}"
        }

    return {
        "provider": "generic",
        "owner": None,
        "repo": None,
        "branch": None,
        "clean_url": clean_url
    }


def is_remote_location(location: str) -> bool:
    """Check if location is a remote URL rather than a local file path."""
    if not location:
        return False
    loc = location.strip().lower()
    return loc.startswith("http://") or loc.startswith("https://") or loc.startswith("git@") or "github.com" in loc


def is_skill_file_path(path: str) -> bool:
    """Determine whether a file path in a repository tree represents a skill/rule document."""
    norm_path = path.replace("\\", "/").strip()
    base_name = os.path.basename(norm_path).lower()
    
    # Exclude non-skill general markdown files at root
    if "/" not in norm_path and base_name in IGNORE_NAMES:
        return False
    if base_name in IGNORE_NAMES and not norm_path.startswith("skills/") and not norm_path.startswith("rules/"):
        return False

    for pattern in SKILL_FILE_PATTERNS:
        if re.search(pattern, norm_path, re.IGNORECASE):
            return True
            
    # Also match any .md file inside a directory called skills/ or rules/ or prompt/
    parts = norm_path.split("/")
    if len(parts) > 1 and parts[0] in ("skills", "rules", "prompts", "vault", "skills-vault") and norm_path.endswith(".md"):
        return True

    return False


class RemoteRepoScanner:
    """
    Lightweight remote repository scanner.
    Indexes skills from remote git repos without cloning or storing the full repository.
    """

    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self.meta_cache_dir = os.path.join(cache_dir, "remote_meta")
        self.blob_cache_dir = os.path.join(cache_dir, "remote_blobs")
        os.makedirs(self.meta_cache_dir, exist_ok=True)
        os.makedirs(self.blob_cache_dir, exist_ok=True)

    def _get_auth_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": "Argus-Skill-Proxy/1.0",
            "Accept": "application/vnd.github.v3+json, text/plain, */*"
        }
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def scan_remote_source(
        self,
        source: SkillSource,
        parse_frontmatter_func: Any,
        infer_capabilities_func: Any,
        infer_frameworks_func: Any,
        estimate_tokens_func: Any,
        force_refresh: bool = False
    ) -> List[SkillPackage]:
        """
        Scan and return all skills from a remote repository.
        Uses cached metadata if fresh, otherwise runs zero-clone remote discovery.
        """
        meta_file = os.path.join(self.meta_cache_dir, f"{source.id}.json")
        
        # Check cache if not forcing refresh
        if not force_refresh and os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    packages = []
                    for item in data.get("skills", []):
                        pkg = SkillPackage(
                            id=item["id"],
                            source_id=source.id,
                            name=item["name"],
                            format=SkillFormat(item.get("format", SkillFormat.ANTIGRAVITY_SKILL.value)),
                            description=item.get("description", ""),
                            category=item.get("category", "general"),
                            tags=item.get("tags", []),
                            version=item.get("version", "1.0.0"),
                            author=item.get("author", "remote"),
                            capabilities=item.get("capabilities", []),
                            compatible_frameworks=item.get("compatible_frameworks", []),
                            conflicts_with=item.get("conflicts_with", []),
                            required_tools=item.get("required_tools", []),
                            actionability_score=item.get("actionability_score", 0.9),
                            file_path=item.get("file_path"),
                            remote_url=item.get("remote_url"),
                            raw_content=item.get("raw_content"),
                            token_count=item.get("token_count", 0),
                            metadata=item.get("metadata", {})
                        )
                        packages.append(pkg)
                    return packages
            except Exception:
                pass

        # Perform remote discovery without full clone
        discovered_files = self._fetch_remote_skill_files(source)
        
        packages: List[SkillPackage] = []
        for file_path, content, raw_url in discovered_files:
            pkg = self._parse_remote_skill_file(
                file_path=file_path,
                content=content,
                raw_url=raw_url,
                source=source,
                parse_frontmatter_func=parse_frontmatter_func,
                infer_capabilities_func=infer_capabilities_func,
                infer_frameworks_func=infer_frameworks_func,
                estimate_tokens_func=estimate_tokens_func
            )
            if pkg:
                packages.append(pkg)

        # Save to metadata cache
        try:
            cache_payload = {
                "source_id": source.id,
                "location": source.location,
                "synced_at": time.time(),
                "skill_count": len(packages),
                "skills": [p.to_dict() for p in packages]
            }
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(cache_payload, f, indent=2)
        except Exception:
            pass

        return packages

    def _fetch_remote_skill_files(self, source: SkillSource) -> List[Tuple[str, str, Optional[str]]]:
        """
        Multi-tier remote fetcher:
        1. Local mirror if available (fast path for offline/local environments)
        2. Tier 1: GitHub Trees API + Raw Content (Fastest, zero disk)
        3. Tier 2: In-Memory Streaming Tarball (Fallback if GitHub rate limit)
        4. Tier 3: Shallow Sparse Git Checkout (Generic/Private Git)
        """
        scratch_alt = os.path.expanduser("~/.gemini/antigravity/scratch/skills-and-rules")
        if os.path.exists(scratch_alt) and "skills-and-rules" in source.location:
            results: List[Tuple[str, str, Optional[str]]] = []
            for root, dirs, files in os.walk(scratch_alt):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__")]
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, scratch_alt).replace("\\", "/")
                    if is_skill_file_path(rel_p):
                        try:
                            with open(full_p, "r", encoding="utf-8", errors="replace") as fh:
                                results.append((rel_p, fh.read(), None))
                        except Exception:
                            pass
            if results:
                return results

        parsed = parse_git_url(source.location)
        branch = source.branch or parsed.get("branch") or "main"
        
        # Tier 1: GitHub Trees API
        if parsed.get("provider") == "github" and parsed.get("owner") and parsed.get("repo"):
            owner = parsed["owner"]
            repo = parsed["repo"]
            
            # 1. Try Git Trees API
            tree_skills = self._try_github_trees_api(owner, repo, branch)
            if tree_skills is not None and len(tree_skills) > 0:
                return tree_skills

            # 2. Try In-Memory Stream Tarball
            tar_skills = self._try_stream_tarball(owner, repo, branch)
            if tar_skills is not None and len(tar_skills) > 0:
                return tar_skills

        # Tier 3: Sparse git filter clone
        sparse_skills = self._try_sparse_git_filter(source.location, branch, source.id)
        if sparse_skills:
            return sparse_skills

        return []

    def _try_github_trees_api(self, owner: str, repo: str, branch: str) -> Optional[List[Tuple[str, str, Optional[str]]]]:
        """Query GitHub Recursive Tree API and fetch only skill file contents."""
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        req = urllib.request.Request(api_url, headers=self._get_auth_headers())
        
        try:
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status != 200:
                    return None
                data = json.loads(response.read().decode("utf-8"))
                tree = data.get("tree", [])
                
                skill_entries = [
                    item for item in tree
                    if item.get("type") == "blob" and is_skill_file_path(item.get("path", ""))
                ]

                results: List[Tuple[str, str, Optional[str]]] = []
                for entry in skill_entries:
                    file_path = entry["path"]
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
                    
                    # Fetch raw text
                    content = self._fetch_raw_url(raw_url)
                    if content is not None:
                        results.append((file_path, content, raw_url))

                return results
        except Exception:
            return None

    def _try_stream_tarball(self, owner: str, repo: str, branch: str) -> Optional[List[Tuple[str, str, Optional[str]]]]:
        """Stream tarball from GitHub and extract only skill/rule files into memory."""
        import io
        tar_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.tar.gz"
        req = urllib.request.Request(tar_url, headers=self._get_auth_headers())
        
        try:
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status != 200:
                    return None
                
                # Stream into memory and parse with tarfile
                compressed_data = io.BytesIO(response.read())
                results: List[Tuple[str, str, Optional[str]]] = []
                
                with tarfile.open(fileobj=compressed_data, mode="r:gz") as tar:
                    for member in tar.getmembers():
                        if member.isfile():
                            # Remove root archive directory name (e.g. 'skills-and-rules-main/...')
                            parts = member.name.split("/", 1)
                            rel_path = parts[1] if len(parts) > 1 else parts[0]
                            
                            if is_skill_file_path(rel_path):
                                f = tar.extractfile(member)
                                if f:
                                    content = f.read().decode("utf-8", errors="replace")
                                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{rel_path}"
                                    results.append((rel_path, content, raw_url))

                return results
        except Exception:
            return None

    def _try_sparse_git_filter(self, location: str, branch: str, source_id: str) -> List[Tuple[str, str, Optional[str]]]:
        """
        Generic Git fallback using git blob-filter and sparse checkout.
        Only fetches commit metadata and skill directories, never downloading the whole repo.
        """
        sparse_dir = os.path.join(self.cache_dir, f"sparse_{source_id}")
        results: List[Tuple[str, str, Optional[str]]] = []
        
        try:
            if not os.path.exists(os.path.join(sparse_dir, ".git")):
                os.makedirs(sparse_dir, exist_ok=True)
                # Clone with no blobs downloaded and fast connect timeout
                cmd = ["git", "-c", "http.connectTimeout=2", "-c", "http.lowSpeedTime=2", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1"]
                if branch:
                    cmd.extend(["-b", branch])
                cmd.extend([location, sparse_dir])
                res = subprocess.run(cmd, capture_output=True, timeout=5)
                if res.returncode != 0:
                    return results

                # Enable sparse checkout for skill patterns only
                subprocess.run(["git", "-C", sparse_dir, "sparse-checkout", "init", "--cone"], capture_output=True, timeout=3)
                subprocess.run(["git", "-C", sparse_dir, "sparse-checkout", "set", "skills", "rules", ".cursor", ".github", "prompts"], capture_output=True, timeout=3)
                subprocess.run(["git", "-C", sparse_dir, "checkout"], capture_output=True, timeout=5)
            else:
                subprocess.run(["git", "-C", sparse_dir, "pull", "--ff-only"], capture_output=True, timeout=5)

            # Scan the sparse checked-out directory
            for root, dirs, files in os.walk(sparse_dir):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__")]
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, sparse_dir).replace("\\", "/")
                    if is_skill_file_path(rel_p):
                        try:
                            with open(full_p, "r", encoding="utf-8", errors="replace") as fh:
                                content = fh.read()
                                results.append((rel_p, content, None))
                        except Exception:
                            pass
        except Exception:
            pass

        return results

    def _fetch_raw_url(self, url: str) -> Optional[str]:
        """Fetch raw content of a single remote skill file."""
        req = urllib.request.Request(url, headers=self._get_auth_headers())
        try:
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    return response.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return None

    def fetch_skill_raw_content(self, source: SkillSource, pkg: SkillPackage) -> Optional[str]:
        """Retrieve full markdown content for a specific remote skill on demand."""
        # 1. Return if already in package
        if pkg.raw_content:
            return pkg.raw_content

        # 2. Check cached blob file
        blob_path = os.path.join(self.blob_cache_dir, f"{source.id}_{pkg.id}.md")
        if os.path.exists(blob_path):
            try:
                with open(blob_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass

        # 3. Fetch from remote_url if available
        if pkg.remote_url:
            content = self._fetch_raw_url(pkg.remote_url)
            if content:
                try:
                    with open(blob_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass
                return content

        # 4. Fallback to GitHub raw calculation
        parsed = parse_git_url(source.location)
        if parsed.get("provider") == "github" and parsed.get("owner") and parsed.get("repo") and pkg.file_path:
            branch = source.branch or parsed.get("branch") or "main"
            raw_url = f"https://raw.githubusercontent.com/{parsed['owner']}/{parsed['repo']}/{branch}/{pkg.file_path}"
            content = self._fetch_raw_url(raw_url)
            if content:
                try:
                    with open(blob_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass
                return content

        return None

    def _parse_remote_skill_file(
        self,
        file_path: str,
        content: str,
        raw_url: Optional[str],
        source: SkillSource,
        parse_frontmatter_func: Any,
        infer_capabilities_func: Any,
        infer_frameworks_func: Any,
        estimate_tokens_func: Any
    ) -> Optional[SkillPackage]:
        """Parse raw remote content into a standardized SkillPackage."""
        if not content or len(content.strip()) < 20:
            return None

        meta, body = parse_frontmatter_func(content)
        norm_path = file_path.replace("\\", "/")
        base_name = os.path.splitext(os.path.basename(norm_path))[0]
        
        # Determine format
        if norm_path.endswith("SKILL.md"):
            s_format = SkillFormat.ANTIGRAVITY_SKILL
            folder_name = os.path.basename(os.path.dirname(norm_path))
            skill_id = meta.get("name", folder_name or base_name)
        elif norm_path.endswith(".mdc") or norm_path.endswith(".cursorrules"):
            s_format = SkillFormat.CURSOR_MDC
            skill_id = f"cursor-{base_name}"
        elif "copilot" in norm_path.lower():
            s_format = SkillFormat.COPILOT_INSTRUCTION
            skill_id = "github-copilot-instructions"
        else:
            s_format = SkillFormat.GENERIC_MARKDOWN
            skill_id = base_name

        name = meta.get("name")
        if not name:
            # Look for heading
            for line in content.splitlines():
                if line.startswith("# "):
                    name = line[2:].strip()
                    break
            if not name:
                name = skill_id

        description = meta.get("description", "")
        if not description:
            lines = [l.strip() for l in body.splitlines() if l.strip() and not l.startswith("#")]
            description = lines[0] if lines else f"Remote skill: {name}"

        # Category detection
        category = meta.get("category", "")
        if not category:
            parts = norm_path.split("/")
            if len(parts) > 2:
                category = parts[len(parts) - 2]
            else:
                category = "remote-skills"

        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        caps = meta.get("capabilities", [])
        if not caps:
            caps = infer_capabilities_func(name, description, body)

        frameworks = meta.get("frameworks", meta.get("compatible_frameworks", []))
        if not frameworks:
            frameworks = infer_frameworks_func(name, description, body)

        return SkillPackage(
            id=skill_id,
            source_id=source.id,
            name=name,
            format=s_format,
            description=description,
            category=category,
            tags=tags,
            version=str(meta.get("version", "1.0.0")),
            author=meta.get("author", f"github:{parsed['owner']}" if (parsed := parse_git_url(source.location)).get("owner") else "remote"),
            capabilities=caps,
            compatible_frameworks=frameworks,
            conflicts_with=[],
            required_tools=[],
            actionability_score=0.95 if ("```" in body or "## " in body) else 0.8,
            file_path=norm_path,
            remote_url=raw_url,
            raw_content=content,
            token_count=estimate_tokens_func(content),
            metadata=meta
        )
