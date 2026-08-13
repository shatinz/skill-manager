import os
import unittest
from askill.vault import VaultConnector
from askill.models import VaultIndex, SkillDetail

class TestVaultConnector(unittest.TestCase):
    def setUp(self):
        self.vault = VaultConnector()

    def test_load_index(self):
        index = self.vault.load_index()
        self.assertIsInstance(index, VaultIndex)
        self.assertGreater(index.total_skills, 15)
        self.assertIn("coding", index.categories)
        self.assertIn("testing-quality", index.categories)

    def test_get_skill_exact_id(self):
        skill = self.vault.get_skill("coding.api-design.fastapi-rest-craft")
        self.assertIsInstance(skill, SkillDetail)
        self.assertEqual(skill.name, "fastapi-rest-craft")
        self.assertEqual(skill.category, "coding")
        self.assertIn("FastAPI", skill.content)

    def test_get_skill_by_name(self):
        skill = self.vault.get_skill("postgres-query-tuning")
        self.assertIsInstance(skill, SkillDetail)
        self.assertEqual(skill.id, "coding.database-architecture.postgres-query-tuning")
        self.assertIn("EXPLAIN", skill.content)

    def test_get_nonexistent_skill(self):
        with self.assertRaises(KeyError):
            self.vault.get_skill("nonexistent-magic-skill-xyz")

    def test_list_categories(self):
        cats = self.vault.list_categories()
        self.assertIn("devops-cloud", cats)
        self.assertIn("ci-cd", cats["devops-cloud"])
        self.assertIn("docker-multi-stage-build", cats["devops-cloud"]["ci-cd"])

if __name__ == "__main__":
    unittest.main()
