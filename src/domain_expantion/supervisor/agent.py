from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware, ModelRetryMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from domain_expantion.config import Settings
from domain_expantion.llm import build_model
from domain_expantion.supervisor.prompt import SUPERVISOR_PROMPT
from domain_expantion.supervisor.tools import delegate, list_agents


def build_supervisor(
    settings: Settings | None = None,
    *,
    checkpointer: InMemorySaver | None = None,
) -> Any:
    settings = settings or Settings.from_env()
    return create_agent(
        model=build_model(settings),
        tools=[list_agents, delegate],
        system_prompt=SUPERVISOR_PROMPT,
        checkpointer=checkpointer or InMemorySaver(),
        middleware=[
            ModelCallLimitMiddleware(run_limit=settings.run_limit, exit_behavior="end"),
            ModelRetryMiddleware(max_retries=2),
        ],
        name="supervisor",
    )
