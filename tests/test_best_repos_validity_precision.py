"""
Argus Best Skill Repositories Validity & Precision Test Suite.
Verifies:
1. Repository Validity (URLs, schemas, trust scores, branch targets, metadata).
2. Pattern Matching Precision (Zero false positives on non-skill files, 100% precision on skill files).
3. Parsing & Normalization Precision across Antigravity, Cursor, Anthropic, and Agentic rules.
4. Goal-Aware Ranking & Synergy Precision.
5. Dynamic Update & Repository Discovery Engine Integrity.
"""

import os
import sys
import unittest
import json
import tempfile
from unittest.mock import patch, MagicMock

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if os.path.join(BASE_DIR, "cli") not in sys.path:
    sys.path.insert(0, os.path.join(BASE_DIR, "cli"))

from argus.models import SkillSource, SkillPackage, SourceType, SkillFormat, GoalAnalysis
from argus.remote import (
    parse_git_url, is_skill_file_path, is_remote_location, RemoteRepoScanner
)
from argus.sources import (
    SourceManager, DEFAULT_SOURCES, parse_frontmatter, estimate_tokens
)
from argus.engine import GoalAnalyzer, ArgusSearchIndex
from argus.ranker import GoalAwareRanker


class TestBestReposValidity(unittest.TestCase):
    """Verifies validity of all pre-configured best skill repositories."""

    def test_default_sources_integrity(self):
        """Ensure all default skill sources are properly defined with valid metadata."""
        self.assertGreaterEqual(len(DEFAULT_SOURCES), 10, "Expected at least 10 premier skill sources")
        
        source_ids = {s.id for s in DEFAULT_SOURCES}
        expected_ids = {
            "builtin-vault",
            "antigravity-system",
            "skills-and-rules-repo",
            "cursor-workspace-rules",
            "obra-superpowers",
            "anthropics-skills",
            "leonxlnx-taste-skill",
            "patrickjs-awesome-cursorrules",
            "wshobson-agents",
            "dietrich-gebert-ponytail",
            "modelcontextprotocol-servers"
        }
        for exp in expected_ids:
            self.assertIn(exp, source_ids, f"Required premier source '{exp}' missing from DEFAULT_SOURCES")

    def test_repository_urls_and_branches(self):
        """Validate that all remote sources have valid GitHub URLs and default branches."""
        for src in DEFAULT_SOURCES:
            self.assertTrue(src.id, "Source ID must not be empty")
            self.assertTrue(src.name, f"Source '{src.id}' must have a valid display name")
            self.assertIsInstance(src.source_type, SourceType)
            self.assertGreater(src.priority, 0, f"Source '{src.id}' priority must be positive")
            self.assertGreater(src.trust_score, 0.0, f"Source '{src.id}' trust score must be positive")
            self.assertLessEqual(src.trust_score, 1.0, f"Source '{src.id}' trust score cannot exceed 1.0")

            if src.source_type == SourceType.GIT_REPO:
                self.assertTrue(
                    is_remote_location(src.location),
                    f"GIT_REPO source '{src.id}' location '{src.location}' must be a remote URL"
                )
                parsed = parse_git_url(src.location)
                self.assertEqual(parsed["provider"], "github", f"Source '{src.id}' must target GitHub")
                self.assertIsNotNone(parsed["owner"], f"Source '{src.id}' must have an owner")
                self.assertIsNotNone(parsed["repo"], f"Source '{src.id}' must have a repo name")
                self.assertTrue(src.branch in ("main", "master"), f"Source '{src.id}' branch must be main or master")


