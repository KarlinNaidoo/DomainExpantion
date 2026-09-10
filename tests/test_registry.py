from __future__ import annotations

from pathlib import Path

import pytest

from domain_expantion.registry import Registry, UnknownAgentError


def test_load_skips_underscore_templates(tmp_path: Path) -> None:
    template = tmp_path / "_template"
    template.mkdir()
    (template / "SPEC.toml").write_text(
        'name = "example"\nstatus = "planned"\n',
        encoding="utf-8",
    )
    live = tmp_path / "research"
    live.mkdir()
    (live / "SPEC.toml").write_text(
        'name = "research"\ntitle = "Research"\nstatus = "stub"\nwhen_to_use = "facts"\n',
        encoding="utf-8",
    )
    registry = Registry.load(tmp_path)
    assert [spec.name for spec in registry.list_specs()] == ["research"]


def test_unknown_agent(registry: Registry) -> None:
    with pytest.raises(UnknownAgentError):
        registry.get("cooking")


def test_stub_delegate_echoes_brief(registry: Registry) -> None:
    result = registry.invoke("research", "Survey LangGraph supervisor patterns.")
    assert "STUB" in result
    assert "Survey LangGraph supervisor patterns." in result
    assert "not live" in result


def test_empty_brief_is_rejected(registry: Registry) -> None:
    result = registry.invoke("code", "   ")
    assert "empty brief" in result


def test_catalog_lists_stubs(registry: Registry) -> None:
    catalog = registry.render_catalog()
    assert "research (stub)" in catalog
    assert "code (stub)" in catalog
    assert "must not be impersonated" in catalog
