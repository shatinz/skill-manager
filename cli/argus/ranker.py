"""
Argus Goal-Aware Multi-Tier Ranker & Compatibility Engine.
Ranks skills based on how well they fulfill the user prompt's end-to-end goal,
capability actionability, framework compatibility, and source trust.
"""

from typing import List, Dict, Set, Tuple, Optional, Any
from .models import GoalAnalysis, SkillPackage, SkillGoalMatch, SkillSource, ArgusBundle
from .engine import ArgusSearchIndex, tokenize


# Role mapping templates based on deliverable and capability
ROLE_TEMPLATES = {
    ("3d_web_application", "3d_rendering"): ("Primary 3D Graphics & Mesh Engine", "Provides Three.js/WebGL scene graphs, procedural meshes, and animation rendering."),
    ("3d_web_application", "frontend_ui"): ("Web Canvas Host & Application Shell", "Hosts the WebGL viewport, manages DOM overlays, and provides reactive state."),
    ("3d_web_application", "styling_tokens"): ("Responsive UI & Anti-Slop Design System", "Ensures modern typography, high-craft aesthetics, and fluid layout controls."),
    ("rest_api_service", "api_backend"): ("Core REST API & Router Engine", "Implements high-throughput async endpoints with strict Pydantic validation."),
    ("rest_api_service", "database_sql"): ("Persistence & Query Optimization Layer", "Handles database migrations, connection pooling, and optimized queries."),
    ("fullstack_web_app", "frontend_ui"): ("Client Architecture & Component Shell", "Delivers server-side/client rendering and fluid user interactions."),
    ("fullstack_web_app", "database_sql"): ("Backend-as-a-Service & Auth Persistence", "Provides realtime sync, database tables, and row-level security."),
    ("ai_agent_system", "ai_agents"): ("Agent Workflow & Context Synthesis", "Coordinates LLM reasoning loops, tool calling, and RAG retrieval pipelines.")
}


