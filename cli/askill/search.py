"""
Smart Search Engine for askill.
Combines BM25 lexical token matching, trigger pattern alignment, action intent classification, and tag overlap.
"""

import re
import math
from typing import List, Dict, Set, Tuple, Optional
from .models import VaultIndex, SkillSummary, SearchResult

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by",
    "from", "about", "into", "through", "during", "before", "after",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "and", "or", "but", "if", "then", "else", "when",
    "up", "down", "out", "over", "under", "again", "further", "then", "once",
    "i", "me", "my", "myself", "we", "our", "you", "your", "they", "them"
}

INTENT_MAP = {
    "api": ["api-design", "coding"],
    "endpoint": ["api-design", "coding"],
    "crud": ["api-design", "database-architecture"],
    "database": ["database-architecture", "data-pipelines"],
    "sql": ["database-architecture", "data-pipelines"],
    "query": ["database-architecture"],
    "index": ["database-architecture"],
    "slow": ["database-architecture", "frontend-engineering"],
    "optimize": ["database-architecture", "frontend-engineering", "ci-cd"],
    "performance": ["database-architecture", "frontend-engineering", "data-pipelines"],
    "refactor": ["refactoring-clean-code"],
    "clean": ["refactoring-clean-code"],
    "legacy": ["refactoring-clean-code"],
    "solid": ["refactoring-clean-code"],
    "dry": ["refactoring-clean-code"],
    "frontend": ["frontend-engineering"],
    "ui": ["frontend-engineering"],
    "render": ["frontend-engineering"],
    "component": ["frontend-engineering"],
    "css": ["frontend-engineering"],
    "test": ["unit-integration"],
    "unit": ["unit-integration"],
    "mock": ["unit-integration"],
    "e2e": ["unit-integration"],
    "playwright": ["unit-integration"],
    "pytest": ["unit-integration"],
    "security": ["security-sast", "code-hardening"],
    "audit": ["security-sast", "code-hardening"],
    "vulnerability": ["security-sast"],
    "leak": ["security-sast"],
    "secret": ["security-sast"],
    "owasp": ["security-sast"],
    "docker": ["ci-cd"],
    "ci": ["ci-cd"],
    "pipeline": ["ci-cd", "data-pipelines"],
    "workflow": ["ci-cd"],
    "iac": ["infrastructure-as-code"],
    "terraform": ["infrastructure-as-code"],
    "aws": ["infrastructure-as-code"],
    "cloud": ["infrastructure-as-code"],
    "metrics": ["observability"],
    "monitor": ["observability"],
    "telemetry": ["observability"],
    "grafana": ["observability"],
    "prometheus": ["observability"],
    "rag": ["llm-rag"],
    "embedding": ["llm-rag"],
    "vector": ["llm-rag"],
    "prompt": ["llm-rag"],
    "llm": ["llm-rag"],
    "analytics": ["data-pipelines"],
    "parquet": ["data-pipelines"],
    "duckdb": ["data-pipelines"],
    "polars": ["data-pipelines"],
    "jwt": ["code-hardening"],
    "auth": ["code-hardening"],
    "oauth": ["code-hardening"],
    "token": ["code-hardening"],
    "sanitize": ["code-hardening"],
    "xss": ["code-hardening"],
    "docs": ["api-docs", "architecture-decision-records"],
    "openapi": ["api-docs"],
    "swagger": ["api-docs"],
    "adr": ["architecture-decision-records"],
    "rfc": ["architecture-decision-records"],
}

def tokenize(text: str) -> List[str]:
    cleaned = re.sub(r"[^a-zA-Z0-9\-_./]", " ", text.lower())
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    return tokens

def compute_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0

