from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from domain_expantion.planet.state import family_payload
from domain_expantion.registry import Registry, set_registry

STATIC_DIR = Path(__file__).resolve().parent / "static"


class PlanetHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/api/family", "/api/family/"}:
            body = json.dumps(family_payload()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path in {"/", "/index.html"}:
            data = (STATIC_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_error(404, "Not found")


def serve_planet(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    set_registry(Registry.load())
    return ThreadingHTTPServer((host, port), PlanetHandler)
