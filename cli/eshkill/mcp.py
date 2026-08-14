"""
Model Context Protocol (MCP) Server for eshkill.
Enables Anthropic Claude Desktop, Cursor, Antigravity, and autonomous AI agents
to discover, inspect, route, install, and propose skills over standard JSON-RPC 2.0 stdio.
"""

import sys
import os
import json
import logging
from typing import Dict, Any, Optional, List
from .vault import VaultConnector
from .search import SmartSkillSearch
from .router import AutoRouter
from .installer import SkillInstaller
from .agent import AgentFormatter
from .propose import ProposalManager
from .models import MCPToolResult

# Configure stderr logging for MCP (stdio stdout is reserved for JSON-RPC messages)
logger = logging.getLogger("eshkill.mcp")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("[eshkill-mcp] %(levelname)s: %(message)s"))
logger.addHandler(handler)

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "eshkill-mcp"
SERVER_VERSION = "1.1.0"


class MCPServer:
    def __init__(self, vault_connector: Optional[VaultConnector] = None):
        self.vault = vault_connector or VaultConnector()
        self.search_engine = SmartSkillSearch(self.vault.load_index())
        self.router = AutoRouter(self.vault)
        self.installer = SkillInstaller(self.vault)
        self.proposer = ProposalManager(self.vault)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_skills",
                "description": "Smart semantic search across the Agentic Skill Vault using BM25, intent matching, and trigger patterns.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Task description, technology keyword, or natural language query (e.g. 'optimize postgres query' or 'fastapi pydantic')"
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category filter (e.g. 'coding', 'testing-quality', 'devops-cloud', 'data-ai-engineering', 'security-compliance')"
                        },
                        "tag": {
                            "type": "string",
                            "description": "Optional tag filter (e.g. 'react', 'postgres', 'docker', 'rag')"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_skill",
                "description": "Retrieve the full operational instructions, trigger patterns, and metadata for a specific skill by ID or name.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "description": "The unique skill ID (e.g. 'coding.api-design.fastapi-rest-craft' or 'fastapi-rest-craft')"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "xml", "system", "json"],
                            "description": "Output representation format (default: 'markdown')"
                        }
                    },
                    "required": ["skill_id"]
                }
            },
            {
                "name": "auto_select_skill",
                "description": "Autonomous Vibe-Coding Skill Router: Analyzes a raw user prompt or project task, detects architectural components (Next.js, Supabase, Tailwind, FastAPI, etc.), selects complementary skills, and returns an optimized unified context payload.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The user's raw vibe-coding prompt or task requirements (e.g. 'build a real-time chat with supabase and nextjs 15')"
                        },
                        "max_skills": {
                            "type": "integer",
                            "description": "Maximum complementary skills to orchestrate (default: 3, max: 5)"
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "install_skill",
                "description": "Install a skill into the local workspace (.agents/skills/<skill_id>/SKILL.md) or global agent configuration.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "description": "The skill ID or name to install"
                        },
                        "mode": {
                            "type": "string",
                            "enum": ["workspace", "global", "temp"],
                            "description": "Installation mode: 'workspace' (.agents/skills/), 'global' (~/.gemini/config/skills/), or 'temp' (ephemeral)"
                        },
                        "workspace_dir": {
                            "type": "string",
                            "description": "Custom workspace root directory path (optional)"
                        }
                    },
                    "required": ["skill_id"]
                }
            },
            {
                "name": "propose_skill_update",
                "description": "Autonomous Agent Tool: Propose an improvement, bugfix, or modern pattern update to a living skill in the vault with automatic agent tagging and unified diffing.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "description": "Target skill ID to update"
                        },
                        "proposed_content": {
                            "type": "string",
                            "description": "Complete updated markdown content of the skill"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for the proposal or description of improvements"
                        },
                        "proposer_id": {
                            "type": "string",
                            "description": "Identifier of the agent or developer making the proposal (e.g. 'agent:claude-3-5-sonnet')"
                        },
                        "is_agent": {
                            "type": "boolean",
                            "description": "Flag indicating this proposal is submitted autonomously by an AI agent (default: true)"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags describing the proposal origin and focus (e.g. ['autonomous_agent', 'runtime_feedback'])"
                        }
                    },
                    "required": ["skill_id", "proposed_content"]
                }
            },
            {
                "name": "auto_propose_skill_fix",
                "description": "Autonomous Self-Improvement Tool: Automatically formulates and submits a proposal to improve a skill based on live execution feedback, deprecations, or runtime error recoveries.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "description": "Target skill ID to improve"
                        },
                        "execution_feedback": {
                            "type": "string",
                            "description": "Runtime error trace, compiler warning, or task outcome observation"
                        },
                        "suggested_fix": {
                            "type": "string",
                            "description": "The specific guideline, rule addition, or code fix to append/integrate into the skill"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Brief explanation of why the fix is necessary"
                        },
                        "agent_model": {
                            "type": "string",
                            "description": "Name/version of the autonomous LLM agent (e.g. 'claude-3-5-sonnet', 'gpt-4o')"
                        }
                    },
                    "required": ["skill_id", "execution_feedback", "suggested_fix"]
                }
            },
            {
                "name": "list_categories",
                "description": "List all skill categories and subcategories in the catalog hierarchy.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the requested tool and returns standard MCP tool call envelope."""
        try:
            if tool_name == "search_skills":
                query = args.get("query", "")
                cat = args.get("category")
                tag = args.get("tag")
                top_k = int(args.get("top_k", 5))
                results = self.search_engine.search(query=query, category=cat, tag=tag, top_k=top_k)
                data = {
                    "query": query,
                    "total_found": len(results),
                    "results": [r.to_dict() for r in results]
                }
                return {
                    "content": [{"type": "text", "text": json.dumps(data, indent=2)}],
                    "isError": False
                }

            elif tool_name == "get_skill":
                skill_id = args.get("skill_id", "")
                fmt = args.get("format", "markdown").lower()
                skill = self.vault.get_skill(skill_id)

                if fmt == "xml":
                    text = AgentFormatter.to_xml(skill)
                elif fmt == "system":
                    text = AgentFormatter.to_system_prompt(skill)
                elif fmt == "json":
                    text = json.dumps(AgentFormatter.to_json_envelope(skill), indent=2)
                else:
                    text = skill.content

                return {
                    "content": [{"type": "text", "text": text}],
                    "isError": False
                }

            elif tool_name == "auto_select_skill":
                prompt = args.get("prompt", "")
                max_skills = int(args.get("max_skills", 3))
                decision = self.router.route(prompt=prompt, max_skills=max_skills)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": decision.unified_payload
                        }
                    ],
                    "isError": False
                }

            elif tool_name == "install_skill":
                skill_id = args.get("skill_id", "")
                mode = args.get("mode", "workspace")
                ws_dir = args.get("workspace_dir")
                result = self.installer.install(skill_id_or_name=skill_id, mode=mode, workspace_dir=ws_dir)
                return {
                    "content": [{"type": "text", "text": json.dumps(result.to_dict(), indent=2)}],
                    "isError": not result.success
                }

            elif tool_name == "propose_skill_update":
                skill_id = args.get("skill_id", "")
                content = args.get("proposed_content", "")
                reason = args.get("reason", "")
                proposer = args.get("proposer_id", "agent:mcp-autonomous-worker")
                is_agent = args.get("is_agent", True)
                tags = args.get("tags", ["autonomous_agent", "ai_generated"])
                result = self.proposer.submit_proposal(
                    skill_id=skill_id,
                    proposer_id=proposer,
                    proposed_content=content,
                    reason=reason,
                    is_agent=is_agent,
                    tags=tags
                )
                return {
                    "content": [{"type": "text", "text": json.dumps(result.to_dict(), indent=2)}],
                    "isError": not result.success
                }

            elif tool_name == "auto_propose_skill_fix":
                skill_id = args.get("skill_id", "")
                feedback = args.get("execution_feedback", "")
                suggested_fix = args.get("suggested_fix", "")
                reason = args.get("reason", "Autonomous skill refinement based on runtime feedback")
                agent_model = args.get("agent_model", "claude-3-5-sonnet")
                result = self.proposer.auto_propose_from_feedback(
                    skill_id=skill_id,
                    execution_feedback=feedback,
                    suggested_modifications=suggested_fix,
                    reason=reason,
                    agent_model=agent_model
                )
                return {
                    "content": [{"type": "text", "text": json.dumps(result.to_dict(), indent=2)}],
                    "isError": not result.success
                }

            elif tool_name == "list_categories":
                cats = self.vault.list_categories()
                return {
                    "content": [{"type": "text", "text": json.dumps(cats, indent=2)}],
                    "isError": False
                }

            else:
                return {
                    "content": [{"type": "text", "text": f"Unknown tool '{tool_name}'"}],
                    "isError": True
                }

        except Exception as e:
            logger.error(f"Error handling tool '{tool_name}': {e}", exc_info=True)
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processes an incoming JSON-RPC 2.0 request."""
        req_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        logger.info(f"Incoming JSON-RPC request: method='{method}' id={req_id}")

        # Standard MCP Methods
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    },
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        },
                        "resources": {
                            "subscribe": False,
                            "listChanged": False
                        },
                        "prompts": {
                            "listChanged": False
                        }
                    }
                }
            }

        elif method == "notifications/initialized" or method == "initialized":
            # Client notification acknowledgment, no response required
            return None

        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": self.get_tool_definitions()
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            args = params.get("arguments", {})
            result = self.handle_tool_call(tool_name, args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }

        elif method == "resources/list":
            index = self.vault.load_index()
            resources = [
                {
                    "uri": "skill://catalog",
                    "name": "Public Skill Vault Catalog",
                    "description": "Full directory index of community agent skills",
                    "mimeType": "application/json"
                }
            ]
            for s in index.skills:
                resources.append({
                    "uri": f"skill://{s.id}",
                    "name": s.title,
                    "description": s.description,
                    "mimeType": "text/markdown"
                })
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "resources": resources
                }
            }

        elif method == "resources/read":
            uri = params.get("uri", "")
            if uri == "skill://catalog":
                index = self.vault.load_index()
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "contents": [
                            {
                                "uri": uri,
                                "mimeType": "application/json",
                                "text": json.dumps(index.to_dict(), indent=2)
                            }
                        ]
                    }
                }
            elif uri.startswith("skill://"):
                skill_id = uri.replace("skill://", "")
                try:
                    skill = self.vault.get_skill(skill_id)
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "contents": [
                                {
                                    "uri": uri,
                                    "mimeType": "text/markdown",
                                    "text": skill.content
                                }
                            ]
                        }
                    }
                except KeyError as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32602,
                            "message": str(e)
                        }
                    }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32602,
                    "message": f"Resource not found: {uri}"
                }
            }

        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "prompts": [
                        {
                            "name": "vibe-code-router",
                            "description": "Auto-routes a vibe-coding prompt to the best complementary skills and formats unified instructions",
                            "arguments": [
                                {
                                    "name": "prompt",
                                    "description": "User's vibe coding task description",
                                    "required": True
                                }
                            ]
                        },
                        {
                            "name": "activate-skill",
                            "description": "Formats a specific skill as a high-density system prompt",
                            "arguments": [
                                {
                                    "name": "skill_id",
                                    "description": "Skill ID to activate",
                                    "required": True
                                }
                            ]
                        }
                    ]
                }
            }

        elif method == "prompts/get":
            prompt_name = params.get("name", "")
            prompt_args = params.get("arguments", {})
            if prompt_name == "vibe-code-router":
                raw_prompt = prompt_args.get("prompt", "")
                decision = self.router.route(raw_prompt)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "description": f"Activated stack for: {raw_prompt}",
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": decision.unified_payload
                                }
                            }
                        ]
                    }
                }
            elif prompt_name == "activate-skill":
                skill_id = prompt_args.get("skill_id", "")
                skill = self.vault.get_skill(skill_id)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "description": f"Skill: {skill.title}",
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": AgentFormatter.to_system_prompt(skill)
                                }
                            }
                        ]
                    }
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Prompt '{prompt_name}' not found"
                }
            }

        else:
            if req_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }
            return None

    def run_stdio(self):
        """Runs the MCP server over standard input/output with JSON-RPC framing."""
        logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION} on stdio...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except json.JSONDecodeError:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error: Invalid JSON"
                    }
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Unexpected error in stdio loop: {e}", exc_info=True)


def run_mcp_server():
    server = MCPServer()
    server.run_stdio()


if __name__ == "__main__":
    run_mcp_server()
