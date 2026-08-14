---
id: ai-llm-agents.agent-tooling.modelcontextprotocol-server-dev
name: modelcontextprotocol-server-dev
title: Model Context Protocol (MCP) Server Development & FastMCP Integration
category: ai-llm-agents
subcategory: agent-tooling
version: 1.2.0
tags:
- mcp
- model-context-protocol
- fastmcp
- json-rpc
- tools
- resources
- prompts
- claude
- cursor
trust_rating: 0.99
estimated_tokens: 1850
description: Architect and deploy production-ready Model Context Protocol (MCP) servers
  using Python FastMCP and TypeScript MCP SDK, exposing typed tools, dynamic resources,
  prompts, and stdio/SSE transports to Claude Desktop, Cursor, and Antigravity agents.
trigger_patterns:
- create model context protocol server
- fastmcp python tool definition
- mcp server claude cursor integration
- mcp dynamic resources json-rpc 2.0
- mcp sse stdio transport server
---

# Model Context Protocol (MCP) Server Development & FastMCP Integration

## Objective
Build standardized, secure Model Context Protocol (MCP) servers that connect AI agents directly to enterprise databases, local developer tools, APIs, and custom execution runtimes over JSON-RPC 2.0 stdio and SSE transports.

## Architecture Blueprint
```
Claude Desktop / Cursor / Antigravity Agent
   | (JSON-RPC 2.0 over stdio or SSE)
   v
FastMCP Server (`server.py`)
   ├── Tools: Executable functions with Pydantic type validation & docstrings
   ├── Resources: Dynamic URI templates (`sqlite:///{db}/tables/{table}`)
   └── Prompts: Reusable parameterized prompt templates for user interaction
```

## Production FastMCP Python Implementation (`mcp_server.py`)
```python
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import sqlite3
import os

# 1. Initialize MCP Server instance
mcp = FastMCP(
    "Enterprise Data & Dev Tools",
    dependencies=["pydantic", "sqlite3"]
)

# 2. Expose Typed Tool with Rich Docstring & Parameter Schema
@mcp.tool()
async def query_database(
    sql_query: str = Field(..., description="Read-only SQL query to execute against the analytics database"),
    max_rows: int = Field(default=50, ge=1, le=500, description="Max rows to return"),
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Execute a read-only SQL query against the local SQLite analytics store.
    Prevents destructive operations (DROP, DELETE, UPDATE) and returns structured JSON rows.
    """
    if ctx:
        await ctx.info(f"Executing query: {sql_query[:60]}...")

    # Guardrail against write operations
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    if any(kw in sql_query.upper() for kw in forbidden):
        raise ValueError("Write operations are forbidden. Use dedicated migration tools.")

    conn = sqlite3.connect(os.environ.get("ANALYTICS_DB_PATH", "analytics.db"))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        rows = [dict(row) for row in cursor.fetchmany(max_rows)]
        return {"row_count": len(rows), "data": rows}
    finally:
        conn.close()

# 3. Expose Dynamic Resource Template
@mcp.resource("schema://{table_name}")
def get_table_schema(table_name: str) -> str:
    """Retrieve SQL CREATE TABLE schema definition for an analytics table."""
    conn = sqlite3.connect(os.environ.get("ANALYTICS_DB_PATH", "analytics.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    row = cursor.fetchone()
    conn.close()
    if not row or not row[0]:
        return f"Table '{table_name}' does not exist."
    return row[0]

# 4. Standard stdio entrypoint
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Client Configuration (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "enterprise-tools": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"],
      "env": {
        "ANALYTICS_DB_PATH": "/data/analytics.db"
      }
    }
  }
}
```

## Anti-Patterns
- ❌ Logging non-protocol messages to `stdout` in stdio mode (stdout is strictly reserved for JSON-RPC messages; use `stderr` or `ctx.info()` instead).
- ❌ Omitting parameter descriptions and type annotations (LLMs rely on Pydantic `Field(description=...)` to understand tool arguments).
