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

    def test_submit_proposal_autonomous_agent(self):
        res = self.proposer.submit_proposal(
            skill_id="fastapi-production-craft",
            proposer_id="agent:claude-3-5-sonnet",
            proposed_content="# Enhanced FastAPI Guidelines\n\nAdded RFC 7807 problem details.",
            reason="Autonomous RFC 7807 compliance update",
            is_agent=True,
            tags=["autonomous_agent", "self_healing"]
        )
        self.assertTrue(res.success)
        self.assertTrue(res.is_agent)
        self.assertIn("autonomous_agent", res.tags)

    def test_auto_propose_from_feedback(self):
        res = self.proposer.auto_propose_from_feedback(
            skill_id="fastapi-production-craft",
            execution_feedback="DeprecationWarning: Starlette 0.40 deprecated synchronous form parsing",
            suggested_modifications="Always use `await request.form()` with python-multipart>=0.0.20",
            agent_id="agent:autonomous-debugger",
            reason="Fix Starlette form parsing deprecation"
        )
        self.assertTrue(res.success)
        self.assertTrue(res.is_agent)
        self.assertIn("autonomous_agent", res.tags)
        self.assertIn("self_healing", res.tags)


if __name__ == "__main__":
    unittest.main()
