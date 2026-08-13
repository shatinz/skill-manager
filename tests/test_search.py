import unittest
from eshkill.vault import VaultConnector
from eshkill.search import SmartSkillSearch, tokenize, compute_fuzzy_token_similarity


class TestSmartSkillSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vault = VaultConnector()
        cls.index = cls.vault.load_index()
        cls.engine = SmartSkillSearch(cls.index)

    def test_search_fastapi_rest(self):
        results = self.engine.search("build fastapi rest api", top_k=3)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].skill.name, "fastapi-production-craft")
        self.assertGreater(results[0].score, 0.5)

    def test_search_postgres_query(self):
        results = self.engine.search("optimize slow sql query explain analyze", top_k=3)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].skill.name, "postgres-query-tuning")

    def test_search_rag_embeddings(self):
        results = self.engine.search("rag semantic chunking hybrid vector search", top_k=3)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].skill.name, "rag-chunking-hybrid-search")

    def test_search_category_filter(self):
        results = self.engine.search("", category="security-sast-hardening", top_k=10)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r.skill.category, "security-sast-hardening")

    def test_find_best_match(self):
        match = self.engine.find_best_match("I need to write unit tests with pytest fixtures and mocks")
        self.assertIsNotNone(match)
        self.assertEqual(match.skill.name, "pytest-mocking-mastery")

    def test_search_docker_distroless(self):
        match = self.engine.find_best_match("docker multi stage build distroless image")
        self.assertIsNotNone(match)
        self.assertEqual(match.skill.name, "docker-multi-stage-distroless")

    def test_query_expansion_supabase(self):
        results = self.engine.search("supabase real-time database", top_k=3)
        self.assertGreater(len(results), 0)
        names = [r.skill.name for r in results]
        self.assertTrue("supabase-realtime-auth-rls" in names or "postgres-query-tuning" in names)

    def test_fuzzy_typo_matching(self):
        results = self.engine.search("playwreight automated browser testing", top_k=3)
        self.assertGreater(len(results), 0)
        names = [r.skill.name for r in results]
        self.assertIn("playwright-e2e-automation", names)


if __name__ == "__main__":
    unittest.main()
