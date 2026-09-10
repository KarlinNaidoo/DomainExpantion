from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ModelRetryMiddleware

from domain_expantion.config import Settings
from domain_expantion.llm import build_model
from domain_expantion.messages import message_text
from domain_expantion.specialists.web_fetch import fetch_url

RESEARCH_PROMPT = """You are Karli's research specialist for Domain Expantion.

You look up facts and return a briefing. You do not talk to Karli.
You do not decide what Karli should do. You do not write or patch code.

Tools:
- web_search: current web pages and docs (default). xAI runs this server-side and can browse hits.
- fetch_url: read one public http(s) page when you already have a URL.

Prefer primary sources. If sources disagree, say so.
If you cannot find something, say so. Do not invent URLs or quotes.

Put the full briefing in your final message using this shape:

## Findings
(tight bullets or short paragraphs)

## Sources
- Title — URL

## Confidence
high | medium | low

## Gaps
what is still unknown or unverified
"""

SERVER_TOOLS = [{"type": "web_search"}]


def build_research_agent(settings: Settings | None = None) -> Any:
    settings = settings or Settings.from_env()
    model = build_model(settings).bind_tools(SERVER_TOOLS)
    return create_agent(
        model=model,
        tools=[fetch_url],
        system_prompt=RESEARCH_PROMPT,
        middleware=[
            ModelCallLimitMiddleware(
                run_limit=settings.research_run_limit,
                exit_behavior="end",
            ),
            ModelRetryMiddleware(max_retries=2),
        ],
        name="research",
    )


def run(
    brief: str,
    *,
    settings: Settings | None = None,
    model: Any | None = None,
    agent: Any | None = None,
) -> str:
    """Run one research job. The worker only sees `brief`."""
    if agent is not None:
        result = agent.invoke({"messages": [{"role": "user", "content": brief}]})
        messages = result["messages"] if isinstance(result, dict) else [result]
        text = message_text(messages[-1]).strip()
    elif model is not None:
        result = model.invoke(
            [
                {"role": "system", "content": RESEARCH_PROMPT},
                {"role": "user", "content": brief},
            ]
        )
        text = message_text(result).strip()
    else:
        result = build_research_agent(settings).invoke(
            {"messages": [{"role": "user", "content": brief}]}
        )
        text = message_text(result["messages"][-1]).strip()
    if not text:
        return (
            "Research specialist returned an empty briefing. "
            "Ask the supervisor to send a narrower brief."
        )
    return text
