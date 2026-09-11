from __future__ import annotations

from domain_expantion.planet.chats import list_chats, record_chat


def test_record_and_list_chats(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    record_chat("colony-main", agent="supervisor", preview="What is the new BMW concept?")
    record_chat("colony-research", agent="research", preview="Follow up")
    chats = list_chats()
    assert chats[0]["thread_id"] == "colony-research"
    assert "BMW" in chats[1]["preview"]
