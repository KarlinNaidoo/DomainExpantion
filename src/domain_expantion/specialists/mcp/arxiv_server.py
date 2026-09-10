from __future__ import annotations

import arxiv
from fastmcp import FastMCP

server = FastMCP("arxiv")


def _format_result(paper: arxiv.Result) -> str:
    authors = ", ".join(a.name for a in paper.authors[:8])
    if len(paper.authors) > 8:
        authors += ", …"
    published = paper.published.date().isoformat() if paper.published else "unknown"
    summary = " ".join(paper.summary.split())
    if len(summary) > 800:
        summary = summary[:797] + "…"
    return (
        f"id: {paper.entry_id}\n"
        f"title: {paper.title}\n"
        f"authors: {authors}\n"
        f"published: {published}\n"
        f"url: {paper.entry_id}\n"
        f"pdf: {paper.pdf_url}\n"
        f"summary: {summary}"
    )


def search_arxiv_text(query: str, max_results: int = 5) -> str:
    limit = max(1, min(max_results, 10))
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=limit, sort_by=arxiv.SortCriterion.Relevance)
    papers = list(client.results(search))
    if not papers:
        return f"No arXiv results for: {query}"
    return "\n\n".join(_format_result(paper) for paper in papers)


def get_arxiv_paper_text(arxiv_id: str) -> str:
    cleaned = arxiv_id.strip().removeprefix("arXiv:").removeprefix("arxiv:")
    client = arxiv.Client()
    search = arxiv.Search(id_list=[cleaned])
    papers = list(client.results(search))
    if not papers:
        return f"No arXiv paper found for id: {arxiv_id}"
    return _format_result(papers[0])


@server.tool
def search_arxiv(query: str, max_results: int = 5) -> str:
    """Search arXiv for papers. Use for scholarly / preprint literature."""
    return search_arxiv_text(query, max_results)


@server.tool
def get_arxiv_paper(arxiv_id: str) -> str:
    """Fetch one arXiv paper by id (e.g. 1706.03762 or arXiv:1706.03762)."""
    return get_arxiv_paper_text(arxiv_id)
