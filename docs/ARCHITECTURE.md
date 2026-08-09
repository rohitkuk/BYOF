# BYOF Architecture

## Core idea

Curate feeds from multiple sources, weigh by personal preference, aggregate and rank
into one view. Everything runs locally — no data leaves the device.

## Components

**Connector agents** (`connectors/`)
One per source. Each implements the Connector Contract (see CLAUDE.md) — fetches raw
items from its source and returns them as `list[dict]` in a standard shape. Independent
of each other; no shared state between connectors.

**Local database** (`db/store.py`)
SQLite. Stores curated items from all connectors. Privacy boundary — everything upstream
fetches from the open internet (unavoidable); everything from here onward stays on-device.

Schema (items table):
- `id`, `title`, `url`, `source`, `published_at`, `raw` (JSON), `fetched_at`
- `image_url` — article og:image or publisher logo URL
- `image_type` — `'article'` | `'logo'` | NULL (priority: article > logo > NULL,
  prevents logos overwriting article images on subsequent refreshes)
- `article_url` — resolved canonical article URL (cached; avoids re-running Playwright)

Schema (publisher_logos table):
- `source_href` (PK), `logo_url`, `fetched_at`
- One logo per publisher domain, fetched once, validated with HEAD before caching

**Image resolution pipeline** (`db/store.py`)
Two-phase, runs after `save_items()`:

1. `refresh_article_images()` — Phase 1 (concurrent, 8 workers): constructs
   `domain/YYYY/MM/DD/slug/` URL from title + date, fetches HTML, extracts og:image.
   Phase 2 (optional, sequential): Playwright headless browser follows Google News JS
   redirects for publishers whose URLs can't be slug-constructed (e.g. People.com),
   extracts og:image from rendered DOM.
2. `refresh_publisher_logos()` — fetches publisher homepage og:image or apple-touch-icon
   as fallback for items that still have no image. Logo URLs validated with HEAD before
   caching to prevent storing 404s.

**Weighing agent** (`agents/weighing.py`)
Scores items against user preferences (categories + subcategories). V1: static preference
set once via UI, stored in `preferences.json`. Returns items with `_weight` field.

**Aggregation agent** (`agents/aggregation.py`)
Takes weighed items, computes `_score = recency_timestamp × weight`, sorts descending.
Accepts optional `limit` parameter — V1 caps feed at 20 items (anti-doom-scroll).

**API server** (`api.py` — FastAPI, port 8000)
- 5 endpoints: `GET /health`, `GET/POST /preferences`, `GET /feed`, `POST /refresh`
- `/feed`: runs weighing + aggregation agents, applies optional query filters
  (category, date, type, source), returns up to 20 shaped items
- `/refresh`: runs all connectors + image pipeline (no Playwright — too slow for interactive use)
- CORS: allows `http://localhost:5173` only

**Frontend** (`frontend/` — React Vite, port 5173)
- Glacier Modern Editorial design system (`docs/DESIGN.md`)
- Fonts: Playfair Display (headlines/wordmark) + Hanken Grotesk (everything else)
- View state routing: `useState('feed')` in `App.jsx` — no React Router
- Auth gate: `localStorage.getItem('byof_signed_in')` → show `LandingPage` or app shell
- Components:
  - `LandingPage`: full-viewport landing, ambient bg image (opacity 0.30 overlay), gradient,
    "Your world, curated." heading, "Sign in with Google" pill (bypasses OAuth via localStorage)
  - `TopBar`: fixed 64px header — mobile: hamburger/wordmark/avatar; desktop: hamburger/wordmark + nav links (For You/Explore/Saved/Profile) + avatar
  - `BottomNav`: mobile-only fixed bottom nav, 4 tabs, active pill + dot indicator, frosted glass
  - `FeedCard`: full-viewport scroll-snap cards, article image, gradient overlay, category pills, title, source meta, READ link
  - `ActionRail`: fixed right-side LIKE / SKIP / SAVE buttons, per-item signals, active-state colours
  - `ProgressDots`: desktop-only fixed right-edge scroll indicator
  - `ExplorePage`: content format segmented control (All/Articles/Newsletters/Papers), topic bento pills (multi-select), source list with color-coded initials + checkbox; Apply navigates back to feed with filters
  - `SavedPage`: search bar, type filter pills, saved item cards (from `signals[url].saved`), empty state
  - `ProfilePage`: avatar, stats row (articles read/saved/liked), preferences pills, app info rows

**CLI fetch script** (`app.py`)
Offline fetch pipeline: `fetch()` → `save_items()` → `refresh_article_images(use_playwright=True)`
→ `refresh_publisher_logos()`. Use for initial backfill or cron — Playwright runs here,
not in Streamlit.

## Data flow

```
Open app
  → Preference setup (first run)

┌─────────── privacy boundary — local only from here ───────────┐
│  Connector agents (Google News, TechCrunch, etc.)              │
│    → save_items() → SQLite                                     │
│    → refresh_article_images() (slug phase → Playwright phase)  │
│    → refresh_publisher_logos()                                 │
│    → Weighing agent (score by category/subcategory prefs)      │
│    → Aggregation agent (rank, cap at 20)                       │
│    → FastAPI api.py (:8000) → React frontend (:5173)          │
└───────────────────────────────────────────────────────────────┘
```

## Design principles

- **Local-first**: no cloud sync, no external persistence, no telemetry.
- **Vertical slices over horizontal layers**: build one connector end-to-end before
  adding the next, rather than building all connectors before any agent logic.
- **Connector contract**: every connector exposes exactly one function — `fetch() ->
  list[dict]`. Agents consume that shape only; nothing reaches into connector internals.
- **Image priority system**: `image_type` column prevents regressions — article-specific
  images are never overwritten by publisher logos on subsequent refreshes.
- **Agent count scales with complexity tier, not feature count** — see ROADMAP.md.
  V1 keeps agent count fixed and small on purpose; later versions deliberately increase
  agent orchestration complexity as a learning goal.

## Non-goals (for now)

- No auth, no multi-user support — single local user only.
- No hosting/deployment — runs on developer's own machine.
- No real-time sync across devices.

## Frontend (complete — all 5 pages)

Streamlit replaced by FastAPI + React (Vite). All pages pixel-matched to `design/screens/` references.

Pages: LandingPage → Feed (For You) → Explore → Saved → Profile

Privacy boundary unchanged — both processes run locally only.
