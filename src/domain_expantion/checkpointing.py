from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from langgraph.checkpoint.postgres import PostgresSaver

from domain_expantion.config import Settings


@contextmanager
def open_checkpointer(settings: Settings | None = None) -> Iterator[Any]:
    settings = settings or Settings.from_env()
    uri = settings.require_database_url()
    try:
        with PostgresSaver.from_conn_string(uri) as saver:
            saver.setup()
            yield saver
    except Exception as exc:
        raise RuntimeError(
            "Could not open the Postgres checkpointer. "
            "Start it with: docker compose up -d\n"
            f"DATABASE_URL={uri}\n{exc}"
        ) from exc
