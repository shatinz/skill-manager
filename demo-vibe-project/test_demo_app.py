"""
Test Suite for Demo Vibe-Coding Project.
Adhering strictly to testing-qa-automation.unit-integration-python.pytest-mocking-mastery.
"""

import unittest
from fastapi.testclient import TestClient
from backend_api import app, canvas_store

client = TestClient(app)

class TestDemoVibeApp(unittest.TestCase):
    def setUp(self):
        canvas_store.messages.clear()

    def test_health_check(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertGreaterEqual(data["active_channels"], 1)

    def test_unauthorized_message_rejection(self):
        # Missing header
        response = client.post("/api/v1/messages", json={
            "sender": "vibe_coder",
            "text": "Check out this new component!"
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn("Missing Authorization header", response.json()["detail"])

    def test_invalid_scheme_rejection(self):
        # Invalid Scheme
        response = client.post(
            "/api/v1/messages",
            json={"sender": "vibe_coder", "text": "Hello!"},
            headers={"Authorization": "Basic 12345678"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Bearer required", response.json()["detail"])

    def test_successful_message_creation_and_retrieval(self):
        # Valid message with Bearer token
        headers = {"Authorization": "Bearer valid_jwt_session_token_123"}
        response = client.post(
            "/api/v1/messages",
            json={
                "sender": "lead_architect",
                "text": "Adopted Next.js 15 Server Actions and Supabase RLS.",
                "canvas_node_id": "node_99"
            },
            headers=headers
        )
        self.assertEqual(response.status_code, 201)
        msg = response.json()
        self.assertEqual(msg["sender"], "lead_architect")
        self.assertEqual(msg["canvas_node_id"], "node_99")
        self.assertIn("id", msg)

        # Retrieve messages
        get_res = client.get("/api/v1/messages", headers=headers)
        self.assertEqual(get_res.status_code, 200)
        items = get_res.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["text"], "Adopted Next.js 15 Server Actions and Supabase RLS.")

    def test_pydantic_schema_validation_rejects_extra_fields(self):
        # Forbidden extra fields
        headers = {"Authorization": "Bearer valid_jwt_session_token_123"}
        response = client.post(
            "/api/v1/messages",
            json={
                "sender": "attacker",
                "text": "Injected field test",
                "malicious_extra_field": "exploit"
            },
            headers=headers
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
