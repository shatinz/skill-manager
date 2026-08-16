"""
Unit & Integration Tests for Argus Remote Repository Search & Zero-Clone Indexing.
Verifies searching and matching skills across remote GitHub repositories without
downloading the whole repository on the local machine.
"""

import unittest
import json
import os
import io
import tarfile
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from argus.models import SkillSource, SkillPackage, SourceType, SkillFormat
from argus.remote import (
    parse_git_url, is_remote_location, is_skill_file_path,
    RemoteRepoScanner
)
from argus.sources import SourceManager, parse_frontmatter, estimate_tokens
from argus.proxy import ArgusProxy


class TestRemoteRepoParser(unittest.TestCase):
    def test_parse_github_https_urls(self):
        res1 = parse_git_url("https://github.com/shatinz/skills-and-rules")
        self.assertEqual(res1["provider"], "github")
        self.assertEqual(res1["owner"], "shatinz")
        self.assertEqual(res1["repo"], "skills-and-rules")
        self.assertEqual(res1["branch"], "main")

        res2 = parse_git_url("https://github.com/facebook/react/tree/main")
        self.assertEqual(res2["owner"], "facebook")
        self.assertEqual(res2["repo"], "react")
        self.assertEqual(res2["branch"], "main")

        res3 = parse_git_url("https://github.com/owner/repo.git")
        self.assertEqual(res3["owner"], "owner")
        self.assertEqual(res3["repo"], "repo")

    def test_parse_github_ssh_urls(self):
        res = parse_git_url("git@github.com:shatinz/skills-and-rules.git")
        self.assertEqual(res["provider"], "github")
        self.assertEqual(res["owner"], "shatinz")
        self.assertEqual(res["repo"], "skills-and-rules")

    def test_is_remote_location(self):
        self.assertTrue(is_remote_location("https://github.com/owner/repo"))
        self.assertTrue(is_remote_location("http://github.com/owner/repo"))
        self.assertTrue(is_remote_location("git@github.com:owner/repo.git"))
        self.assertFalse(is_remote_location("/home/user/my-skills"))
        self.assertFalse(is_remote_location("./skills-vault"))

    def test_is_skill_file_path(self):
        self.assertTrue(is_skill_file_path("skills/3d-graphics/img2threejs/SKILL.md"))
        self.assertTrue(is_skill_file_path("SKILL.md"))
        self.assertTrue(is_skill_file_path(".cursor/rules/web-design.mdc"))
        self.assertTrue(is_skill_file_path("skills/divar/SKILL.md"))
        self.assertTrue(is_skill_file_path(".cursorrules"))
        self.assertTrue(is_skill_file_path("copilot-instructions.md"))
        self.assertTrue(is_skill_file_path("rules/AGENTS.md"))
        
        # Ignored files
        self.assertFalse(is_skill_file_path("README.md"))
        self.assertFalse(is_skill_file_path("LICENSE.md"))
        self.assertFalse(is_skill_file_path("src/index.ts"))
        self.assertFalse(is_skill_file_path("package.json"))
        self.assertFalse(is_skill_file_path("assets/logo.png"))


