from __future__ import annotations

from typing import Any

from domain_expantion import __version__
from domain_expantion.registry import Registry, get_registry


def family_payload(registry: Registry | None = None) -> dict[str, Any]:
    registry = registry or get_registry()
    inhabitants: list[dict[str, str]] = [
        {
            "id": "supervisor",
            "name": "supervisor",
            "title": "Supervisor",
            "status": "live",
            "role": "coordinator",
            "description": "Talks to Karli, routes work, synthesizes. Does not do specialist jobs.",
            "when_to_use": "Every conversation starts here.",
        }
    ]
    for spec in registry.list_specs():
        inhabitants.append(
            {
                "id": spec.name,
                "name": spec.name,
                "title": spec.title,
                "status": spec.status,
                "role": "specialist",
                "description": spec.description,
                "when_to_use": spec.when_to_use,
            }
        )
    return {
        "version": __version__,
        "note": "Visual only. The planet does not start agents.",
        "inhabitants": inhabitants,
    }
