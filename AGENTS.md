# Agent instructions (this repo)

- The supervisor is the only agent that talks to Karli.
- Specialists are registered in `family/<name>/SPEC.toml`. Folder name must match `name`. Folders starting with `_` are templates, not agents.
- `status = "stub"` means `delegate` must return a stub payload. Never fake the specialist's job.
- `research` is live. It may use xAI `web_search`, `fetch_url`, arXiv MCP, and GitHub MCP (read-only, token optional). Do not add those tools to the supervisor. `fetch_url` is public http(s) only. GitHub MCP must not create issues, PRs, or pushes.
- `architecture` is live. It produces an implementation pack (Mermaid, ADRs, contracts, slices) for `code`. It must not write production code. Draw in Mermaid only.
- Do not add MCP or domain tools to the supervisor. Attach them to a specialist later.
- The planet is Bot Crossing (vendored) plus a Domain Expantion harness adapter. It must not start agents. Working state is `.data/planet-activity.json` / `planet-family.json`.
- Models go through SpaceXAI / xAI (`XAI_API_KEY`, `https://api.x.ai/v1`). Default chat model is `grok-4.6` unless `XAI_MODEL` is set.
- Tests in CI must not require network, Docker, or an API key. Use `InMemorySaver` in unit tests.
- Supervisor threads persist with LangGraph `PostgresSaver` against local Docker Compose (host port 5433). Do not add Entity Framework to this repo.
