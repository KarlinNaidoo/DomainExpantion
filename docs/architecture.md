# Architecture

Domain Expantion is a personal agent family. The first live agent is the **supervisor**. Specialists join the family through the registry. A later 3D planet, if any, is a **read-only picture** of this state. Agents do not live in the planet.

## Layers

| Layer | Job | In v0 |
| --- | --- | --- |
| Models | Think and call tools | Grok via SpaceXAI (`XAI_API_KEY`, `https://api.x.ai/v1`) |
| Supervisor | Talk to Karli, decompose, route, synthesize, refuse | `create_agent` + `list_agents` + `delegate` |
| Family registry | Who exists, when to use them, live vs stub | `family/*/SPEC.toml` |
| Specialists | Domain work via tools/MCP | `research` live (`web_search`, `fetch_url`); `code` stub |
| Observability | Traces and evals | Optional LangSmith env vars |
| Persistence | Supervisor threads across CLI restarts | Postgres via Docker Compose (`PostgresSaver`) |
| Planet | Visual presence | Out of scope. Never imported by the runtime |

## Supervisor contract

The supervisor owns conversation, routing, briefs, synthesis, and policy.

It does **not** own web search, git, trading, mail, or deploys. Those attach to specialists later.

Clarifying incoming work:

- Missing **intent** → ask Karli
- Missing **facts** → `delegate` to `research` (live; web search + fetch URL)
- Irreversible action → stop and ask

## Adding a specialist

1. Copy `family/_template` to `family/<name>/`.
2. Set `name` to match the folder, `status = "stub"`.
3. Fill `when_to_use` so the supervisor can route.
4. Open a `feature/*` PR. The supervisor picks the new spec up on load.
5. Later, implement a live runtime and flip `status` to `"live"`.

A stub is a real catalog entry. The supervisor must not impersonate it.

## Runtime vs planet

```
registry + supervisor  →  source of truth
planet (future)        →  reads status, never starts an agent
```

If the planet is closed, the family still runs.

## Persistence

Threads use LangGraph's Postgres checkpointer, not Entity Framework.

Local: `docker compose up -d` publishes Postgres on **host port 5433** (avoids clashing with a local 5432). Default URL is in `.env.example`. The CLI command `domain-expantion db` creates checkpoint tables and does not call Grok.

CI and unit tests keep `InMemorySaver`. They do not require Docker.

