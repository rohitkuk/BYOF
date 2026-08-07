# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**BYOF (Build Your Own Feed)** — local-first, multi-agent feed aggregator. Sources curated by user, weighted by preference, displayed in one place. No data leaves the device.

Primary entrypoint: `app.py` (Python).

## Current Focus

**Active slice: V1 Slice 2** — Google News connector → write items to SQLite (no agents yet).
Full plan: see `docs/ROADMAP.md`. Architecture/flow: see `docs/ARCHITECTURE.md`.
Do not build ahead of the current slice — flag it if a request seems to skip steps.

## Directory Structure

| Dir | Purpose |
|-----|---------|
| `agents/` | Multi-agent logic (weighing, aggregation, etc.) |
| `connectors/` | Source integrations (RSS, APIs, etc.) |
| `db/` | Local storage layer |
| `docs/` | Architecture and roadmap docs |

## Architecture Principles

- **Local-first**: all data stays on device — no cloud sync, no external persistence
- **Multi-agent**: separate agents handle fetching, ranking, and presenting feeds
- **Connector pattern**: each source type lives in `connectors/`; agents consume connector output
- **Vertical slices**: build one connector end-to-end before adding the next, rather than building all connectors before any agent logic

## README Maintenance

**Whenever a slice or feature is completed, immediately update `README.md`:**
- Check the completed item's checkbox in the Progress section (`- [ ]` → `- [x]`)
- Update the Current Focus section in this file to reflect the next slice
- Do this in the same commit as the completed work — never let the README lag

## Hard Rules

- **Never commit without explicit user permission.** Always stage, show what will be committed, and wait for "commit this" or equivalent before running `git commit`.
- **Commit messages: short and project-relevant.** One line, conventional-commits prefix (`feat/fix/docs/refactor`), no Co-Authored-By lines, no verbose body unless user asks.
- No data leaves the device. No cloud DB, no telemetry, no analytics, no external persistence of any kind — the only outbound calls allowed are fetches *from* source APIs/RSS.
- No new connector without following the Connector Contract below.
- Never edit `requirements.txt` or manually manage `venv/` — use `uv add`/`uv remove` and let `uv.lock` track versions.
  
  
## Connector Contract

Every file in `connectors/` exposes one function:

```python
def fetch() -> list[dict]:
    """Returns items shaped as:
    {"title": str, "url": str, "source": str, "published_at": str, "raw": dict}
    """
```

Agents in `agents/` consume this shape only — never reach into a connector's internals.

## Development

- Environment & dependencies: [uv](https://github.com/astral-sh/uv) — do not use pip/venv directly
- Setup: `uv sync`
- Add a dependency: `uv add <package>`
- Run: `uv run python app.py`

_(test/lint commands: add here once they exist)_