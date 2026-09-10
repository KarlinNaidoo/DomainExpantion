from __future__ import annotations

import pytest

from domain_expantion.config import DEFAULT_DATABASE_URL, Settings


def test_default_database_url_targets_compose_port() -> None:
    settings = Settings(
        xai_api_key=None,
        model="grok-4.6",
        run_limit=8,
        research_run_limit=6,
        architecture_run_limit=8,
        database_url=DEFAULT_DATABASE_URL,
    )
    assert ":5433/" in settings.database_url
    assert "domain_expantion" in settings.database_url


def test_empty_database_url_is_rejected() -> None:
    settings = Settings(
        xai_api_key=None,
        model="grok-4.6",
        run_limit=8,
        research_run_limit=6,
        architecture_run_limit=8,
        database_url="  ",
    )
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        settings.require_database_url()
