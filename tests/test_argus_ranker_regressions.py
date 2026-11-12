"""Regression tests for Argus goal-aware ranking and duplicate suppression."""
import unittest
from argus.engine import GoalAnalyzer, ArgusSearchIndex, tokenize
from argus.models import SkillFormat, SkillPackage
from argus.ranker import GoalAwareRanker


def skill(id, source, name, description, capabilities=None, frameworks=None):
    return SkillPackage(
        id=id,
        source_id=source,
        name=name,
        format=SkillFormat.ANTIGRAVITY_SKILL,
        description=description,
        category="general",
        capabilities=capabilities or [],
        compatible_frameworks=frameworks or [],
        actionability_score=0.95,
    )


class RankerRegressionTests(unittest.TestCase):
    def test_python_relevance_goal_detected(self):
        analysis = GoalAnalyzer().analyze(
            "Audit and optimize Python skill search ranking relevance and tests"
        )
        self.assertEqual(analysis.deliverable_type, "retrieval_ranking")
        self.assertIn("python", analysis.detected_frameworks)

    def test_unique_names_across_sources(self):
        packages = [
            skill("alpha", "source1", "E2E Testing Patterns", "test search ranking"),
            skill("alpha", "source2", "e2e-testing-patterns", "test search ranking"),
            skill("beta", "source3", "Ranking Evaluator", "evaluate relevance ranking search"),
        ]
        goal = GoalAnalyzer().analyze("Evaluate skill search ranking relevance")
        matches = GoalAwareRanker().rank_candidates(
            goal, packages, ArgusSearchIndex(packages), top_k=3
        )
        self.assertEqual(len(matches), 2)
        self.assertEqual(len({
            "".join(c for c in m.skill.name.lower() if c.isalnum())
            for m in matches
        }), 2)

    def test_unicode_skill_names_are_deduplicated(self):
        packages = [
            skill("persian1", "a", "مهارت جستجو", "search relevance ranking"),
            skill("persian2", "b", "مهارت-جستجو", "search relevance ranking"),
        ]
        goal = GoalAnalyzer().analyze("search relevance ranking")
        matches = GoalAwareRanker().rank_candidates(
            goal, packages, ArgusSearchIndex(packages), top_k=5
        )
        self.assertEqual(len(matches), 1)

    def test_path_traversal_goal_prefers_sanitization(self):
        goal = GoalAnalyzer().analyze(
            "Python safe path join prevents path traversal and symlink escapes securely"
        )
        self.assertEqual(goal.deliverable_type, "security_hardening_audit")
        packages = [
            skill("a", "local", "OAuth Router", "API auth login", capabilities=["api_backend"]),
            skill("b", "local", "Input Sanitization Guard",
                  "prevent path traversal and validate untrusted file input",
                  capabilities=["security_hardening"]),
        ]
        matches = GoalAwareRanker().rank_candidates(
            goal, packages, ArgusSearchIndex(packages), top_k=2
        )
        self.assertEqual(matches[0].skill.id, "b")

    def test_ranking_skill_beats_unrelated_frontend(self):
        packages = [
            skill("frontend", "local", "Optimize Frontend", "optimize responsive frontend UI",
                  capabilities=["frontend_ui"], frameworks=["javascript"]),
            skill("ranking", "local", "Recsys Ranking",
                  "search relevance ranking pipeline and retrieval evaluation",
                  capabilities=["ai_agents"]),
        ]
        goal = GoalAnalyzer().analyze("Optimize Python skill search relevance ranking")
        results = GoalAwareRanker().rank_candidates(
            goal, packages, ArgusSearchIndex(packages), top_k=2
        )
        self.assertEqual(results[0].skill.id, "ranking")

    def test_empty_query_does_not_recommend_arbitrary_skills(self):
        packages = [skill("x", "s", "Some skill", "general useful skills")]
        matches = GoalAwareRanker().rank_candidates(
            GoalAnalyzer().analyze(""), packages, ArgusSearchIndex(packages)
        )
        self.assertEqual(matches, [])

    def test_bm25_uses_precomputed_term_frequencies(self):
        pkg = skill("s", "source", "Search Search", "search ranking retrieval")
        index = ArgusSearchIndex([pkg])
        self.assertEqual(index.doc_term_freq[pkg.qualified_id]["search"], 3)
        first = index.compute_bm25_score(tokenize("search ranking"), pkg)
        self.assertGreater(first, 0.0)
        self.assertEqual(first, index.compute_bm25_score(tokenize("search ranking"), pkg))


if __name__ == "__main__":
    unittest.main()
