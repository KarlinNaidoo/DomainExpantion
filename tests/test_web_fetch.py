from __future__ import annotations

import pytest

from domain_expantion.specialists.web_fetch import html_to_text, validate_fetch_url


def test_rejects_non_http() -> None:
    with pytest.raises(ValueError, match="http"):
        validate_fetch_url("file:///etc/passwd")


def test_rejects_loopback() -> None:
    with pytest.raises(ValueError, match="Private"):
        validate_fetch_url("http://127.0.0.1/secret")


def test_rejects_localhost() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        validate_fetch_url("https://localhost/docs")


def test_accepts_https() -> None:
    assert validate_fetch_url("https://docs.langchain.com/oss/python/langgraph/interrupts")


def test_html_to_text_drops_scripts() -> None:
    html = "<html><script>alert(1)</script><p>Hello <b>world</b></p></html>"
    text = html_to_text(html)
    assert "alert" not in text
    assert "Hello" in text
    assert "world" in text
