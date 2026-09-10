from __future__ import annotations

import asyncio
import logging
import os
import warnings
from typing import Any

from langchain_core._api.beta_decorator import LangChainBetaWarning

from domain_expantion.specialists.mcp.arxiv_server import server as arxiv_server
from domain_expantion.specialists.mcp.github_server import server as github_server

warnings.filterwarnings("ignore", category=LangChainBetaWarning)
from langchain.mcp import MCPAdapter  # noqa: E402

logger = logging.getLogger(__name__)

_cache: list[Any] | None = None


def github_token() -> str | None:
    return os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or None


async def _list_tools(server: Any, label: str) -> list[Any]:
    try:
        async with MCPAdapter(server) as adapter:
            tools = await adapter.list_tools()
            logger.info("Loaded %s MCP tools from %s", len(tools), label)
            return list(tools)
    except Exception:
        logger.exception("Failed to load MCP server %s", label)
        return []


async def discover_research_mcp_tools() -> list[Any]:
    tools: list[Any] = []
    tools.extend(await _list_tools(arxiv_server, "arxiv"))
    if github_token():
        tools.extend(await _list_tools(github_server, "github"))
    else:
        logger.info("GITHUB_TOKEN not set; skipping GitHub MCP")
    return tools


def load_research_mcp_tools(*, refresh: bool = False) -> list[Any]:
    """Sync helper for the CLI. Cached for the process lifetime."""
    global _cache
    if _cache is not None and not refresh:
        return list(_cache)
    _cache = asyncio.run(discover_research_mcp_tools())
    return list(_cache)


def reset_mcp_tool_cache() -> None:
    global _cache
    _cache = None
