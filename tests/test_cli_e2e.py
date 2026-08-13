import unittest
import subprocess
import json
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ESH_BIN = os.path.join(BASE_DIR, "bin", "eshkill")
ASK_BIN = os.path.join(BASE_DIR, "bin", "askill")
PYTHON_BIN = sys.executable


class TestCLIEndToEnd(unittest.TestCase):
    def run_cmd(self, bin_path: str, args: list) -> subprocess.CompletedProcess:
        cmd = [PYTHON_BIN, bin_path] + args
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{os.path.join(BASE_DIR, 'cli')}:{os.path.join(BASE_DIR, 'backend')}"
        return subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)

    def test_eshkill_version(self):
        res = self.run_cmd(ESH_BIN, ["--version"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("eshkill", res.stdout)
        self.assertIn("1.1.0", res.stdout)

    def test_askill_version(self):
        res = self.run_cmd(ASK_BIN, ["--version"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("askill", res.stdout)
        self.assertIn("1.1.0", res.stdout)

    def test_cli_list_json(self):
        res = self.run_cmd(ESH_BIN, ["list", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertGreater(data["total"], 20)
        self.assertIn("skills", data)

    def test_cli_categories_json(self):
        res = self.run_cmd(ESH_BIN, ["categories", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertTrue("web-frameworks" in data or "databases-storage" in data)

    def test_cli_search_json(self):
        res = self.run_cmd(ESH_BIN, ["search", "fastapi pydantic rest api", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertGreater(data["total_results"], 0)
        self.assertEqual(data["results"][0]["id"], "web-frameworks.python-api.fastapi-production-craft")

    def test_cli_search_unicode_persian(self):
        res = self.run_cmd(ESH_BIN, ["search", "دیوار", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertGreater(data["total_results"], 0)
        self.assertEqual(data["results"][0]["name"], "divar-marketplace-automation")

    def test_cli_auto_select_json(self):
        res = self.run_cmd(ESH_BIN, ["auto-select", "build a real-time chat with supabase and nextjs 15", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("detected_stack", data)
        self.assertIn("selected_skills", data)
        self.assertIn("unified_payload", data)
        self.assertGreaterEqual(len(data["selected_skills"]), 2)

    def test_cli_auto_select_cursor_format(self):
        res = self.run_cmd(ESH_BIN, ["auto-select", "build nextjs and tailwind app", "--format", "cursor"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Cursor Vibe-Coding Rules", res.stdout)
        self.assertIn("nextjs", res.stdout.lower())

    def test_cli_match_xml(self):
        res = self.run_cmd(ESH_BIN, ["match", "--task", "Write playwright end to end automated tests", "--format", "xml"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("<agent_skill", res.stdout)
        self.assertIn("playwright-e2e-automation", res.stdout)

    def test_cli_match_system(self):
        res = self.run_cmd(ESH_BIN, ["match", "--task", "optimize postgres database query performance", "--format", "system"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("ACTIVATED AGENT SKILL", res.stdout)
        self.assertIn("PostgreSQL", res.stdout)

    def test_cli_install_temp_json(self):
        res = self.run_cmd(ESH_BIN, ["install", "fastapi-production-craft", "--temp", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertTrue(data["success"])
        self.assertEqual(data["mode"], "temp")
        self.assertIn("FastAPI", data["ephemeral_content"])

    def test_cli_install_cursor_ide(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_ws:
            res = self.run_cmd(ESH_BIN, ["install", "tailwind-v4-tokens", "--ide", "cursor", "--dir", tmp_ws])
            self.assertEqual(res.returncode, 0)
            rule_path = os.path.join(tmp_ws, ".cursor", "rules", "tailwind-v4-tokens.mdc")
            self.assertTrue(os.path.exists(rule_path))
            with open(rule_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("globs: *", content)
            self.assertIn("Tailwind CSS v4", content)

    def test_cli_install_stack(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_ws:
            res = self.run_cmd(ESH_BIN, ["install-stack", "build a fastapi service with docker and postgres", "--ide", "all", "--dir", tmp_ws, "--json"])
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertGreaterEqual(data["installed_count"], 2)
            # Check created files in temp workspace
            self.assertTrue(os.path.exists(os.path.join(tmp_ws, ".windsurfrules")))
            self.assertTrue(os.path.exists(os.path.join(tmp_ws, "CLAUDE.md")))
            self.assertTrue(os.path.exists(os.path.join(tmp_ws, ".github", "copilot-instructions.md")))

    def test_cli_get_markdown(self):
        res = self.run_cmd(ESH_BIN, ["get", "web-frameworks.python-api.fastapi-production-craft"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("FastAPI", res.stdout)

    def test_cli_info_json(self):
        res = self.run_cmd(ESH_BIN, ["info", "owasp-top10-scanner", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data["name"], "owasp-top10-scanner")
        self.assertEqual(data["category"], "security-sast-hardening")

    def test_cli_propose_json(self):
        res = self.run_cmd(ESH_BIN, [
            "propose",
            "--skill", "fastapi-production-craft",
            "--content", "# Updated guidelines\n\n- Added CORS middleware setup.",
            "--reason", "Add CORS middleware best practices",
            "--json"
        ])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertTrue(data["success"])
        self.assertIn(data["status"], ["pending", "ready_for_pr"])

    def test_cli_test_router(self):
        res = self.run_cmd(ESH_BIN, ["test-router"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("Running eshkill Auto-Router Validation Suite", res.stdout)
        self.assertIn("6/6 tests passed", res.stdout)


if __name__ == "__main__":
    unittest.main()

