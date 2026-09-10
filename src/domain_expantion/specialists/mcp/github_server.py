from __future__ import annotations

import base64
import os

import httpx
from fastmcp import FastMCP

API = "https://api.github.com"
USER_AGENT = "DomainExpantion-research/0.1"

server = FastMCP("github")


def _headers() -> dict[str, str]:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or ""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get(path: str, params: dict[str, str] | None = None) -> httpx.Response:
    with httpx.Client(timeout=20.0, headers=_headers()) as client:
        response = client.get(f"{API}{path}", params=params)
        return response


@server.tool
def github_search_repos(query: str, max_results: int = 5) -> str:
    """Search public GitHub repositories. Read-only."""
    limit = max(1, min(max_results, 10))
    response = _get("/search/repositories", {"q": query, "per_page": str(limit)})
    if response.status_code >= 400:
        return f"GitHub search failed ({response.status_code}): {response.text[:300]}"
    items = response.json().get("items", [])
    if not items:
        return f"No GitHub repositories for: {query}"
    lines = []
    for item in items:
        lines.append(
            f"{item.get('full_name')} — {item.get('html_url')}\n"
            f"stars: {item.get('stargazers_count')}  "
            f"desc: {item.get('description') or ''}"
        )
    return "\n\n".join(lines)


@server.tool
def github_get_repo(owner: str, repo: str) -> str:
    """Get metadata for a public GitHub repository. Read-only."""
    response = _get(f"/repos/{owner}/{repo}")
    if response.status_code >= 400:
        return f"GitHub repo lookup failed ({response.status_code}): {response.text[:300]}"
    data = response.json()
    return (
        f"{data.get('full_name')} — {data.get('html_url')}\n"
        f"description: {data.get('description') or ''}\n"
        f"stars: {data.get('stargazers_count')}  forks: {data.get('forks_count')}\n"
        f"default_branch: {data.get('default_branch')}  language: {data.get('language')}\n"
        f"topics: {', '.join(data.get('topics') or [])}"
    )


@server.tool
def github_get_file(owner: str, repo: str, path: str, ref: str = "") -> str:
    """Read a file from a public GitHub repo (README, source). Read-only. Max ~100KB."""
    params = {"ref": ref} if ref.strip() else None
    response = _get(f"/repos/{owner}/{repo}/contents/{path.lstrip('/')}", params)
    if response.status_code >= 400:
        return f"GitHub file lookup failed ({response.status_code}): {response.text[:300]}"
    data = response.json()
    if isinstance(data, list):
        names = [item.get("path") or item.get("name") for item in data[:50]]
        return "Directory listing:\n" + "\n".join(str(n) for n in names)
    encoding = data.get("encoding")
    if encoding == "base64" and data.get("content"):
        raw = base64.b64decode(data["content"])
        text = raw[:100_000].decode("utf-8", errors="replace")
        if len(raw) > 100_000:
            text += "\n\n[truncated]"
        return f"{data.get('html_url')}\n\n{text}"
    return data.get("html_url") or str(data)[:500]
