from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace

from domain_expantion.specialists.mcp.arxiv_server import search_arxiv_text
from domain_expantion.specialists.mcp.arxiv_server import server as arxiv_server
from domain_expantion.specialists.mcp.github_server import server as github_server
from domain_expantion.specialists.mcp.loader import _list_tools, as_sync_tool
from domain_expantion.specialists.research import RESEARCH_PROMPT


def test_research_prompt_mentions_mcp_apis() -> None:
    assert "search_arxiv" in RESEARCH_PROMPT
    assert "github_search_repos" in RESEARCH_PROMPT
    assert "web_search" in RESEARCH_PROMPT


def test_async_mcp_tool_can_run_sync() -> None:
    from pydantic import BaseModel

    class PingIn(BaseModel):
        q: str = ""

    class Fake:
        name = "ping"
        description = "ping the fake tool"
        args_schema = PingIn

        async def ainvoke(self, payload, config=None):
            return f"pong:{payload}"

    tool = as_sync_tool(Fake())
    result = tool.invoke({"q": "hi"})
    assert "pong:" in result
    assert "hi" in result


def test_arxiv_mcp_lists_search_tools() -> None:
    tools = asyncio.run(_list_tools(arxiv_server, "arxiv"))
    names = {tool.name for tool in tools}
    assert "search_arxiv" in names
    assert "get_arxiv_paper" in names


def test_github_mcp_lists_read_only_tools() -> None:
    tools = asyncio.run(_list_tools(github_server, "github"))
    names = {tool.name for tool in tools}
    assert "github_search_repos" in names
    assert "github_get_repo" in names
    assert "github_get_file" in names
    assert not any("create" in name or "push" in name for name in names)


def test_search_arxiv_text_formats_results(monkeypatch) -> None:
    paper = SimpleNamespace(
        entry_id="http://arxiv.org/abs/1706.03762",
        title="Attention Is All You Need",
        authors=[SimpleNamespace(name="Ashish Vaswani")],
        published=datetime(2017, 6, 12, tzinfo=UTC),
        summary="The dominant sequence transduction models are based on complex RNNs.",
        pdf_url="http://arxiv.org/pdf/1706.03762",
    )

    class FakeClient:
        def results(self, _search):
            return [paper]

    monkeypatch.setattr(
        "domain_expantion.specialists.mcp.arxiv_server.arxiv.Client",
        FakeClient,
    )
    text = search_arxiv_text("transformer")
    assert "Attention Is All You Need" in text
    assert "1706.03762" in text
