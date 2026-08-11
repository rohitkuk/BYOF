# BYOF Roadmap

Two independent tracks: **source phases** (which connectors exist) and **versions**
(how agent orchestration works). Advance either independently — don't couple them.
Recommendation: stay on Phase 1 sources until at least V3 below.

## Source phases

- **Phase 1** (current): Newsletter, Papers with Code, TechCrunch, Google News —
  no login required.
- **Phase 2**: Instagram + LinkedIn, via current browser session.
- **Phase 3**: Instagram Reels (downloadable view etc).
- **Phase 4**: YouTube reels.

## Version roadmap (agent orchestration complexity)

### V1 — Foundation *(current)*
Working curated feed from Phase 1 sources, weighted, ranked, filterable.
- Agents: 1 per connector + 1 weighing + 1 aggregation (~6 total, fixed)
- Skill: basic single-agent orchestration, prompt design, local DB schema
- Slices:
  1. ✅ Google News connector → print to terminal
  2. ✅ Same connector → write to SQLite (dedup, `db/store.py`)
  3. ✅ Aggregation agent → rank by recency only (placeholder weighing)
  4. ✅ Streamlit page → reads DB, shows ranked list
  5. ✅ Weighing agent → real preference ranking (category + subcategory scoring)
  6. ✅ Reel feed UI — snap-scroll cards, article og:images (slug + Playwright fallback),
        publisher logo fallback, category/date/type filters, 20-item feed cap
     6b. ✅ Reel UI redesign — FAB drawer, scroll snap, action rail, like/skip/save session state
     6c. ✅ Frontend migration — Streamlit → FastAPI + React
           Glacier design system. See `docs/DESIGN.md`.
  7. ✅ Add TechCrunch connector
  8. ✅ Add remaining Phase 1 connectors (Papers with Code, The Rundown AI newsletter)

### V2 — Item-level swarm *(current)*
Per-item content fetch + LLM scoring. Each item gets its own short-lived Claude agent.
- Agents: one per content item (20–200+/day, concurrent pool of 5)
- Skill: concurrency control, worker pools, partial-failure handling, per-run cost tracking
- Slices:
  1. ✅ `uv add anthropic` — Anthropic SDK added
  2. ✅ `db/store.py` — 6 new columns (body, llm_summary, llm_keywords, llm_categories, llm_score, scored_at) + refresh_runs table
  3. ✅ `agents/content_fetcher.py` — full page text + og:image + Playwright screenshot fallback
  4. ✅ `agents/item_scorer.py` — Claude Haiku per-item scorer (summary + keywords + categories + score)
  5. ✅ `agents/swarm.py` — ThreadPoolExecutor orchestrator with failure isolation + token tracking
  6. ✅ `agents/aggregation.py` — LLM score path (recency × llm_score × 10) with V1 keyword fallback
  7. ✅ `api.py` — /refresh wired to swarm, /runs endpoint added, /feed includes summary + llm_scored
  8. ✅ `app.py` — swarm wired into CLI with cost summary print

### V3 — Persona twins
Feed reflects multiple facets of taste (researcher / generalist / hands-on engineer
lenses), toggleable.
- Agents: V2 item-agents + 3–5 persona agents scoring the same pool independently
- Skill: running many agents over identical input with independent judgments
- Planned: mind map — cross-article relationship graph, topic clustering from llm_keywords
- Planned: over-time preference learning — persist like/save/skip signals to backend, drift scoring weights

### V4 — Consensus jury
Top rankings come with a visible "why this beat that" — agents disagree, a judge resolves.
- Agents: V3 agents + 1–3 judge/arbiter agents
- Skill: multi-agent consensus, structured debate protocols

### V5 — Dynamic allocation (stretch)
Niche content triggers a temporary specialist persona agent that spins up and retires
automatically, within a budget.
- Agents: variable, potentially dozens — a controller agent decides spawn count per run
- Skill: dynamic agent lifecycle management, budget-aware orchestration

## Status

Current: **V2 complete** — item-level swarm with LLM scoring live. Next: V3 planning.