"""
Unit & Integration Tests for Argus: Multi-Repository Skill Proxy & Goal-Aware Search Engine.
"""

import unittest
import json
import os
import shutil
import tempfile
from argus.models import SourceType, SkillFormat
from argus.engine import GoalAnalyzer, tokenize
from argus.sources import SourceManager, parse_frontmatter
from argus.proxy import ArgusProxy
from argus.mcp import ArgusMCPServer


class TestArgusGoalAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = GoalAnalyzer()

    def test_analyze_3d_website_prompt(self):
        analysis = self.analyzer.analyze("make a 3d website with interactive scene and animations")
        self.assertEqual(analysis.deliverable_type, "3d_web_application")
        self.assertIn("3d-graphics", analysis.target_domains)
        self.assertIn("threejs", analysis.detected_frameworks)
        self.assertIn("3d_rendering_engine", analysis.inferred_needs)

    def test_analyze_fastapi_rest_backend(self):
        analysis = self.analyzer.analyze("build a high throughput fastapi backend with postgres and pydantic")
        self.assertEqual(analysis.deliverable_type, "rest_api_service")
        self.assertIn("web-frameworks", analysis.target_domains)
        self.assertIn("fastapi", analysis.detected_frameworks)
        self.assertIn("postgres", analysis.detected_frameworks)

    def test_analyze_fullstack_dashboard(self):
        analysis = self.analyzer.analyze("create a modern nextjs app router dashboard with supabase realtime and tailwind")
        self.assertEqual(analysis.deliverable_type, "fullstack_web_app")
        self.assertIn("nextjs", analysis.detected_frameworks)
        self.assertIn("supabase", analysis.detected_frameworks)
        self.assertIn("tailwind", analysis.detected_frameworks)

    def test_analyze_ai_agent(self):
        analysis = self.analyzer.analyze("build an autonomous rag agent with embeddings and mcp tool calling")
        self.assertEqual(analysis.deliverable_type, "ai_agent_system")
        self.assertIn("ai-llm-agents", analysis.target_domains)


class TestArgusSourceManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sm = SourceManager(config_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_sources_initialized(self):
        sources = self.sm.list_sources()
        self.assertGreater(len(sources), 0)
        ids = [s.id for s in sources]
        self.assertIn("builtin-vault", ids)
        self.assertIn("antigravity-system", ids)

    def test_add_and_remove_source(self):
        custom_src = self.sm.add_source(
            id="my-custom-vault",
            name="Custom Vault",
            source_type=SourceType.LOCAL_DIR,
            location="/tmp/custom-skills"
        )
        self.assertEqual(custom_src.id, "my-custom-vault")
        self.assertIsNotNone(self.sm.get_source("my-custom-vault"))

        removed = self.sm.remove_source("my-custom-vault")
        self.assertTrue(removed)
        self.assertIsNone(self.sm.get_source("my-custom-vault"))

    def test_parse_frontmatter(self):
        text = "---\nname: test-skill\ndescription: A test skill\ncapabilities: [a, b]\n---\n# Instructions\nDo something."
        meta, body = parse_frontmatter(text)
        self.assertEqual(meta["name"], "test-skill")
        self.assertEqual(meta["description"], "A test skill")
        self.assertEqual(meta["capabilities"], ["a", "b"])
        self.assertIn("# Instructions", body)


class TestArgusProxyAndMatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proxy = ArgusProxy()

    def test_match_3d_website(self):
        bundle = self.proxy.match("make a 3d website", top_k=5)
        self.assertIsNotNone(bundle)
        self.assertEqual(bundle.goal_analysis.deliverable_type, "3d_web_application")
        self.assertGreater(len(bundle.selected_matches), 0)
        
        # Check that top match relates to 3D rendering
        top = bundle.selected_matches[0]
        self.assertGreater(top.composite_rank_score, 0.5)
        self.assertTrue("3d" in top.skill.name.lower() or "canvas" in top.skill.name.lower() or "img2threejs" in top.skill.name.lower())
        self.assertIn("# ARGUS AUTONOMOUS AGENT SKILL MANIFEST", bundle.compiled_agent_instructions)

    def test_search_skills(self):
        results = self.proxy.search("fastapi rest api", top_k=3)
        self.assertGreater(len(results), 0)
        names = [r.skill.name for r in results]
        self.assertTrue(any("fastapi" in n for n in names))

    def test_fetch_skill(self):
        # Fetch an existing skill
        content = self.proxy.fetch("threejs-procedural-canvas")
        if not content:
            content = self.proxy.fetch("img2threejs")
        self.assertIsNotNone(content)
        self.assertGreater(len(content), 20)


class TestArgusMCPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proxy = ArgusProxy()
        cls.server = ArgusMCPServer(cls.proxy)

    def test_initialize(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        resp = self.server.handle_request(req)
        self.assertEqual(resp["result"]["serverInfo"]["name"], "argus-skill-proxy-mcp")

    def test_tools_list(self):
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        resp = self.server.handle_request(req)
        tool_names = [t["name"] for t in resp["result"]["tools"]]
        self.assertIn("argus_match_goal", tool_names)
        self.assertIn("argus_search_skills", tool_names)
        self.assertIn("argus_fetch_skill", tool_names)
        self.assertIn("argus_list_sources", tool_names)

    def test_call_match_goal(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "argus_match_goal",
                "arguments": {"prompt": "make a 3d website", "top_k": 3}
            }
        }
        resp = self.server.handle_request(req)
        self.assertIn("result", resp)
        self.assertIn("ARGUS AUTONOMOUS AGENT SKILL MANIFEST", resp["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