class GoalAwareRanker:
    """Ranks and synthesizes skills tailored to specific user goals."""

    def __init__(self, sources_map: Optional[Dict[str, SkillSource]] = None):
        self.sources_map = sources_map or {}

    def rank_candidates(
        self,
        goal: GoalAnalysis,
        candidates: List[SkillPackage],
        search_index: ArgusSearchIndex,
        top_k: int = 5
    ) -> List[SkillGoalMatch]:
        query_tokens = tokenize(goal.raw_prompt)
        matches: List[SkillGoalMatch] = []

        for pkg in candidates:
            # 1. Source Trust
            src = self.sources_map.get(pkg.source_id)
            trust_score = src.trust_score if src else 0.85

            # 2. BM25 Lexical & Semantic Score
            bm25 = search_index.compute_bm25_score(query_tokens, pkg)
            normalized_bm25 = min(1.0, bm25 / 15.0)

            # 3. Goal Relevancy Score (Does this skill address the core deliverable or target domains?)
            goal_relevancy = self._compute_goal_relevancy(goal, pkg, normalized_bm25)

            # 4. Capability Fit Score (Does the skill provide actionable tools/code for inferred needs?)
            capability_fit = self._compute_capability_fit(goal, pkg)

            # 5. Compatibility Score (Synergy with detected frameworks)
            compatibility = self._compute_compatibility(goal, pkg)

            # Composite Rank
            # Weights: Goal Relevancy (45%), Capability Fit (25%), Compatibility (20%), Trust (10%)
            composite = (
                0.45 * goal_relevancy +
                0.25 * capability_fit +
                0.20 * compatibility +
                0.10 * trust_score
            )

            # Determine Goal Role & Alignment Reason
            role, reason = self._determine_role_and_reason(goal, pkg, goal_relevancy)

            # Calculate confidence
            confidence = "high" if composite >= 0.70 else ("medium" if composite >= 0.45 else "low")

            matches.append(SkillGoalMatch(
                skill=pkg,
                goal_relevancy_score=goal_relevancy,
                capability_fit_score=capability_fit,
                compatibility_score=compatibility,
                provenance_trust_score=trust_score,
                composite_rank_score=composite,
                goal_role=role,
                goal_alignment_reason=reason,
                synergy_skills=[],
                confidence=confidence
            ))

        # Sort by composite rank descending
        matches.sort(key=lambda m: m.composite_rank_score, reverse=True)
        return matches[:top_k]

    def _compute_goal_relevancy(self, goal: GoalAnalysis, pkg: SkillPackage, bm25: float) -> float:
        score = bm25 * 0.4

        # Domain overlap bonus
        if goal.target_domains:
            for domain in goal.target_domains:
                if domain.lower() in pkg.category.lower() or domain.lower() in [t.lower() for t in pkg.tags]:
                    score += 0.35
                    break

        # Deliverable type specific boosting
        if goal.deliverable_type == "3d_web_application":
            if "3d_rendering" in pkg.capabilities or "3d" in pkg.tags or "threejs" in pkg.compatible_frameworks:
                score += 0.40
            elif "frontend_ui" in pkg.capabilities or "react" in pkg.compatible_frameworks or "styling" in pkg.category:
                score += 0.25
        elif goal.deliverable_type == "rest_api_service":
            if "api_backend" in pkg.capabilities or "fastapi" in pkg.compatible_frameworks:
                score += 0.40
            elif "database_sql" in pkg.capabilities:
                score += 0.25
        elif goal.deliverable_type == "ai_agent_system":
            if "ai_agents" in pkg.capabilities or "rag" in pkg.tags or "mcp" in pkg.tags:
                score += 0.40

        return min(1.0, max(0.0, score))

    def _compute_capability_fit(self, goal: GoalAnalysis, pkg: SkillPackage) -> float:
        base_fit = pkg.actionability_score * 0.5
        
        # Check inferred needs match
        matches = 0
        for need in goal.inferred_needs:
            for cap in pkg.capabilities:
                if cap in need or need in cap:
                    matches += 1
                    break
        
        need_bonus = min(0.5, matches * 0.25)
        return min(1.0, base_fit + need_bonus)

    def _compute_compatibility(self, goal: GoalAnalysis, pkg: SkillPackage) -> float:
        if not goal.detected_frameworks:
            return 0.85

        score = 0.5
        for fw in goal.detected_frameworks:
            if fw in pkg.compatible_frameworks or fw in [t.lower() for t in pkg.tags]:
                score += 0.25
            elif fw in pkg.name.lower() or fw in pkg.description.lower():
                score += 0.15

        # Penalize if skill conflicts with detected frameworks
        for conflict in pkg.conflicts_with:
            if conflict.lower() in [f.lower() for f in goal.detected_frameworks]:
                score -= 0.40

        return min(1.0, max(0.1, score))

    def _determine_role_and_reason(self, goal: GoalAnalysis, pkg: SkillPackage, relevancy: float) -> Tuple[str, str]:
        # Check predefined templates
        for cap in pkg.capabilities:
            key = (goal.deliverable_type, cap)
            if key in ROLE_TEMPLATES:
                return ROLE_TEMPLATES[key]

        # Generic role deduction
        if "3d_rendering" in pkg.capabilities:
            return (
                "3D Rendering & Scene Craft",
                f"Addresses 3D graphics requirement for '{goal.raw_prompt[:40]}' using procedural shaders, scene graph, and mesh optimization."
            )
        elif "frontend_ui" in pkg.capabilities:
            return (
                "Frontend Host & UI Shell",
                f"Provides responsive layout, component architecture, and interaction states for '{goal.raw_prompt[:40]}'."
            )
        elif "api_backend" in pkg.capabilities:
            return (
                "API Backend & Endpoint Logic",
                f"Delivers robust backend routes, validation schemas, and service logic for '{goal.raw_prompt[:40]}'."
            )
        elif "database_sql" in pkg.capabilities:
            return (
                "Data Persistence & Query Engine",
                f"Implements schema storage, query execution, and database optimization for '{goal.raw_prompt[:40]}'."
            )
        else:
            return (
                "Specialized Technical Skill",
                f"Selected to support goal '{goal.primary_goal}' with domain-specific patterns and guardrails."
            )

    def build_bundle(
        self,
        prompt: str,
        goal: GoalAnalysis,
        matches: List[SkillGoalMatch],
        sources_queried: List[str],
        total_skills_evaluated: int
    ) -> ArgusBundle:
        """Compile a unified multi-skill execution bundle for an AI Agent."""
        framework_stack: Set[str] = set(goal.detected_frameworks)
        for m in matches:
            framework_stack.update(m.skill.compatible_frameworks)

        # Build compiled agent prompt
        lines = [
            f"# ARGUS AUTONOMOUS AGENT SKILL MANIFEST",
            f"**Goal**: {goal.primary_goal}",
            f"**Deliverable Type**: `{goal.deliverable_type}` (Complexity: `{goal.complexity_level}`)",
            f"**Selected Stack**: {', '.join(sorted(framework_stack)) if framework_stack else 'Standard Web'}",
            "",
            "## Selected Complementary Skills & Architecture Roles:"
        ]

        for i, m in enumerate(matches, 1):
            lines.append(
                f"### {i}. {m.skill.name} (`{m.skill.qualified_id}`) [Rank Score: {m.composite_rank_score:.2f} | Confidence: {m.confidence.upper()}]\n"
                f"- **Role**: {m.goal_role}\n"
                f"- **Goal Alignment**: {m.goal_alignment_reason}\n"
                f"- **Source**: `{m.skill.source_id}` ({m.skill.format.value})\n"
                f"- **Capabilities**: {', '.join(m.skill.capabilities) if m.skill.capabilities else 'general'}\n"
            )

        lines.append("## Directives for Agent Execution:")
        lines.append("1. **Synthesize**: Integrate the above specialized skills as a unified architecture.")
        lines.append("2. **Anti-Slop**: Follow strict anti-slop guidelines and clean, production-ready code.")
        lines.append("3. **Execute**: Implement the requested user deliverable with zero unnecessary fluff.")

        compiled = "\n".join(lines)

        return ArgusBundle(
            prompt=prompt,
            goal_analysis=goal,
            selected_matches=matches,
            sources_queried=sources_queried,
            total_skills_evaluated=total_skills_evaluated,
            compiled_agent_instructions=compiled,
            framework_stack=sorted(list(framework_stack)),
            warnings_or_conflicts=[]
        )
