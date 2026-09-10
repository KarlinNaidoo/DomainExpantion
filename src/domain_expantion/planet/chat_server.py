from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from domain_expantion.checkpointing import open_checkpointer
from domain_expantion.config import Settings
from domain_expantion.planet.activity import set_activity
from domain_expantion.registry import Registry, set_registry
from domain_expantion.supervisor.agent import build_supervisor
from domain_expantion.supervisor.stream import events_from_update

STATIC = Path(__file__).resolve().parent / "static"
CHAT_PORT = 8766

_runtime_lock = threading.Lock()
_turn_lock = threading.Lock()
_runtime: dict[str, Any] = {}


def start_chat_runtime() -> None:
    with _runtime_lock:
        if _runtime.get("agent"):
            return
        set_registry(Registry.load())
        settings = Settings.from_env()
        cm = open_checkpointer(settings)
        checkpointer = cm.__enter__()
        _runtime["cm"] = cm
        _runtime["settings"] = settings
        _runtime["agent"] = build_supervisor(settings, checkpointer=checkpointer)


def _event_payload(event: Any) -> dict[str, Any]:
    return {
        "kind": event.kind,
        "name": event.name,
        "args": event.args or {},
        "text": event.text,
    }


def stream_turn(thread_id: str, message: str):
    start_chat_runtime()
    agent = _runtime.get("agent")
    if agent is None:
        yield {
            "kind": "error",
            "name": "",
            "args": {},
            "text": "Chat runtime is not ready. Check XAI_API_KEY and Postgres.",
        }
        return
    config = {"configurable": {"thread_id": thread_id}}
    set_activity("supervisor", "working", message)
    with _turn_lock:
        try:
            chunks = agent.stream(
                {"messages": [{"role": "user", "content": message}]},
                config,
                stream_mode="updates",
            )
            reply = ""
            for chunk in chunks:
                for event in events_from_update(chunk):
                    if event.kind == "reply":
                        reply = event.text
                    yield _event_payload(event)
            if not reply:
                yield {"kind": "reply", "name": "", "args": {}, "text": "(no reply)"}
        except Exception as exc:
            set_activity("supervisor", "error", "chat turn failed")
            yield {"kind": "error", "name": "", "args": {}, "text": str(exc)}
            return
        set_activity("supervisor", "idle")


class ChatHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/chat.html"}:
            data = (STATIC / "chat.html").read_bytes()
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if parsed.path == "/embed.js":
            data = (STATIC / "embed.js").read_bytes()
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if parsed.path == "/api/health":
            body = b'{"ok":true}'
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/chat":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        message = str(payload.get("message") or "").strip()
        thread_id = str(payload.get("thread_id") or "colony-default").strip() or "colony-default"
        if not message:
            self.send_error(400, "message required")
            return
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        for event in stream_turn(thread_id, message):
            self.wfile.write((json.dumps(event) + "\n").encode("utf-8"))
            self.wfile.flush()


def serve_chat(host: str = "127.0.0.1", port: int = CHAT_PORT) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), ChatHandler)


def start_chat_server_thread(port: int = CHAT_PORT) -> threading.Thread:
    httpd = serve_chat("127.0.0.1", port)

    def run() -> None:
        try:
            start_chat_runtime()
        except Exception:
            pass
        httpd.serve_forever()

    thread = threading.Thread(target=run, name="de-chat", daemon=True)
    thread.start()
    return thread
