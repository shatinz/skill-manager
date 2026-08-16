"""
Argus Model Context Protocol (MCP) Server.
Enables AI Agents (Antigravity, Claude, Cursor, Copilot, Cline) to autonomously
query external multi-repository skill vaults and synthesize goal-matched execution bundles.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional
from .proxy import ArgusProxy
from .models import SourceType

logging.basicConfig(level=logging.INFO, format="[argus-mcp] %(levelname)s: %(message)s", stream=sys.stderr)
logger = logging.getLogger("argus-mcp")


class ArgusMCPServer:
    """JSON-RPC 2.0 MCP Server for Argus Multi-Repository Proxy."""

    def __init__(self, proxy: Optional[ArgusProxy] = None):
        self.proxy = proxy or ArgusProxy()
        self.tools = [
            {
                "name": "argus_match_goal",
                "description": "Intelligent goal-aware skill search and architecture synthesizer across multiple skill repositories. Understands user prompts (e.g. 'make a 3d website') and selects complementary skills ranked by goal relevancy, capability fit, and framework compatibility.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The user prompt, task goal, or architectural requirement."
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Maximum number of complementary skills to match and compile.",
                            "default": 5
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "argus_search_skills",
                "description": "Search across all connected skill repositories, local vaults, and remote git hubs for skills by keyword or capability.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keywords, technology names, or domain capabilities to search for."
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Maximum results to return.",
                            "default": 10
                        },
                        "source": {
                            "type": "string",
                            "description": "Optional source ID filter (e.g. 'builtin-vault', 'antigravity-system', 'skills-and-rules-repo')."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "argus_fetch_skill",
                "description": "Retrieve full instruction markdown, recipes, and rules for a specific skill from any repository.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "skill_id": {
                            "type": "string",
                            "description": "The skill ID or fully qualified ID (e.g. 'antigravity-system:img2threejs' or 'threejs-scene-craft')."
                        }
                    },
                    "required": ["skill_id"]
                }
            },
            {
                "name": "argus_list_sources",
                "description": "List all configured skill repositories, local vaults, and git remotes with health and skill counts.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "argus_add_source",
                "description": "Register a new external skill repository (local folder or remote Git URL) as a proxy source.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Unique identifier for this source."},
                        "name": {"type": "string", "description": "Human readable name."},
                        "source_type": {
                            "type": "string",
                            "enum": ["local_dir", "git_repo", "cursor_rules", "builtin_vault"],
                            "description": "Type of source."
                        },
                        "location": {"type": "string", "description": "Filesystem path or Git clone URL."},
                        "branch": {"type": "string", "description": "Git branch if git_repo."}
                    },
                    "required": ["id", "name", "source_type", "location"]
                }
            },
            {
                "name": "argus_sync_sources",
                "description": "Synchronize and re-index all enabled skill sources and repositories.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False}
                    },
                    "serverInfo": {
                        "name": "argus-skill-proxy-mcp",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": self.tools
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            return self._execute_tool(req_id, tool_name, arguments)

        elif method == "resources/list":
            skills = self.proxy.get_all_skills()
            resources = []
            for s in skills[:50]:
                resources.append({
                    "uri": f"skill://{s.qualified_id}",
                    "name": s.name,
                    "description": s.description,
                    "mimeType": "text/markdown"
                })
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"resources": resources}
            }

        elif method == "resources/read":
            uri = params.get("uri", "")
            skill_id = uri.replace("skill://", "")
            content = self.proxy.fetch(skill_id)
            if content:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "contents": [
                            {"uri": uri, "mimeType": "text/markdown", "text": content}
                        ]
                    }
                }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": f"Skill '{skill_id}' not found"}
            }

        elif method == "notifications/initialized":
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            }

    def _execute_tool(self, req_id: Any, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if tool_name == "argus_match_goal":
                prompt = args.get("prompt", "")
                top_k = args.get("top_k", 5)
                bundle = self.proxy.match(prompt=prompt, top_k=top_k)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": bundle.compiled_agent_instructions},
                            {"type": "text", "text": json.dumps(bundle.to_dict(), indent=2)}
                        ]
                    }
                }

            elif tool_name == "argus_search_skills":
                query = args.get("query", "")
                top_k = args.get("top_k", 10)
                source = args.get("source")
                results = self.proxy.search(query=query, top_k=top_k, source_filter=source)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps([r.to_dict() for r in results], indent=2)}
                        ]
                    }
                }

            elif tool_name == "argus_fetch_skill":
                skill_id = args.get("skill_id", "")
                content = self.proxy.fetch(skill_id)
                if content:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": content}]
                        }
                    }
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "isError": True,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: Skill '{skill_id}' not found in any repository."}]
                    }
                }

            elif tool_name == "argus_list_sources":
                sources = self.proxy.list_sources()
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps([s.to_dict() for s in sources], indent=2)}]
                    }
                }

            elif tool_name == "argus_add_source":
                stype_str = args.get("source_type", "local_dir")
                try:
                    stype = SourceType(stype_str)
                except ValueError:
                    stype = SourceType.LOCAL_DIR
                src = self.proxy.add_source(
                    id=args["id"],
                    name=args["name"],
                    source_type=stype,
                    location=args["location"],
                    branch=args.get("branch")
                )
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Source '{src.name}' added successfully ({src.id})."}]
                    }
                }

            elif tool_name == "argus_sync_sources":
                sync_res = self.proxy.sync_all()
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(sync_res, indent=2)}]
                    }
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "isError": True,
                    "error": {"code": -32601, "message": f"Unknown tool '{tool_name}'"}
                }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "isError": True,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }

    def run_stdio(self):
        """Run MCP JSON-RPC loop over STDIN / STDOUT."""
        logger.info("Starting Argus MCP Server over STDIO...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error handling MCP input: {e}")
