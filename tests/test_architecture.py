from __future__ import annotations

from types import SimpleNamespace

from domain_expantion.registry import Registry
from domain_expantion.specialists.architecture import ARCHITECTURE_PROMPT, run


class _FakeModel:
    def invoke(self, _messages: object) -> SimpleNamespace:
        return SimpleNamespace(
            content=(
                "## Intent\nBuild a notes API.\n"
                "## Implementation slices\n1. FastAPI app and health route\n"
                "```mermaid\nflowchart LR\nUser-->API\n```"
            )
        )


def test_architecture_run_uses_injected_model() -> None:
    text = run("Design a notes API.", model=_FakeModel())
    assert "Intent" in text
    assert "mermaid" in text


def test_architecture_prompt_is_an_implementation_pack() -> None:
    assert "Mermaid" in ARCHITECTURE_PROMPT
    assert "## Decisions" in ARCHITECTURE_PROMPT
    assert "## Contracts" in ARCHITECTURE_PROMPT
    assert "## Implementation slices" in ARCHITECTURE_PROMPT
    assert "do not write production code" in ARCHITECTURE_PROMPT


def test_live_architecture_dispatches_runner(tmp_path) -> None:
    folder = tmp_path / "architecture"
    folder.mkdir()
    (folder / "SPEC.toml").write_text(
        'name = "architecture"\ntitle = "Architecture"\nstatus = "live"\n'
        'when_to_use = "design"\n',
        encoding="utf-8",
    )
    registry = Registry.load(tmp_path, runners={"architecture": lambda brief: f"PACK:{brief}"})
    result = registry.invoke("architecture", "Design a notes API.")
    assert result == "PACK:Design a notes API."