class TestRemoteRepoZeroCloneScanner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scanner = RemoteRepoScanner(self.temp_dir)
        self.sample_skill_md = """---
name: remote-super-skill
description: A high-performance remote AI skill for WebGL and Canvas 3D rendering.
category: 3d-graphics
tags: [webgl, threejs, 3d, shader]
capabilities: [3d_rendering, frontend_ui]
frameworks: [threejs, react]
---
# Remote Super Skill
## Instructions
Execute WebGL canvas shaders with procedural 3D meshes.
"""

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("urllib.request.urlopen")
    def test_github_trees_api_zero_clone_discovery(self, mock_urlopen):
        # 1. Mock the GitHub Recursive Tree response
        mock_tree_json = json.dumps({
            "sha": "abc12345",
            "tree": [
                {"path": "skills/remote-super-skill/SKILL.md", "type": "blob", "size": len(self.sample_skill_md)},
                {"path": "large_dataset.bin", "type": "blob", "size": 104857600},  # Should be skipped!
                {"path": "src/main.rs", "type": "blob", "size": 4096},             # Should be skipped!
                {"path": "README.md", "type": "blob", "size": 500}                 # Should be skipped!
            ]
        }).encode("utf-8")

        # Mock responses: 1st call for tree, 2nd call for raw SKILL.md content
        mock_resp_tree = MagicMock()
        mock_resp_tree.status = 200
        mock_resp_tree.read.return_value = mock_tree_json
        mock_resp_tree.__enter__.return_value = mock_resp_tree

        mock_resp_raw = MagicMock()
        mock_resp_raw.status = 200
        mock_resp_raw.read.return_value = self.sample_skill_md.encode("utf-8")
        mock_resp_raw.__enter__.return_value = mock_resp_raw

        mock_urlopen.side_effect = [mock_resp_tree, mock_resp_raw]

        source = SkillSource(
            id="remote-github-test",
            name="Remote Test Vault",
            source_type=SourceType.GIT_REPO,
            location="https://github.com/shatinz/skills-and-rules",
            branch="main"
        )

        packages = self.scanner.scan_remote_source(
            source=source,
            parse_frontmatter_func=parse_frontmatter,
            infer_capabilities_func=lambda n, d, b: ["3d_rendering"],
            infer_frameworks_func=lambda n, d, b: ["threejs"],
            estimate_tokens_func=estimate_tokens,
            force_refresh=True
        )

        self.assertEqual(len(packages), 1)
        pkg = packages[0]
        self.assertEqual(pkg.id, "remote-super-skill")
        self.assertEqual(pkg.name, "remote-super-skill")
        self.assertIn("3d_rendering", pkg.capabilities)
        self.assertIn("threejs", pkg.compatible_frameworks)
        self.assertTrue(pkg.remote_url.startswith("https://raw.githubusercontent.com/shatinz/skills-and-rules/main/"))

        # Verify metadata was cached on disk without storing repo files
        cache_file = os.path.join(self.scanner.meta_cache_dir, "remote-github-test.json")
        self.assertTrue(os.path.exists(cache_file))

    @patch("urllib.request.urlopen")
    def test_in_memory_streaming_tarball_extraction(self, mock_urlopen):
        # Create an in-memory gzipped tar archive containing 1 skill file and 1 large dummy file
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
            # Skill file
            skill_data = self.sample_skill_md.encode("utf-8")
            ti_skill = tarfile.TarInfo(name="repo-main/skills/remote-super-skill/SKILL.md")
            ti_skill.size = len(skill_data)
            tar.addfile(ti_skill, io.BytesIO(skill_data))

            # Non-skill heavy source file (should NOT be written or saved)
            heavy_data = b"x" * 2048
            ti_heavy = tarfile.TarInfo(name="repo-main/src/heavy_binary.dat")
            ti_heavy.size = len(heavy_data)
            tar.addfile(ti_heavy, io.BytesIO(heavy_data))

        tar_buffer.seek(0)
        tar_bytes = tar_buffer.getvalue()

        # Mock 1st call (Tree API fail -> simulate rate limit), 2nd call (Tarball stream success)
        mock_tree_fail = MagicMock()
        mock_tree_fail.status = 403
        mock_tree_fail.__enter__.side_effect = Exception("Rate limit exceeded")

        mock_tar_resp = MagicMock()
        mock_tar_resp.status = 200
        mock_tar_resp.read.return_value = tar_bytes
        mock_tar_resp.__enter__.return_value = mock_tar_resp

        mock_urlopen.side_effect = [Exception("Rate limit"), mock_tar_resp]

        source = SkillSource(
            id="stream-tar-test",
            name="Stream Tar Vault",
            source_type=SourceType.GIT_REPO,
            location="https://github.com/shatinz/skills-and-rules",
            branch="main"
        )

        packages = self.scanner.scan_remote_source(
            source=source,
            parse_frontmatter_func=parse_frontmatter,
            infer_capabilities_func=lambda n, d, b: ["3d_rendering"],
            infer_frameworks_func=lambda n, d, b: ["threejs"],
            estimate_tokens_func=estimate_tokens,
            force_refresh=True
        )

        self.assertEqual(len(packages), 1)
        self.assertEqual(packages[0].id, "remote-super-skill")


class TestArgusRemoteIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sm = SourceManager(config_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_remote_source_properties(self):
        src = self.sm.add_source(
            id="custom-github-remote",
            name="Community GitHub Skills",
            source_type=SourceType.GIT_REPO,
            location="https://github.com/someuser/skills-repo"
        )
        self.assertTrue(src.is_remote)
        self.assertEqual(src.source_type, SourceType.GIT_REPO)

        src_dict = src.to_dict()
        self.assertTrue(src_dict["is_remote"])

    def test_proxy_search_and_fetch_with_remote_source(self):
        proxy = ArgusProxy(config_dir=self.temp_dir)
        
        # Inject a mock remote skill package
        mock_remote_pkg = SkillPackage(
            id="remote-cloud-architect",
            source_id="custom-github-remote",
            name="Remote Cloud Architect",
            format=SkillFormat.ANTIGRAVITY_SKILL,
            description="Designs serverless Kubernetes and Terraform pipelines on AWS.",
            category="devops-cloud",
            tags=["terraform", "kubernetes", "aws", "docker"],
            capabilities=["devops_deploy"],
            compatible_frameworks=["docker"],
            actionability_score=0.95,
            remote_url="https://raw.githubusercontent.com/someuser/skills-repo/main/skills/remote-cloud-architect/SKILL.md",
            raw_content="# Cloud Architect Instructions\nDeploy infrastructure.",
            token_count=50
        )

        proxy._cached_skills = [mock_remote_pkg]
        from argus.engine import ArgusSearchIndex
        proxy._cached_index = ArgusSearchIndex([mock_remote_pkg])

        # Search should find the remote skill
        results = proxy.search("kubernetes terraform cloud deploy")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].skill.id, "remote-cloud-architect")
        self.assertEqual(results[0].skill.source_id, "custom-github-remote")

        # Mock source_manager.scan_source_skills for fetch test
        with patch.object(proxy.source_manager, "scan_source_skills", return_value=[mock_remote_pkg]):
            content = proxy.fetch("remote-cloud-architect")
            self.assertIsNotNone(content)
            self.assertIn("Cloud Architect Instructions", content)


if __name__ == "__main__":
    unittest.main()
