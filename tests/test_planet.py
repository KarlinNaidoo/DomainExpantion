from __future__ import annotations

import json
from threading import Thread
from urllib.request import urlopen

from domain_expantion.planet.server import serve_planet
from domain_expantion.planet.state import family_payload
from domain_expantion.registry import Registry


def test_planet_payload_includes_supervisor_and_specs(tmp_path) -> None:
    folder = tmp_path / "research"
    folder.mkdir()
    (folder / "SPEC.toml").write_text(
        'name = "research"\ntitle = "Research"\nstatus = "live"\n'
        'description = "Facts."\nwhen_to_use = "facts"\n',
        encoding="utf-8",
    )
    registry = Registry.load(tmp_path, runners={})
    payload = family_payload(registry)
    names = [item["name"] for item in payload["inhabitants"]]
    assert names[0] == "supervisor"
    assert "research" in names
    assert payload["note"].startswith("Visual only")
    research = next(item for item in payload["inhabitants"] if item["name"] == "research")
    assert research["status"] == "live"
    assert research["run_state"] == "idle"


def test_family_snapshot_is_written(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    from domain_expantion.planet.state import snapshot_path, write_family_snapshot
    from domain_expantion.registry import Registry

    folder = tmp_path / "code"
    folder.mkdir()
    (folder / "SPEC.toml").write_text(
        'name = "code"\ntitle = "Code"\nstatus = "stub"\nwhen_to_use = "code"\n',
        encoding="utf-8",
    )
    path = write_family_snapshot(Registry.load(tmp_path, runners={}))
    assert path == snapshot_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert any(item["name"] == "code" for item in data["inhabitants"])


def test_activity_roundtrip(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    from domain_expantion.planet.activity import load_activity, set_activity

    set_activity("architecture", "working", "Design a site")
    data = load_activity()
    assert data["architecture"]["state"] == "working"
    assert "Design" in data["architecture"]["detail"]


def test_planet_http_serves_family_json() -> None:
    httpd = serve_planet("127.0.0.1", 0)
    port = httpd.server_address[1]
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urlopen(f"http://127.0.0.1:{port}/api/family") as resp:
            data = json.load(resp)
        names = [item["name"] for item in data["inhabitants"]]
        assert "supervisor" in names
        assert "architecture" in names
    finally:
        httpd.shutdown()
        httpd.server_close()
