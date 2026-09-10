from __future__ import annotations

import argparse
import uuid
from typing import Any

from domain_expantion import __version__
from domain_expantion.config import Settings
from domain_expantion.registry import Registry, get_registry, set_registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="domain-expantion",
        description="Karli's supervisor for the Domain Expantion agent family.",
    )
    parser.add_argument("--version", action="version", version=f"domain-expantion {__version__}")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("agents", help="Print the family catalog (no LLM).")
    sub.add_parser("db", help="Create checkpoint tables and verify Postgres (no LLM).")
    chat = sub.add_parser("chat", help="Talk to the supervisor.")
    chat.add_argument("--thread", default="local-default", help="Conversation thread id.")

    args = parser.parse_args(argv)
    if args.command == "agents":
        return cmd_agents()
    if args.command == "db":
        return cmd_db()
    if args.command == "chat":
        return cmd_chat(args.thread)
    parser.print_help()
    return 0


def cmd_agents() -> int:
    set_registry(Registry.load())
    print(get_registry().render_catalog())
    return 0


def _chat_turn(agent: Any, user: str, config: dict[str, Any]) -> None:
    from domain_expantion.supervisor.stream import render_turn

    chunks = agent.stream(
        {"messages": [{"role": "user", "content": user}]},
        config,
        stream_mode="updates",
    )
    reply = render_turn(chunks)
    if not reply:
        print("Supervisor: (no reply)")


def cmd_db() -> int:
    from domain_expantion.checkpointing import open_checkpointer

    settings = Settings.from_env()
    with open_checkpointer(settings):
        print(f"Postgres checkpointer ready. {settings.database_url}")
    return 0


def cmd_chat(thread_id: str) -> int:
    from domain_expantion.checkpointing import open_checkpointer
    from domain_expantion.supervisor.agent import build_supervisor

    set_registry(Registry.load())
    settings = Settings.from_env()
    config: dict[str, Any] = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}

    print(f"Domain Expantion supervisor v{__version__}")
    print(f"Model: {settings.model}  thread: {config['configurable']['thread_id']}")
    print("Checkpointer: postgres")
    print("Type a message. /quit to exit. /agents to print the catalog.")
    print("Tool calls stream as they happen.")
    print()

    with open_checkpointer(settings) as checkpointer:
        agent = build_supervisor(settings, checkpointer=checkpointer)
        while True:
            try:
                user = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                return 0
            if not user:
                continue
            if user in {"/quit", "/exit"}:
                print("Bye.")
                return 0
            if user == "/agents":
                print(get_registry().render_catalog())
                continue

            _chat_turn(agent, user, config)
            print()
    return 0
