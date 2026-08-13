import unittest
from eshkill.vault import VaultConnector
from eshkill.agent import AgentFormatter
from eshkill.search import SmartSkillSearch
from eshkill.propose import ProposalManager


class TestAgentAndPropose(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vault = VaultConnector()
        cls.skill = cls.vault.get_skill("fastapi-production-craft")
        cls.proposer = ProposalManager(cls.vault)

    def test_xml_formatter(self):
        xml_out = AgentFormatter.to_xml(self.skill)
        self.assertTrue(xml_out.startswith("<agent_skill"))
        self.assertIn("fastapi-production-craft", xml_out)
        self.assertIn("<instructions>", xml_out)
        self.assertTrue(xml_out.endswith("</agent_skill>"))

    def test_system_prompt_formatter(self):
        prompt_out = AgentFormatter.to_system_prompt(self.skill)
        self.assertIn("ACTIVATED AGENT SKILL", prompt_out)
        self.assertIn("MISSION & CONTEXT:", prompt_out)
        self.assertIn("OPERATIONAL INSTRUCTIONS & WORKFLOW:", prompt_out)

    def test_json_envelope_formatter(self):
        json_env = AgentFormatter.to_json_envelope(self.skill)
        self.assertEqual(json_env["id"], self.skill.id)
        self.assertIn("instructions_markdown", json_env)

    def test_diff_generation(self):
        original = "Line 1\nLine 2\nLine 3\n"
        modified = "Line 1\nLine 2 Updated\nLine 3\n"
        diff = self.proposer.generate_diff(original, modified)
        self.assertIn("-Line 2", diff)
        self.assertIn("+Line 2 Updated", diff)

    def test_submit_proposal(self):
        res = self.proposer.submit_proposal(
            skill_id="fastapi-production-craft",
            proposer_id="unit_test_agent",
            proposed_content="# Enhanced FastAPI Guidelines\n\nAdded RFC 7807 problem details.",
            reason="Add RFC 7807 compliance"
        )
        self.assertTrue(res.success)
        self.assertIn(res.status, ["pending", "ready_for_pr"])


if __name__ == "__main__":
    unittest.main()
