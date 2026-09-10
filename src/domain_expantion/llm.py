from __future__ import annotations

from langchain_xai import ChatXAI

from domain_expantion.config import XAI_BASE_URL, Settings


def build_model(settings: Settings) -> ChatXAI:
    return ChatXAI(
        model=settings.model,
        api_key=settings.require_api_key(),
        base_url=XAI_BASE_URL,
        temperature=0,
    )
