"""
Argus Multi-Repository Skill Proxy.
High-level orchestrator connecting AI Agents with distributed skill repositories,
local vaults, and remote git hubs with goal-aware ranking.
"""

from typing import List, Dict, Optional, Tuple, Any
from .models import (
    SkillSource, SkillPackage, GoalAnalysis, SkillGoalMatch,
    ArgusBundle, SourceType, SkillFormat
)
from .sources import SourceManager
from .engine import GoalAnalyzer, ArgusSearchIndex
from .ranker import GoalAwareRanker


class ArgusProxy:
    """Intelligent Skill Search Engine & Multi-Repository Proxy for AI Agents."""

    def __init__(self, config_dir: Optional[str] = None):
        self.source_manager = SourceManager(config_dir=config_dir)
        self.goal_analyzer = GoalAnalyzer()
        self._cached_skills: Optional[List[SkillPackage]] = None
        self._cached_index: Optional[ArgusSearchIndex] = None

    def refresh_catalog(self) -> List[SkillPackage]:
        """Scan all active sources and build an aggregated skill catalog."""
        all_skills: List[SkillPackage] = []
        for src in self.source_manager.list_sources():
            if src.enabled:
                skills = self.source_manager.scan_source_skills(src)
                src.skill_count = len(skills)
                all_skills.extend(skills)

        self._cached_skills = all_skills
        self._cached_index = ArgusSearchIndex(all_skills)
        self.source_manager.save_sources()
        return all_skills

    def get_all_skills(self) -> List[SkillPackage]:
        if self._cached_skills is None:
            return self.refresh_catalog()
        return self._cached_skills

    def get_search_index(self) -> ArgusSearchIndex:
        if self._cached_index is None:
            self.refresh_catalog()
        return self._cached_index

    def match(self, prompt: str, top_k: int = 5) -> ArgusBundle:
        """Goal-Aware Skill Matching & Bundle Synthesis for an AI Agent."""
        goal = self.goal_analyzer.analyze(prompt)
        skills = self.get_all_skills()
        search_index = self.get_search_index()

        sources_map = {s.id: s for s in self.source_manager.list_sources()}
        ranker = GoalAwareRanker(sources_map=sources_map)
        
        matches = ranker.rank_candidates(
            goal=goal,
            candidates=skills,
            search_index=search_index,
            top_k=top_k
        )

        sources_queried = [s.id for s in self.source_manager.list_sources() if s.enabled]
        
        return ranker.build_bundle(
            prompt=prompt,
            goal=goal,
            matches=matches,
            sources_queried=sources_queried,
            total_skills_evaluated=len(skills)
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        source_filter: Optional[str] = None
    ) -> List[SkillGoalMatch]:
        """Cross-repository skill search with goal analysis."""
        goal = self.goal_analyzer.analyze(query)
        skills = self.get_all_skills()
        
        if source_filter:
            skills = [s for s in skills if s.source_id == source_filter]

        search_index = ArgusSearchIndex(skills)
        sources_map = {s.id: s for s in self.source_manager.list_sources()}
        ranker = GoalAwareRanker(sources_map=sources_map)

        return ranker.rank_candidates(
            goal=goal,
            candidates=skills,
            search_index=search_index,
            top_k=top_k
        )

    def fetch(self, qualified_or_skill_id: str) -> Optional[str]:
        """Fetch raw skill instruction markdown across all configured sources."""
        if ":" in qualified_or_skill_id:
            source_id, skill_id = qualified_or_skill_id.split(":", 1)
            return self.source_manager.fetch_skill_content(source_id, skill_id)

        # Search across all sources
        for src in self.source_manager.list_sources():
            content = self.source_manager.fetch_skill_content(src.id, qualified_or_skill_id)
            if content:
                return content

        return None

    def list_sources(self) -> List[SkillSource]:
        return self.source_manager.list_sources()

    def add_source(
        self,
        id: str,
        name: str,
        source_type: SourceType,
        location: str,
        priority: int = 100,
        trust_score: float = 1.0,
        branch: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SkillSource:
        src = self.source_manager.add_source(
            id=id,
            name=name,
            source_type=source_type,
            location=location,
            priority=priority,
            trust_score=trust_score,
            branch=branch,
            metadata=metadata
        )
        self.refresh_catalog()
        return src

    def remove_source(self, source_id: str) -> bool:
        res = self.source_manager.remove_source(source_id)
        if res:
            self.refresh_catalog()
        return res

    def toggle_source(self, source_id: str, enabled: bool) -> bool:
        res = self.source_manager.toggle_source(source_id, enabled)
        if res:
            self.refresh_catalog()
        return res

    def sync_all(self) -> Dict[str, Any]:
        """Synchronize all enabled repositories."""
        results = {}
        for src in self.source_manager.list_sources():
            if src.enabled:
                success, msg, count = self.source_manager.sync_source(src.id)
                results[src.id] = {
                    "success": success,
                    "message": msg,
                    "skill_count": count
                }
        self.refresh_catalog()
        return results
