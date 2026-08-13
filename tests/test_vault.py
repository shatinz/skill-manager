import os
import unittest
from eshkill.vault import VaultConnector
from eshkill.models import VaultIndex, SkillDetail


class TestVaultConnector(unittest.TestCase):
    def setUp(self):
        self.vault = VaultConnector()

    def test_load_index(self):
        index = self.vault.load_index()
        self.assertIsInstance(index, VaultIndex)
        self.assertGreaterEqual(index.total_skills, 50)
        self.assertIn("web-frameworks", index.categories)
        self.assertIn("databases-storage", index.categories)
        self.assertIn("devops-cloud-serverless", index.categories)

    def test_get_skill_exact_id(self):
        skill = self.vault.get_skill("web-frameworks.python-api.fastapi-production-craft")
        self.assertIsInstance(skill, SkillDetail)
        self.assertEqual(skill.name, "fastapi-production-craft")
        self.assertEqual(skill.category, "web-frameworks")
        self.assertIn("FastAPI", skill.content)

    def test_get_skill_by_name(self):
        skill = self.vault.get_skill("postgres-query-tuning")
        self.assertIsInstance(skill, SkillDetail)
        self.assertEqual(skill.id, "databases-storage.relational-sql.postgres-query-tuning")
        self.assertIn("EXPLAIN", skill.content)

    def test_get_nonexistent_skill(self):
        with self.assertRaises(KeyError):
            self.vault.get_skill("nonexistent-magic-skill-xyz")

    def test_list_categories(self):
        cats = self.vault.list_categories()
        self.assertIn("devops-cloud-serverless", cats)
        self.assertIn("containerization", cats["devops-cloud-serverless"])
        self.assertIn("docker-multi-stage-distroless", cats["devops-cloud-serverless"]["containerization"])


if __name__ == "__main__":
    unittest.main()
