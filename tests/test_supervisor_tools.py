from __future__ import annotations

from domain_expantion.supervisor.prompt import SUPERVISOR_PROMPT
from domain_expantion.supervisor.tools import delegate, list_agents


def test_list_agents_tool(registry) -> None:
    text = list_agents.invoke({})
    assert "research" in text
    assert "code" in text


def test_delegate_unknown(registry) -> None:
    text = delegate.invoke({"agent_name": "cooking", "brief": "Make soup."})
    assert "Unknown specialist" in text


def test_delegate_stub(registry) -> None:
    text = delegate.invoke(
        {"agent_name": "Research", "brief": "What is a LangGraph interrupt?"}
    )
    assert "STUB" in text
    assert "LangGraph interrupt" in text


def test_prompt_is_policy_not_encyclopedia() -> None:
    assert "list_agents" in SUPERVISOR_PROMPT
    assert "delegate" in SUPERVISOR_PROMPT
    assert "Do not impersonate" in SUPERVISOR_PROMPT
    assert "If a live specialist fits, delegate" in SUPERVISOR_PROMPT
    assert "architecture" in SUPERVISOR_PROMPT
    assert "`code` is still a stub" in SUPERVISOR_PROMPT
    assert "dangerous or irreversible" in SUPERVISOR_PROMPT
