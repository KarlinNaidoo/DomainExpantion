from __future__ import annotations

from pathlib import Path

import pytest

from domain_expantion.registry import Registry, set_registry


@pytest.fixture
def family_root(tmp_path: Path) -> Path:
    research = tmp_path / "research"
    research.mkdir()
    (research / "SPEC.toml").write_text(
        """
name = "research"
title = "Research specialist"
status = "stub"
description = "Looks up facts."
when_to_use = "When facts are missing."
""".strip()
        + "\n",
        encoding="utf-8",
    )
    code = tmp_path / "code"
    code.mkdir()
    (code / "SPEC.toml").write_text(
        """
name = "code"
title = "Code specialist"
status = "stub"
description = "Works in repos."
when_to_use = "When the work is source code."
""".strip()
        + "\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def registry(family_root: Path) -> Registry:
    loaded = Registry.load(family_root)
    set_registry(loaded)
    yield loaded
    set_registry(None)
