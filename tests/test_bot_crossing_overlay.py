from __future__ import annotations

from pathlib import Path

OVERLAY = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "domain_expantion"
    / "planet"
    / "bot_crossing"
    / "index.mjs"
)


def test_overlay_registers_only_domain_expantion() -> None:
    text = OVERLAY.read_text(encoding="utf-8")
    assert "domain-expantion" in text
    assert "claude-code" not in text
    assert "cursor" not in text
    assert "codex" not in text
    assert "HARNESSES = [domainExpantion]" in text
