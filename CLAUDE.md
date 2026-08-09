# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repo.

## Project

**BYOF (Build Your Own Feed)** — local-first, multi-agent feed aggregator. Sources curated by user, weighted by preference, shown in one place. No data leaves device.

Entrypoint: `app.py` (Python).

## Current Focus

**Active: Frontend migration — Streamlit → FastAPI + React.**
Prompts in `docs/FRONTEND.md`. Run Step 1 next session.
Do not start Slice 7 (TechCrunch) until migration is complete.

Full plan: `docs/ROADMAP.md`. Architecture/flow: `docs/ARCHITECTURE.md`.
Don't build ahead of current slice — flag if request skips steps.

**Recently completed:** Slice 8 — `connectors/papers_with_code.py` + `connectors/the_rundown_ai.py`, source filter in sidebar, Newsletter type support.

## Directory Structure

| Dir | Purpose |
|-----|---------|
| `agents/` | Multi-agent logic (weighing, aggregation, etc.) |
| `connectors/` | Source integrations (RSS, APIs, etc.) |
| `db/` | Local storage layer |
| `docs/` | Architecture and roadmap docs |
| `frontend/` | React (Vite) SPA — not built yet |
| `api.py` | FastAPI server — not built yet |

## Architecture Principles

- **Local-first**: all data stays on device — no cloud sync, no external persistence
- **Multi-agent**: separate agents handle fetching, ranking, presenting feeds
- **Connector pattern**: each source type lives in `connectors/`; agents consume connector output only
- **Vertical slices**: build one connector end-to-end before next, not all connectors before any agent logic

## README Maintenance

**Slice/feature done → update `README.md` right away:**
- Check completed item's box in Progress section (`- [ ]` → `- [x]`)
- Update Current Focus section here to next slice
- Same commit as work — never let README lag

## Hard Rules

- **Never commit without explicit user permission.** Always stage, show what'll be committed, wait for "commit this" or equivalent before `git commit`.
- **Commit messages: short, project-relevant.** One line, conventional-commits prefix (`feat/fix/docs/refactor`), no Co-Authored-By lines, no verbose body unless asked.
- No data leaves device. No cloud DB, no telemetry, no analytics, no external persistence — only outbound calls allowed: fetches *from* source APIs/RSS.
- No new connector without following Connector Contract below.
- Never edit `requirements.txt` or manually manage `venv/` — use `uv add`/`uv remove`, let `uv.lock` track versions.

## Connector Contract

Every file in `connectors/` exposes one function:

```python
def fetch() -> list[dict]:
    """Returns items shaped as:
    {"title": str, "url": str, "source": str, "published_at": str, "raw": dict}
    """
```

Agents in `agents/` consume this shape only — never reach into connector internals.

## Development

- Environment & dependencies: [uv](https://github.com/astral-sh/uv) — no pip/venv directly
- Setup: `uv sync`
- Add dependency: `uv add <package>`
- Run: `uv run python app.py`

Planned (post-migration):
- Backend:  `uv run python api.py`       → http://localhost:8000
- Frontend: `cd frontend && npm run dev` → http://localhost:5173

_(test/lint commands: add once they exist)_

## Current State

- `docs/FRONTEND.md` ✅ — stepwise migration prompts, 7 steps, Step 1 is next
- `streamlit_app.py` ⚠️  — active now, will be deleted after migration Step 7
- `api.py` ⬜ — stub only, build in Step 1
- `frontend/src/` ⬜ — stubs only (App.jsx, FeedCard, ActionRail, ProgressDots, Sidebar, FilterPills, useFeed, usePreferences, index.css), build Steps 2–6