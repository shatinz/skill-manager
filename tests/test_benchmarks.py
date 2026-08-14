import unittest
import json
from eshkill.vault import VaultConnector
from eshkill.router import AutoRouter
from eshkill.mcp import MCPServer

try:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import Base, engine, SessionLocal
    from app.routers.ingestion import seed_database
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


class TestBenchmarksAndEmpiricalRanking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vault = VaultConnector()
        cls.router = AutoRouter(cls.vault)
        cls.mcp_server = MCPServer(cls.vault)
        if HAS_FASTAPI:
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as db:
                seed_database(db)
            cls.client = TestClient(app)

    def test_task_aware_skill_ranking_rust_scenario(self):
        # The user's exact scenario: Rust compiler plugin / Fix CI / GPT-5
        decision = self.router.rank_skills_for_task(
            task="Fix CI async deadlock",
            repository_context="Rust compiler plugin",
            ecosystem="rust",
            model="GPT-5",
            max_skills=3
        )
        self.assertIsNotNone(decision.top_skill)
        self.assertIn("rust", decision.top_skill.id.lower())
        self.assertGreaterEqual(decision.empirical_score, 0.5)
        self.assertGreaterEqual(decision.success_rate, 0.8)

    def test_record_execution_evidence_telemetry(self):
        rec = self.router.record_execution_evidence(
            skill_id="clean-architecture-refactoring.systems-engineering.rust-axum-tokio-async",
            repository_name="Rust compiler plugin",
            task_description="Fix CI",
            outcome="success",
            duration_seconds=180.0,
            model_name="GPT-5",
            cost_usd=0.19,
            tokens_used=14500,
            skill_version="4.1.0",
            feedback_notes="Resolved non-blocking tokio task channels"
        )
        self.assertEqual(rec.repository_name, "Rust compiler plugin")
        self.assertEqual(rec.task_description, "Fix CI")
        self.assertEqual(rec.outcome, "success")
        self.assertEqual(rec.duration_seconds, 180.0)
        self.assertEqual(rec.cost_usd, 0.19)
        self.assertEqual(rec.model_name, "GPT-5")
        self.assertEqual(rec.skill_version, "4.1.0")

    def test_mcp_find_best_skill_for_task(self):
        req = {
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {
                "name": "find_best_skill_for_task",
                "arguments": {
                    "task": "Fix CI",
                    "repository_context": "Rust compiler plugin",
                    "model": "GPT-5"
                }
            }
        }
        resp = self.mcp_server.handle_request(req)
        self.assertFalse(resp["result"]["isError"])
        data = json.loads(resp["result"]["content"][0]["text"])
        self.assertEqual(data["query_task"], "Fix CI")
        self.assertIsNotNone(data["top_skill"])
        self.assertIn("top_skill_full_instructions", data)

    def test_mcp_record_execution_evidence(self):
        req = {
            "jsonrpc": "2.0",
            "id": 102,
            "method": "tools/call",
            "params": {
                "name": "record_execution_evidence",
                "arguments": {
                    "skill_id": "fastapi-production-craft",
                    "repository_name": "Analytics Gateway",
                    "task_description": "Add OAuth2 scopes",
                    "outcome": "success",
                    "duration_seconds": 95.0,
                    "model_name": "GPT-5",
                    "cost_usd": 0.11,
                    "skill_version": "1.0.0"
                }
            }
        }
        resp = self.mcp_server.handle_request(req)
        self.assertFalse(resp["result"]["isError"])
        data = json.loads(resp["result"]["content"][0]["text"])
        self.assertEqual(data["status"], "recorded")
        self.assertEqual(data["evidence"]["repository_name"], "Analytics Gateway")

    def test_backend_benchmarks_api_endpoints(self):
        if not HAS_FASTAPI:
            return  # Skip backend API tests when running standalone CLI unittest suite
        # 1. Record evidence via API
        r = self.client.post("/api/benchmarks/evidence", json={
            "skill_id": "fastapi-production-craft",
            "repository_name": "Order Processing API",
            "task_description": "Add database healthcheck",
            "outcome": "success",
            "duration_seconds": 45.0,
            "model_name": "Claude 3.5 Sonnet",
            "cost_usd": 0.05,
            "skill_version_tag": "1.0.0"
        })
        self.assertEqual(r.status_code, 200)
        ev = r.json()
        self.assertEqual(ev["repository_name"], "Order Processing API")

        # 2. Get recent evidence ledger
        r_rec = self.client.get("/api/benchmarks/recent?limit=10")
        self.assertEqual(r_rec.status_code, 200)
        ev_list = r_rec.json()
        self.assertGreaterEqual(len(ev_list), 1)

        # 3. Get skill benchmarks summary
        r_sum = self.client.get("/api/benchmarks/skills/FastAPI Auto-CRUD")
        self.assertEqual(r_sum.status_code, 200)
        sum_data = r_sum.json()
        self.assertGreaterEqual(sum_data["total_runs"], 1)
        self.assertGreaterEqual(sum_data["success_rate"], 0.8)

        # 4. Rank skills for task
        r_rank = self.client.post("/api/benchmarks/rank", json={
            "task": "Fix CI on rust compiler plugin",
            "repository_context": "Rust compiler plugin",
            "model": "GPT-5",
            "max_results": 3
        })
        self.assertEqual(r_rank.status_code, 200)
        rank_data = r_rank.json()
        self.assertIsNotNone(rank_data["top_skill"])
        self.assertGreaterEqual(len(rank_data["ranked_skills"]), 1)


if __name__ == "__main__":
    unittest.main()
