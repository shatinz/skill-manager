# ⚡ eshkill — The npm / apt for AI Agent Skills

> **The ultimate package manager, autonomous skill auto-router, MCP server, and smart search engine for AI agents, Claude Desktop, Cursor, Antigravity, and vibe coders.**

Connecting autonomous AI agents to living, community-driven skill capabilities with zero overhead and sub-millisecond retrieval.

---

## 🚀 Features

- 🧠 **Autonomous Skill Auto-Router (`eshkill auto-select`):**
  - Takes raw vibe-coding prompts (e.g. *"build a real-time chat with supabase and nextjs 15"*).
  - Detects architectural stack components (Next.js 15, Tailwind v4, Supabase RLS, etc.).
  - Selects 1–3 complementary skills across frontend, database, auth, devops, and testing pillars.
  - Combines their instructions into an optimized, unified agent context payload.
- ⚡ **Model Context Protocol (MCP) Server (`eshkill mcp`):**
  - Full JSON-RPC 2.0 stdio compliance for **Anthropic Claude Desktop**, **Cursor IDE**, and **Antigravity**.
  - Exposes tools: `search_skills`, `get_skill`, `auto_select_skill`, `install_skill`, `propose_skill_update`, `list_categories`.
  - Exposes resources (`skill://catalog`, `skill://<skill_id>`) and prompts (`vibe-code-router`, `activate-skill`).
- 📦 **Skill Package Installer (`eshkill install`):**
  - Local Workspace: `.agents/skills/<skill_id>/SKILL.md` (and `metadata.json`).
  - Global Configuration: `~/.gemini/config/skills/<skill_id>/SKILL.md` and `~/.eshkill/skills/`.
  - Ephemeral / Temp: returns instant in-memory or temporary buffers.
- 🔍 **Upgraded Smart Search Engine (`eshkill search`):**
  - BM25 lexical token matching + length normalization.
  - Multi-token query expansion (synonyms, tech stack aliases e.g., Supabase -> Postgres/Auth).
  - Intent classification mapping natural queries to domain categories.
  - Levenshtein & Jaccard fuzzy trigger pattern matcher with typo tolerance.
- 🌐 **Zero-Dependency REST Server (`eshkill serve`):**
  - Lightweight HTTP JSON daemon running on standard Python library `http.server`.
  - Endpoints: `/v1/health`, `/v1/search`, `/v1/auto-route`, `/v1/match`, `/v1/skills`, `/v1/install`, `/v1/proposals`.
- 🔄 **100% Backwards Compatibility:**
  - Both `eshkill` and `askill` CLI commands and Python packages are fully supported.

---

## 🛠️ CLI Quickstart

### 1. Autonomous Vibe-Coding Router (`auto-select`)
```bash
# Get unified agent prompt payload for a complete tech stack
eshkill auto-select "build a real-time chat with supabase and nextjs 15 and tailwind styling"

# Get brief stack summary
eshkill auto-select "deploy docker container to aws with terraform" -f summary

# Machine-readable JSON output
eshkill auto-select "build high-accuracy rag pipeline with hybrid search" --json
```

### 2. Smart Skill Search (`search`)
```bash
# Natural language search with query expansion
eshkill search "optimize slow postgres queries with explain analyze"

# Machine-readable JSON for agents
eshkill search "fastapi pydantic rest api" --json
```

### 3. Prompt Injection (`match`)
```bash
# Format matching skill as XML tags (<agent_skill>)
eshkill match --task "write playwright e2e tests" --format xml

# Format as system prompt preamble
eshkill match --task "jwt oauth2 token rotation" --format system
```

### 4. Install Skills (`install`)
```bash
# Install to current workspace (.agents/skills/<skill_id>/SKILL.md)
eshkill install nextjs-15-app-router

# Install globally to ~/.gemini/config/skills/
eshkill install fastapi-production-craft --global

# Ephemeral temp install
eshkill install docker-multi-stage-distroless --temp
```

### 5. Fetch Skill On-Demand (`get`)
```bash
eshkill get fastapi-production-craft
```

### 6. Model Context Protocol (MCP) Server (`mcp`)
```bash
# Run stdio MCP server for Claude Desktop / Cursor
eshkill mcp
```

### 7. Run Local REST Daemon (`serve`)
```bash
eshkill serve --port 8080
```

### 8. Run Router Validation Suite (`test-router`)
```bash
eshkill test-router
```

---

## 🐍 Python SDK

```python
from eshkill import Eshkill, AutoRouter, SmartSkillSearch, MCPServer, SkillInstaller

# Initialize unified facade
esh = Eshkill()

# 1. Autonomous Vibe-Coding Auto-Router
decision = esh.route("build a real-time chat with supabase and nextjs 15")
print("Detected Stack:", decision.detected_stack)
print("Unified Payload:\n", decision.unified_payload)

# 2. Smart Search
results = esh.search("fastapi pydantic", top_k=3)
for r in results:
    print(f"{r.skill.name}: score={r.score:.2f}")

# 3. Direct Fetch
skill = esh.get("fastapi-production-craft")
print(skill.content)

# 4. Install
install_res = esh.install("tailwind-v4-tokens", mode="workspace")
print("Installed to:", install_res.target_path)
```

---

## 🧪 Testing

Run the full test suite with 100% test passing:

```bash
python3 -m unittest discover tests
```
