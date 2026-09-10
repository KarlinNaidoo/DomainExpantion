from __future__ import annotations

from typing import Any

from langchain.messages import HumanMessage, SystemMessage

from domain_expantion.config import Settings
from domain_expantion.llm import build_model
from domain_expantion.messages import message_text

RESEARCH_PROMPT = """You are Karli's research specialist for Domain Expantion.

You look up facts on the web and return a briefing. You do not talk to Karli.
You do not decide what Karli should do. You do not write or patch code.

Use web search when the brief needs current or sourced information.
Cite sources with titles and URLs when you used the web.
If you cannot find something, say so. Do not invent sources.

Put the full briefing in your final message. Keep it tight.
"""

WEB_SEARCH_TOOL = {"type": "web_search"}


def run(brief: str, *, settings: Settings | None = None, model: Any | None = None) -> str:
    """Run one research job. The worker only sees `brief`."""
    llm = model or build_model(settings or Settings.from_env()).bind_tools([WEB_SEARCH_TOOL])
    result = llm.invoke(
        [
            SystemMessage(content=RESEARCH_PROMPT),
            HumanMessage(content=brief),
        ]
    )
    text = message_text(result).strip()
    if not text:
        return (
            "Research specialist returned an empty briefing. "
            "Ask the supervisor to send a narrower brief."
        )
    return text
