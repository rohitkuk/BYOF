# Preference Learning — Design Spec

**Date:** 2026-08-12
**Status:** Approved
**Track:** V3

---

## Context

V3 Persona Twins gave the feed a static lens. Preference learning makes the feed adaptive — likes, saves, and skips drift the ranking weights over time. Signals are captured in the frontend already; this slice persists them to SQLite, computes recency-decayed source and keyword boosts, and applies them on top of the existing persona reweighting.

---

## Decisions

- **Both source + keyword signals** — liked/saved items boost their source and keywords; skipped items demote both
- **Batched** — weights recomputed during `_do_refresh()`, stored in `preferences.json["learned"]`; not recomputed on every request
- **Recency decay** — exponential with 7-day half-life; a like today outweighs one from two weeks ago by 4×
- **Skipped URLs** — permanently filtered from feed output (not just demoted)

---

## Components

### `signals` table (new, `db/store.py` `init_db()`)

```sql
CREATE TABLE IF NOT EXISTS signals (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    url        TEXT NOT NULL,
    action     TEXT NOT NULL,   -- "liked" | "saved" | "skipped"
    created_at TEXT NOT NULL
)
```

Append-only. Multiple signals per URL allowed — weight computation aggregates all.

### `save_signal(conn, url, action)` (new, `db/store.py`)

```python
def save_signal(conn: sqlite3.Connection, url: str, action: str) -> None:
    conn.execute(
        "INSERT INTO signals (url, action, created_at) VALUES (?, ?, ?)",
        (url, action, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
```

### `POST /signals` (new, `api.py`)

```
Body: {"url": str, "action": "liked" | "saved" | "skipped"}
Response: {"status": "ok"}
```

Calls `save_signal()`, then `_invalidate_feed_cache()`.

### `agents/learning.py` (new)

```python
def compute_learned_weights(conn: sqlite3.Connection) -> dict:
    """
    Returns:
    {
      "source_boosts": {source_name: float},   # clamped to [0.4, 2.5]
      "keyword_boosts": {keyword: float},       # clamped to [0.4, 2.5]
      "skipped_urls": [url, ...]
    }
    """
```

**Algorithm:**

1. Load all signals joined with items to get `source` and `llm_keywords`:
   ```sql
   SELECT s.url, s.action, s.created_at, i.source, i.llm_keywords
   FROM signals s
   LEFT JOIN items i ON s.url = i.url
   ORDER BY s.created_at DESC
   ```

2. For each signal, compute decay:
   ```python
   import math
   days_ago = (now - signal_ts).total_seconds() / 86400
   decay = math.exp(-math.log(2) / 7 * days_ago)
   ```

3. Signal values: `liked` = +1.0, `saved` = +1.5, `skipped` = -1.0

4. Accumulate weighted signal per source and per keyword:
   ```python
   source_raw[source] += signal_value * decay
   for kw in llm_keywords:
       keyword_raw[kw] += signal_value * decay
   ```

5. Convert raw scores to boosts:
   ```python
   boost = max(0.4, min(2.5, 1.0 + raw * 0.15))
   ```

6. Collect `skipped_urls` = all URLs where any signal has `action == "skipped"`.

### Integration into `_do_refresh()` (`api.py`)

After `save_refresh_run()`, call `compute_learned_weights()` and merge into `preferences.json` under `"learned"` key:

```python
from agents.learning import compute_learned_weights
learned = compute_learned_weights(conn)
prefs = json.load(open(PREFS_PATH)) if os.path.exists(PREFS_PATH) else {}
prefs["learned"] = learned
with open(PREFS_PATH, "w") as f:
    json.dump(prefs, f, indent=2)
```

### Integration into `rank()` (`agents/aggregation.py`)

After `apply_persona()`, apply learned boosts:

```python
from agents.learning import apply_learned_weights
items = apply_learned_weights(items, prefs)
```

`apply_learned_weights(items, prefs)`:
1. Filter out `skipped_urls`
2. For each remaining item, multiply score by `source_boosts.get(source, 1.0)` and by average keyword boost across item's keywords
3. Re-sort descending

### Frontend — `ActionRail.jsx`

On each signal (like/save/skip), fire `POST /signals` alongside the existing `onSignal` callback:

```javascript
const sendSignal = (action) => {
  axios.post('/signals', { url: item.url, action }).catch(() => {})
  onSignal({ liked: action === 'liked', saved: action === 'saved', skipped: action === 'skipped' })
}
```

Fire-and-forget (`.catch(() => {})`) — UI state doesn't depend on server response.

---

## Vite Proxy

Add `/signals` to `vite.config.js` proxy routes:
```javascript
'/signals': { target: 'http://127.0.0.1:8000', changeOrigin: true },
```

---

## What's NOT in this slice

- UI to view or clear signals
- Per-keyword boost display in feed cards
- Signal history endpoint
- Mind map / topic clustering (separate V3 slice)

---

## Verification

```bash
# 1. Send a liked signal
curl -s -X POST http://localhost:8000/signals \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/...", "action": "liked"}'

# 2. Check DB
sqlite3 db/byof.db "SELECT * FROM signals ORDER BY id DESC LIMIT 5;"

# 3. Trigger refresh to recompute weights
curl -s -X POST http://localhost:8000/refresh

# 4. Check preferences.json has "learned" key
python3 -c "import json; d=json.load(open('preferences.json')); print(json.dumps(d.get('learned',{}), indent=2))"

# 5. Fetch feed — items from liked source should rank higher
curl -s http://localhost:8000/feed | python3 -c "
import json, sys
for i in json.load(sys.stdin)[:5]: print(i['source'], round(i['score'],3))"

# 6. Send a skipped signal, verify that URL disappears from feed after refresh
curl -s -X POST http://localhost:8000/signals \
  -H "Content-Type: application/json" \
  -d '{"url": "https://...", "action": "skipped"}'
curl -s -X POST http://localhost:8000/refresh
curl -s http://localhost:8000/feed | python3 -c "
import json, sys
urls = [i['url'] for i in json.load(sys.stdin)]
print('skipped url present:', 'https://...' in urls)"
```
