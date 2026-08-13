import unittest
import subprocess
import json
import os

CLI_BIN = "/mnt/c/Users/PC/prj/skill-manager/bin/askill"
PYTHON_BIN = "/home/shatix/venv-skm/bin/python3"

class TestCLIEndToEnd(unittest.TestCase):
    def run_cmd(self, args: list) -> subprocess.CompletedProcess:
        cmd = [PYTHON_BIN, CLI_BIN] + args
        return subprocess.run(cmd, capture_output=True, text=True, check=False)

    def test_cli_version(self):
        res = self.run_cmd(["--version"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("askill", res.stdout)

    def test_cli_list_json(self):
        res = self.run_cmd(["list", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertGreater(data["total"], 20)
        self.assertIn("skills", data)

    def test_cli_categories_json(self):
        res = self.run_cmd(["categories", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("coding", data)
        self.assertIn("data-ai-engineering", data)

    def test_cli_search_json(self):
        res = self.run_cmd(["search", "fastapi pydantic rest api", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertGreater(data["total_results"], 0)
        self.assertEqual(data["results"][0]["id"], "coding.api-design.fastapi-rest-craft")

    def test_cli_match_xml(self):
        res = self.run_cmd(["match", "--task", "Write playwright end to end automated tests", "--format", "xml"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("<agent_skill", res.stdout)
        self.assertIn("playwright-e2e-automation", res.stdout)

    def test_cli_match_system(self):
        res = self.run_cmd(["match", "--task", "optimize postgres database query performance", "--format", "system"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("ACTIVATED AGENT SKILL", res.stdout)
        self.assertIn("PostgreSQL Performance Optimization", res.stdout)

    def test_cli_get_markdown(self):
        res = self.run_cmd(["get", "coding.api-design.fastapi-rest-craft"])
        self.assertEqual(res.returncode, 0)
        self.assertIn("# FastAPI REST API Production Craft", res.stdout)

    def test_cli_info_json(self):
        res = self.run_cmd(["info", "owasp-top10-scanner", "--json"])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertEqual(data["name"], "owasp-top10-scanner")
        self.assertEqual(data["category"], "testing-quality")

    def test_cli_propose_json(self):
        res = self.run_cmd([
            "propose",
            "--skill", "fastapi-rest-craft",
            "--content", "# Updated guidelines\n\n- Added CORS middleware setup.",
            "--reason", "Add CORS middleware best practices",
            "--json"
        ])
        self.assertEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertTrue(data["success"])
        self.assertIn(data["status"], ["pending", "ready_for_pr"])

if __name__ == "__main__":
    unittest.main()
