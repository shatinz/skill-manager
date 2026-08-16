# 👁️ ARGUS — Multi-Repository Skill Proxy & Goal-Aware Search Engine

> **Argus connects autonomous AI agents with distributed skill repositories, local vaults, and remote git hubs. It deconstructs user prompt goals, evaluates capability actionability, and ranks the best complementary skills to accomplish the mission.**

---

## 🌟 Why Argus?

Traditional skill managers lock you into a single local directory or static list of files. 

**Argus shifts the paradigm:**
- **No Vault Lock-In:** Instead of maintaining a solitary silo of skills, Argus is an **intelligent proxy** between your AI agent and any number of external repositories, git remotes, local folders, or prompt catalogs.
- **Goal-Aware vs. Keyword Matching:** When you prompt an agent with *"make a 3d website"*, the objective is **not** just to find an isolated 3D model parser. The objective is to fulfill the complete **goal**: 3D rendering (Three.js/WebGL) + Canvas Web Host (React/Vite/Next.js) + Responsive UI Overlay (Tailwind/CSS tokens) + Animation Loop.
- **Actionability & Compatibility Engine:** Argus analyzes whether skills provide runnable code templates vs passive documentation, and validates that recommended skills synergize cleanly without framework conflicts.

---

## 🏛️ System Architecture

```
                               ┌────────────────────────────────────────────────────────┐
                               │                    USER PROMPT                         │
                               │             "make an interactive 3d website"           │
                               └──────────────────────────┬─────────────────────────────┘
                                                          │
                                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                      ARGUS CORE ENGINE                                                 │
│                                                                                                                        │
│  1. GOAL DECONSTRUCTION                2. MULTI-REPO PROXY & INDEXING              3. GOAL-AWARE RANKER & SYNTHESIS    │
│  ┌───────────────────────────────┐     ┌─────────────────────────────────────┐     ┌─────────────────────────────────┐ │
│  │ • Deliverable: 3d_web_app     │     │ • Builtin Standard Vault            │     │ • Goal Relevancy Score (45%)    │ │
│  │ • Stacks: Three.js, React     │ ──► │ • Antigravity System Skills         │ ──► │ • Capability Fit Score (25%)    │ │
│  │ • Needs: Canvas host, Shaders │     │ • GitHub Skills & Rules Remotes     │     │ • Stack Compatibility (20%)     │ │
│  │ • Complexity: Complex         │     │ • Cursor Rules & Claude Prompts     │     │ • Provenance & Trust (10%)      │ │
│  └───────────────────────────────┘     └─────────────────────────────────────┘     └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                                          │
                                                          ▼
                               ┌────────────────────────────────────────────────────────┐
                               │                 COMPILED AGENT MANIFEST                │
                               │  [1] threejs-procedural-canvas (3D Mesh Engine)        │
                               │  [2] img2threejs (Procedural 3D Likeness)              │
                               │  [3] framer-motion-orchestrator (Animation Shell)      │
                               │  [4] shadcn-tailwind-accessible-ui (Canvas Host Shell) │
                               └────────────────────────────────────────────────────────┘
```

---

## 🚀 CLI Commands & Usage

### 1. Goal-Aware Skill Matching (`argus match`)

Matches complementary skills across all repositories tailored to accomplish the prompt goal:

```bash
# Goal matching with breakdown
argus match "make a 3d website"

# Generate complete compiled agent instructions payload
argus match "build an async fastapi rest api with postgresql" --agent

# Output machine-readable JSON for agentic pipelines
argus match "create fullstack nextjs dashboard with supabase" --json
```

**Example Output:**
```text
[ARGUS GOAL MATCHING REPORT]
User Prompt:       "make a 3d website"
Synthesized Goal:  Build an interactive 3D web experience using threejs with rendering, canvas hosting, and responsive controls.
Deliverable Type:  3d_web_application (Complexity: complex)
Target Domains:    3d-graphics, ui-design-antislop, web-frameworks
Detected Stacks:   threejs
Sources Queried:   builtin-vault, antigravity-system, skills-and-rules-repo, cursor-workspace-rules (282 skills evaluated)

--- Top Complementary Skills for this Goal (5 selected) ---

[1] threejs-procedural-canvas  (Score: 0.81 | Confidence: HIGH)
    Source:          builtin-vault (antigravity_skill)
    Assigned Role:   Primary 3D Graphics & Mesh Engine
    Goal Alignment:  Provides Three.js/WebGL scene graphs, procedural meshes, and animation rendering.
    Capabilities:    database_sql, ai_agents, 3d_rendering, frontend_ui
    Compatibility:   0.75 | Capability Fit: 0.72

[2] img2threejs  (Score: 0.59 | Confidence: MEDIUM)
    Source:          antigravity-system (antigravity_skill)
    Assigned Role:   Primary 3D Graphics & Mesh Engine
    Goal Alignment:  Provides Three.js/WebGL scene graphs, procedural meshes, and animation rendering.
    Capabilities:    ai_agents, 3d_rendering
    Compatibility:   0.65 | Capability Fit: 0.72
```

