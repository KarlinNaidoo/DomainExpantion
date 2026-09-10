from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "grok-4.6"
DEFAULT_RUN_LIMIT = 8
XAI_BASE_URL = "https://api.x.ai/v1"


def family_dir() -> Path:
    env = os.getenv("DOMAIN_EXPANTION_FAMILY")
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        candidate = parent / "family"
        if candidate.is_dir():
            return candidate
    return Path.cwd() / "family"


@dataclass(frozen=True)
class Settings:
    xai_api_key: str | None
    model: str
    run_limit: int

    @classmethod
    def from_env(cls) -> Settings:
        raw_limit = os.getenv("SUPERVISOR_RUN_LIMIT", str(DEFAULT_RUN_LIMIT))
        try:
            run_limit = int(raw_limit)
        except ValueError:
            run_limit = DEFAULT_RUN_LIMIT
        return cls(
            xai_api_key=os.getenv("XAI_API_KEY") or None,
            model=os.getenv("XAI_MODEL", DEFAULT_MODEL),
            run_limit=max(1, run_limit),
        )

    def require_api_key(self) -> str:
        if not self.xai_api_key:
            raise RuntimeError(
                "XAI_API_KEY is not set. Copy .env.example to .env and add a key from https://console.x.ai"
            )
        return self.xai_api_key
