"""
Argus Goal Deconstruction & Semantic Search Engine.
Understands user prompts, breaks down architecture requirements,
identifies primary deliverables, and extracts technical capabilities needed.
"""

import re
import math
from typing import List, Dict, Set, Tuple, Optional, Any
from .models import GoalAnalysis, SkillPackage, SkillSource

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by",
    "from", "about", "into", "through", "during", "before", "after",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "and", "or", "but", "if", "then", "else", "when",
    "up", "down", "out", "over", "under", "again", "further", "then", "once",
    "i", "me", "my", "myself", "we", "our", "you", "your", "they", "them",
    "how", "what", "which", "who", "whom", "this", "that", "these", "those",
    "want", "need", "please", "can", "could", "should", "make", "create", "build"
}

# Domain & Goal Ontologies
GOAL_ONTOLOGY = {
    "3d_web_application": {
        "triggers": [
            r"\b3d\b", r"\bthree(\.?js)?\b", r"\bwebgl\b", r"\bcanvas\b", r"\b3d website\b",
            r"\binteractive 3d\b", r"\bmesh\b", r"\bshader\b", r"\bspline\b", r"\br3f\b"
        ],
        "domains": ["3d-graphics", "ui-design-antislop", "web-frameworks"],
        "inferred_needs": ["3d_rendering_engine", "web_canvas_host", "responsive_ui_shell", "animation_loop"],
        "recommended_capabilities": ["3d_rendering", "frontend_ui"]
    },
    "rest_api_service": {
        "triggers": [
            r"\brest\s*api\b", r"\bfastapi\b", r"\bcrud\b", r"\bbackend api\b",
            r"\bendpoints?\b", r"\bhono\b", r"\bexpress\b"
        ],
        "domains": ["web-frameworks", "databases-storage", "security-sast-hardening"],
        "inferred_needs": ["api_router", "schema_validation", "database_persistence", "error_handling"],
        "recommended_capabilities": ["api_backend", "database_sql"]
    },
    "fullstack_web_app": {
        "triggers": [
            r"\bfullstack\b", r"\bweb app(lication)?\b", r"\bnext(\.?js)?\b", r"\breact\b",
            r"\bdashboard\b", r"\bsupabase\b", r"\bsvelte\b"
        ],
        "domains": ["web-frameworks", "ui-design-antislop", "databases-storage"],
        "inferred_needs": ["page_routing", "state_management", "styled_components", "data_layer"],
        "recommended_capabilities": ["frontend_ui", "database_sql", "api_backend"]
    },
    "ai_agent_system": {
        "triggers": [
            r"\bagent(s)?\b", r"\brag\b", r"\bllm\b", r"\blanggraph\b", r"\bmcp\b",
            r"\bembeddings?\b", r"\bvector search\b", r"\bprompt\b"
        ],
        "domains": ["ai-llm-agents", "security-sast-hardening"],
        "inferred_needs": ["context_retrieval", "prompt_synthesis", "tool_calling", "agent_loop"],
        "recommended_capabilities": ["ai_agents", "api_backend"]
    },
    "database_tuning_storage": {
        "triggers": [
            r"\bpostgres(ql)?\b", r"\bsql query\b", r"\bexplain analyze\b", r"\bindexing\b",
            r"\bdatabase tuning\b", r"\bprisma\b", r"\bdrizzle\b"
        ],
        "domains": ["databases-storage"],
        "inferred_needs": ["query_profiling", "schema_indexing", "connection_pooling"],
        "recommended_capabilities": ["database_sql"]
    },
    "devops_container_ci": {
        "triggers": [
            r"\bdocker\b", r"\bcontainer\b", r"\bci/cd\b", r"\bkubernetes\b",
            r"\bdistroless\b", r"\bterraform\b", r"\bdeployment\b"
        ],
        "domains": ["devops-cloud-serverless"],
        "inferred_needs": ["containerization", "pipeline_automation", "cloud_provisioning"],
        "recommended_capabilities": ["devops_deploy"]
    },
    "security_hardening_audit": {
        "triggers": [
            r"\bsecurity\b", r"\bsast\b", r"\bvulnerability\b", r"\bowasp\b",
            r"\bjwt\b", r"\bxss\b", r"\bauth\b", r"\bsanitize\b"
        ],
        "domains": ["security-sast-hardening"],
        "inferred_needs": ["threat_analysis", "input_sanitization", "auth_verification"],
        "recommended_capabilities": ["security_hardening"]
    }
}

