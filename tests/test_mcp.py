import unittest
import json
from eshkill.vault import VaultConnector
from eshkill.mcp import MCPServer


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.vault = VaultConnector()
        self.server = MCPServer(self.vault)

    def test_mcp_initialize(self):
        req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        resp = self.server.handle_request(req)
        self.assertEqual(resp["id"], 1)
        self.assertEqual(resp["result"]["serverInfo"]["name"], "eshkill-mcp")
        self.assertIn("tools", resp["result"]["capabilities"])

    def test_mcp_tools_list(self):
        req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        resp = self.server.handle_request(req)
        tools = resp["result"]["tools"]
        tool_names = [t["name"] for t in tools]
        expected_tools = [
            "search_skills",
            "get_skill",
            "auto_select_skill",
            "install_skill",
            "propose_skill_update",
            "auto_propose_skill_fix",
            "list_categories"
        ]
        for exp in expected_tools:
            self.assertIn(exp, tool_names)

    def test_mcp_tool_call_search(self):
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_skills",
                "arguments": {"query": "fastapi pydantic", "top_k": 3}
            }
        }
        resp = self.server.handle_request(req)
        self.assertFalse(resp["result"]["isError"])
        data = json.loads(resp["result"]["content"][0]["text"])
        self.assertGreater(data["total_found"], 0)
        self.assertEqual(data["results"][0]["id"], "web-frameworks.python-api.fastapi-production-craft")

    def test_mcp_tool_call_auto_select(self):
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "auto_select_skill",
                "arguments": {"prompt": "build real-time chat with nextjs and supabase", "max_skills": 3}
            }
        }
        resp = self.server.handle_request(req)
        self.assertFalse(resp["result"]["isError"])
        text = resp["result"]["content"][0]["text"]
        self.assertIn("ACTIVATED UNIFIED AGENT SKILL STACK", text)

    def test_mcp_tool_call_get_skill(self):
        req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_skill",
                "arguments": {"skill_id": "fastapi-production-craft", "format": "markdown"}
            }
        }
        resp = self.server.handle_request(req)
        self.assertFalse(resp["result"]["isError"])
        self.assertIn("FastAPI", resp["result"]["content"][0]["text"])

    def test_mcp_resources(self):
        req_list = {"jsonrpc": "2.0", "id": 6, "method": "resources/list", "params": {}}
        resp_list = self.server.handle_request(req_list)
        resources = resp_list["result"]["resources"]
        self.assertGreater(len(resources), 5)

        req_read = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "resources/read",
            "params": {"uri": "skill://catalog"}
        }
        resp_read = self.server.handle_request(req_read)
        self.assertIn("total_skills", resp_read["result"]["contents"][0]["text"])

    def test_mcp_tool_call_auto_propose(self):
        req = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "auto_propose_skill_fix",
                "arguments": {
                    "skill_id": "fastapi-production-craft",
                    "execution_feedback": "RuntimeError: sqlalchemy query without async session failed",
                    "suggested_fix": "Always use AsyncSession and `await session.execute()`",
                    "reason": "Fix async sqlalchemy execution in FastAPI",
                    "agent_model": "claude-3-5-sonnet"
                }
            }
        }
        resp = self.server.handle_request(req)
        self.assertFalse(resp["result"]["isError"])
        data = json.loads(resp["result"]["content"][0]["text"])
        self.assertTrue(data["success"])
        self.assertTrue(data["is_agent"])
        self.assertIn("autonomous_agent", data["tags"])


if __name__ == "__main__":
    unittest.main()
