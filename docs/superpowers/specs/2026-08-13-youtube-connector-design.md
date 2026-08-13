# YouTube Connector Design

**Goal:** Add a personalized YouTube connector that fetches the user's home feed (regular videos + Shorts) via browser session, conforming to BYOF's connector contract.

**Architecture:** Playwright navigates to `youtube.com` using a saved browser session (cookies). On first run, a headed browser opens for the user to sign in; thereafter all runs are headless. Feed data is extracted from `window.ytInitialData` — a structured JSON object YouTube embeds in every page load. Regular videos and Shorts are parsed from distinct renderer types in that JSON tree and returned as two source types (`"YouTube"` and `"YouTube Shorts"`).

**Tech Stack:** Playwright (already in project), Python stdlib (`json`, `time`, `pathlib`). No new dependencies.

---

## Global Constraints

- Connector contract: `fetch() -> list[dict]` with keys `title`, `url`, `source`, `published_at`, `raw`
- No new pip/PyPI packages — use `uv add` if anything is needed; Playwright is already installed
- Session file `sessions/youtube.json` must be gitignored — contains personal cookies, never committed
- `source` field for regular videos: `"YouTube"`; for Shorts: `"YouTube Shorts"` (exact strings — matched by `_SOURCE_TYPE` in `api.py`)
- `_SOURCE_LIMIT = 12` cap applied in `api.py` (unchanged)
- Glacier design system only — no new colours in frontend changes
- Fonts: Playfair Display + Hanken Grotesk only

---

## Files

| Action | Path | Purpose |
|--------|------|---------|
| Create | `connectors/youtube.py` | Connector — session auth + ytInitialData extraction |
| Modify | `db/store.py` | `refresh_direct_images()` — handle YouTube thumbnail from `raw` |
| Modify | `api.py` | Import + wire connector; add source category/type mappings; add `channel` to shaped item |
| Modify | `frontend/src/components/ExplorePage.jsx` | Add "Videos" and "Shorts" to format filter bar |
| Modify | `frontend/src/components/FeedCard.jsx` | Show channel name as subtitle when source is YouTube/YouTube Shorts |
| Modify | `.gitignore` | Add `sessions/` |

---

## Component 1: `connectors/youtube.py`

### Session management — `_ensure_auth(p)`

```
sessions/youtube.json exists?
  YES → launch headless, load storage_state, goto youtube.com
        → check for #avatar-btn (3s timeout)
        → logged in? → return (ctx, page)
        → not logged in? → ctx.close(), fall through to fresh login
  NO / expired → launch headed (headless=False), goto youtube.com
        → poll loop:
            every 10s: check for #avatar-btn
            at 5 min elapsed: print "Still waiting — please complete sign-in in the browser window..."
            continue polling until avatar found (no hard timeout)
        → save ctx.storage_state(path="sessions/youtube.json")
        → ctx.close()
        → launch headless, load saved state, goto youtube.com
        → return (ctx, page)
```

### Content extraction — `_parse_home(data)`

Input: `window.ytInitialData` dict from `page.evaluate("window.ytInitialData")`.

Path to feed items:
```
data
  ["contents"]
  ["twoColumnBrowseResultsRenderer"]
  ["tabs"][0]
  ["tabRenderer"]["content"]
  ["richGridRenderer"]["contents"]   ← list of rich items
```

Each rich item is one of:
- `richItemRenderer.content.videoRenderer` → regular video
- `richSectionRenderer.content.reelShelfRenderer.items[N].reelItemRenderer` → Short

**Regular video fields:**
| Field | ytInitialData path |
|-------|--------------------|
| `video_id` | `.videoId` |
| `title` | `.title.runs[0].text` |
| `channel` | `.ownerText.runs[0].text` |
| `thumbnail_url` | `.thumbnail.thumbnails[-1].url` |
| `duration` | `.lengthText.simpleText` (e.g. `"12:34"`) — absent for Shorts |
| `published_at` | `.publishedTimeText.simpleText` (e.g. `"3 hours ago"`) |

**Short fields:**
| Field | ytInitialData path |
|-------|--------------------|
| `video_id` | `.videoId` |
| `title` | `.headline.simpleText` |
| `channel` | `.navigationEndpoint.reelWatchEndpoint.overlay...` (best-effort; fallback `""`) |
| `thumbnail_url` | `https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg` (constructed) |
| `published_at` | `""` (not available in reel renderer) |

**Output shape per item:**

Regular video:
```python
{
    "title": title,
    "url": f"https://www.youtube.com/watch?v={video_id}",
    "source": "YouTube",
    "published_at": published_at_str,   # e.g. "3 hours ago"
    "raw": {
        "channel": channel,
        "video_id": video_id,
        "thumbnail_url": thumbnail_url,
        "duration": duration,           # None for Shorts
        "is_short": False,
    },
}
```

