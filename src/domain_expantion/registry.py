from __future__ import annotations

import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from domain_expantion.config import family_dir

AgentStatus = Literal["stub", "live", "planned"]


@dataclass(frozen=True)
class AgentSpec:
    name: str
    title: str
    status: AgentStatus
    description: str
    when_to_use: str
    spec_path: Path

    def summary_line(self) -> str:
        return f"- {self.name} ({self.status}): {self.title} — {self.when_to_use}"


class UnknownAgentError(KeyError):
    pass


class Registry:
    def __init__(
        self,
        specs: dict[str, AgentSpec],
        runners: dict[str, Callable[[str], str]] | None = None,
    ) -> None:
        self._specs = specs
        self._runners = runners if runners is not None else {}

    @classmethod
    def load(
        cls,
        root: Path | None = None,
        runners: dict[str, Callable[[str], str]] | None = None,
    ) -> Registry:
        root = root or family_dir()
        specs: dict[str, AgentSpec] = {}
        if root.exists():
            for spec_path in sorted(root.glob("*/SPEC.toml")):
                if spec_path.parent.name.startswith("_"):
                    continue
                spec = _load_spec(spec_path)
                specs[spec.name] = spec
        if runners is None:
            runners = _default_runners()
        return cls(specs, runners)

    def get(self, name: str) -> AgentSpec:
        key = name.strip().lower()
        spec = self._specs.get(key)
        if spec is None:
            known = ", ".join(sorted(self._specs)) or "(none)"
            raise UnknownAgentError(f"Unknown specialist '{key}'. Known: {known}")
        return spec

    def list_specs(self) -> list[AgentSpec]:
        return [self._specs[name] for name in sorted(self._specs)]

    def render_catalog(self) -> str:
        specs = self.list_specs()
        if not specs:
            return (
                "No specialists are registered yet. "
                "Do not invent work. Tell Karli the family catalog is empty."
            )
        lines = ["Registered specialists:"]
        lines.extend(spec.summary_line() for spec in specs)
        lines.append(
            "Only `live` specialists can do real work. "
            "`stub` and `planned` agents must not be impersonated."
        )
        return "\n".join(lines)

    def invoke(self, agent_name: str, brief: str) -> str:
        try:
            spec = self.get(agent_name)
        except UnknownAgentError as exc:
            return str(exc)

        cleaned = brief.strip()
        if not cleaned:
            return (
                f"Specialist '{spec.name}' was called with an empty brief. "
                "Rewrite a self-contained ticket and try again."
            )

        if spec.status != "live":
            return (
                f"STUB: specialist '{spec.name}' ({spec.title}) is registered but not live yet.\n"
                f"Status: {spec.status}\n"
                f"When to use: {spec.when_to_use}\n"
                f"Brief received:\n{cleaned}\n"
                "Do not invent this specialist's work. Tell Karli the agent is not live, "
                "show the brief you would have sent, and wait."
            )

        runner = self._runners.get(spec.name)
        if runner is None:
            return (
                f"Live specialist '{spec.name}' has no runtime registered. "
                "Do not impersonate it."
            )
        return runner(cleaned)


def _load_spec(path: Path) -> AgentSpec:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    name = str(data["name"]).strip().lower()
    status = str(data.get("status", "stub")).strip().lower()
    if status not in {"stub", "live", "planned"}:
        raise ValueError(f"Invalid status '{status}' in {path}")
    folder_name = path.parent.name.lower()
    if folder_name != name:
        raise ValueError(f"Spec name '{name}' must match folder '{folder_name}' ({path})")
    return AgentSpec(
        name=name,
        title=str(data.get("title", name)).strip(),
        status=status,  # type: ignore[arg-type]
        description=str(data.get("description", "")).strip(),
        when_to_use=str(data.get("when_to_use", "")).strip(),
        spec_path=path,
    )


_registry: Registry | None = None


def _default_runners() -> dict[str, Callable[[str], str]]:
    from domain_expantion.specialists.research import run as run_research

    return {"research": run_research}


def get_registry() -> Registry:
    global _registry
    if _registry is None:
        _registry = Registry.load()
    return _registry


def set_registry(registry: Registry | None) -> None:
    global _registry
    _registry = registry
