from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Literal

from domain_expantion.messages import message_text

RESULT_LIMIT = 1200

EventKind = Literal["tool_call", "tool_result", "reply"]


@dataclass(frozen=True)
class StreamEvent:
    kind: EventKind
    name: str = ""
    args: dict[str, Any] | None = None
    text: str = ""


def events_from_update(chunk: Any) -> list[StreamEvent]:
    if not isinstance(chunk, dict):
        return []
    events: list[StreamEvent] = []
    for data in chunk.values():
        if not isinstance(data, dict):
            continue
        raw = data.get("messages", [])
        if raw is None:
            continue
        messages = raw if isinstance(raw, list) else [raw]
        for message in messages:
            events.extend(_events_from_message(message))
    return events


def format_event(event: StreamEvent) -> str:
    if event.kind == "tool_call":
        lines = [f"  → {event.name}"]
        for key, value in (event.args or {}).items():
            rendered = _one_line(value)
            lines.append(f"      {key}: {rendered}")
        return "\n".join(lines)
    if event.kind == "tool_result":
        body = _truncate(event.text.strip() or "(empty)")
        indented = "\n".join(f"      {line}" for line in body.splitlines())
        label = event.name or "tool"
        return f"  ← {label}\n{indented}"
    return f"Supervisor: {event.text}"


def render_turn(chunks: Iterator[Any]) -> str:
    """Consume graph update chunks. Returns the last supervisor reply text."""
    reply = ""
    for chunk in chunks:
        for event in events_from_update(chunk):
            print(format_event(event), flush=True)
            if event.kind == "reply":
                reply = event.text
    return reply


def _events_from_message(message: Any) -> list[StreamEvent]:
    msg_type = getattr(message, "type", None) or type(message).__name__.lower()
    if msg_type in {"human", "system"}:
        return []

    events: list[StreamEvent] = []
    tool_calls = getattr(message, "tool_calls", None) or []
    for call in tool_calls:
        if isinstance(call, dict):
            name = str(call.get("name") or "tool")
            args = call.get("args") if isinstance(call.get("args"), dict) else {}
        else:
            name = str(getattr(call, "name", "tool"))
            raw_args = getattr(call, "args", {})
            args = raw_args if isinstance(raw_args, dict) else {}
        events.append(StreamEvent(kind="tool_call", name=name, args=args))

    if msg_type in {"tool", "toolmessage"}:
        name = str(getattr(message, "name", "") or getattr(message, "tool_call_id", "") or "tool")
        events.append(StreamEvent(kind="tool_result", name=name, text=message_text(message)))
        return events

    text = message_text(message).strip()
    if text and not tool_calls:
        events.append(StreamEvent(kind="reply", text=text))
    return events


def _one_line(value: Any) -> str:
    text = value if isinstance(value, str) else str(value)
    collapsed = " ".join(text.split())
    return _truncate(collapsed, limit=240)


def _truncate(text: str, limit: int = RESULT_LIMIT) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"
