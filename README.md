# BYOF — Build Your Own Feed

> A local-first, multi-agent feed aggregator. Curate your sources, weigh them by personal preference, and view everything in one ranked feed. **No data leaves your device.**

---

## What is this?

BYOF lets you pull content from multiple sources (news, blogs, research papers, social platforms), score it against your preferences, and surface the most relevant items — without sending your reading habits to any server.

It's also a learning project for progressively complex multi-agent AI architectures. Each version deliberately increases agent orchestration complexity as a first-class goal, independent of source coverage.

---

## Stack

| Layer | Tool |
|---|---|
| Language | Python 3.13+ |
| Package manager | [uv](https://github.com/astral-sh/uv) |
| RSS parsing | feedparser |
| Local database | SQLite *(Slice 2+)* |
| Frontend | Streamlit *(Slice 4+)* |
| Agent orchestration | Custom multi-agent *(V2+)* |

---

## Architecture

```
Open app
  → Select connectors
  → Set preferences

┌─────────── privacy boundary — local only from here ───────────┐
│  Connector agents (Google News, TechCrunch, Papers, etc.)      │
│    → SQLite (local DB)                                         │
│    → Weighing agent (rank by preference & history)             │
│    → Aggregation agent (finalize, dedupe across sources)       │
│    → Streamlit frontend (filterable by source / date / type)   │
└───────────────────────────────────────────────────────────────┘
```

**Key principle:** connectors are stateless and independent. Each exposes a single `fetch() -> list[dict]` function. Agents consume that shape only — nothing reaches into connector internals.

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

- [x] **Slice 1** — Google News connector → print to terminal
- [x] **Slice 2** — Same connector → write to SQLite
- [x] **Slice 3** — Aggregation agent → rank by recency (placeholder weighing)
- [x] **Slice 4** — Streamlit page → reads DB, shows ranked list
- [ ] **Slice 5** — Weighing agent → real preference ranking replaces recency
- [ ] **Slice 6** — Metadata filter in Streamlit (source / date / type)
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
uv run python app.py
```

---

## Contributing

This is an open project. Contributions welcome — especially new connectors following the Connector Contract and improvements to agent logic.

Before opening a PR, read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — specifically the Connector Contract and the vertical-slice principle (don't add a connector without wiring it end-to-end).

---

## License

[MIT](LICENSE)
