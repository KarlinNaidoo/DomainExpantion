from __future__ import annotations

import json
from threading import Thread
from urllib.request import Request, urlopen

from domain_expantion.planet.chat_server import serve_chat


def test_chat_health_and_page() -> None:
    httpd = serve_chat("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{port}/api/health") as resp:
            data = json.loads(resp.read().decode("utf-8"))
        assert data["ok"] is True
        with urlopen(f"http://127.0.0.1:{port}/chat.html") as resp:
            html = resp.read().decode("utf-8")
        assert "Supervisor" in html
        with urlopen(f"http://127.0.0.1:{port}/embed.js") as resp:
            js = resp.read().decode("utf-8")
        assert "/api/open" in js
        assert "domain-expantion" in js
        with urlopen(f"http://127.0.0.1:{port}/api/chats") as resp:
            catalog = json.loads(resp.read().decode("utf-8"))
        assert "chats" in catalog
        with urlopen(f"http://127.0.0.1:{port}/api/history?thread_id=missing") as resp:
            hist = json.loads(resp.read().decode("utf-8"))
        assert hist["events"] == [] or isinstance(hist["events"], list)
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_chat_rejects_empty_message() -> None:
    httpd = serve_chat("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        req = Request(
            f"http://127.0.0.1:{port}/api/chat",
            data=b'{"message":""}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            urlopen(req)
            raise AssertionError("expected HTTP error")
        except Exception as exc:
            assert "400" in str(exc)
    finally:
        httpd.shutdown()
        httpd.server_close()