Short:
```python
{
    "title": title,
    "url": f"https://www.youtube.com/shorts/{video_id}",
    "source": "YouTube Shorts",
    "published_at": "",
    "raw": {
        "channel": channel,
        "video_id": video_id,
        "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        "duration": None,
        "is_short": True,
    },
}
```

### `fetch()` top-level

`_session_exists()` = `SESSION_PATH.exists()` (simple path check).

`_ensure_auth(p)` owns the full browser lifecycle — launches headed or headless as needed, handles re-auth on expired session, returns `(browser, ctx, page)` ready to scrape. `fetch()` never calls `p.chromium.launch()` directly.

```python
def fetch() -> list[dict]:
    with sync_playwright() as p:
        browser, ctx, page = _ensure_auth(p)
        page.goto("https://www.youtube.com/")
        page.wait_for_load_state("networkidle")
        data = page.evaluate("window.ytInitialData")
        items = _parse_home(data)
        ctx.close()
        browser.close()
    return items
```

Error handling: wrap `_parse_home` in try/except; if `ytInitialData` path fails (YouTube restructured), log warning and return `[]`. Connector failure must never crash the refresh pipeline.

---

## Component 2: `db/store.py` — `refresh_direct_images()`

Existing function already handles items with direct image URLs. Extend: for items where `source` is `"YouTube"` or `"YouTube Shorts"` and `image_url IS NULL`, read `raw` JSON, extract `thumbnail_url`, write to `image_url` with `image_type = 'article'`.

```python
# pseudocode addition inside refresh_direct_images():
rows = conn.execute(
    "SELECT id, raw FROM items WHERE source IN ('YouTube','YouTube Shorts') AND image_url IS NULL"
).fetchall()
for row_id, raw_json in rows:
    raw = json.loads(raw_json or "{}")
    thumb = raw.get("thumbnail_url")
    if thumb:
        conn.execute(
            "UPDATE items SET image_url=?, image_type='article' WHERE id=?",
            (thumb, row_id)
        )
conn.commit()
```

---

## Component 3: `api.py`

```python
from connectors.youtube import fetch as fetch_youtube

_SOURCE_CATEGORY["YouTube"]        = ["Technology"]
_SOURCE_CATEGORY["YouTube Shorts"] = ["Technology"]

_SOURCE_TYPE["YouTube"]        = "Video"
_SOURCE_TYPE["YouTube Shorts"] = "Short"
```

In `_do_refresh()`, add to `all_items`:
```python
+ fetch_youtube()[:_SOURCE_LIMIT]
```

In `_shape_item()`, add `channel` field. `raw` from DB is a JSON string — parse it:
```python
import json as _json

def _get_raw(item):
    r = item.get("raw", "{}")
    if isinstance(r, str):
        try:
            return _json.loads(r)
        except Exception:
            return {}
    return r or {}

# inside _shape_item():
"channel": _get_raw(item).get("channel", ""),
```

---

## Component 4: `frontend/src/components/ExplorePage.jsx`

Format filter bar currently: `["All", "Articles", "Newsletters", "Papers"]`

Change to: `["All", "Articles", "Newsletters", "Papers", "Videos", "Shorts"]`

No other frontend changes needed for format filter — the `type` query param already passes through to `/feed`.

---

## Component 5: `frontend/src/components/FeedCard.jsx`

When `item.source === "YouTube"` or `item.source === "YouTube Shorts"`, display channel name as a subtitle line below the source pill, e.g.:

```
YouTube  •  Fireship
```

Use `item.channel` (new field from `_shape_item`). If empty string, render nothing extra.

---

## Component 6: `.gitignore`

Add:
```
sessions/
```

---

## Error handling summary

| Scenario | Behaviour |
|----------|-----------|
| `ytInitialData` parse fails | Log warning, return `[]` — refresh continues with other connectors |
| Session expired mid-run | Catch navigation redirect to sign-in, re-run `_ensure_auth`, retry once |
| No Shorts shelf on home page | `reelShelfRenderer` block simply absent — parse returns empty Shorts list, no error |
| Thumbnail 404 | `image_url` set but broken; existing logo fallback in feed card handles gracefully |
| `published_at` unparseable | `_parse_ts` returns `None`; item ranked as oldest — acceptable |

---

## Out of scope

- Instagram and LinkedIn connectors (separate spec)
- YouTube subscriptions feed (`/feed/subscriptions`) — home feed covers this
- Video playback inside BYOF
- Download or caching of video content
- YouTube Data API v3 OAuth (browser session is sufficient)
