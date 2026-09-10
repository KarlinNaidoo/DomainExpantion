from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

VALID_STATES = {"idle", "working", "waiting", "error"}


def activity_path() -> Path:
    path = Path.cwd() / ".data" / "planet-activity.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_activity() -> dict[str, Any]:
    path = activity_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def set_activity(name: str, state: str, detail: str = "") -> None:
    if state not in VALID_STATES:
        state = "idle"
    data = load_activity()
    data[name] = {
        "state": state,
        "detail": detail[:240],
        "ts": time.time(),
    }
    path = activity_path()
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)
    from domain_expantion.planet.state import write_family_snapshot

    write_family_snapshot()
