"""
Lightweight REST daemon for eshkill.
Runs with standard Python library http.server (zero third-party dependencies required).
Allows local and remote AI agents, microservices, and subagents to query, route, and install skills via JSON API.
"""

import json
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Optional
from .vault import VaultConnector
from .search import SmartSkillSearch
from .router import AutoRouter
from .installer import SkillInstaller
from .agent import AgentFormatter
from .propose import ProposalManager
from . import __version__


class SkillAPIHandler(BaseHTTPRequestHandler):
    vault = VaultConnector()
    search_engine = SmartSkillSearch(vault.load_index())
    router = AutoRouter(vault)
    installer = SkillInstaller(vault)
    proposer = ProposalManager(vault)

    def _send_json(self, data: dict, status_code: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, status_code: int = 200, content_type: str = "text/plain"):
        body = text.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Health
        if path in ("", "/v1/health"):
            index = self.vault.load_index()
            self._send_json({
                "status": "ok",
                "service": "eshkill-daemon",
                "version": __version__,
                "total_skills": index.total_skills,
                "categories": list(index.categories.keys())
            })
            return

        # 2. Categories
        if path == "/v1/categories":
            self._send_json(self.vault.list_categories())
            return

        # 3. Search
        if path == "/v1/search":
            q = query.get("q", [""])[0]
            cat = query.get("category", [None])[0]
            subcat = query.get("subcategory", [None])[0]
            tag = query.get("tag", [None])[0]
            top_k = int(query.get("top_k", ["5"])[0])

            results = self.search_engine.search(query=q, category=cat, subcategory=subcat, tag=tag, top_k=top_k)
            self._send_json({
                "query": q,
                "total_results": len(results),
                "results": [r.to_dict() for r in results]
            })
            return

        # 4. Auto-Route (Vibe Coding Router)
        if path == "/v1/auto-route":
            prompt = query.get("prompt", query.get("q", [""]))[0]
            max_skills = int(query.get("max_skills", ["3"])[0])
            fmt = query.get("format", ["json"])[0].lower()
            mode = query.get("mode", ["full"])[0].lower()

            if not prompt:
                self._send_json({"error": "Query parameter 'prompt' is required."}, status_code=400)
                return

            decision = self.router.route(prompt=prompt, max_skills=max_skills, mode=mode)
            if fmt in ("text", "raw", "unified"):
                self._send_text(decision.unified_payload)
            elif fmt == "cursor":
                self._send_text(AutoRouter.to_cursor_rules(decision))
            elif fmt == "windsurf":
                self._send_text(AutoRouter.to_windsurf_rules(decision))
            elif fmt == "copilot":
                self._send_text(AutoRouter.to_copilot_instructions(decision))
            elif fmt == "claude":
                self._send_text(AutoRouter.to_claude_instructions(decision))
            else:
                self._send_json(decision.to_dict())
            return

        # 5. Match for Single-Skill Agent Injection
        if path == "/v1/match":
            task = query.get("task", query.get("q", [""]))[0]
            fmt = query.get("format", ["xml"])[0].lower()

            best_match = self.search_engine.find_best_match(task)
            if not best_match:
                self._send_json({"error": "No matching skill found for task", "task": task}, status_code=404)
                return

            skill_detail = self.vault.get_skill(best_match.skill.id)
            if fmt == "xml":
                self._send_text(AgentFormatter.to_xml(skill_detail), content_type="application/xml")
            elif fmt == "system":
                self._send_text(AgentFormatter.to_system_prompt(skill_detail))
            elif fmt == "compact":
                self._send_text(AgentFormatter.to_compact_summary(skill_detail))
            else:
                self._send_json(AgentFormatter.to_json_envelope(skill_detail, best_match))
            return

        # 6. List Skills
        if path == "/v1/skills":
            index = self.vault.load_index()
            cat = query.get("category", [None])[0]
            skills = [s.to_dict() for s in index.skills if not cat or s.category == cat]
            self._send_json({"total": len(skills), "skills": skills})
            return

        # 7. Skill Detail
        if path.startswith("/v1/skills/"):
            skill_id = path.replace("/v1/skills/", "").strip()
            fmt = query.get("format", ["json"])[0].lower()
            try:
                skill_detail = self.vault.get_skill(skill_id)
                if fmt == "xml":
                    self._send_text(AgentFormatter.to_xml(skill_detail), content_type="application/xml")
                elif fmt in ("markdown", "raw"):
                    self._send_text(skill_detail.content, content_type="text/markdown")
                elif fmt == "system":
                    self._send_text(AgentFormatter.to_system_prompt(skill_detail))
                else:
                    self._send_json(AgentFormatter.to_json_envelope(skill_detail))
            except KeyError as e:
                self._send_json({"error": str(e)}, status_code=404)
            return

        self._send_json({"error": f"Endpoint '{path}' not found"}, status_code=404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        content_len = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            self._send_json({"error": "Invalid JSON body"}, status_code=400)
            return

        # POST /v1/auto-route
        if path == "/v1/auto-route":
            prompt = payload.get("prompt", "")
            max_skills = int(payload.get("max_skills", 3))
            fmt = payload.get("format", "json").lower()
            mode = payload.get("mode", "full").lower()

            if not prompt:
                self._send_json({"error": "'prompt' field is required in JSON body"}, status_code=400)
                return

            decision = self.router.route(prompt=prompt, max_skills=max_skills, mode=mode)
            if fmt in ("text", "raw", "unified"):
                self._send_text(decision.unified_payload)
            else:
                self._send_json(decision.to_dict())
            return

        # POST /v1/install
        if path == "/v1/install":
            skill_id = payload.get("skill_id")
            mode = payload.get("mode", "workspace")
            workspace_dir = payload.get("workspace_dir")

            if not skill_id:
                self._send_json({"error": "'skill_id' is required"}, status_code=400)
                return

            res = self.installer.install(skill_id_or_name=skill_id, mode=mode, workspace_dir=workspace_dir)
            self._send_json(res.to_dict(), status_code=200 if res.success else 400)
            return

        # POST /v1/install-stack
        if path == "/v1/install-stack":
            prompt = payload.get("prompt", "")
            mode = payload.get("mode", "all-ide")
            workspace_dir = payload.get("workspace_dir")

            if not prompt:
                self._send_json({"error": "'prompt' is required to install stack"}, status_code=400)
                return

            decision = self.router.route(prompt=prompt)
            results = self.installer.install_stack(decision, mode=mode, workspace_dir=workspace_dir)
            self._send_json({
                "prompt": prompt,
                "installed_count": len(results),
                "results": [r.to_dict() for r in results]
            })
            return

        # POST /v1/proposals
        if path == "/v1/proposals":
            skill_id = payload.get("skill_id")
            proposer_id = payload.get("proposer_id", "agent_client")
            content = payload.get("proposed_content")
            reason = payload.get("reason", "")
            prop_type = payload.get("proposal_type", "modification")

            if not skill_id or not content:
                self._send_json({"error": "skill_id and proposed_content are required"}, status_code=400)
                return

            res = self.proposer.submit_proposal(
                skill_id=skill_id,
                proposer_id=proposer_id,
                proposal_type=prop_type,
                proposed_content=content,
                reason=reason
            )
            self._send_json(res.to_dict())
            return

        self._send_json({"error": f"Endpoint '{path}' not found"}, status_code=404)


def run_server(port: int = 8080, host: str = "0.0.0.0"):
    server = ThreadingHTTPServer((host, port), SkillAPIHandler)
    print(f"[*] eshkill multi-threaded daemon listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down eshkill daemon.")
        server.server_close()
