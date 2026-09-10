# Agent instructions (this repo)

- The supervisor is the only agent that talks to Karli.
- Specialists are registered in `family/<name>/SPEC.toml`. Folder name must match `name`. Folders starting with `_` are templates, not agents.
- `status = "stub"` means `delegate` must return a stub payload. Never fake the specialist's job.
- Do not add MCP or domain tools to the supervisor. Attach them to a specialist later.
- A planet or 3D world, if added, is a read-only view. It must not start agents or live on the `delegate` path.
- Models go through SpaceXAI / xAI (`XAI_API_KEY`, `https://api.x.ai/v1`). Default chat model is `grok-4.6` unless `XAI_MODEL` is set.
- Tests in CI must not require network or an API key.
