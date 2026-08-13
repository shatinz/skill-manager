"""
Autonomous Skill Auto-Router for eshkill.
Analyzes raw vibe-coding prompts, detects architectural stack components, selects top complementary skills,
and compiles an optimized, unified agent context payload.
"""

import re
from typing import List, Dict, Set, Tuple, Optional, Any
from .models import VaultIndex, SkillDetail, RoutingDecision
from .vault import VaultConnector
from .search import SmartSkillSearch, tokenize

# Architectural Pillars & Rules mapped directly to the Skill Vault catalog
STACK_RULES: List[Dict[str, Any]] = [
    # --- FRONTEND & FULLSTACK PILLARS ---
    {
        "name": "Next.js 15 App Router & React Fullstack",
        "pillar": "frontend",
        "skill_id": "web-frameworks.react-fullstack.nextjs-15-app-router",
        "patterns": [
            r"\b(next(\.?js)?(13|14|15)?)\b", r"\breact(\s*19)?\b", r"\bapp[- ]router\b",
            r"\bserver[- ]actions\b", r"\bnextjs\b"
        ],
        "weight": 4.5
    },
    {
        "name": "Tailwind CSS v4 & Tokenized Design System",
        "pillar": "styling",
        "skill_id": "ui-design-antislop.styling-tokens.tailwind-v4-tokens",
        "patterns": [
            r"\btailwind(css)?(\s*v4)?\b", r"\bshadcn\b", r"\bdesign[- ]system\b",
            r"\bdark[- ]mode\b", r"\btokenized styling\b"
        ],
        "weight": 3.4
    },

    # --- BACKEND & API PILLARS ---
    {
        "name": "FastAPI Production REST Architecture",
        "pillar": "backend",
        "skill_id": "web-frameworks.python-api.fastapi-production-craft",
        "patterns": [
            r"\bfastapi\b", r"\bpydantic(\s*v2)?\b", r"\brest[- ]api\b", r"\bpython (backend|api|service)\b",
            r"\bcrud endpoints?\b", r"\basyncapi\b"
        ],
        "weight": 4.5
    },
    {
        "name": "Hono Edge & Cloudflare Workers API",
        "pillar": "edge_api",
        "skill_id": "web-frameworks.edge-runtime.hono-edge-api",
        "patterns": [
            r"\bhono\b", r"\bedge runtime\b", r"\bcloudflare workers\b", r"\blightweight api\b"
        ],
        "weight": 3.8
    },

    # --- DATABASE & STORAGE PILLARS ---
    {
        "name": "Supabase Realtime & Row Level Security (RLS)",
        "pillar": "baas",
        "skill_id": "databases-storage.backend-as-a-service.supabase-realtime-auth-rls",
        "patterns": [
            r"\bsupabase\b", r"\brls\b", r"\brow level security\b", r"\brealtime database\b"
        ],
        "weight": 3.6
    },
    {
        "name": "PostgreSQL Performance & Query Tuning",
        "pillar": "database",
        "skill_id": "databases-storage.relational-sql.postgres-query-tuning",
        "patterns": [
            r"\bpostgres(ql)?\b", r"\bsql\b", r"\bexplain analyze\b",
            r"\bindex(ing)?\b", r"\bdatabase (tuning|optimization|performance)\b",
            r"\bneon\b", r"\brds\b"
        ],
        "weight": 3.2
    },
    {
        "name": "Prisma ORM & Data Access",
        "pillar": "orm",
        "skill_id": "databases-storage.orm-data-access.prisma-orm-mastery",
        "patterns": [
            r"\bprisma\b", r"\borm\b", r"\btypescript db\b",
            r"\bprisma migration(s)?\b", r"\bdatabase schema\b"
        ],
        "weight": 3.0
    },
    {
        "name": "Drizzle ORM Type-Safe Persistence",
        "pillar": "orm",
        "skill_id": "databases-storage.orm-data-access.drizzle-orm-type-safe",
        "patterns": [
            r"\bdrizzle\b", r"\bdrizzle-orm\b", r"\btype-safe sql\b"
        ],
        "weight": 3.0
    },
    {
        "name": "Redis Caching & Distributed Rate Limiting",
        "pillar": "cache",
        "skill_id": "databases-storage.key-value-cache.redis-caching-rate-limiting",
        "patterns": [
            r"\bredis\b", r"\bcach(e|ing)\b", r"\brate limit(ing)?\b", r"\bupstash\b"
        ],
        "weight": 2.8
    },

    # --- SECURITY & HARDENING PILLARS ---
    {
        "name": "JWT & OAuth2 Secure Authentication",
        "pillar": "auth",
        "skill_id": "security-sast-hardening.auth-security.jwt-oauth2-secureshop",
        "patterns": [
            r"\bjwt\b", r"\boauth(2)?\b", r"\bauth\b", r"\bauthentication\b",
            r"\btoken(s)?\b", r"\bsession(s)?\b", r"\blogin\b", r"\bsupabase auth\b",
            r"\brbac\b", r"\brole[- ]based\b"
        ],
        "weight": 3.2
    },
    {
        "name": "Input Sanitization & XSS Defense",
        "pillar": "web_defense",
        "skill_id": "security-sast-hardening.web-defense.input-sanitization-xss-defense",
        "patterns": [
            r"\bsanitiz(e|ation)\b", r"\bxss\b", r"\binput validation\b",
            r"\bzod validation\b", r"\bdompurify\b", r"\bdefense\b"
        ],
        "weight": 2.8
    },
    {
        "name": "OWASP Top 10 Security Audit",
        "pillar": "sast",
        "skill_id": "security-sast-hardening.application-security.owasp-top10-scanner",
        "patterns": [
            r"\bowasp\b", r"\bvulnerabilit(y|ies)\b", r"\bsecurity audit\b",
            r"\bsast\b", r"\bsecurity scan\b", r"\bpenetration\b", r"\bsqli\b", r"\bssrf\b"
        ],
        "weight": 3.2
    },
    {
        "name": "Secret Leak Pre-commit Guard",
        "pillar": "secrets",
        "skill_id": "security-sast-hardening.secrets-management.secret-leak-precommit-guard",
        "patterns": [
            r"\bsecret(s)?\b", r"\bgitleaks\b", r"\bapi key(s)?\b",
            r"\bleaked (credentials|tokens)\b", r"\bpre[- ]commit scan\b"
        ],
        "weight": 2.7
    },

    # --- DEVOPS & INFRA PILLARS ---
    {
        "name": "Multi-Stage Docker Distroless Optimization",
        "pillar": "containerization",
        "skill_id": "devops-cloud-serverless.containerization.docker-multi-stage-distroless",
        "patterns": [
            r"\bdocker(file)?\b", r"\bcontainer(ize|ization)?\b", r"\bmulti[- ]stage\b",
            r"\bdistroless\b", r"\bimage size\b", r"\bcompose\b"
        ],
        "weight": 3.4
    },
    {
        "name": "Terraform AWS Modular Infrastructure",
        "pillar": "iac",
        "skill_id": "devops-cloud-serverless.iac-cloud.terraform-aws-modules",
        "patterns": [
            r"\bterraform\b", r"\baws\b", r"\biac\b", r"\bcloud infrastructure\b",
            r"\becs\b", r"\bs3\b", r"\bvpc\b", r"\bcloudformation\b"
        ],
        "weight": 3.4
    },
    {
        "name": "GitHub Actions Matrix CI/CD",
        "pillar": "cicd",
        "skill_id": "devops-cloud-serverless.ci-cd.github-actions-matrix-ci",
        "patterns": [
            r"\bgithub actions\b", r"\bci/cd\b", r"\bworkflow\b", r"\bpipeline\b",
            r"\bmatrix build\b", r"\baction(s)?\b"
        ],
        "weight": 2.8
    },
    {
        "name": "Prometheus & Grafana Telemetry",
        "pillar": "observability",
        "skill_id": "devops-cloud-serverless.observability.prometheus-grafana-telemetry",
        "patterns": [
            r"\bprometheus\b", r"\bgrafana\b", r"\btelemetry\b", r"\bopentelemetry\b",
            r"\bmetrics\b", r"\btracing\b", r"\bobservabilit(y|ies)\b", r"\balert(s)?\b"
        ],
        "weight": 3.0
    },

    # --- AI & LLM AGENTS PILLARS ---
    {
        "name": "RAG Chunking & Hybrid Vector Search",
        "pillar": "rag",
        "skill_id": "ai-llm-agents.rag-retrieval.rag-chunking-hybrid-search",
        "patterns": [
            r"\brag\b", r"\bembedding(s)?\b", r"\bvector(s)?\b", r"\bhybrid search\b",
            r"\bsemantic search\b", r"\bchunking\b", r"\bretrieval\b", r"\bvector-db\b"
        ],
        "weight": 3.6
    },
    {
        "name": "LangGraph Multi-Agent Workflow Engine",
        "pillar": "agent_flow",
        "skill_id": "ai-llm-agents.agent-workflows.langgraph-multi-agent-flow",
        "patterns": [
            r"\blanggraph\b", r"\bmulti[- ]agent\b", r"\bagent flow\b", r"\bstate machine\b",
            r"\bgraph agent\b", r"\bcycles\b"
        ],
        "weight": 3.5
    },
    {
        "name": "Prompt Engineering & System Prompt Distillation",
        "pillar": "prompt",
        "skill_id": "ai-llm-agents.prompt-craft.prompt-engineering-distiller",
        "patterns": [
            r"\bprompt engineering\b", r"\bsystem prompt\b", r"\bcot\b",
            r"\bfew[- ]shot\b", r"\bprompt\b", r"\bagent instruction(s)?\b"
        ],
        "weight": 2.8
    },
    {
        "name": "MCP Server Protocol Implementation",
        "pillar": "mcp",
        "skill_id": "ai-llm-agents.mcp-protocol.mcp-server-protocol-craft",
        "patterns": [
            r"\bmcp\b", r"\bmodel context protocol\b", r"\bmcp server\b", r"\bjson-rpc\b"
        ],
        "weight": 3.5
    },
    {
        "name": "DuckDB & Polars Fast Analytics",
        "pillar": "olap",
        "skill_id": "databases-storage.olap-embedded.duckdb-polars-analytics",
        "patterns": [
            r"\bduckdb\b", r"\bpolars\b", r"\bparquet\b", r"\banalytics\b",
            r"\bdataframe\b", r"\bdata pipeline\b", r"\bolap\b"
        ],
        "weight": 3.2
    },

    # --- TESTING & QA PILLARS ---
    {
        "name": "Pytest Deterministic Mocking & Fixtures",
        "pillar": "unit_test",
        "skill_id": "testing-qa-automation.unit-integration-python.pytest-mocking-mastery",
        "patterns": [
            r"\bpytest\b", r"\bunit test(s)?\b", r"\bmock(ing)?\b",
            r"\bfixture(s)?\b", r"\bcoverage\b", r"\bpython testing\b"
        ],
        "weight": 3.2
    },
    {
        "name": "Playwright End-to-End Test Automation",
        "pillar": "e2e_test",
        "skill_id": "testing-qa-automation.e2e-testing.playwright-e2e-automation",
        "patterns": [
            r"\bplaywright\b", r"\be2e\b", r"\bend[- ]to[- ]end\b",
            r"\bbrowser (test|automation)\b", r"\bpage object\b"
        ],
        "weight": 3.4
    },

    # --- CLEAN ARCHITECTURE & REFACTORING ---
    {
        "name": "DRY & SOLID Clean Architecture",
        "pillar": "clean_arch",
        "skill_id": "clean-architecture-refactoring.principles-patterns.dry-solid-clean-architecture",
        "patterns": [
            r"\bsolid\b", r"\bdry\b", r"\bclean code\b", r"\brefactor(ing)?\b",
            r"\bdesign pattern(s)?\b"
        ],
        "weight": 2.8
    },
    {
        "name": "Legacy Code Modernizer",
        "pillar": "modernization",
        "skill_id": "clean-architecture-refactoring.code-modernization.legacy-code-modernizer",
        "patterns": [
            r"\blegacy\b", r"\bmoderniz(e|ation)\b", r"\bmonolith\b",
            r"\bdecoupling\b", r"\btechnical debt\b"
        ],
        "weight": 2.8
    },
    {
        "name": "Architecture Decision Record (ADR) Writer",
        "pillar": "docs",
        "skill_id": "clean-architecture-refactoring.architectural-docs.adr-architecture-decision-records",
        "patterns": [
            r"\badr\b", r"\barchitecture decision\b", r"\brfc\b",
            r"\bsystem design doc\b"
        ],
        "weight": 2.6
    },
    {
        "name": "Stripe Subscriptions & Webhooks",
        "pillar": "billing",
        "skill_id": "business-ecommerce-growth.payments-billing.stripe-subscription-webhooks",
        "patterns": [
            r"\bstripe\b", r"\bsubscription(s)?\b", r"\bpayments?\b", r"\bwebhook(s)?\b", r"\bbilling\b"
        ],
        "weight": 3.2
    }
]


