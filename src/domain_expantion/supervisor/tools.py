from __future__ import annotations

from langchain.tools import tool

from domain_expantion.registry import get_registry


@tool
def list_agents() -> str:
    """List specialists in the family and when to use each one."""
    return get_registry().render_catalog()


@tool
def delegate(agent_name: str, brief: str) -> str:
    """Assign a self-contained task to a specialist.

    The worker only sees this brief, not the rest of the conversation.
    Use a complete ticket: goal, constraints, and what done looks like.
    """
    return get_registry().invoke(agent_name, brief)
