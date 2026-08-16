"""
Argus Standalone HTTP REST API Server.
Provides fast REST endpoints for AI Agent integrations, Web UIs, and CLI queries.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional
from .proxy import ArgusProxy
from .models import SourceType

logger = logging.getLogger("argus-server")


class ArgusAPIHandler(BaseHTTPRequestHandler):
    proxy: ArgusProxy = None  # Injected on startup

    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        if path in ("", "/health", "/v1/health"):
            self._send_json(200, {
                "status": "healthy",
                "service": "argus-skill-proxy",
                "sources_count": len(self.proxy.list_sources()),
                "total_skills": len(self.proxy.get_all_skills())
            })

        elif path in ("/v1/match", "/match"):
            prompt = params.get("prompt", params.get("q", [""]))[0]
            top_k = int(params.get("top_k", [5])[0])
            if not prompt:
                self._send_json(400, {"error": "Missing 'prompt' parameter"})
                return
            bundle = self.proxy.match(prompt=prompt, top_k=top_k)
            self._send_json(200, bundle.to_dict())

        elif path in ("/v1/search", "/search"):
            q = params.get("q", params.get("query", [""]))[0]
            top_k = int(params.get("top_k", [10])[0])
            source = params.get("source", [None])[0]
            results = self.proxy.search(query=q, top_k=top_k, source_filter=source)
            self._send_json(200, {"query": q, "results": [r.to_dict() for r in results]})

        elif path in ("/v1/sources", "/sources"):
            sources = self.proxy.list_sources()
            self._send_json(200, {"sources": [s.to_dict() for s in sources]})

        elif path in ("/v1/fetch", "/fetch"):
            skill_id = params.get("id", [""])[0]
            if not skill_id:
                self._send_json(400, {"error": "Missing 'id' parameter"})
                return
            content = self.proxy.fetch(skill_id)
            if content:
                self._send_json(200, {"id": skill_id, "content": content})
            else:
                self._send_json(404, {"error": f"Skill '{skill_id}' not found"})

        else:
            self._send_json(404, {"error": f"Path '{path}' not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(length) if length > 0 else b"{}"

        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        if path in ("/v1/match", "/match"):
            prompt = body.get("prompt", "")
            top_k = int(body.get("top_k", 5))
            if not prompt:
                self._send_json(400, {"error": "Missing 'prompt' in request body"})
                return
            bundle = self.proxy.match(prompt=prompt, top_k=top_k)
            self._send_json(200, bundle.to_dict())

        elif path in ("/v1/sources", "/sources"):
            try:
                stype_str = body.get("source_type", "local_dir")
                try:
                    stype = SourceType(stype_str)
                except ValueError:
                    stype = SourceType.LOCAL_DIR
                src = self.proxy.add_source(
                    id=body["id"],
                    name=body["name"],
                    source_type=stype,
                    location=body["location"],
                    branch=body.get("branch")
                )
                self._send_json(201, {"message": "Source added", "source": src.to_dict()})
            except KeyError as e:
                self._send_json(400, {"error": f"Missing field: {e}"})

        elif path in ("/v1/sync", "/sync"):
            results = self.proxy.sync_all()
            self._send_json(200, {"message": "Sync completed", "results": results})

        else:
            self._send_json(404, {"error": f"Path '{path}' not found"})


def run_server(host: str = "0.0.0.0", port: int = 8765, proxy: Optional[ArgusProxy] = None):
    ArgusAPIHandler.proxy = proxy or ArgusProxy()
    server = HTTPServer((host, port), ArgusAPIHandler)
    print(f"Argus Multi-Repository Skill Proxy running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Argus server...")
        server.server_close()
