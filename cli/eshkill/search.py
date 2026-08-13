"""
Smart Search Engine for eshkill.
Combines BM25 lexical token matching, multi-token query expansion, intent classification,
fuzzy trigger pattern matching, and tag overlap.
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
    "i", "me", "my", "myself", "we", "our", "you", "your", "they", "them",
    "how", "what", "which", "who", "whom", "this", "that", "these", "those"
}

# Domain Intent mapping to categories/subcategories
INTENT_MAP = {
    # Web & APIs
    "api": ["python-api", "web-frameworks", "edge-runtime"],
    "endpoint": ["python-api", "web-frameworks", "edge-runtime"],
    "fastapi": ["python-api", "web-frameworks"],
    "nextjs": ["react-fullstack", "web-frameworks"],
    "react": ["react-fullstack", "web-frameworks"],
    "remix": ["react-fullstack", "web-frameworks"],
    "svelte": ["svelte", "web-frameworks"],
    "astro": ["content-ssg", "web-frameworks"],
    "hono": ["edge-runtime", "web-frameworks"],
    "crud": ["python-api", "relational-sql", "orm-data-access"],

    # Databases & Storage
    "database": ["relational-sql", "databases-storage", "orm-data-access", "backend-as-a-service"],
    "sql": ["relational-sql", "databases-storage", "orm-data-access"],
    "postgres": ["relational-sql", "databases-storage"],
    "postgresql": ["relational-sql", "databases-storage"],
    "supabase": ["backend-as-a-service", "databases-storage", "auth-security"],
    "prisma": ["orm-data-access", "databases-storage"],
    "drizzle": ["orm-data-access", "databases-storage"],
    "redis": ["key-value-cache", "databases-storage"],
    "duckdb": ["olap-embedded", "databases-storage"],
    "query": ["relational-sql", "databases-storage"],
    "index": ["relational-sql", "databases-storage"],
    "indexing": ["relational-sql", "databases-storage"],
    "explain": ["relational-sql", "databases-storage"],

    # UI & Design
    "frontend": ["react-fullstack", "web-frameworks", "ui-design-antislop"],
    "ui": ["styling-tokens", "component-systems", "ui-design-antislop"],
    "tailwind": ["styling-tokens", "ui-design-antislop"],
    "shadcn": ["component-systems", "ui-design-antislop"],
    "css": ["styling-tokens", "ui-design-antislop"],
    "animation": ["animations", "ui-design-antislop"],
    "threejs": ["3d-graphics", "ui-design-antislop"],
    "styling": ["styling-tokens", "ui-design-antislop"],
    "responsive": ["responsive-layout", "ui-design-antislop"],

    # AI & LLM Agents
    "rag": ["rag-retrieval", "ai-llm-agents"],
    "embedding": ["rag-retrieval", "ai-llm-agents"],
    "vector": ["rag-retrieval", "ai-llm-agents"],
    "langgraph": ["agent-workflows", "ai-llm-agents"],
    "prompt": ["prompt-craft", "ai-llm-agents"],
    "llm": ["ai-llm-agents", "prompt-craft", "rag-retrieval"],
    "mcp": ["mcp-protocol", "ai-llm-agents"],
    "structured": ["structured-outputs", "ai-llm-agents"],
    "function": ["function-calling", "ai-llm-agents"],
    "agent": ["agent-workflows", "multi-agent-teams", "ai-llm-agents"],

    # DevOps & Cloud
    "docker": ["containerization", "devops-cloud-serverless"],
    "container": ["containerization", "devops-cloud-serverless"],
    "ci": ["ci-cd", "devops-cloud-serverless"],
    "github": ["ci-cd", "devops-cloud-serverless"],
    "pipeline": ["ci-cd", "devops-cloud-serverless"],
    "terraform": ["iac-cloud", "devops-cloud-serverless"],
    "aws": ["iac-cloud", "devops-cloud-serverless"],
    "cloud": ["iac-cloud", "devops-cloud-serverless"],
    "kubernetes": ["orchestration", "devops-cloud-serverless"],
    "metrics": ["observability", "devops-cloud-serverless"],
    "grafana": ["observability", "devops-cloud-serverless"],
    "prometheus": ["observability", "devops-cloud-serverless"],
    "telemetry": ["observability", "devops-cloud-serverless"],
    "vercel": ["deployment-gitops", "devops-cloud-serverless"],

    # Security
    "security": ["application-security", "security-sast-hardening", "auth-security"],
    "owasp": ["application-security", "security-sast-hardening"],
    "jwt": ["auth-security", "security-sast-hardening"],
    "auth": ["auth-security", "security-sast-hardening"],
    "secret": ["secrets-management", "security-sast-hardening"],
    "sanitize": ["web-defense", "security-sast-hardening"],
    "xss": ["web-defense", "security-sast-hardening"],
    "cve": ["supply-chain", "security-sast-hardening"],

    # Testing & QA
    "test": ["unit-integration-python", "e2e-testing", "testing-qa-automation"],
    "testing": ["unit-integration-python", "e2e-testing", "testing-qa-automation"],
    "unit": ["unit-integration-python", "frontend-unit", "testing-qa-automation"],
    "mock": ["unit-integration-python", "testing-qa-automation"],
    "pytest": ["unit-integration-python", "testing-qa-automation"],
    "playwright": ["e2e-testing", "testing-qa-automation"],
    "e2e": ["e2e-testing", "testing-qa-automation"],
    "load": ["load-testing", "testing-qa-automation"],

    # Business & Clean Architecture
    "stripe": ["payments-billing", "business-ecommerce-growth"],
    "billing": ["payments-billing", "business-ecommerce-growth"],
    "seo": ["seo-growth", "business-ecommerce-growth"],
    "telegram": ["chat-automation", "business-ecommerce-growth"],
    "refactor": ["code-modernization", "principles-patterns", "clean-architecture-refactoring"],
    "solid": ["principles-patterns", "clean-architecture-refactoring"],
    "dry": ["principles-patterns", "clean-architecture-refactoring"],
    "legacy": ["code-modernization", "clean-architecture-refactoring"],
    "adr": ["architectural-docs", "clean-architecture-refactoring"]
}

# Multi-token query expansion synonyms & tech stacks (including Persian/multilingual keywords)
QUERY_EXPANSIONS: Dict[str, List[str]] = {
    # Fullstack & Frontend
    "supabase": ["postgres", "postgres-query-tuning", "supabase-realtime-auth-rls", "jwt-oauth2-secureshop", "database", "auth"],
    "nextjs": ["nextjs-15-app-router", "react", "tailwind-v4-tokens", "frontend", "web-vitals"],
    "next.js": ["nextjs-15-app-router", "react", "tailwind-v4-tokens", "frontend"],
    "react": ["nextjs-15-app-router", "frontend", "web-vitals", "shadcn-ui-mastery"],
    "tailwind": ["tailwind-v4-tokens", "shadcn-ui-mastery", "css", "tokens", "styling"],
    "shadcn": ["shadcn-ui-mastery", "tailwind-v4-tokens", "react", "component"],
    "fastapi": ["fastapi-production-craft", "pydantic", "python", "crud", "rest"],
    "prisma": ["prisma-orm-mastery", "database", "typescript", "orm", "migrations"],
    "drizzle": ["drizzle-orm-type-safe", "database", "typescript", "orm", "sql"],
    "docker": ["docker-multi-stage-distroless", "container", "multi-stage", "distroless"],
    "terraform": ["terraform-aws-modules", "aws", "iac", "cloud", "s3"],
    "rag": ["rag-chunking-hybrid-search", "embeddings", "hybrid-search", "vector-db", "llm"],
    "langgraph": ["langgraph-multi-agent-flow", "agent", "workflow", "multi-agent"],
    "mcp": ["mcp-server-protocol-craft", "model-context-protocol", "json-rpc"],
    "duckdb": ["duckdb-polars-analytics", "polars", "analytics", "parquet", "sql"],
    "jwt": ["jwt-oauth2-secureshop", "oauth2", "auth", "tokens"],
    "auth": ["jwt-oauth2-secureshop", "supabase-realtime-auth-rls", "security", "tokens"],
    "owasp": ["owasp-top10-scanner", "security", "sast", "vulnerability"],
    "pytest": ["pytest-mocking-mastery", "testing", "fixtures", "mocking", "coverage"],
    "playwright": ["playwright-e2e-automation", "e2e", "testing", "browser"],
    "browser": ["playwright-e2e-automation", "e2e", "testing"],
    "playwreight": ["playwright-e2e-automation", "playwright", "e2e", "testing"],
    "stripe": ["stripe-subscription-webhooks", "billing", "payments", "webhooks"],
    "solid": ["dry-solid-clean-architecture", "solid", "dry", "clean-architecture"],
    "legacy": ["legacy-code-modernizer", "refactoring", "clean-code", "monolith"],
    "adr": ["adr-architecture-decision-records", "architecture", "decisions", "rfc"],
    "seo": ["open-seo-audit-engine", "seo", "audit", "meta-tags", "sitemap"],
    "locust": ["locust-performance-load-testing", "load-test", "stress-test", "benchmark"],
    
    # Persian / Regional Market Integrations & Synonyms
    "دیوار": ["divar-marketplace-automation", "divar", "marketplace", "oauth2", "api"],
    "divar": ["divar-marketplace-automation", "marketplace", "api"],
    "ترب": ["torob-marketplace-integration", "torob", "marketplace", "catalog", "pricing"],
    "torob": ["torob-marketplace-integration", "marketplace", "catalog"],
    "تلگرام": ["telegram-bot-agent-controller", "telegram", "bot", "chat-automation"],
    "telegram": ["telegram-bot-agent-controller", "bot", "chat-automation"],
    "احراز": ["jwt-oauth2-secureshop", "auth", "security", "jwt"],
    "امنیت": ["owasp-top10-scanner", "jwt-oauth2-secureshop", "security"],
    "پایتون": ["fastapi-production-craft", "pytest-mocking-mastery", "python"],
    "داکر": ["docker-multi-stage-distroless", "container", "docker"],
    "فرانت": ["nextjs-15-app-router", "tailwind-v4-tokens", "react"],
    "فرانت_اند": ["nextjs-15-app-router", "tailwind-v4-tokens", "react"]
}


def normalize_unicode_text(text: str) -> str:
    """Normalizes Arabic/Persian letter variants and lowercases text."""
    t = text.lower()
    t = t.replace("ي", "ی").replace("ك", "ک").replace("ة", "ه").replace("‌", " ")  # remove zero-width non-joiner
    return t


def tokenize(text: str) -> List[str]:
    """Tokenizes text into cleaned lowercase Unicode tokens."""
    norm = normalize_unicode_text(text)
    # Match Unicode word characters, plus hyphen, underscore, dot, slash
    tokens = re.findall(r"[\w\-_./]+", norm)
    # Clean boundary punctuation
    cleaned = [t.strip("-_./") for t in tokens if t.strip("-_./")]
    return cleaned


def compute_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Computes Jaccard similarity between two token sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union > 0 else 0.0


def compute_fuzzy_token_similarity(s1: str, s2: str) -> float:
    """Levenshtein-based ratio approximation for handling typos in queries."""
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    if s1 in s2 or s2 in s1:
        return len(min(s1, s2, key=len)) / len(max(s1, s2, key=len))

    def ngrams(word: str, n: int = 2) -> Set[str]:
        return {word[i:i+n] for i in range(len(word) - n + 1)} if len(word) >= n else {word}

    g1, g2 = ngrams(s1), ngrams(s2)
    return compute_jaccard_similarity(g1, g2)


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

    def expand_query(self, tokens: List[str]) -> List[str]:
        """Expands query tokens with known technology synonyms and intent keywords."""
        expanded = list(tokens)
        for t in tokens:
            if t in QUERY_EXPANSIONS:
                expanded.extend(QUERY_EXPANSIONS[t])
        return list(dict.fromkeys(expanded))

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        tag: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.05
    ) -> List[SearchResult]:
        # Handle category aliases (e.g. security-compliance -> security-sast-hardening, coding -> web-frameworks, devops-cloud -> devops-cloud-serverless)
        cat_filter = category
        if category:
            cat_lower = category.lower()
            if "security" in cat_lower:
                cat_filter = "security-sast-hardening"
            elif "devops" in cat_lower or "cloud" in cat_lower:
                cat_filter = "devops-cloud-serverless"
            elif "testing" in cat_lower:
                cat_filter = "testing-qa-automation"
            elif "data" in cat_lower or "ai" in cat_lower:
                cat_filter = "ai-llm-agents"

        if not query or not query.strip():
            results = []
            for s in self.skills:
                if cat_filter and s.category != cat_filter and category not in s.category:
                    continue
                if subcategory and s.subcategory != subcategory and subcategory not in s.subcategory:
                    continue
                if tag and tag not in s.tags:
                    continue
                results.append(SearchResult(skill=s, score=s.trust_rating, match_reasons=["Category filter"]))
            results.sort(key=lambda r: r.skill.trust_rating, reverse=True)
            return results[:top_k]

        q_lower = query.lower().strip()
        q_tokens = tokenize(q_lower)
        expanded_tokens = self.expand_query(q_tokens)
        q_token_set = set(expanded_tokens)

        # Detect intent subcategories and categories
        intent_subcats: Set[str] = set()
        for t in expanded_tokens:
            if t in INTENT_MAP:
                intent_subcats.update(INTENT_MAP[t])

        raw_results: List[Tuple[SkillSummary, float, List[str], List[str], List[str]]] = []

        for s in self.skills:
            if cat_filter and s.category != cat_filter and category not in s.category:
                continue
            if subcategory and s.subcategory != subcategory and subcategory not in s.subcategory:
                continue
            if tag and tag not in s.tags:
                continue

            score = 0.0
            matched_triggers: List[str] = []
            matched_tags: List[str] = []
            match_reasons: List[str] = []

            # 1. BM25 Base Relevance
            bm25_orig = self._bm25_score(q_tokens, s)
            bm25_exp = self._bm25_score(expanded_tokens, s)
            bm25 = (bm25_orig * 0.7) + (bm25_exp * 0.3)
            score += bm25 * 0.8
            if bm25 > 0:
                match_reasons.append(f"Text relevance (BM25: {bm25:.2f})")

            # 2. Trigger Pattern Match
            for trigger in s.trigger_patterns:
                trig_lower = trigger.lower()
                if trig_lower in q_lower or q_lower in trig_lower:
                    score += 4.5
                    matched_triggers.append(trigger)
                    match_reasons.append(f"Trigger exact match: '{trigger}'")
                    break
                else:
                    trig_tokens = set(tokenize(trig_lower))
                    sim = compute_jaccard_similarity(q_token_set, trig_tokens)
                    if sim > 0.35:
                        boost = sim * 3.5
                        score += boost
                        matched_triggers.append(trigger)
                        match_reasons.append(f"Trigger pattern affinity ({sim*100:.0f}%): '{trigger}'")
                        break
                    else:
                        for qt in q_tokens:
                            if len(qt) > 4:
                                for tt in trig_tokens:
                                    if len(tt) > 4 and compute_fuzzy_token_similarity(qt, tt) > 0.7:
                                        score += 2.2
                                        matched_triggers.append(trigger)
                                        match_reasons.append(f"Fuzzy trigger token match: '{qt}' ~ '{tt}'")
                                        break

            # 3. Direct Tag Matching
            for t in s.tags:
                if t in q_token_set or t in q_lower:
                    score += 2.0
                    matched_tags.append(t)
                else:
                    for qt in q_tokens:
                        if len(qt) > 4 and compute_fuzzy_token_similarity(qt, t) > 0.75:
                            score += 1.5
                            matched_tags.append(f"{t}~")
                            break
            if matched_tags:
                match_reasons.append(f"Matched tags: {matched_tags}")

            # 4. Intent Classification Affinity
            if s.subcategory in intent_subcats or s.category in intent_subcats:
                score += 2.0
                match_reasons.append(f"Intent domain match: '{s.category}/{s.subcategory}'")

            # 5. Name / ID Exact Substring
            if s.name in q_lower or s.name.replace("-", " ") in q_lower:
                score += 4.5
                match_reasons.append(f"Exact name match: '{s.name}'")
            elif s.id in q_lower:
                score += 5.0
                match_reasons.append(f"Exact ID match: '{s.id}'")

            # 6. Trust Rating Quality Factor
            score *= (1.0 + (s.trust_rating - 0.5) * 0.2)

            if score >= min_score:
                raw_results.append((s, score, matched_triggers, matched_tags, match_reasons))

        raw_results.sort(key=lambda x: x[1], reverse=True)

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
