from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def chats_path() -> Path:
    path = Path.cwd() / ".data" / "colony-chats.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_chats() -> dict[str, Any]:
    path = chats_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def record_chat(thread_id: str, *, agent: str = "supervisor", preview: str = "") -> None:
    data = load_chats()
    data[thread_id] = {
        "thread_id": thread_id,
        "agent": agent,
        "preview": " ".join(preview.split())[:160],
        "ts": time.time(),
    }
    path = chats_path()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def list_chats() -> list[dict[str, Any]]:
    items = list(load_chats().values())
    items.sort(key=lambda row: float(row.get("ts") or 0), reverse=True)
    return items[:40]