class TestSkillPatternPrecision(unittest.TestCase):
    """Verifies that skill path detection has 100% precision and zero false positives."""

    def test_positive_skill_paths(self):
        """Verify all legitimate skill and rule patterns are recognized."""
        valid_paths = [
            "skills/systematic-debugging/SKILL.md",
            "skills/test-driven-development/SKILL.md",
            "skills/subagent-driven-development/SKILL.md",
            "skills/algorithmic-art/SKILL.md",
            "skills/taste-skill/SKILL.md",
            "skills/brandkit/SKILL.md",
            "rules/typescript.mdc",
            "rules/react.mdc",
            "rules/fastapi.mdc",
            ".cursor/rules/000-project-conventions.mdc",
            ".cursor/rules/architecture-guidelines.md",
            ".agents/rules/ponytail.md",
            ".clinerules",
            ".clinerules/backend.md",
            ".cursorrules",
            ".github/copilot-instructions.md",
            "skills-vault/skills/devops/kubernetes.md",
            "rules/sast-hardening.md",
            "AGENTS.md",
            "CLAUDE.md",
            "GEMINI.md"
        ]
        for path in valid_paths:
            self.assertTrue(
                is_skill_file_path(path),
                f"Expected '{path}' to be recognized as a valid skill path"
            )

    def test_negative_non_skill_paths(self):
        """Verify that non-skill assets and files are strictly excluded (zero false positives)."""
        invalid_paths = [
            "README.md",
            "readme.md",
            "CHANGELOG.md",
            "LICENSE",
            "LICENSE.md",
            "LICENSE.txt",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "TODO.md",
            "docs/testing.md",
            "docs/README.md",
            "docs/porting-to-a-new-harness.md",
            "package.json",
            "package-lock.json",
            "src/index.ts",
            "src/server.py",
            "assets/logo.png",
            "examples/floria-full.webp",
            "scripts/helper.js",
            ".github/FUNDING.yml",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            "tests/test_search.py"
        ]
        for path in invalid_paths:
            self.assertFalse(
                is_skill_file_path(path),
                f"Expected '{path}' to be excluded from skill paths (false positive)"
            )


class TestParserNormalizationPrecision(unittest.TestCase):
    """Verifies that remote skill markdown files are normalized into accurate SkillPackage objects."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.scanner = RemoteRepoScanner(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_anthropic_skill(self):
        """Test parsing an Anthropic-format SKILL.md."""
        content = """---
name: web-search-pro
description: Advanced web research, citation synthesis, and source verification.
category: research-intelligence
tags: [search, research, citations, verification]
capabilities: [web_search, fact_checking]
frameworks: [python, node]
version: 2.1.0
---

# Web Search Pro Skill

Execute deep search and synthesize verifiable citations.

## Usage
```python
results = search_and_verify(query="AI benchmarks 2026")
```
"""
        source = SkillSource(
            id="anthropics-skills",
            name="Anthropic Claude Agent Skills",
            source_type=SourceType.GIT_REPO,
            location="https://github.com/anthropics/skills",
            branch="main"
        )
        pkg = self.scanner._parse_remote_skill_file(
            file_path="skills/web-search-pro/SKILL.md",
            content=content,
            raw_url="https://raw.githubusercontent.com/anthropics/skills/main/skills/web-search-pro/SKILL.md",
            source=source,
            parse_frontmatter_func=parse_frontmatter,
            infer_capabilities_func=lambda n, d, b: [],
            infer_frameworks_func=lambda n, d, b: [],
            estimate_tokens_func=estimate_tokens
        )
        self.assertIsNotNone(pkg)
        self.assertEqual(pkg.id, "web-search-pro")
        self.assertEqual(pkg.name, "web-search-pro")
        self.assertEqual(pkg.category, "research-intelligence")
        self.assertIn("web_search", pkg.capabilities)
        self.assertEqual(pkg.format, SkillFormat.ANTIGRAVITY_SKILL)
        self.assertGreater(pkg.actionability_score, 0.9)

    def test_parse_cursor_mdc_rule(self):
        """Test parsing a Cursor .mdc rule from Awesome-Cursorrules."""
        content = """---
description: Comprehensive FastAPI production standards with Pydantic v2 and async SQLAlchemy.
globs: ["backend/**/*.py", "api/**/*.py"]
---

# FastAPI Production Rules