---

### 2. Multi-Repository Management (`argus sources`)

Manage distributed repositories, local folders, and upstream Git mirrors without downloading entire repositories:

- **Zero-Clone Remote Discovery:** Argus connects to remote GitHub & Git repositories using the GitHub Recursive Trees API, streaming archive extraction, and sparse git filters. It indexes skill frontmatters, capabilities, and tags without downloading or storing the full repository codebase on the local machine.
- **On-Demand Content Streaming:** Full skill markdown instructions and recipes are fetched and cached on demand only when accessed.

```bash
# List registered sources and skill counts
argus sources list

# Connect a new external GitHub repository (zero-clone discovery)
argus sources add --id my-team-skills --name "Team Skills Repo" --type git_repo --location "https://github.com/org/team-skills" --branch main

# Connect a local custom folder
argus sources add --id custom-vault --name "Local R&D Vault" --type local_dir --location "~/prj/my-skills"

# Remove a source
argus sources remove my-team-skills

# Synchronize & refresh index for all enabled repositories
argus sync
```

---

### 3. Cross-Repository Search (`argus search`)

Search keywords, categories, and technical tags across all connected vaults:

```bash
# Keyword & capability search
argus search "playwright e2e automation"

# Filter by a specific source repository
argus search "pydantic validation" --source builtin-vault
```

---

### 4. Fetch Full Skill Instructions (`argus fetch`)

Retrieve full normalized instruction markdown and recipes from any source:

```bash
argus fetch "threejs-procedural-canvas"
# or with qualified ID
argus fetch "builtin-vault:threejs-procedural-canvas"
```

---

### 5. Diagnostics & System Health (`argus doctor`)

```bash
argus doctor
```

---

## 🤖 AI Agent & MCP Integration

Argus includes a native **Model Context Protocol (MCP)** server over STDIO.

### MCP Configuration for Claude Desktop (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "argus": {
      "command": "argus",
      "args": ["mcp"]
    }
  }
}
```

### MCP Configuration for Cursor IDE (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "argus": {
      "command": "argus",
      "args": ["mcp"]
    }
  }
}
```

### Exposed MCP Tools:
- `argus_match_goal`: Goal-aware skill synthesis and bundle builder.
- `argus_search_skills`: Fast cross-source capability search.
- `argus_fetch_skill`: Fetch full instructions for a skill from any repository.
- `argus_list_sources`: List configured repositories and status.
- `argus_add_source`: Register an external git repo or directory.
- `argus_sync_sources`: Re-index and pull updates from all sources.

---

## 🌐 Zero-Dependency REST Server

Launch the standalone HTTP daemon:

```bash
argus serve --port 8765 --host 0.0.0.0
```

### REST Endpoints:
- `GET /v1/health` — Service health and aggregated skill counts.
- `GET /v1/match?prompt=...&top_k=5` or `POST /v1/match {"prompt": "..."}` — Goal matching.
- `GET /v1/search?q=...&top_k=10` — Skill search.
- `GET /v1/sources` & `POST /v1/sources` — Source management.
- `GET /v1/fetch?id=...` — Raw markdown content.
- `POST /v1/sync` — Synchronize all repositories.

---

## 🐍 Python SDK

```python
from argus import ArgusProxy

proxy = ArgusProxy()

# Goal-aware matching
bundle = proxy.match("build a realtime chat with supabase and nextjs 15")
print("Synthesized Goal:", bundle.goal_analysis.primary_goal)
for match in bundle.selected_matches:
    print(f"- {match.skill.name} ({match.goal_role}): {match.goal_alignment_reason}")

# Access compiled instructions
print(bundle.compiled_agent_instructions)
```

---

## 📄 License
MIT License.
