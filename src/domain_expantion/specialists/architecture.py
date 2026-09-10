from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ModelRetryMiddleware

from domain_expantion.config import Settings
from domain_expantion.llm import build_model
from domain_expantion.messages import message_text
from domain_expantion.specialists.web_fetch import fetch_url

ARCHITECTURE_PROMPT = """You are Karli's architecture specialist for Domain Expantion.

You design. You do not talk to Karli. You do not write production code, tests, or patches.
The `code` specialist will implement your pack later. Make it concrete enough to code
end to end without guessing.

Draw with Mermaid only (C4 context/container, sequence, ER as needed). No images.

Tools:
- web_search: patterns, vendor docs, existing public systems.
- fetch_url: read a public spec or doc you have a URL for.
- GitHub MCP (if loaded): inspect an existing public repo. Read-only.

If facts are missing, state them under Open questions. Do not invent APIs, schemas, or SLAs.

Put the full pack in your final message using this shape:

## Intent
problem, users, success

## Constraints
must / must-not, stack if known, compliance, scale

## Context
C4 context and container in Mermaid. Actors and systems.

## Decisions
ADRs: title, status (proposed), context, decision, consequences

## Contracts
APIs, events, and data shapes the code agent will implement
(OpenAPI-like or typed sketches)

## Runtime
processes, stores, auth, failure modes

## Implementation slices
ordered backlog for `code`: slice name, files/modules, acceptance
Each slice must be independently shippable if possible.

## Open questions
what Karli or research must still answer
"""

SERVER_TOOLS = [{"type": "web_search"}]


def build_architecture_agent(
    settings: Settings | None = None,
    extra_tools: list[Any] | None = None,
) -> Any:
    settings = settings or Settings.from_env()
    model = build_model(settings).bind_tools(SERVER_TOOLS)
    from domain_expantion.specialists.mcp.loader import load_research_mcp_tools

    mcp_tools = extra_tools if extra_tools is not None else load_research_mcp_tools()
    prompt = ARCHITECTURE_PROMPT
    if mcp_tools:
        names = ", ".join(getattr(tool, "name", "tool") for tool in mcp_tools)
        prompt += f"\nMCP tools currently loaded: {names}\n"
    return create_agent(
        model=model,
        tools=[fetch_url, *mcp_tools],
        system_prompt=prompt,
        middleware=[
            ModelCallLimitMiddleware(
                run_limit=settings.architecture_run_limit,
                exit_behavior="end",
            ),
            ModelRetryMiddleware(max_retries=2),
        ],
        name="architecture",
    )


def run(
    brief: str,
    *,
    settings: Settings | None = None,
    model: Any | None = None,
    agent: Any | None = None,
) -> str:
    """Run one architecture job. The worker only sees `brief`."""
    if agent is not None:
        result = agent.invoke({"messages": [{"role": "user", "content": brief}]})
        messages = result["messages"] if isinstance(result, dict) else [result]
        text = message_text(messages[-1]).strip()
    elif model is not None:
        result = model.invoke(
            [
                {"role": "system", "content": ARCHITECTURE_PROMPT},
                {"role": "user", "content": brief},
            ]
        )
        text = message_text(result).strip()
    else:
        result = build_architecture_agent(settings).invoke(
            {"messages": [{"role": "user", "content": brief}]}
        )
        text = message_text(result["messages"][-1]).strip()
    if not text:
        return (
            "Architecture specialist returned an empty pack. "
            "Ask the supervisor to send a narrower brief."
        )
    return text