Always use async def endpoints and validate request models with Pydantic v2.

```python
@app.get("/items", response_model=ItemResponse)
async def read_items(db: AsyncSession = Depends(get_db)):
    pass
```
"""
        source = SkillSource(
            id="patrickjs-awesome-cursorrules",
            name="Awesome Cursor Rules",
            source_type=SourceType.GIT_REPO,
            location="https://github.com/PatrickJS/awesome-cursorrules",
            branch="main"
        )
        pkg = self.scanner._parse_remote_skill_file(
            file_path="rules/fastapi-production.mdc",
            content=content,
            raw_url="https://raw.githubusercontent.com/PatrickJS/awesome-cursorrules/main/rules/fastapi-production.mdc",
            source=source,
            parse_frontmatter_func=parse_frontmatter,
            infer_capabilities_func=lambda n, d, b: ["rest_api", "database_sql"],
            infer_frameworks_func=lambda n, d, b: ["fastapi", "pydantic"],
            estimate_tokens_func=estimate_tokens
        )
        self.assertIsNotNone(pkg)
        self.assertEqual(pkg.id, "cursor-fastapi-production")
        self.assertEqual(pkg.format, SkillFormat.CURSOR_MDC)
        self.assertIn("rest_api", pkg.capabilities)
        self.assertIn("fastapi", pkg.compatible_frameworks)


class TestGoalMatchingAndRankingPrecision(unittest.TestCase):
    """Verifies that goal-aware matching selects the exact right skills for specific user goals."""

    def setUp(self):
        self.goal_analyzer = GoalAnalyzer()
        self.source_map = {
            "obra-superpowers": SkillSource(
                id="obra-superpowers",
                name="Agentic Superpowers",
                source_type=SourceType.GIT_REPO,
                location="https://github.com/obra/superpowers",
                priority=94,
                trust_score=0.97
            ),
            "leonxlnx-taste-skill": SkillSource(
                id="leonxlnx-taste-skill",
                name="Frontend Taste",
                source_type=SourceType.GIT_REPO,
                location="https://github.com/Leonxlnx/taste-skill",
                priority=88,
                trust_score=0.93
            ),
            "patrickjs-awesome-cursorrules": SkillSource(
                id="patrickjs-awesome-cursorrules",
                name="Cursor Rules",
                source_type=SourceType.GIT_REPO,
                location="https://github.com/PatrickJS/awesome-cursorrules",
                priority=89,
                trust_score=0.94
            )
        }
        self.mock_skills = [
            SkillPackage(
                id="systematic-debugging",
                source_id="obra-superpowers",
                name="Systematic Debugging & Root Cause Analysis",
                format=SkillFormat.ANTIGRAVITY_SKILL,
                description="Rigorous debugging framework for isolating root causes before writing fixes.",
                category="engineering-discipline",
                tags=["debugging", "root-cause", "investigation"],
                capabilities=["debugging_logging", "unit_testing"],
                compatible_frameworks=[],
                actionability_score=0.98
            ),
            SkillPackage(
                id="taste-skill-minimalist",
                source_id="leonxlnx-taste-skill",
                name="Minimalist High-Taste UI Design",
                format=SkillFormat.ANTIGRAVITY_SKILL,
                description="Frontend design system preventing AI-slop with clean typography and spacing.",
                category="ui-design",
                tags=["design", "ui", "minimalist", "anti-slop"],
                capabilities=["frontend_ui", "styling_css"],
                compatible_frameworks=["tailwind", "react"],
                actionability_score=0.95
            ),
            SkillPackage(
                id="cursor-fastapi-backend",
                source_id="patrickjs-awesome-cursorrules",
                name="FastAPI Production Backend Rules",
                format=SkillFormat.CURSOR_MDC,
                description="Production guidelines for high-throughput FastAPI and PostgreSQL applications.",
                category="backend",
                tags=["fastapi", "python", "backend"],
                capabilities=["rest_api", "database_sql"],
                compatible_frameworks=["fastapi", "python"],
                actionability_score=0.92
            )
        ]
        self.search_index = ArgusSearchIndex(self.mock_skills)
        self.ranker = GoalAwareRanker(sources_map=self.source_map)

    def test_debugging_goal_matches_superpowers(self):
        """A prompt requesting systematic debugging must rank systematic-debugging at top 1."""
        prompt = "We have a subtle race condition in our background worker, need to debug root cause systematically"
        goal = self.goal_analyzer.analyze(prompt)
        matches = self.ranker.rank_candidates(goal, self.mock_skills, self.search_index, top_k=3)
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].skill.id, "systematic-debugging")
        self.assertEqual(matches[0].skill.source_id, "obra-superpowers")
        self.assertEqual(matches[0].confidence, "high")

    def test_frontend_taste_goal_matches_taste_skill(self):
        """A prompt requesting anti-slop clean design must rank taste skill at top 1."""
        prompt = "Redesign our website interface with minimalist typography and avoid AI slop aesthetics"
        goal = self.goal_analyzer.analyze(prompt)
        matches = self.ranker.rank_candidates(goal, self.mock_skills, self.search_index, top_k=3)
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].skill.id, "taste-skill-minimalist")
        self.assertEqual(matches[0].skill.source_id, "leonxlnx-taste-skill")


class TestSourceManagerUpdateBest(unittest.TestCase):
    """Verifies update_best_repositories and dynamic GitHub repository discovery."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mgr = SourceManager(config_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_update_best_repositories_without_discovery(self):
        """Ensure all default best repositories are populated and persisted."""
        res = self.mgr.update_best_repositories(auto_discover=False)
        self.assertIn("total_sources", res)
        self.assertGreaterEqual(res["total_sources"], 10)
        
        # Verify persistence on disk
        sources_file = os.path.join(self.temp_dir.name, "sources.json")
        self.assertTrue(os.path.exists(sources_file))
        with open(sources_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            stored_ids = {s["id"] for s in data["sources"]}
            self.assertIn("obra-superpowers", stored_ids)
            self.assertIn("anthropics-skills", stored_ids)
            self.assertIn("leonxlnx-taste-skill", stored_ids)
            self.assertIn("patrickjs-awesome-cursorrules", stored_ids)

    def test_preserves_custom_user_sources(self):
        """Ensure that user-added custom sources are preserved during best repos sync."""
        self.mgr.add_source(
            id="my-private-vault",
            name="My Private Skills",
            source_type=SourceType.LOCAL_DIR,
            location="/custom/path"
        )
        res = self.mgr.update_best_repositories(auto_discover=False)
        self.assertIsNotNone(self.mgr.get_source("my-private-vault"))
        self.assertEqual(self.mgr.get_source("my-private-vault").name, "My Private Skills")

    @patch("urllib.request.urlopen")
    def test_auto_discover_github_repos(self, mock_urlopen):
        """Verify dynamic discovery of trending GitHub skill repos with stars >= 500."""
        mock_api_resp = json.dumps({
            "items": [
                {
                    "name": "nextgen-agent-skills",
                    "html_url": "https://github.com/cool-ai/nextgen-agent-skills",
                    "stargazers_count": 12500,
                    "default_branch": "main",
                    "description": "State-of-the-art agent skills collection",
                    "owner": {"login": "cool-ai"}
                }
            ]
        }).encode("utf-8")

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = mock_api_resp
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.mgr.update_best_repositories(auto_discover=True)
        self.assertGreaterEqual(res.get("auto_discovered_count", 0), 1)
        self.assertIn("gh-cool-ai-nextgen-agent-skills", self.mgr.sources)
        discovered_src = self.mgr.sources["gh-cool-ai-nextgen-agent-skills"]
        self.assertEqual(discovered_src.location, "https://github.com/cool-ai/nextgen-agent-skills")
        self.assertTrue(discovered_src.metadata.get("auto_discovered"))


if __name__ == "__main__":
    unittest.main()
