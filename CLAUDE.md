# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repo.

## Project

**BYOF (Build Your Own Feed)** — local-first, multi-agent feed aggregator. Sources curated by user, weighted by preference, shown in one place. No data leaves device.

Entrypoint: `app.py` (Python).

## Current Focus

**Active: V1 Slice 7 — TechCrunch connector.**
Frontend migration (Slice 6c) complete — FastAPI + React live, Streamlit removed.

Full plan: `docs/ROADMAP.md`. Architecture/flow: `docs/ARCHITECTURE.md`.
Don't build ahead of current slice — flag if request skips steps.

**Recently completed:** Slice 8 — `connectors/papers_with_code.py` + `connectors/the_rundown_ai.py`, source filter in sidebar, Newsletter type support.

## Directory Structure

| Dir | Purpose |
|-----|---------|
| `agents/` | Multi-agent logic (weighing, aggregation, etc.) |
| `connectors/` | Source integrations (RSS, APIs, etc.) |
| `db/` | Local storage layer |
| `design/` | Stitch reference screens + screenshots (read-only) |
| `docs/` | Architecture and roadmap docs |
| `frontend/` | React (Vite) SPA — Glacier design system, migration complete |
| `api.py` | FastAPI server — 5 endpoints, :8000 |

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
- Design system: Glacier palette only — see `docs/DESIGN.md`. Never introduce a colour not in that file.
- Fonts: Playfair Display (headlines/wordmark) + Hanken Grotesk (everything else) — no other fonts.
- UI reference: always read `design/screens/{screen}.html` before building any component.

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
- Fetch + image pipeline: `uv run python app.py`
- Backend:  `uv run python api.py`       → http://localhost:8000
- Frontend: `cd frontend && npm run dev` → http://localhost:5173

_(test/lint commands: add once they exist)_

## Current State

- `docs/DESIGN.md` ✅ — Glacier design system + migration steps 1-7
- `design/screens/` ✅ — 5 Stitch HTML reference screens
- `design/screenshots/` ✅ — 5 reference PNGs
- `api.py` ✅ — FastAPI backend (Step 1)
- `frontend/` ✅ — React SPA complete (Steps 2–6): FeedCard, ActionRail, ProgressDots, Sidebar, FilterPills