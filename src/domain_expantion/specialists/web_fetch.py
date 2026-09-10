from __future__ import annotations

import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx
from langchain.tools import tool

MAX_BYTES = 200_000
TIMEOUT_SECONDS = 15.0
USER_AGENT = "DomainExpantion-research/0.1"
BLOCKED_HOSTS = {"localhost", "metadata.google.internal"}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, _attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = False
        if tag in {"p", "div", "br", "li", "h1", "h2", "h3", "tr"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._chunks.append(data)

    def text(self) -> str:
        raw = "".join(self._chunks)
        return re.sub(r"\n{3,}", "\n\n", raw).strip()


def validate_fetch_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http and https URLs can be fetched.")
    if parsed.username or parsed.password:
        raise ValueError("URLs with credentials are not allowed.")
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        raise ValueError("URL is missing a host.")
    if host in BLOCKED_HOSTS or host.endswith(".localhost"):
        raise ValueError("That host is not allowed.")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None and (
        ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved
    ):
        raise ValueError("Private or local addresses are not allowed.")
    return url


def _assert_resolved_public(host: str) -> None:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve host: {host}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise ValueError("Private or local addresses are not allowed.")


def html_to_text(html: str) -> str:
    extractor = _TextExtractor()
    extractor.feed(html)
    extractor.close()
    return extractor.text()


def fetch_url_text(url: str) -> str:
    checked = validate_fetch_url(url)
    host = urlparse(checked).hostname
    if host:
        _assert_resolved_public(host)
    with httpx.Client(
        timeout=TIMEOUT_SECONDS,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
        max_redirects=3,
    ) as client:
        response = client.get(checked)
        final = str(response.url)
        validate_fetch_url(final)
        final_host = urlparse(final).hostname
        if final_host:
            _assert_resolved_public(final_host)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        body = response.content[:MAX_BYTES]
        text = body.decode(response.encoding or "utf-8", errors="replace")
        looks_html = "html" in content_type.lower() or text.lstrip()[:15].lower().startswith(
            "<!doctype html"
        )
        if looks_html:
            text = html_to_text(text)
        if len(response.content) > MAX_BYTES:
            text += "\n\n[truncated]"
        return text or "(empty page)"


@tool
def fetch_url(url: str) -> str:
    """Fetch a public http(s) URL and return readable text. Use after search to read a source."""
    try:
        return fetch_url_text(url)
    except Exception as exc:
        return f"Could not fetch {url}: {exc}"