FRAMEWORK_PATTERNS = {
    "threejs": [r"\bthree(\.?js)?\b", r"\bwebgl\b", r"\br3f\b", r"\b3d\b"],
    "react": [r"\breact\b", r"\bjsx\b", r"\btsx\b"],
    "nextjs": [r"\bnext(\.?js)?\b", r"\bapp[- ]router\b"],
    "vite": [r"\bvite\b", r"\bspa\b"],
    "tailwind": [r"\btailwind(css)?\b", r"\bshadcn\b"],
    "fastapi": [r"\bfastapi\b", r"\bpydantic\b"],
    "hono": [r"\bhono\b", r"\bcloudflare workers\b"],
    "supabase": [r"\bsupabase\b", r"\brls\b"],
    "postgres": [r"\bpostgres(ql)?\b", r"\bsql\b"],
    "docker": [r"\bdocker\b", r"\bcontainer\b"],
    "playwright": [r"\bplaywright\b", r"\be2e\b"],
    "pytest": [r"\bpytest\b", r"\bunit test\b"]
}


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into meaningful keywords."""
    clean = re.sub(r"[^\w\s\-]", " ", text.lower())
    tokens = [t.strip() for t in clean.split() if t.strip()]
    return [t for t in tokens if len(t) > 1 and t not in STOP_WORDS]


class GoalAnalyzer:
    """Deconstructs user prompt into actionable architectural goals and requirements."""

    def analyze(self, prompt: str) -> GoalAnalysis:
        prompt_clean = prompt.strip()
        tokens = tokenize(prompt_clean)
        
        deliverable_type = "general_software_task"
        target_domains: Set[str] = set()
        inferred_needs: Set[str] = set()
        
        # Match goal ontology
        best_ontology_score = 0
        best_ontology_name = ""

        for name, spec in GOAL_ONTOLOGY.items():
            matches = 0
            for pattern in spec["triggers"]:
                if re.search(pattern, prompt_clean, re.IGNORECASE):
                    matches += 1
            if matches > best_ontology_score:
                best_ontology_score = matches
                best_ontology_name = name
                deliverable_type = name
                target_domains.update(spec["domains"])
                inferred_needs.update(spec["inferred_needs"])

        # Detect specific frameworks
        detected_frameworks: List[str] = []
        for fw, patterns in FRAMEWORK_PATTERNS.items():
            if any(re.search(p, prompt_clean, re.IGNORECASE) for p in patterns):
                detected_frameworks.append(fw)

        # Infer additional domains from detected frameworks
        if "threejs" in detected_frameworks:
            target_domains.add("3d-graphics")
            inferred_needs.add("3d_rendering_engine")
        if "react" in detected_frameworks or "nextjs" in detected_frameworks or "vite" in detected_frameworks:
            target_domains.add("web-frameworks")
            inferred_needs.add("frontend_ui")
        if "fastapi" in detected_frameworks or "hono" in detected_frameworks:
            target_domains.add("web-frameworks")
            inferred_needs.add("api_backend")
        if "postgres" in detected_frameworks or "supabase" in detected_frameworks:
            target_domains.add("databases-storage")
            inferred_needs.add("database_persistence")

        # Determine complexity level
        word_count = len(prompt_clean.split())
        complexity = "simple"
        if len(detected_frameworks) >= 3 or len(inferred_needs) >= 3 or word_count > 25:
            complexity = "complex"
        elif len(detected_frameworks) >= 2 or len(inferred_needs) >= 2 or word_count > 10:
            complexity = "intermediate"

        primary_goal = self._synthesize_primary_goal(prompt_clean, deliverable_type, detected_frameworks)

        return GoalAnalysis(
            raw_prompt=prompt_clean,
            primary_goal=primary_goal,
            deliverable_type=deliverable_type,
            target_domains=sorted(list(target_domains)),
            detected_frameworks=sorted(detected_frameworks),
            inferred_needs=sorted(list(inferred_needs)),
            complexity_level=complexity,
            constraints=[]
        )

    def _synthesize_primary_goal(self, prompt: str, deliverable_type: str, frameworks: List[str]) -> str:
        if deliverable_type == "3d_web_application":
            fw_text = f" using {', '.join(frameworks)}" if frameworks else ""
            return f"Build an interactive 3D web experience{fw_text} with rendering, canvas hosting, and responsive controls."
        elif deliverable_type == "rest_api_service":
            return f"Architect a robust, performant REST API backend service."
        elif deliverable_type == "fullstack_web_app":
            return f"Construct a modern fullstack web application with responsive UI and integrated data layer."
        elif deliverable_type == "ai_agent_system":
            return f"Develop an autonomous AI agent workflow with context retrieval and tool orchestration."
        else:
            return f"Implement solution for: '{prompt[:80]}...'" if len(prompt) > 80 else f"Implement solution for: '{prompt}'"


class ArgusSearchIndex:
    """Aggregated multi-source search index."""

    def __init__(self, packages: List[SkillPackage]):
        self.packages = packages
        self.doc_count = len(packages)
        self.avg_doc_len = 1.0
        self.doc_tokens: Dict[str, List[str]] = {}
        self.doc_freq: Dict[str, int] = {}
        self._build_index()

    def _build_index(self):
        total_len = 0
        for pkg in self.packages:
            text = f"{pkg.name} {pkg.description} {pkg.category} {' '.join(pkg.tags)} {' '.join(pkg.capabilities)} {' '.join(pkg.compatible_frameworks)}"
            tokens = tokenize(text)
            self.doc_tokens[pkg.qualified_id] = tokens
            total_len += len(tokens)
            
            seen = set(tokens)
            for token in seen:
                self.doc_freq[token] = self.doc_freq.get(token, 0) + 1

        self.avg_doc_len = (total_len / max(1, self.doc_count)) if self.doc_count > 0 else 1.0

    def compute_bm25_score(self, query_tokens: List[str], pkg: SkillPackage, k1: float = 1.5, b: float = 0.75) -> float:
        score = 0.0
        tokens = self.doc_tokens.get(pkg.qualified_id, [])
        doc_len = len(tokens)
        if doc_len == 0:
            return 0.0

        # Term frequency in document
        tf_dict: Dict[str, int] = {}
        for t in tokens:
            tf_dict[t] = tf_dict.get(t, 0) + 1

        for q in query_tokens:
            tf = tf_dict.get(q, 0)
            if tf == 0:
                continue

            df = self.doc_freq.get(q, 0)
            idf = math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))
            
            num = tf * (k1 + 1.0)
            denom = tf + k1 * (1.0 - b + b * (doc_len / self.avg_doc_len))
            score += idf * (num / denom)

        return max(0.0, score)
