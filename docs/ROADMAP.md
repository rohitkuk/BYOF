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
     6c. ⬜ Frontend migration — Streamlit → FastAPI + React
           Glacier design system. See `docs/DESIGN.md`.
  7. ✅ Add TechCrunch connector
  8. ✅ Add remaining Phase 1 connectors (Papers with Code, The Rundown AI newsletter)

### V2 — Item-level swarm
Same feed, but scoring happens per content item instead of per feed batch.
- Agents: one short-lived agent per content item (20–200+/day, dynamic)
- Skill: concurrency control, worker pools, rate limiting, partial-failure handling,
  per-run cost tracking

### V3 — Persona twins
Feed reflects multiple facets of taste (researcher / generalist / hands-on engineer
lenses), toggleable.
- Agents: V2 item-agents + 3–5 persona agents scoring the same pool independently
- Skill: running many agents over identical input with independent judgments

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

Current slice: **Slice 6c** — frontend migration in progress. See `docs/DESIGN.md`.