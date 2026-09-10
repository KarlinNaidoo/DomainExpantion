from __future__ import annotations

from types import SimpleNamespace

from domain_expantion.messages import message_text


def test_plain_content() -> None:
    assert message_text(SimpleNamespace(content="hello")) == "hello"


def test_text_blocks() -> None:
    message = SimpleNamespace(
        content=[{"type": "text", "text": "one"}, {"type": "text", "text": "two"}]
    )
    assert message_text(message) == "onetwo"
