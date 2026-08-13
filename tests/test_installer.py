import unittest
import os
import shutil
import tempfile
from eshkill.vault import VaultConnector
from eshkill.installer import SkillInstaller
from eshkill.models import InstallResult


class TestSkillInstaller(unittest.TestCase):
    def setUp(self):
        self.vault = VaultConnector()
        self.installer = SkillInstaller(self.vault)
        self.temp_ws = tempfile.mkdtemp(prefix="eshkill_ws_test_")

    def tearDown(self):
        if os.path.exists(self.temp_ws):
            shutil.rmtree(self.temp_ws)

    def test_install_workspace(self):
        res = self.installer.install(
            skill_id_or_name="fastapi-production-craft",
            mode="workspace",
            workspace_dir=self.temp_ws
        )

        self.assertIsInstance(res, InstallResult)
        self.assertTrue(res.success)
        self.assertEqual(res.mode, "workspace")
        self.assertTrue(os.path.exists(res.target_path))
        self.assertTrue(res.target_path.endswith("SKILL.md"))

        # Verify metadata.json was generated
        meta_path = os.path.join(os.path.dirname(res.target_path), "metadata.json")
        self.assertTrue(os.path.exists(meta_path))

        # Verify content
        with open(res.target_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("FastAPI", content)

        # Verify list_installed
        installed = self.installer.list_installed(mode="workspace", workspace_dir=self.temp_ws)
        self.assertEqual(len(installed), 1)
        self.assertEqual(installed[0]["id"], "web-frameworks.python-api.fastapi-production-craft")

        # Verify uninstall
        removed = self.installer.uninstall("web-frameworks.python-api.fastapi-production-craft", mode="workspace", workspace_dir=self.temp_ws)
        self.assertTrue(removed)
        self.assertFalse(os.path.exists(res.target_path))

    def test_install_temp_ephemeral(self):
        res = self.installer.install(
            skill_id_or_name="docker-multi-stage-distroless",
            mode="temp"
        )
        self.assertTrue(res.success)
        self.assertEqual(res.mode, "temp")
        self.assertIsNotNone(res.ephemeral_content)
        self.assertIn("Docker", res.ephemeral_content)

    def test_install_nonexistent_skill(self):
        res = self.installer.install(
            skill_id_or_name="nonexistent-skill-404",
            mode="workspace",
            workspace_dir=self.temp_ws
        )
        self.assertFalse(res.success)
        self.assertIn("not found", res.message)


if __name__ == "__main__":
    unittest.main()
