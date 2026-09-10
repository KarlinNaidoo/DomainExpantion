from __future__ import annotations

from types import SimpleNamespace

from domain_expantion.registry import Registry
from domain_expantion.specialists.research import RESEARCH_PROMPT, SERVER_TOOLS, run


class _FakeModel:
    def invoke(self, _messages: object) -> SimpleNamespace:
        return SimpleNamespace(
            content=(
                "LangGraph interrupts pause a graph until a human resumes it. "
                "Source: https://docs.langchain.com/oss/python/langgraph/interrupts"
            )
        )


def test_research_run_uses_injected_model() -> None:
    text = run("What is a LangGraph interrupt?", model=_FakeModel())
    assert "interrupts" in text.lower()
    assert "docs.langchain.com" in text


def test_live_research_dispatches_runner(tmp_path) -> None:
    folder = tmp_path / "research"
    folder.mkdir()
    (folder / "SPEC.toml").write_text(
        'name = "research"\ntitle = "Research"\nstatus = "live"\nwhen_to_use = "facts"\n',
        encoding="utf-8",
    )
    registry = Registry.load(tmp_path, runners={"research": lambda brief: f"RAN:{brief}"})
    result = registry.invoke("research", "Survey interrupts.")
    assert result == "RAN:Survey interrupts."


def test_research_prompt_requires_sources_and_gaps() -> None:
    assert "web_search" in RESEARCH_PROMPT
    assert "fetch_url" in RESEARCH_PROMPT
    assert "search_arxiv" in RESEARCH_PROMPT
    assert "## Sources" in RESEARCH_PROMPT
    assert "## Gaps" in RESEARCH_PROMPT
    assert {"type": "web_search"} in SERVER_TOOLS


def test_live_without_runner_does_not_impersonate(tmp_path) -> None:
    folder = tmp_path / "research"
    folder.mkdir()
    (folder / "SPEC.toml").write_text(
        'name = "research"\ntitle = "Research"\nstatus = "live"\nwhen_to_use = "facts"\n',
        encoding="utf-8",
    )
    registry = Registry.load(tmp_path, runners={})
    result = registry.invoke("research", "Survey interrupts.")
    assert "no runtime" in result.lower()
    assert "Do not impersonate" in result
