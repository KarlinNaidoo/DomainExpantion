# Bot Crossing tech stack

The colony UI is [Bot Crossing](https://github.com/Station-Sciences/bot-crossing) (MIT, Jarren Rocks), vendored at `vendor/bot-crossing`. It is a local Node web app: Vite serves the page and the API in one process. It does not run Grok, LangGraph, or Postgres. It **reads** a harness snapshot and draws astronauts.

KayKit art in `public/assets` is CC0 (Kay Lousberg).

## Runtime

| | |
| --- | --- |
| Language | JavaScript (ES modules) |
| Node | ≥ 22.13 (official) |
| Dev / build | Vite 7 |
| Prod serve | `node server/serve.mjs` after `vite build` |
| Bind | `127.0.0.1` only; answers its own origin |
| Default URL here | http://localhost:5275/ |

```bash
npm install && npm run dev
```

`npm run dev` is the whole thing: the API lives inside the Vite dev server.

## Client (the 3D colony)

| | |
| --- | --- |
| 3D | Three.js ~0.185 |
| Rendering | WebGL, instanced GPU-skinned crew |
| Scene | Hex plots, KayKit GLBs (`spacebase`, `forest`, `crew`) |
| UI | Plain DOM HUD (no React/Vue) |
| Icons | `@mdi/js` |
| Assets pipeline | `@gltf-transform` (`npm run assets`) |

## Server (inside Vite)

| | |
| --- | --- |
| API | Custom Node HTTP (`server/api.mjs`) — `/api/threads`, `/api/state`, `/api/open` |
| Persistence | One file: `data/colony.json` (layout only) |
| Harnesses | Adapters in `server/harnesses/*.mjs` |
| Pathfinding | Custom A* grid (`src/agents/navigation.js`) |
| Tests | Node `node:test` |

Upstream harnesses: Claude Code, Codex, Cursor. This repo’s overlay registers **Domain Expantion only**.

## What it is not

No LangGraph, no Grok, no Postgres. Opening a thread is normally an OS deep link (`claude://`, `codex://`). Here, Open / New conversation is patched to the in-page supervisor chat on **http://127.0.0.1:8766/**.

## How Domain Expantion plugs in

| Colony | Domain Expantion |
| --- | --- |
| One astronaut + building | supervisor / research / architecture / code |
| Harness adapter | `src/domain_expantion/planet/bot_crossing/` (copied onto vendor at launch) |
| Snapshot | `.data/planet-family.json` (Python writes; Bot Crossing only reads) |
| Working / idle | `.data/planet-activity.json` |
| In-page chat | Python sidecar `:8766` + `embed.js` iframe |

`domain-expantion planet` installs the overlay, starts the chat sidecar, then runs Bot Crossing.

See also [architecture.md](architecture.md).
