from __future__ import annotations

from langchain.messages import AIMessage, HumanMessage, ToolMessage

from domain_expantion.supervisor.stream import events_from_update, format_event, render_turn


def test_skips_human_messages() -> None:
    chunk = {"model": {"messages": [HumanMessage(content="hello")]}}
    assert events_from_update(chunk) == []


def test_tool_call_and_result() -> None:
    model = {
        "model": {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "delegate",
                            "args": {
                                "agent_name": "research",
                                "brief": "Survey LangGraph interrupts.",
                            },
                            "id": "call-1",
                            "type": "tool_call",
                        }
                    ],
                )
            ]
        }
    }
    tools = {
        "tools": {
            "messages": [
                ToolMessage(
                    content="STUB: specialist 'research' is registered but not live yet.",
                    tool_call_id="call-1",
                    name="delegate",
                )
            ]
        }
    }
    reply = {
        "model": {
            "messages": [
                AIMessage(content="Research is a stub. Here is the brief I would have sent.")
            ]
        }
    }

    call = events_from_update(model)
    assert len(call) == 1
    assert call[0].kind == "tool_call"
    assert call[0].name == "delegate"
    assert call[0].args is not None
    assert call[0].args["agent_name"] == "research"

    result = events_from_update(tools)
    assert result[0].kind == "tool_result"
    assert "STUB" in result[0].text

    final = events_from_update(reply)
    assert final[0].kind == "reply"
    assert "stub" in final[0].text.lower()


def test_format_shows_brief() -> None:
    events = events_from_update(
        {
            "model": {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": "delegate",
                                "args": {"agent_name": "code", "brief": "Patch the CLI."},
                                "id": "c1",
                                "type": "tool_call",
                            }
                        ],
                    )
                ]
            }
        }
    )
    rendered = format_event(events[0])
    assert "→ delegate" in rendered
    assert "agent_name: code" in rendered
    assert "brief: Patch the CLI." in rendered


def test_render_turn_prints_steps(capsys) -> None:
    chunks = [
        {
            "model": {
                "messages": [
                    AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": "list_agents",
                                "args": {},
                                "id": "c1",
                                "type": "tool_call",
                            }
                        ],
                    )
                ]
            }
        },
        {
            "tools": {
                "messages": [
                    ToolMessage(
                        content="Registered specialists: research",
                        tool_call_id="c1",
                        name="list_agents",
                    )
                ]
            }
        },
        {"model": {"messages": [AIMessage(content="Family has stubs only.")]}},
    ]
    reply = render_turn(iter(chunks))
    out = capsys.readouterr().out
    assert "→ list_agents" in out
    assert "← list_agents" in out
    assert "Supervisor: Family has stubs only." in out
    assert reply == "Family has stubs only."
