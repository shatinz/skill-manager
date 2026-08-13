---
id: ai-llm-agents.mcp-protocol.mcp-server-protocol-craft
name: mcp-server-protocol-craft
title: Model Context Protocol (MCP) Server & Tool Architecture
category: ai-llm-agents
subcategory: mcp-protocol
version: 1.3.0
tags:
- mcp
- model-context-protocol
- stdio
- sse
- typescript
- python
- fastmcp
trust_rating: 0.98
estimated_tokens: 1650
description: Construct production-ready Model Context Protocol (MCP) servers using
  FastMCP / TypeScript SDK, exposing tools, resources, and prompts over stdio and
  Server-Sent Events (SSE).
trigger_patterns:
- create mcp server python fastmcp
- model context protocol typescript sdk
- mcp stdio sse transport
- mcp tool resource prompt registration
---

# Model Context Protocol (MCP) Server & Tool Architecture

## Objective
Author standards-compliant Model Context Protocol (MCP) servers to expose local system tools, data resources, and structured prompt templates to AI clients (Claude Desktop, Cursor, AI agents).

## FastMCP Server Blueprint (`mcp_server.py`)
```python
from mcp.server.fastmcp import FastMCP, Context
import os
import subprocess

mcp = FastMCP("DevOps Commander")

@mcp.tool()
async def run_git_status(repo_path: str, ctx: Context) -> str:
    # Check the git status of a local repository
    ctx.info(f"Checking status for {repo_path}")
    if not os.path.isdir(repo_path):
        raise ValueError(f"Directory {repo_path} does not exist.")

    res = subprocess.run(["git", "status", "-s"], cwd=repo_path, capture_output=True, text=True)
    return res.stdout or "Working tree clean."

@mcp.resource("config://app-settings")
def get_app_config() -> str:
    # Retrieve active system configurations
    return "ENVIRONMENT=production\nDEBUG=false"

@mcp.prompt()
def review_commit(commit_hash: str) -> str:
    # Generate a prompt to review a specific commit
    return f"Please review the changes in commit {commit_hash} for security vulnerabilities."

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Anti-Patterns
- ❌ Outputting plain `print()` statements to stdout in stdio transport mode (corrupts JSON-RPC protocol frames).
- ❌ Running unsanitized shell commands directly without strict argument whitelisting.
