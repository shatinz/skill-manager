# 🌐 Skill Manager — The Empirical Infrastructure Layer for Autonomous Agents

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Standard](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io/)
[![Security: Audited](https://img.shields.io/badge/Security%20Gate-Verified%200%20Vulns-success)](security_audit_report.md)
[![Ecosystem](https://img.shields.io/badge/Vault-60%20Curated%20Skills-cyan)](#-the-living-skill-vault-60-skills)

**[English](README.md)** • **[فارسی (Persian)](README.fa.md)** • **[Русский (Russian)](README.ru.md)** • **[中文 (Chinese)](README.zh.md)**

</div>

---

## 💡 The Core Philosophy: Evidence Over Popularity

> **Skill Manager is not a static skill repository. It is an infrastructure layer for autonomous AI agents.**

Traditional skill repositories operate like static app stores:
> *"Here is a list of 500 markdown files. Search through them, star your favorites, or install 50 skills at once."*

**This model breaks down for autonomous agents.** Agents don't need vanity GitHub stars, unvetted prompt dumps, or bloated context windows.

### The Agentic Paradigm Shift

When an autonomous agent tackles an engineering task, it does not think:
> ❌ *"Let me search through a folder of 50 skills to see what might fit."*

The agent thinks:
> 🧠 **"I am debugging a Rust networking issue. Let me retrieve the highest-rated Rust debugging workflow that has proven to succeed for similar repositories."**

```
                TRADITIONAL SKILL REPOS vs. SKILL MANAGER
┌───────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│        Static Repositories            │   │              Skill Manager               │
├───────────────────────────────────────┤   ├──────────────────────────────────────────┤
│ • Popularity & star-driven metrics    │   │ • Real-world empirical evidence ledger   │
│ • Static markdown copy-paste          │   │ • Task-aware dynamic ranking engine      │
│ • Monolithic "install everything"     │   │ • Sub-millisecond on-demand injection   │
│ • Stagnant, unverified instructions   │   │ • 7-stage nonlinear evolutionary merge   │
│ • Blind prompt execution              │   │ • Closed feedback loops (Outcome, Cost)  │
└───────────────────────────────────────┘   └──────────────────────────────────────────┘
```

---

## 📊 Real-World Project Feedback & Empirical Evidence Ledger

Skills in Skill Manager are benchmarked and ranked using actual task execution outcomes on real-world codebases. Every agent execution contributes to the global evidence ledger:

<div align="center">

```yaml
Repository:    "Rust compiler plugin"
Task:          "Fix CI async deadlock in worker channels"
Outcome:       ✅ Success
Time (MTTR):   3 min (180s)
Model:         GPT-5
Cost:          $0.19
Tokens:        14,500
Skill Version: v4.1.0
Evidence Note: "Resolved non-blocking tokio task channels and updated lifetime bounds."
```

</div>

When another agent encounters a related task, Skill Manager evaluates semantic compatibility, empirical success rates, MTTR, and model performance to return the single most proven workflow.

---

## ⚡ The 7-Stage Evolutionary Intelligence Pipeline

```
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │                 7-STAGE AUTONOMOUS EVOLUTION ARCHITECTURE                   │
  └─────────────────────────────────────────────────────────────────────────────┘
      │
  [Stage A: Ingestion] ──────► Ingests from GitHub repos, AST parser, RFC schemas
      │
  [Stage B: Evidence & Usage] ► Logs real project telemetry (Repo, Task, MTTR, Cost)
      │
  [Stage C: Batch Accumulation] Dynamic window clustering of agent & human proposals
      │
  [Stage D: Nonlinear Merge] ─► Attention-weighted synthesis (Sybil-resistant trust)
      │
  [Stage E: Security Sentinel]  SAST AST scanner, Canary sandboxing, zero vulnerabilities
      │
  [Stage F: Canary Release] ──► Canary rollouts with automated fallback & lineage chains
      │
  [Stage G: Agent Serving] ───► Task-aware ranking, FastMCP stdio/SSE & REST daemon
```

### Nonlinear Trust Synthesis Formula
Proposals converging on identical fixes multiply influence logarithmically while dampening radical rewrites from unproven accounts:
$$\text{Effective Weight} = \left(\sum \text{Trust}_i\right) \times \left(1 + \ln(N) \cdot W_{\text{redundancy}}\right) \times (1 - \text{Dampening})$$

---

## 🚀 Quick Start for Autonomous Agents & Developers

### 1. Installation
Install the lightweight agent CLI (`eshkill` / `askill`):

```bash
# Clone the repository
git clone https://github.com/shatinz/skill-manager.git
cd skill-manager

# Install CLI locally in editable mode
pip install -e ./cli
```

### 2. Task-Aware Dynamic Skill Retrieval (`rank`)
Instead of manually searching, request the highest-ranked proven workflow for your task:

```bash
# Agent queries highest-proven workflow based on task & repository context
eshkill rank --task "Fix CI" --repo "Rust compiler plugin" --model "GPT-5"
```

**Output:**
```text
⚡ EMPIRICAL SKILL RANKING (EVIDENCE-BASED ENGINE)
• Target Task: Fix CI
• Repository Context: Rust compiler plugin
• Target Model: GPT-5
────────────────────────────────────────────────────────────

🏆 #1 TOP PROVEN WORKFLOW: Rust Axum & Tokio High-Throughput Async Architecture
• Empirical Reliability: 99% Success Rate
• Avg Resolution Time (MTTR): 2.0 min
• Avg Cost Efficiency: $0.12
• Real-World Runs: 42 evidence records
• Recommended Version: v1.3.0

Selected based on verified real-world runs on similar Rust compiler plugins.
```

### 3. Record Execution Telemetry (`report-evidence`)
Close the loop by recording execution outcome back to the platform:

```bash
eshkill report-evidence \
  --skill rust-axum-tokio-async \
  --repo "Rust compiler plugin" \
  --task "Fix CI" \
  --outcome success \
  --duration 180 \
  --model "GPT-5" \
  --cost 0.19 \
  --version "4.1.0" \
  --notes "Resolved non-blocking tokio task channels"
```

### 4. Autonomous Agent Self-Healing & Proposal (`auto-propose`)
When an agent encounters compiler warnings, deprecations, or runtime errors, it automatically submits a proposal with explicit `🤖 Autonomous Agent` origin tagging:

```bash
eshkill auto-propose \
  --skill fastapi-production-craft \
  --feedback "DeprecationWarning: Starlette 0.40 form parsing changed" \
  --fix "Enforce async request.form() with python-multipart>=0.0.20" \
  --reason "Resolve Starlette async form deprecation" \
  --agent-id "agent:autonomous-debugger" \
  --model "claude-3-5-sonnet"
```

---

## 🔌 Model Context Protocol (MCP) Integration

Skill Manager provides native Model Context Protocol (MCP) support over standard JSON-RPC 2.0 stdio and SSE transports. Compatible with **Claude Desktop**, **Cursor**, **Windsurf**, and **Antigravity**.

### Configuration (`claude_desktop_config.json` / Cursor MCP)
```json
{
  "mcpServers": {
    "skill-manager": {
      "command": "python",
      "args": ["-m", "eshkill.cli", "mcp"],
      "env": {
        "SKILL_MANAGER_API_URL": "http://127.0.0.1:8000/api"
      }
    }
  }
}
```

### Exposed MCP Agent Tools:
1. `find_best_skill_for_task`: Autonomously retrieves the highest-rated workflow for any engineering task and repository context based on empirical evidence.
2. `record_execution_evidence`: Logs task execution duration, cost, outcome, and telemetry into the benchmark ledger.
3. `auto_propose_skill_fix`: Self-improves skills based on runtime error feedback.
4. `get_skill`: Streams skill instructions formatted as Markdown, XML, or System Prompts.
5. `auto_select_skill`: Automatically compiles a multi-skill context stack for vibe-coding prompts.

---

## 🏛️ The Living Skill Vault (60 Curated Skills)

The Skill Vault houses 60 high-impact, battle-tested skills across 9 core engineering categories:

| Category | Description & Key Patterns |
| :--- | :--- |
| **🤖 AI & LLM Agents** | FastMCP Server Dev, Knowledge Graph Memory, Sequential Thinking & Tree-of-Thought, LangGraph Multi-Agent Workflows, RAG Hybrid Search. |
| **🌐 Web Frameworks** | Next.js 15 App Router, TanStack Router & Query v5, React 19 Server Actions, FastAPI Production Craft, Hono Cloudflare Edge, Astro 5. |
| **🎨 UI & Anti-Slop Design** | Shadcn UI & Tailwind v4 Tokens, Dark Mode Ambient Gradients, Responsive Fluid Layouts, Accessible Micro-Interactions. |
| **🗄️ Databases & Storage** | Postgres Explain Analyze Tuning, Supabase RLS Realtime, Prisma ORM, Drizzle Type-Safe SQL, DuckDB & Polars Analytics. |
| **☁️ DevOps & Cloud** | ArgoCD GitOps & Kubernetes Helm, Docker Distroless Multi-Stage, GitHub Actions Matrix CI, OpenTelemetry & Prometheus Telemetry. |
| **🛡️ SAST & Security** | OWASP Top 10 Scanner, Secret Leak Pre-Commit Guards, JWT OAuth2 Defense, Input Sanitization & XSS Prevention. |
| **🧪 Testing & QA** | Pytest Mocking & Fixtures, Playwright E2E Automation, Hypothesis Property-Based Testing, Chaos Fault Injection. |
| **📈 Business & E-Commerce** | Stripe Billing & Webhooks, Multi-Currency Ledger, SEO Meta Generation, Funnel Conversion Optimization. |
| **📐 Clean Architecture** | Rust Axum & Tokio Async, Event Sourcing & Outbox Pattern, Michael Nygard ADR Decision Records, DRY/SOLID Modernization. |

---

## 🖥️ Live Full-Stack Architecture & Web Dashboard

Skill Manager includes a FastAPI backend and a responsive Single Page Application (SPA) dashboard:

```bash
# Start backend server
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` to inspect:
- **📊 Real-Time Evidence Ledger**: Inspect live project execution telemetry (Repo, Task, Outcome, Model, Cost, Time).
- **🧭 Dynamic Workflow Matcher**: Test task-aware empirical ranking queries interactively.
- **🕸️ Neural Skill Network Canvas**: Interactive force-directed physics graph visualizing skill dependencies and cluster merges.
- **🛡️ Security Quarantine Queue**: Review flagged AST mutations and safety overrides.

---

## 📜 Documentation & Deep Dives

- [Detailed Architecture & Lifecycle Stages](docs/ARCHITECTURE.md)
- [Security Sentinel Audit Report (Zero Findings)](security_audit_report.md)
- [CLI Reference & Cheatsheet](docs/CLI_REFERENCE.md)
- [MCP Integration Guide](docs/MCP_INTEGRATION.md)

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
