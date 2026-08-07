# BYOF — Build Your Own Feed

> A local-first, multi-agent feed aggregator. Curate your sources, weigh them by personal preference, and view everything in one ranked feed. **No data leaves your device.**

---

## What is this?

BYOF lets you pull content from multiple sources (news, blogs, research papers, social platforms), score it against your preferences, and surface the most relevant 20 items — without sending your reading habits to any server.

It's also a learning project for progressively complex multi-agent AI architectures. Each version deliberately increases agent orchestration complexity as a first-class goal, independent of source coverage.

---

## Stack

| Layer | Tool |
|---|---|
| Language | Python 3.13+ |
| Package manager | [uv](https://github.com/astral-sh/uv) |
| RSS parsing | feedparser |
| Local database | SQLite |
| Frontend | Streamlit |
| Image resolution | requests (slug-based) + Playwright (JS redirect fallback) |
| Agent orchestration | Custom multi-agent *(V2+)* |

---

## Architecture

```
Open app
  → Preference setup (categories + subcategories, saved locally)

┌─────────────── privacy boundary — local only from here ───────────────┐
│  Connector agents (Google News, TechCrunch, etc.)                      │
│    → SQLite (items + publisher_logos tables)                           │
│    → Image pipeline: slug fetch → Playwright fallback → logo fallback  │
│    → Weighing agent (score by category/subcategory preferences)        │
│    → Aggregation agent (rank by score, cap at 20 items)                │
│    → Streamlit reel feed (filter by category / date / type)            │
└───────────────────────────────────────────────────────────────────────┘
```

**Key principles:**
- Connectors are stateless and independent — each exposes `fetch() -> list[dict]` only
- Images resolved in two phases: fast concurrent slug construction, then Playwright headless browser for publishers with non-standard URL patterns
- Feed capped at 20 items (anti-doom-scroll) — ranked by preference score × recency

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for full design notes.

---

## Roadmap

Two independent tracks — advance either without coupling to the other.

### Source phases

| Phase | Sources | Status |
|---|---|---|
| 1 | Google News, TechCrunch, Papers with Code, Newsletter | 🔄 In progress |
| 2 | Instagram + LinkedIn (via browser session) | ⏳ Planned |
| 3 | Instagram Reels | ⏳ Planned |
| 4 | YouTube | ⏳ Planned |

### Version roadmap (agent complexity)

| Version | What changes | Agents |
|---|---|---|
| **V1** Foundation | Working curated feed, weighted, ranked, filterable | ~6 fixed |
| **V2** Item swarm | One short-lived agent per content item | 20–200+/day, dynamic |
| **V3** Persona twins | Multiple taste lenses (researcher / generalist / engineer) | V2 + 3–5 persona agents |
| **V4** Consensus jury | Agents debate; a judge resolves; "why this beat that" is visible | V3 + 1–3 judge agents |
| **V5** Dynamic allocation | Niche content triggers temporary specialist agents within a budget | Variable, controller-managed |

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for full detail.

---

## Progress

### V1 Slices

- [x] **Slice 1** — Google News RSS connector → terminal output
- [x] **Slice 2** — Persist items to SQLite with dedup (`db/store.py`)
- [x] **Slice 3** — Aggregation agent ranks by recency (placeholder weighing)
- [x] **Slice 4** — Streamlit feed page reads DB and shows ranked list
- [x] **Slice 5** — Weighing agent with real preference ranking (category + subcategory scoring)
- [x] **Slice 6** — Snap-scroll reel cards, article og:images (slug + Playwright fallback), publisher logo fallback, category/date/type filters, 20-item feed cap
- [ ] **Slice 7** — TechCrunch connector
- [ ] **Slice 8** — Papers with Code + Newsletter connectors

### Sources

- [x] Google News (RSS)
- [ ] TechCrunch
- [ ] Papers with Code
- [ ] Newsletter
- [ ] Instagram / LinkedIn *(Phase 2)*
- [ ] YouTube *(Phase 4)*

---

## Getting Started

**Requires:** Python 3.13+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/rohitkuk/BYOF.git
cd BYOF
uv sync
uv run playwright install chromium   # for JS redirect resolution
uv run python app.py                 # fetch + resolve images (full pipeline)
uv run streamlit run streamlit_app.py
```

On first open, BYOF asks which categories you care about (AI & ML, Technology, Business, etc.) — then shows a ranked, filtered feed of up to 20 items.

Use **Refresh** in the app to pull new articles. For a full image backfill (including Playwright resolution), run `app.py` from the terminal.

---

## Contributing

This is an open project. Contributions welcome — especially new connectors following the Connector Contract and improvements to agent logic.

Before opening a PR, read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — specifically the Connector Contract and the vertical-slice principle (don't add a connector without wiring it end-to-end).

---

## License

[MIT](LICENSE)