class AutoRouter:
    """Autonomous Skill Auto-Router for vibe coding and multi-skill agent prompt orchestration."""

    def __init__(self, vault_connector: Optional[VaultConnector] = None):
        self.vault = vault_connector or VaultConnector()
        self.search_engine = SmartSkillSearch(self.vault.load_index())

    def route(
        self,
        prompt: str,
        max_skills: int = 3,
        max_tokens: Optional[int] = None,
        mode: str = "full"
    ) -> RoutingDecision:
        """
        Analyzes prompt intent, detects stack components, selects top complementary skills,
        and generates an optimized unified payload with optional token budgeting and condensation.
        """
        prompt_clean = prompt.strip()
        p_lower = prompt_clean.lower()

        detected_stack: List[str] = []
        detected_intents: List[str] = []
        pillar_scores: Dict[str, Tuple[str, float, str, str]] = {}  # pillar -> (skill_id, score, name, reason)
        routing_reasons: List[str] = []

        # 1. Pattern Rule Evaluation across pillars
        for rule in STACK_RULES:
            match_count = 0
            matched_terms = []
            for pat in rule["patterns"]:
                found = re.findall(pat, p_lower)
                if found:
                    match_count += len(found)
                    m = re.search(pat, p_lower)
                    if m:
                        matched_terms.append(m.group(0))

            if match_count > 0:
                score = rule["weight"] * (1.0 + min(1.0, (match_count - 1) * 0.4))
                pillar = rule["pillar"]
                reason = f"Detected {rule['name']} keywords: {', '.join(set(matched_terms))}"
                detected_stack.append(rule["name"])
                detected_intents.append(pillar)

                # Keep highest scoring skill per pillar
                if pillar not in pillar_scores or score > pillar_scores[pillar][1]:
                    pillar_scores[pillar] = (rule["skill_id"], score, rule["name"], reason)

        # 2. Hybrid Boost with BM25 Search Engine
        search_results = self.search_engine.search(prompt_clean, top_k=6, min_score=0.1)
        for sres in search_results:
            sid = sres.skill.id
            cat = sres.skill.category
            matched_existing = False
            for pillar, (p_sid, p_score, p_name, p_reason) in list(pillar_scores.items()):
                if p_sid == sid:
                    pillar_scores[pillar] = (p_sid, p_score + (sres.score * 2.0), p_name, p_reason)
                    matched_existing = True
                    break

            if not matched_existing and len(pillar_scores) < max_skills:
                pillar = f"search_{cat}"
                reason = f"Search engine semantic relevance ({sres.score*100:.0f}%)"
                pillar_scores[pillar] = (sid, sres.score * 2.5, sres.skill.title, reason)
                if sres.skill.title not in detected_stack:
                    detected_stack.append(sres.skill.title)

        # 3. Select top complementary skills from distinct pillars
        sorted_candidates = sorted(pillar_scores.values(), key=lambda x: x[1], reverse=True)
        selected_candidates = sorted_candidates[:max_skills]

        # Fallback if no specific patterns matched
        if not selected_candidates:
            best_match = self.search_engine.find_best_match(prompt_clean)
            if best_match:
                selected_candidates = [(best_match.skill.id, 1.0, best_match.skill.title, "General best semantic match")]
                detected_stack.append(best_match.skill.title)

        selected_skills: List[SkillDetail] = []
        match_scores: Dict[str, float] = {}
        for sid, score, name, reason in selected_candidates:
            try:
                skill_detail = self.vault.get_skill(sid)
                selected_skills.append(skill_detail)
                match_scores[skill_detail.id] = round(score, 2)
                routing_reasons.append(f"[{skill_detail.title}] {reason}")
            except KeyError:
                pass

        # 4. Compose Unified High-Density Agent Payload
        unified_payload = self._compose_unified_payload(
            prompt=prompt_clean,
            skills=selected_skills,
            detected_stack=detected_stack,
            reasons=routing_reasons,
            mode=mode,
            max_tokens=max_tokens
        )
        total_tokens = sum(s.estimated_tokens for s in selected_skills) + 250
        if mode == "condensed":
            total_tokens = int(total_tokens * 0.5)
        elif mode == "minimal":
            total_tokens = int(total_tokens * 0.25)

        return RoutingDecision(
            prompt=prompt_clean,
            detected_stack=list(dict.fromkeys(detected_stack)),
            detected_intents=list(dict.fromkeys(detected_intents)),
            selected_skills=selected_skills,
            match_scores=match_scores,
            routing_reasons=routing_reasons,
            unified_payload=unified_payload,
            total_estimated_tokens=total_tokens
        )

    def _compose_unified_payload(
        self,
        prompt: str,
        skills: List[SkillDetail],
        detected_stack: List[str],
        reasons: List[str],
        mode: str = "full",
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Combines and deduplicates skill guidelines into a unified vibe-coding context payload.
        """
        stack_list_str = "\n".join(f"  • {comp}" for comp in detected_stack) if detected_stack else "  • Generic Autonomous Agent Execution"
        skills_summary_str = "\n".join(
            f"  [{i+1}] {s.title} (v{s.version} | Trust: {s.trust_rating*100:.0f}% | ID: `{s.id}`)"
            for i, s in enumerate(skills)
        )

        skill_instructions_blocks = []
        for i, s in enumerate(skills, 1):
            cleaned_content = s.content.strip()
            
            if mode == "minimal":
                # Keep first paragraph and anti-patterns/rules
                lines = cleaned_content.splitlines()
                summary_lines = [l for l in lines[:12] if not l.startswith("```")]
                cleaned_content = "\n".join(summary_lines) + f"\n\n*(Full operational guidelines available in `{s.id}`)*"
            elif mode == "condensed":
                # Trim overly long explanations, keep code and rules
                lines = cleaned_content.splitlines()
                cleaned_content = "\n".join(lines[:45])
                if len(lines) > 45:
                    cleaned_content += f"\n\n*(Condensed view. Use 'eshkill get {s.id}' for full text)*"

            block = f"""### PILLAR {i}: {s.title.upper()} (`{s.id}`)
> **Domain**: `{s.category} / {s.subcategory}` | **Trust Rating**: `{s.trust_rating*100:.0f}%`
> **Role & Purpose**: {s.description}

{cleaned_content}
"""
            skill_instructions_blocks.append(block)

        instructions_combined = "\n--------------------------------------------------------------------------------\n".join(skill_instructions_blocks)

        return f"""================================================================================
⚡ ACTIVATED UNIFIED AGENT SKILL STACK (eshkill Auto-Router)
================================================================================
USER MISSION / PROMPT:
"{prompt}"

DETECTED ARCHITECTURAL STACK:
{stack_list_str}

ACTIVE COMPLEMENTARY SKILLS ({len(skills)} loaded):
{skills_summary_str}

ROUTING RATIONALE:
{chr(10).join('  • ' + r for r in reasons)}

================================================================================
OPERATIONAL EXECUTION PROTOCOL:
1. Architecture & Consistency: Apply all guidelines from the active skills concurrently.
2. Code Standards: Prioritize type safety, zero-regression refactoring, defensive coding, and performance.
3. Verification: Validate implementations against the testing, security, and verification rules below.
================================================================================

{instructions_combined}

================================================================================
END OF ACTIVATED SKILL CONTEXT PAYLOAD
================================================================================
"""

    @staticmethod
    def to_cursor_rules(decision: RoutingDecision) -> str:
        """Generates unified .cursorrules file content from routing decision."""
        rules = [
            f"# Cursor Vibe-Coding Rules — Autonomous Stack: {', '.join(s.name for s in decision.selected_skills)}",
            f"# Mission: {decision.prompt}",
            "",
            "## Architecture & Stack Guidelines",
        ]
        for s in decision.selected_skills:
            rules.append(f"### {s.title} (`{s.id}`)")
            rules.append(s.content.strip())
            rules.append("")
        return "\n".join(rules)

    @staticmethod
    def to_windsurf_rules(decision: RoutingDecision) -> str:
        """Generates .windsurfrules file content."""
        return f"""# Windsurf AI Cascade Rules
# Active Skills: {', '.join(s.name for s in decision.selected_skills)}

{decision.unified_payload}
"""

    @staticmethod
    def to_copilot_instructions(decision: RoutingDecision) -> str:
        """Generates .github/copilot-instructions.md file content."""
        return f"""# GitHub Copilot Instructions

## Active Architectural Skills
{chr(10).join(f"- **{s.title}** (`{s.id}`)" for s in decision.selected_skills)}

{decision.unified_payload}
"""

    @staticmethod
    def to_claude_instructions(decision: RoutingDecision) -> str:
        """Generates CLAUDE.md file content."""
        return f"""# CLAUDE.md — Agent Architectural Guidelines
# Activated Project Stack: {', '.join(s.name for s in decision.selected_skills)}

{decision.unified_payload}
"""
