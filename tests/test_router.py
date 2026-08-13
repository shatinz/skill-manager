import unittest
from eshkill.vault import VaultConnector
from eshkill.router import AutoRouter
from eshkill.models import RoutingDecision


class TestAutoRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vault = VaultConnector()
        cls.router = AutoRouter(cls.vault)

    def test_vibe_coding_fullstack_chat(self):
        prompt = "build a real-time chat with supabase and nextjs 15 and tailwind styling"
        decision = self.router.route(prompt, max_skills=3)

        self.assertIsInstance(decision, RoutingDecision)
        self.assertEqual(decision.prompt, prompt)
        self.assertGreaterEqual(len(decision.selected_skills), 2)
        self.assertLessEqual(len(decision.selected_skills), 3)

        selected_names = [s.name for s in decision.selected_skills]
        # Should include frontend (nextjs/tailwind) and database (supabase/postgres)
        has_frontend = any(x in selected_names for x in ["nextjs-15-app-router", "tailwind-v4-tokens", "react-performance-audit"])
        has_db = any(x in selected_names for x in ["supabase-realtime-auth-rls", "postgres-query-tuning", "prisma-orm-mastery"])
        self.assertTrue(has_frontend)
        self.assertTrue(has_db)

        self.assertIn("ACTIVATED UNIFIED AGENT SKILL STACK", decision.unified_payload)
        self.assertGreater(decision.total_estimated_tokens, 1000)

    def test_vibe_coding_fastapi_backend(self):
        prompt = "create a robust fastapi backend with pydantic schemas and postgres database"
        decision = self.router.route(prompt, max_skills=3)

        selected_names = [s.name for s in decision.selected_skills]
        self.assertIn("fastapi-production-craft", selected_names)
        self.assertIn("postgres-query-tuning", selected_names)
        self.assertIn("FastAPI", decision.unified_payload)

    def test_vibe_coding_devops_infra(self):
        prompt = "containerize microservices with docker multi stage builds and deploy to aws with terraform"
        decision = self.router.route(prompt, max_skills=3)

        selected_names = [s.name for s in decision.selected_skills]
        self.assertIn("docker-multi-stage-distroless", selected_names)
        self.assertIn("terraform-aws-modules", selected_names)

    def test_vibe_coding_security_audit(self):
        prompt = "audit code for owasp top 10 vulnerabilities, protect jwt auth and sanitize inputs"
        decision = self.router.route(prompt, max_skills=3)

        selected_names = [s.name for s in decision.selected_skills]
        self.assertIn("owasp-top10-scanner", selected_names)
        self.assertIn("jwt-oauth2-secureshop", selected_names)

    def test_routing_decision_to_dict(self):
        decision = self.router.route("test prompt with playwright e2e tests", max_skills=2)
        d = decision.to_dict()
        self.assertIn("prompt", d)
        self.assertIn("detected_stack", d)
        self.assertIn("selected_skills", d)
        self.assertIn("unified_payload", d)


if __name__ == "__main__":
    unittest.main()
