# Domain Expantion

Personal AI agent family. A lightweight **supervisor** talks to you and delegates to specialists as they come online.

The planet (if we build one later) is only a visual of this family. Agents do not live in it.

**Repo:** [github.com/KarlinNaidoo/DomainExpantion](https://github.com/KarlinNaidoo/DomainExpantion)

## v0 — what exists

- Supervisor on Grok (`grok-4.6` via SpaceXAI / xAI)
- Two tools: `list_agents`, `delegate`
- Family registry on disk (`family/*/SPEC.toml`)
- Stub specialists: `research`, `code` (registered, not live)
- CLI: `domain-expantion agents` and `domain-expantion chat` (tool calls stream as they happen)
- Loop guard (max model calls per turn)
- Postgres checkpointer via Docker Compose (threads survive restart)

The supervisor can already converse, refuse to impersonate missing workers, and show the brief it *would* have sent.

## Setup

```powershell
git clone https://github.com/KarlinNaidoo/DomainExpantion.git
cd DomainExpantion
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
```

Put `XAI_API_KEY` in `.env` (https://console.x.ai). Then:

```powershell
docker compose up -d
pytest
domain-expantion db
domain-expantion agents
domain-expantion chat
```

`db` and `agents` do not need `XAI_API_KEY`. `chat` does. Threads persist in Postgres (host port **5433**).

## Layout

```
family/                 # specialist specs (source of truth)
src/domain_expantion/
  supervisor/           # prompt, tools, harness
  registry.py           # load specs, stub invoke
  cli.py
docs/                   # architecture, branching, roadmap
```

## Branching

`main` is stable. `develop` is integration. Features go on `feature/<slug>` and merge to `develop` by PR.

Details: [docs/branching.md](docs/branching.md) · architecture: [docs/architecture.md](docs/architecture.md) · plan: [docs/ROADMAP.md](docs/ROADMAP.md)
