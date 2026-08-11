# Persona Twins — Design Spec

**Date:** 2026-08-12
**Status:** Approved
**Track:** V3

---

## Context

V2 delivers a single ranked feed scored by the LLM swarm. Every user sees the same ordering. V3 Persona Twins gives the feed a "lens" — researcher, generalist, or hands-on engineer — so the same item pool surfaces differently depending on who is reading. The active persona is application-level (set in `preferences.json`), not a per-session UI toggle.

---

## Approach: Reweight (with re-score stub)

Personas reweight the existing `base_score` (produced by V2 swarm). No additional LLM calls per refresh. A `SCORING_MODE` constant in `agents/personas.py` gates the path — flip to `"rescore"` to activate the future LLM re-scoring path (stubbed, not implemented in this slice).

**Why reweight first:** free-tier rate limits make 3× LLM calls per refresh impractical. Reweighting uses data already in the DB (`llm_keywords`, `source`, `llm_score`) and runs in microseconds.

---

## Components

### `agents/personas.py` (new)

Single source of truth for persona logic.

```
SCORING_MODE = "reweight"   # flip to "rescore" for LLM path

PERSONAS = {
  "researcher": { source_weights, keyword_affinities, category_weights },
  "generalist": { source_weights, keyword_affinities, category_weights },
  "engineer":   { source_weights, keyword_affinities, category_weights },
}

def apply_persona(items, persona_name) -> list[dict]
def _keyword_boost(item, affinities) -> float
def _rescore_persona(items, persona_name) -> list[dict]   # stub, raises NotImplementedError
```

`apply_persona()` checks `SCORING_MODE`:
- `"reweight"` → multiply `item["score"]` by `source_weight × keyword_boost`, re-sort descending
- `"rescore"` → call `_rescore_persona()` (stub, not implemented)

### `agents/aggregation.py` (modify)

`rank()` signature: `rank(db_path, prefs_path, limit, persona=None)`

After existing scoring loop, if `persona` is set:
```python
from agents.personas import apply_persona
items = apply_persona(items, persona)
```

### `api.py` (modify)

`get_feed()` reads persona from preferences and passes to rank:
```python
prefs = json.load(open(PREFS_PATH)) if os.path.exists(PREFS_PATH) else {}
persona = prefs.get("persona", "generalist")
items = rank(DB_PATH, PREFS_PATH, limit=None, persona=persona)
```

Feed cache keyed by persona: `_feed_cache` becomes `dict[str, dict]` — `_feed_cache[persona] = {"data": ..., "ts": ...}`. Invalidate all keys on refresh.

### `preferences.json` (modify)

Add default: `"persona": "generalist"`. Existing `POST /preferences` already persists any JSON body — no endpoint change needed.

---

## Persona Definitions

### source_weights

| Source | Researcher | Generalist | Engineer |
|--------|-----------|------------|---------|
| ArXiv | 2.0 | 1.0 | 0.7 |
| MIT Technology Review | 1.5 | 1.0 | 0.8 |
| TechCrunch | 0.7 | 1.0 | 1.8 |
| TLDR Tech | 0.8 | 1.0 | 1.8 |
| Google News | 0.9 | 1.0 | 1.0 |

### keyword_affinities

- **Researcher:** `paper, model, study, research, benchmark, dataset, neural, training, analysis, arxiv`
- **Generalist:** _(none — pure source/category weights)_
- **Engineer:** `open-source, tool, api, deploy, build, github, library, framework, release, launch`

### Keyword boost formula

```python
keyword_boost = min(1.6, 1.0 + 0.15 * matching_count)
```

Matches checked against `item["title"].lower()` + each keyword in `item["keywords"]` (from `llm_keywords`). Cap at ×1.6 prevents extreme outliers.

### Final formula

```
persona_score = base_score × source_weight × keyword_boost
```

---

## Changing the Active Persona

No UI in this slice. Set via:

```bash
# curl
curl -X POST http://localhost:8000/preferences \
  -H "Content-Type: application/json" \
  -d '{"persona": "researcher"}'

# or edit directly
# preferences.json → "persona": "engineer"
```

Valid values: `"researcher"`, `"generalist"`, `"engineer"`. Unknown value falls back to `"generalist"`.

---

## What's NOT in this slice

- UI persona toggle (V3 follow-up)
- Re-score LLM path implementation (stub only)
- Per-persona preference learning (separate V3 slice)
- Mind map / topic clustering (separate V3 slice)

---

## Verification

```bash
# 1. Set persona to researcher
curl -X POST http://localhost:8000/preferences \
  -H "Content-Type: application/json" \
  -d '{"persona": "researcher"}'

# 2. Fetch feed — ArXiv/MIT TR items should rank higher
curl -s http://localhost:8000/feed | python3 -m json.tool | grep '"source"' | head -10

# 3. Switch to engineer, re-fetch — TechCrunch/TLDR should dominate
curl -X POST http://localhost:8000/preferences \
  -H "Content-Type: application/json" \
  -d '{"persona": "engineer"}'
curl -s http://localhost:8000/feed | python3 -m json.tool | grep '"source"' | head -10

# 4. Confirm cache is keyed per-persona (different results per persona)
# 5. Confirm unknown persona falls back to generalist
curl -X POST http://localhost:8000/preferences -H "Content-Type: application/json" -d '{"persona": "unknown"}'
curl -s http://localhost:8000/feed | head -5
```
