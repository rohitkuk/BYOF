<div align="center">

# BYOF · Build Your Own Feed

**A local-first, multi-agent feed aggregator.**
**Your sources. Your weights. Your device.**

![Python](https://img.shields.io/badge/Python-3.13+-3776ab?logo=python&logoColor=white&style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white&style=flat-square)
![React](https://img.shields.io/badge/React-Vite-61dafb?logo=react&logoColor=black&style=flat-square)
![SQLite](https://img.shields.io/badge/SQLite-local--only-003b57?logo=sqlite&logoColor=white&style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Haiku-d97706?logo=anthropic&logoColor=white&style=flat-square)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)

</div>

<div align="center">
  <img src="docs/demo.gif" alt="BYOF demo — landing, feed scroll, like/save/skip, explore, saved, profile" width="280" />
</div>

---

## What is BYOF?

BYOF pulls content from multiple sources — news, research papers, newsletters — scores each item with a Claude Haiku agent, and surfaces your most relevant 20 items in a single ranked feed. No account. No tracking. No data leaves your device.

It's also a learning project for progressively complex multi-agent AI architectures. Each version deliberately increases agent orchestration complexity as a first-class goal.

---

## Features

| Feature | Description |
|---|---|
| **Snap-scroll feed** | Full-viewport cards — swipe or scroll through your ranked items |
| **LLM scoring** | Claude Haiku reads each article: generates summary, keywords, relevance score |
| **Persona twins** | Switch between Researcher / Generalist / Engineer lenses — reranks instantly |
| **Preference learning** | Like / save / skip signals drift ranking weights over time — entirely on device |
| **Explore** | Filter by format (Articles · Newsletters · Papers), topic, or source |
| **Saved** | Search and filter everything you've bookmarked |
| **Local-first** | All data stays on your machine — SQLite, no cloud, no telemetry |

---

## Stack

| Layer | Tool |
|---|---|
| Language | Python 3.13+ |
| Package manager | [uv](https://github.com/astral-sh/uv) |
| Database | SQLite |
| API | FastAPI + uvicorn |
| Frontend | React (Vite) — Glacier design system |
| LLM | Claude Haiku (per-item scoring via Anthropic SDK) |
| Sources | Google News · TechCrunch · ArXiv · MIT Tech Review · TLDR Tech |

---

## Architecture

```
Open app → Landing page (localStorage auth gate)
  ↓ first run
Preference setup → preferences.json

┌──────────────────── privacy boundary — local only ─────────────────────┐
│                                                                         │
│  Connectors  Google News · TechCrunch · ArXiv · MIT TR · TLDR Tech     │
│    → save_items() → SQLite                                              │
│    → Image pipeline: slug fetch → Playwright fallback → logo fallback  │
│                                                                         │
│  LLM Swarm   Claude Haiku per-item  (summary + keywords + score)       │
│                                                                         │
│  Ranking pipeline                                                       │
│    → Weighing agent:   category/subcategory preferences                 │
│    → Persona agent:    researcher / generalist / engineer reweighting   │
│    → Learning agent:   like/save/skip decay boosts (7-day half-life)   │
│    → Aggregation:      ranked feed, top 20                              │
│                                                                         │
│  FastAPI api.py :8000  ←→  React Vite frontend :5173                   │
│  Feed (For You) · Explore · Saved · Profile                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Getting Started

**Requires:** Python 3.13+, Node.js 18+, [uv](https://github.com/astral-sh/uv)

```bash
# 1. Clone and install
git clone https://github.com/rohitkuk/BYOF.git
cd BYOF
uv sync
uv run playwright install chromium   # for JS redirect image resolution

# 2. Add your Anthropic API key
cp .env.example .env
# Edit .env → set ANTHROPIC_API_KEY=sk-ant-...

# 3. Initial data fetch (populates DB + resolves images)
uv run python app.py

# 4. Start the backend API
uv run python api.py                 # → http://localhost:8000

# 5. Start the frontend (new terminal)
cd frontend && npm install && npm run dev  # → http://localhost:5173
```

**Prefer a single command?** The start script auto-detects your LAN IP so mobile devices on the same WiFi can connect:

```bash
bash start.sh
```

---

## How to Use

### First Run

Open **http://localhost:5173**. The landing page appears — click **"Sign in with Google"** to enter the app. This uses a `localStorage` bypass; no real OAuth or account is required.

---

### Feed — For You

Your ranked feed. Full-viewport snap-scroll cards, one article at a time.

Each card shows:
- Article image, category pills, title, source, and relative timestamp
- A **READ** link to open the full article

**Action rail** (right side of each card):

| Button | Action | Learning signal |
|---|---|---|
| ❤️ **Like** | Signals interest — boosts that source + keywords in future rankings | +1.0 |
| 🔖 **Save** | Bookmarks to Saved page — stronger interest signal | +1.5 |
| ⏭ **Skip** | Permanently hides this URL — gently demotes source in future rankings | −1.0 |

Signals accumulate across sessions and are weighted by recency. The feed gets smarter the more you use it — all on device.

Desktop users see progress dots on the right edge showing your position in the feed.

---

### Explore

Filter the feed by content type, topic, or source.

- **Format bar** (top): All / Articles / Newsletters / Papers
- **Topic pills**: multi-select to narrow by subject area
- **Source list**: checkbox per source to include or exclude
- Tap **Apply** → filtered feed · **Reset** → clear all filters

---

### Saved

Everything you've bookmarked via the save action.

- Search bar at top — full-text search across saved titles
- Type filter pills (Articles / Newsletters / Papers)
- Empty state shown when nothing saved yet

---

### Profile

- **Stats row**: articles read · items saved · articles liked
- **Preference pills**: your current category preferences
- **App info**: source count, last refresh time, version

---

### Refreshing Content

Trigger a new fetch + LLM scoring cycle:

```bash
curl -X POST http://localhost:8000/refresh
```

Check status:

```bash
curl http://localhost:8000/refresh/status
```

After each refresh, learned weights recompute automatically from your signal history and are applied to the next `/feed` call.

---

## V3 Features

### Persona Twins

Three taste lenses that reweight the same item pool — no re-fetching required.

Edit `preferences.json` and set the `"persona"` field:

```json
{ "persona": "researcher" }
```

| Persona | Boosts |
|---|---|
| `researcher` | ArXiv · MIT Tech Review · papers, benchmarks, methodology, neural networks |
| `engineer` | TechCrunch · TLDR Tech · APIs, infrastructure, open-source, tooling, cloud |
| `generalist` | Balanced across all sources — default |

Switch persona → the next `/feed` call re-ranks instantly from the same SQLite data.

---

### Preference Learning

Every like / save / skip fires `POST /signals` to the backend. On each refresh cycle:

1. Signals are read from SQLite joined with item metadata (source, keywords)
2. Exponential decay applied — recent signals count more (7-day half-life means a signal from 2 weeks ago is worth 4× less than one from today)
3. Per-source and per-keyword boosts computed, clamped to `[0.4 → 2.5]`
4. Skipped URLs **permanently filtered** from feed output
5. Boosts written to `preferences.json["learned"]` — applied on every `/feed` call

```
boost = max(0.4, min(2.5, 1.0 + accumulated_signal × 0.15))
```

The feed improves silently in the background. No model, no server, no sync — just your own signal history on your own machine.

---

## Roadmap

Two independent tracks — advance either without coupling to the other.

### Source phases

| Phase | Sources | Status |
|---|---|---|
| 1 | Google News · TechCrunch · ArXiv · MIT Tech Review · TLDR Tech | ✅ Complete |
| 2 | Instagram + LinkedIn (browser session) | ⏳ Planned |
| 3 | Instagram Reels | ⏳ Planned |
| 4 | YouTube | ⏳ Planned |

### Agent versions

| Version | What changes | Agents | Status |
|---|---|---|---|
| **V1** Foundation | Curated feed, weighted, ranked, filterable | ~6 fixed | ✅ Complete |
| **V2** Item swarm | Claude Haiku per-item: summary + keywords + score | 20–200+/day | ✅ Complete |
| **V3** Persona + learning | Taste lenses + like/save/skip decay boosts | V2 + 2 | ✅ Complete |
| **V4** Consensus jury | Agents debate; judge resolves; "why this beat that" visible | V3 + 1–3 | ⏳ Planned |
| **V5** Dynamic allocation | Specialist agents spin up per niche content, within budget | Variable | ⏳ Planned |

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for full detail.

---

## Progress

### V1 — Foundation

- [x] Slice 1 — Google News RSS connector → terminal output
- [x] Slice 2 — Persist items to SQLite with dedup (`db/store.py`)
- [x] Slice 3 — Aggregation agent ranks by recency (placeholder weighing)
- [x] Slice 4 — Streamlit feed page reads DB and shows ranked list
- [x] Slice 5 — Weighing agent with real preference ranking (category + subcategory scoring)
- [x] Slice 6 — Snap-scroll reel cards, article og:images (slug + Playwright fallback), publisher logo fallback, 20-item feed cap
- [x] Slice 6b — UI redesign: FAB drawer, action rail, like/skip/save
- [x] Slice 6c — Frontend migration: Streamlit → FastAPI + React (Glacier design system)
- [x] Slice 7 — TechCrunch connector
- [x] Slice 8 — ArXiv, MIT Tech Review, TLDR Tech connectors
- [x] Slice 9 — Full navigation redesign: TopBar, BottomNav, Explore, Saved, Profile pages
- [x] Slice 10 — Landing page with localStorage auth bypass

### V2 — Item Swarm

- [x] Anthropic SDK added
- [x] DB schema extended: body, llm_summary, llm_keywords, llm_categories, llm_score, scored_at, signals
- [x] `agents/content_fetcher.py` — full page text + og:image extraction
- [x] `agents/item_scorer.py` — Claude Haiku per-item scorer
- [x] `agents/swarm.py` — ThreadPoolExecutor orchestrator, failure isolation, token tracking
- [x] `agents/aggregation.py` — LLM score path (recency × llm_score × 10)
- [x] `/refresh` endpoint wired to swarm; `/runs` endpoint added
- [x] Performance: WAL mode, DB indexes, 30s feed cache, GZip middleware

### V3 — Persona Twins + Preference Learning

- [x] `agents/personas.py` — researcher / generalist / engineer source + keyword reweighting
- [x] `agents/learning.py` — exponential-decay signal boosts, skipped URL filtering
- [x] `db/store.py` — signals table, `save_signal()`, `get_signals_with_items()`
- [x] `api.py` — `POST /signals` endpoint; learned weights recomputed on each refresh
- [x] `agents/aggregation.py` — persona + learned weights applied in `rank()`
- [x] `frontend/ActionRail.jsx` — fires `POST /signals` on like / save / skip

### Sources

- [x] Google News (RSS)
- [x] TechCrunch
- [x] ArXiv
- [x] MIT Technology Review
- [x] TLDR Tech (newsletter)
- [ ] Instagram / LinkedIn *(Phase 2)*
- [ ] YouTube *(Phase 4)*

---

## Connector Contract

Every file in `connectors/` exposes one function:

```python
def fetch() -> list[dict]:
    """
    Returns items shaped as:
    {"title": str, "url": str, "source": str, "published_at": str, "raw": dict}
    """
```

Agents consume this shape only — nothing reaches into connector internals.

To add a source: create `connectors/<name>.py` implementing `fetch()`, then wire it into `_do_refresh()` in `api.py`.

---

## Contributing

Contributions welcome — especially new connectors and improvements to agent logic.

Before opening a PR, read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — specifically the Connector Contract and the vertical-slice principle (build one connector end-to-end before the next; don't add a connector without wiring it all the way through to the feed).

---

## License

[MIT](LICENSE)
