# BYOF Architecture

## Core idea

Curate feeds from multiple sources, weigh them by personal preference, aggregate and rank
into one view. Everything runs locally — no data leaves the device.

## Components

**Connector agents** (`connectors/`)
One per source. Each implements the Connector Contract (see CLAUDE.md) — fetches raw
items from its source and returns them in a standard shape. Independent of each other;
no shared state between connectors.

**Local database** (`db/`)
SQLite. Stores curated items from all connectors. This is the privacy boundary line —
everything upstream of this point fetches from the open internet (unavoidable); everything
from this point onward stays on-device permanently.

**Weighing agent** (`agents/weighing.py`)
Reads items from the DB, scores them against user preference/history. V1: preference is
static (set once via UI). Later versions: learns from selection history.

**Aggregation agent** (`agents/aggregation.py`)
Takes weighed items, finalizes ranking, dedupes overlapping stories across sources,
produces the final ordered feed.

**Frontend** (`app.py`, Streamlit)
Reads the finalized feed, displays it, supports filtering by metadata (source, date, type).

## Data flow
## Data flow

Open app
  → Select connectors
  → Set preferences

┌─────────────── privacy boundary — local only from here down ───────────────┐
│ Connector agents fetch (Google News, TechCrunch, Instagram, YouTube,        │
│ LinkedIn — each independent)                                                │
│   → Local database (SQLite)                                                 │
│   → Weighing agent (rank by preference & history)                           │
│   → Aggregation agent (finalize & rank, dedupe)                             │
│   → Frontend showcase (Streamlit)                                           │
│   → Filter by metadata (source, date, type)                                 │
└───────────────────────────────────────────────────────────────────────────┘

## Design principles

- **Local-first**: no cloud sync, no external persistence, no telemetry.
- **Vertical slices over horizontal layers**: build one connector end-to-end before
  adding the next, rather than building all connectors before any agent logic.
- **Agent count scales with complexity tier, not with feature count** — see ROADMAP.md.
  V1 keeps agent count fixed and small on purpose; later versions deliberately increase
  agent orchestration complexity as a learning goal, independent of source coverage.

## Non-goals (for now)

- No auth, no multi-user support — single local user only.
- No hosting/deployment — runs on developer's own machine.
- No real-time sync across devices.