class SmartSkillSearch:
    def __init__(self, index: VaultIndex):
        self.index = index
        self.skills = index.skills
        self._build_inverted_index()

    def _build_inverted_index(self):
        self.doc_lengths: Dict[str, int] = {}
        self.term_freqs: Dict[str, Dict[str, int]] = {}
        self.doc_freqs: Dict[str, int] = {}
        self.num_docs = len(self.skills)

        for s in self.skills:
            text_corpus = (
                f"{s.name} {s.title} {s.category} {s.subcategory} "
                f"{' '.join(s.tags)} {s.description} {' '.join(s.trigger_patterns)}"
            )
            tokens = tokenize(text_corpus)
            self.doc_lengths[s.id] = len(tokens)
            
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.term_freqs[s.id] = tf

            for t in set(tokens):
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1

        self.avg_doc_len = sum(self.doc_lengths.values()) / max(1, self.num_docs)

    def _bm25_score(self, query_tokens: List[str], skill: SkillSummary, k1: float = 1.5, b: float = 0.75) -> float:
        score = 0.0
        doc_len = self.doc_lengths.get(skill.id, 100)
        tf_map = self.term_freqs.get(skill.id, {})

        for token in query_tokens:
            if token in STOP_WORDS:
                continue
            tf = tf_map.get(token, 0)
            df = self.doc_freqs.get(token, 0)
            if df == 0:
                continue

            idf = math.log(1 + (self.num_docs - df + 0.5) / (df + 0.5))
            num = tf * (k1 + 1)
            denom = tf + k1 * (1 - b + b * (doc_len / self.avg_doc_len))
            score += idf * (num / denom)
        return max(0.0, score)

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        tag: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.05
    ) -> List[SearchResult]:
        if not query or not query.strip():
            # Return top rated skills in category
            results = []
            for s in self.skills:
                if category and s.category != category:
                    continue
                if subcategory and s.subcategory != subcategory:
                    continue
                if tag and tag not in s.tags:
                    continue
                results.append(SearchResult(skill=s, score=s.trust_rating, match_reasons=["Category filter"]))
            results.sort(key=lambda r: r.skill.trust_rating, reverse=True)
            return results[:top_k]

        q_lower = query.lower().strip()
        q_tokens = tokenize(q_lower)
        q_token_set = set(q_tokens)

        # Detect intent subcategories
        intent_subcats: Set[str] = set()
        for t in q_tokens:
            if t in INTENT_MAP:
                intent_subcats.update(INTENT_MAP[t])

        raw_results: List[Tuple[SkillSummary, float, List[str], List[str], List[str]]] = []

        for s in self.skills:
            if category and s.category != category:
                continue
            if subcategory and s.subcategory != subcategory:
                continue
            if tag and tag not in s.tags:
                continue

            score = 0.0
            matched_triggers: List[str] = []
            matched_tags: List[str] = []
            match_reasons: List[str] = []

            # 1. BM25 Base Relevance
            bm25 = self._bm25_score(q_tokens, s)
            score += bm25 * 0.8
            if bm25 > 0:
                match_reasons.append(f"Text relevance (BM25: {bm25:.2f})")

            # 2. Trigger Pattern Match (Heavy Boost)
            for trigger in s.trigger_patterns:
                trig_lower = trigger.lower()
                if trig_lower in q_lower or q_lower in trig_lower:
                    score += 4.0
                    matched_triggers.append(trigger)
                    match_reasons.append(f"Trigger exact match: '{trigger}'")
                    break
                else:
                    trig_tokens = set(tokenize(trig_lower))
                    sim = compute_jaccard_similarity(q_token_set, trig_tokens)
                    if sim > 0.4:
                        boost = sim * 3.0
                        score += boost
                        matched_triggers.append(trigger)
                        match_reasons.append(f"Trigger pattern affinity ({sim*100:.0f}%): '{trigger}'")

            # 3. Direct Tag Matching
            for t in s.tags:
                if t in q_token_set or t in q_lower:
                    score += 1.8
                    matched_tags.append(t)
            if matched_tags:
                match_reasons.append(f"Matched tags: {matched_tags}")

            # 4. Intent Classification Affinity
            if s.subcategory in intent_subcats or s.category in intent_subcats:
                score += 1.5
                match_reasons.append(f"Intent domain match: '{s.category}/{s.subcategory}'")

            # 5. Name / ID Exact Substring
            if s.name in q_lower or s.name.replace("-", " ") in q_lower:
                score += 3.5
                match_reasons.append(f"Exact name match: '{s.name}'")

            # 6. Trust Rating Quality Factor
            score *= (1.0 + (s.trust_rating - 0.5) * 0.2)

            if score >= min_score:
                raw_results.append((s, score, matched_triggers, matched_tags, match_reasons))

        raw_results.sort(key=lambda x: x[1], reverse=True)

        # Normalize scores to 0.0 - 1.0 range relative to max score
        max_score = raw_results[0][1] if raw_results else 1.0
        final_results = []
        for s, raw_score, triggers, tags, reasons in raw_results[:top_k]:
            normalized_score = min(1.0, raw_score / max(1.0, max_score * 0.95))
            final_results.append(
                SearchResult(
                    skill=s,
                    score=normalized_score,
                    matched_triggers=triggers,
                    matched_tags=tags,
                    match_reasons=reasons
                )
            )

        return final_results

    def find_best_match(self, task_description: str) -> Optional[SearchResult]:
        results = self.search(task_description, top_k=1, min_score=0.1)
        return results[0] if results else None
