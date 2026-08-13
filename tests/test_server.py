import unittest
import threading
import time
import json
import urllib.request
import urllib.error
from http.server import HTTPServer
from eshkill.server import SkillAPIHandler


class TestServerEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 18080
        cls.server = HTTPServer(("127.0.0.1", cls.port), SkillAPIHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.3)
        cls.base_url = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path: str):
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "test-client"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status, resp.read().decode("utf-8")

    def _post(self, path: str, payload: dict):
        url = f"{self.base_url}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "User-Agent": "test-client"}, method="POST")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status, resp.read().decode("utf-8")

    def test_health(self):
        status, body = self._get("/v1/health")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "eshkill-daemon")

    def test_categories(self):
        status, body = self._get("/v1/categories")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("web-frameworks", data)

    def test_search(self):
        status, body = self._get("/v1/search?q=fastapi+pydantic&top_k=2")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertGreater(data["total_results"], 0)

    def test_auto_route_get(self):
        status, body = self._get("/v1/auto-route?prompt=build+a+chat+with+nextjs+and+supabase&format=json")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("detected_stack", data)
        self.assertIn("unified_payload", data)

    def test_auto_route_post(self):
        payload = {"prompt": "deploy docker container to aws with terraform", "max_skills": 2}
        status, body = self._post("/v1/auto-route", payload)
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("selected_skills", data)

    def test_match_xml(self):
        status, body = self._get("/v1/match?task=optimize+slow+postgres+queries&format=xml")
        self.assertEqual(status, 200)
        self.assertIn("<agent_skill", body)
        self.assertIn("postgres-query-tuning", body)

    def test_get_skill(self):
        status, body = self._get("/v1/skills/fastapi-production-craft?format=json")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data["name"], "fastapi-production-craft")


if __name__ == "__main__":
    unittest.main()
