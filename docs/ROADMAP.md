# Roadmap

Move slowly. Do not skip a phase because a later one looks more fun.

## v0 — supervisor bootstrap (this slice)

- [x] Registry of specialists on disk
- [x] Supervisor with `list_agents` and `delegate`
- [x] Stub specialists (`research`, `code`)
- [x] CLI chat + catalog
- [x] Loop guard, Grok via SpaceXAI
- [x] Tests that do not need an API key
- [x] GitHub branching, CI, docs

## v0.1 — talk to Karli better

- [x] Persistent checkpointer (Postgres via Docker Compose) so threads survive restart
- [x] Clearer CLI streaming (tool names as they fire)
- Optional LangSmith traces
- Prompt evals: trivia is not delegated; stubs are not impersonated

## v0.2 — first live specialist

- One real worker (likely `research`) with its own MCP/tools
- Supervisor still has no web tools
- HITL on anything irreversible

## Later

- More specialists (`code`, ops, markets)
- Human-in-the-loop middleware
- Planet/presence UI that **reads** registry and run status only
