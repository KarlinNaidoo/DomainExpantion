# Branching

Simplified Git Flow. `main` is always shippable. Work lands through pull requests.

## Branches

| Branch | Purpose | Merges from |
| --- | --- | --- |
| `main` | Stable, tagged releases (`v0.1.0`) | `develop`, `hotfix/*` |
| `develop` | Integration. Next release. | `feature/*`, `fix/*` |
| `feature/<slug>` | New work (one concern) | branched from `develop` |
| `fix/<slug>` | Bugs that are not production-urgent | branched from `develop` |
| `hotfix/<slug>` | Production emergency | branched from `main`, then back-merge to `develop` |

Never commit directly to `main`. Prefer not to commit directly to `develop`.

## Names

```
feature/supervisor-v0
feature/research-agent
fix/delegate-empty-brief
hotfix/cli-crash-on-missing-key
```

Slugs are lowercase kebab-case.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/):

```
feat(supervisor): add delegate tool
fix(registry): skip _template folders
docs: describe branching
chore(ci): run ruff and pytest
```

Types: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `ci`.

## Pull requests

- PR into `develop` for features and fixes.
- PR `develop` → `main` when a slice is stable (first time: supervisor v0).
- Title matches the commit style.
- CI (`ruff` + `pytest`) must pass.
- Do not mix unrelated concerns.

## Releases

Tag `main`:

```
git tag -a v0.1.0 -m "v0.1.0 supervisor bootstrap"
git push origin v0.1.0
```
