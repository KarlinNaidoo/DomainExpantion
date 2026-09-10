from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from domain_expantion import __version__
from domain_expantion.planet.activity import load_activity
from domain_expantion.registry import Registry, get_registry


def family_payload(registry: Registry | None = None) -> dict[str, Any]:
    registry = registry or get_registry()
    activity = load_activity()
    inhabitants: list[dict[str, str]] = [
        _inhabitant(
            name="supervisor",
            title="Supervisor",
            status="live",
            role="coordinator",
            description="Talks to Karli, routes work, synthesizes. Does not do specialist jobs.",
            when_to_use="Every conversation starts here.",
            activity=activity,
        )
    ]
    for spec in registry.list_specs():
        inhabitants.append(
            _inhabitant(
                name=spec.name,
                title=spec.title,
                status=spec.status,
                role="specialist",
                description=spec.description,
                when_to_use=spec.when_to_use,
                activity=activity,
            )
        )
    return {
        "version": __version__,
        "note": "Visual only. The planet does not start agents.",
        "inhabitants": inhabitants,
    }


def _inhabitant(
    *,
    name: str,
    title: str,
    status: str,
    role: str,
    description: str,
    when_to_use: str,
    activity: dict[str, Any],
) -> dict[str, str]:
    current = activity.get(name) or {}
    run_state = str(current.get("state") or "idle")
    if status != "live" and run_state == "idle":
        run_state = "idle"
    return {
        "id": name,
        "name": name,
        "title": title,
        "status": status,
        "role": role,
        "description": description,
        "when_to_use": when_to_use,
        "run_state": run_state,
        "run_detail": str(current.get("detail") or ""),
        "run_ts": str(current.get("ts") or ""),
    }


def snapshot_path() -> Path:
    path = Path.cwd() / ".data" / "planet-family.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_family_snapshot(registry: Registry | None = None) -> Path:
    path = snapshot_path()
    path.write_text(json.dumps(family_payload(registry), indent=2), encoding="utf-8")
    return path
