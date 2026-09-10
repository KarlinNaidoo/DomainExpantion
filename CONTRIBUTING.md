# Contributing

This is Karlin Naidoo's personal agent family. The same rules apply if you are Karlin.

## Setup

```powershell
cd DomainExpantion
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
docker compose up -d
# put XAI_API_KEY in .env when you want to chat
```

```powershell
ruff check .
pytest
domain-expantion db
domain-expantion agents
domain-expantion chat
```

## How to change things

1. Branch from `develop`: `git checkout -b feature/<slug>`
2. Keep the supervisor lightweight unless the PR is explicitly about a specialist.
3. Add or update tests. Registry and tools must stay testable without `XAI_API_KEY`.
4. Open a pull request into `develop`.

See [docs/branching.md](docs/branching.md) and [docs/architecture.md](docs/architecture.md).

## Do not

- Put web/git/trading tools on the supervisor
- Couple runtime to a planet/renderer
- Commit `.env` or API keys
- Impersonate a stub specialist in tests or prompts
