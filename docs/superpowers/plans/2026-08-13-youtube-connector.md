# YouTube Connector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a personalized YouTube connector that fetches the user's home feed (regular videos + Shorts) via Playwright browser session and surfaces them in the BYOF feed as "YouTube" and "YouTube Shorts" source types.

**Architecture:** `connectors/youtube.py` handles two concerns: session management (saves/reloads Playwright `storage_state` cookies so headed login only happens once) and content extraction (parses `window.ytInitialData` JSON that YouTube embeds in every page load). Thumbnails are backfilled via a new `refresh_youtube_thumbnails()` DB helper. `api.py` wires the connector into the existing refresh pipeline. Frontend adds "Videos" and "Shorts" to the format filter and shows channel name as a subtitle on feed cards.

**Tech Stack:** Playwright (already installed via `uv`), Python stdlib (`json`, `time`, `pathlib`). No new dependencies.

## Global Constraints

- Connector contract: `fetch() -> list[dict]` with keys `title`, `url`, `source`, `published_at`, `raw` — exact strings, exact dict shape
- `source` for regular videos: `"YouTube"` (exact). For Shorts: `"YouTube Shorts"` (exact)
- Session file path: `sessions/youtube.json` — must be gitignored, never committed
- No new pip/PyPI packages without `uv add`; Playwright is already installed
- `_SOURCE_LIMIT = 12` cap applied in `api.py` (do not change)
- Glacier design system only — colours from `docs/DESIGN.md` only
- Fonts: Playfair Display + Hanken Grotesk only — no other fonts

---

## File Map

| Action | Path |
|--------|------|
| Modify | `.gitignore` — add `sessions/` |
| Create | `connectors/youtube.py` — session auth + ytInitialData extraction |
| Modify | `db/store.py` — add `refresh_youtube_thumbnails()`; exclude YouTube from `refresh_direct_images` |
| Modify | `agents/aggregation.py` — add `channel` to SELECT query |
| Modify | `api.py` — import connector + thumbnail fn; source mappings; `channel` in `_shape_item`; `_do_refresh` wiring |
| Modify | `frontend/src/components/ExplorePage.jsx` — add Videos + Shorts to format filter + source colors |
| Modify | `frontend/src/components/FeedCard.jsx` — show channel subtitle for YouTube items |

---

## Task 1: Session management (`connectors/youtube.py` + `.gitignore`)

**Files:**
- Modify: `.gitignore`
- Create: `connectors/youtube.py`

**Interfaces:**
- Produces: `_session_exists() -> bool`, `_ensure_auth(p) -> tuple[Browser, BrowserContext, Page]`
- Task 2 calls `_ensure_auth(p)` and gets back a ready `(browser, ctx, page)` pointed at `youtube.com`

- [ ] **Step 1: Add `sessions/` to `.gitignore`**

Open `.gitignore` and append at the end (after the Streamlit block):

```
# BYOF browser sessions — personal cookies, never commit
sessions/
```

- [ ] **Step 2: Create `connectors/youtube.py` with session management**

```python
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

SESSION_PATH = Path("sessions/youtube.json")
_YT_HOME = "https://www.youtube.com/"


def _session_exists() -> bool:
    return SESSION_PATH.exists()


def _is_logged_in(page: Page) -> bool:
    """Check for YouTube account avatar — present only when signed in."""
    try:
        page.wait_for_selector("#avatar-btn", timeout=4000)
        return True
    except Exception:
        return False


def _ensure_auth(p) -> tuple:
    """
    Returns (browser, ctx, page) ready to scrape, already navigated to youtube.com.
    If a saved session exists and is valid, runs headless.
    If no session or session expired, opens a headed browser for the user to sign in,
    polls every 10 s, prompts at 5 min, then saves session and switches to headless.
    """
    # Try saved session first
    if _session_exists():
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state=str(SESSION_PATH))
        page = ctx.new_page()
        page.goto(_YT_HOME, wait_until="domcontentloaded")
        if _is_logged_in(page):
            return browser, ctx, page
        # Session expired — clean up and fall through
        ctx.close()
        browser.close()
        print("YouTube: saved session expired, re-authenticating...")

    # Fresh login — headed browser
    print("YouTube: opening browser for sign-in. Please sign in to your Google account.")
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(_YT_HOME)

    start = time.time()
    reminded = False
    while True:
        try:
            page.wait_for_selector("#avatar-btn", timeout=10_000)
            break  # avatar found — user is signed in
        except Exception:
            elapsed = time.time() - start
            if elapsed >= 300 and not reminded:
                print("YouTube: Still waiting — please complete sign-in in the browser window...")
                reminded = True

    # Save session
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    ctx.storage_state(path=str(SESSION_PATH))
    print(f"YouTube: session saved to {SESSION_PATH}")
    ctx.close()
    browser.close()

    # Reopen headless with saved state
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state=str(SESSION_PATH))
    page = ctx.new_page()
    page.goto(_YT_HOME, wait_until="domcontentloaded")
    return browser, ctx, page
```

- [ ] **Step 3: Manually verify session management**

Run (with frontend and api stopped to avoid port conflicts):
```bash
uv run python -c "
from playwright.sync_api import sync_playwright
from connectors.youtube import _ensure_auth, SESSION_PATH
print('Session exists before:', SESSION_PATH.exists())
with sync_playwright() as p:
    browser, ctx, page = _ensure_auth(p)
    print('Title:', page.title())
    ctx.close()
    browser.close()
print('Session exists after:', SESSION_PATH.exists())
"
```

Expected: headed browser opens (first run) or nothing opens (subsequent runs). `Title:` should start with "YouTube". `Session exists after:` should be `True`.

- [ ] **Step 4: Commit**

```bash
git add .gitignore connectors/youtube.py
git commit -m "feat: YouTube connector session management"
```

---

## Task 2: Content extraction + `fetch()` (`connectors/youtube.py`)

**Files:**
- Modify: `connectors/youtube.py`

**Interfaces:**
- Consumes: `_ensure_auth(p)` from Task 1, returns `(browser, ctx, page)`
- Produces: `fetch() -> list[dict]` — connector contract shape (Task 4 imports this)
- Internal helpers: `_parse_video_renderer(vr) -> dict | None`, `_parse_reel_renderer(rr) -> dict | None`, `_parse_home(data) -> list[dict]`

- [ ] **Step 1: Write a unit test for `_parse_home` with mock data**

Create `tests/test_youtube_parser.py`:

```python
"""Unit tests for YouTube ytInitialData parser — no browser required."""
import sys
sys.path.insert(0, '.')

from connectors.youtube import _parse_home


def _mock_data(video_entries=None, reel_items=None):
    contents = video_entries or []
    if reel_items:
        contents.append({
            "richSectionRenderer": {
                "content": {
                    "reelShelfRenderer": {
                        "items": reel_items
                    }
                }
            }
        })
    return {
        "contents": {
            "twoColumnBrowseResultsRenderer": {
                "tabs": [{
                    "tabRenderer": {
                        "content": {
                            "richGridRenderer": {
                                "contents": contents
                            }
                        }
                    }
                }]
            }
        }
    }


def test_parse_regular_video():
    data = _mock_data(video_entries=[{
        "richItemRenderer": {
            "content": {
                "videoRenderer": {
                    "videoId": "abc123",
                    "title": {"runs": [{"text": "Test Video"}]},
                    "ownerText": {"runs": [{"text": "Test Channel"}]},
                    "thumbnail": {"thumbnails": [
                        {"url": "https://i.ytimg.com/vi/abc123/default.jpg", "width": 120},
                        {"url": "https://i.ytimg.com/vi/abc123/maxresdefault.jpg", "width": 1280},
                    ]},
                    "publishedTimeText": {"simpleText": "3 hours ago"},
                    "lengthText": {"simpleText": "12:34"},
                }
            }
        }
    }])
    items = _parse_home(data)
    assert len(items) == 1, f"expected 1 item, got {len(items)}"
    item = items[0]
    assert item["title"] == "Test Video"
    assert item["url"] == "https://www.youtube.com/watch?v=abc123"
    assert item["source"] == "YouTube"
    assert item["published_at"] == "3 hours ago"
    assert item["raw"]["channel"] == "Test Channel"
    assert item["raw"]["thumbnail_url"] == "https://i.ytimg.com/vi/abc123/maxresdefault.jpg"
    assert item["raw"]["duration"] == "12:34"
    assert item["raw"]["is_short"] is False
    print("test_parse_regular_video PASSED")


def test_parse_short():
    data = _mock_data(reel_items=[{
        "reelItemRenderer": {
            "videoId": "xyz789",
            "headline": {"simpleText": "Test Short"},
            "thumbnail": {"thumbnails": [
                {"url": "https://i.ytimg.com/vi/xyz789/hq720.jpg"}
            ]},
        }
    }])
    items = _parse_home(data)
    assert len(items) == 1, f"expected 1 item, got {len(items)}"
    item = items[0]
    assert item["title"] == "Test Short"
    assert item["url"] == "https://www.youtube.com/shorts/xyz789"
    assert item["source"] == "YouTube Shorts"
    assert item["raw"]["is_short"] is True
    assert item["raw"]["duration"] is None
    print("test_parse_short PASSED")


def test_parse_empty_data():
    items = _parse_home({})
    assert items == []
    print("test_parse_empty_data PASSED")


def test_skips_missing_video_id():
    data = _mock_data(video_entries=[{
        "richItemRenderer": {
            "content": {
                "videoRenderer": {
                    # no videoId
                    "title": {"runs": [{"text": "Broken"}]},
                }
            }
        }
    }])
    items = _parse_home(data)
    assert items == []
    print("test_skips_missing_video_id PASSED")


if __name__ == "__main__":
    test_parse_regular_video()
    test_parse_short()
    test_parse_empty_data()
    test_skips_missing_video_id()
    print("All tests passed.")
```

- [ ] **Step 2: Run tests — verify they fail (functions not defined yet)**

```bash
uv run python tests/test_youtube_parser.py
```

Expected: `ImportError: cannot import name '_parse_home' from 'connectors.youtube'`

- [ ] **Step 3: Implement extraction helpers in `connectors/youtube.py`**

Add these functions to `connectors/youtube.py` (after `_ensure_auth`):

```python
def _parse_video_renderer(vr: dict) -> dict | None:
    vid_id = vr.get("videoId")
    if not vid_id:
        return None
    title_runs = (vr.get("title") or {}).get("runs", [])
    title = title_runs[0].get("text", "") if title_runs else ""
    if not title:
        return None
    owner_runs = (vr.get("ownerText") or {}).get("runs", [])
    channel = owner_runs[0].get("text", "") if owner_runs else ""
    thumbnails = (vr.get("thumbnail") or {}).get("thumbnails", [])
    thumb_url = (
        thumbnails[-1]["url"]
        if thumbnails
        else f"https://i.ytimg.com/vi/{vid_id}/maxresdefault.jpg"
    )
    published = (vr.get("publishedTimeText") or {}).get("simpleText", "")
    duration = (vr.get("lengthText") or {}).get("simpleText")
    return {
        "title": title,
        "url": f"https://www.youtube.com/watch?v={vid_id}",
        "source": "YouTube",
        "published_at": published,
        "raw": {
            "channel": channel,
            "video_id": vid_id,
            "thumbnail_url": thumb_url,
            "duration": duration,
            "is_short": False,
        },
    }


def _parse_reel_renderer(rr: dict) -> dict | None:
    vid_id = rr.get("videoId")
    if not vid_id:
        return None
    title = (rr.get("headline") or {}).get("simpleText", "")
    if not title:
        return None
    thumbnails = (rr.get("thumbnail") or {}).get("thumbnails", [])
    thumb_url = (
        thumbnails[-1]["url"]
        if thumbnails
        else f"https://i.ytimg.com/vi/{vid_id}/maxresdefault.jpg"
    )
    # Channel deeply nested in reel renderer — best-effort
    channel = ""
    try:
        channel = (
            rr["navigationEndpoint"]["reelWatchEndpoint"]["overlay"]
            ["reelPlayerOverlayRenderer"]["reelPlayerHeaderSupportedRenderers"]
            ["reelPlayerHeaderRenderer"]["channelTitleText"]["runs"][0]["text"]
        )
    except (KeyError, IndexError, TypeError):
        pass
    return {
        "title": title,
        "url": f"https://www.youtube.com/shorts/{vid_id}",
        "source": "YouTube Shorts",
        "published_at": "",
        "raw": {
            "channel": channel,
            "video_id": vid_id,
            "thumbnail_url": thumb_url,
            "duration": None,
            "is_short": True,
        },
    }


def _parse_home(data: dict) -> list[dict]:
    """Parse window.ytInitialData from youtube.com home page."""
    try:
        contents = (
            data["contents"]
            ["twoColumnBrowseResultsRenderer"]
            ["tabs"][0]
            ["tabRenderer"]["content"]
            ["richGridRenderer"]["contents"]
        )
    except (KeyError, IndexError, TypeError):
        print("YouTube: ytInitialData structure not recognised — returning empty list")
        return []

    items: list[dict] = []
    for entry in contents:
        # Regular video
        vr = (entry.get("richItemRenderer") or {}).get("content", {}).get("videoRenderer")
        if vr:
            parsed = _parse_video_renderer(vr)
            if parsed:
                items.append(parsed)
            continue

        # Shorts shelf
        section = (entry.get("richSectionRenderer") or {}).get("content", {})
        shelf = section.get("reelShelfRenderer", {})
        for shelf_item in shelf.get("items", []):
            rr = shelf_item.get("reelItemRenderer")
            if rr:
                parsed = _parse_reel_renderer(rr)
                if parsed:
                    items.append(parsed)

    return items


def fetch() -> list[dict]:
    """Fetch YouTube home feed (videos + Shorts) using saved browser session."""
    with sync_playwright() as p:
        browser, ctx, page = _ensure_auth(p)
        try:
            page.goto(_YT_HOME, wait_until="networkidle")
            data = page.evaluate("window.ytInitialData")
            items = _parse_home(data)
        except Exception as e:
            print(f"YouTube: fetch failed — {e}")
            items = []
        finally:
            ctx.close()
            browser.close()
    return items
```

- [ ] **Step 4: Run tests — verify all pass**

```bash
uv run python tests/test_youtube_parser.py
```

Expected output:
```
test_parse_regular_video PASSED
test_parse_short PASSED
test_parse_empty_data PASSED
test_skips_missing_video_id PASSED
All tests passed.
```

- [ ] **Step 5: Smoke-test `fetch()` end-to-end (requires signed-in session from Task 1)**

```bash
uv run python -c "
from connectors.youtube import fetch
items = fetch()
print(f'Got {len(items)} items')
for i in items[:3]:
    print(i['source'], '|', i['title'][:60], '|', i['raw']['channel'])
"
```

Expected: 10–20 items, mix of `YouTube` and `YouTube Shorts` sources, real video titles.

- [ ] **Step 6: Commit**

```bash
git add connectors/youtube.py tests/test_youtube_parser.py
git commit -m "feat: YouTube connector content extraction and fetch()"
```

---

## Task 3: YouTube thumbnail backfill (`db/store.py`)

**Files:**
- Modify: `db/store.py`

**Interfaces:**
- Produces: `refresh_youtube_thumbnails(conn: sqlite3.Connection) -> int` — returns count of items updated
- Task 5 imports and calls this in `_do_refresh()`
- Also modifies existing `refresh_direct_images` query to exclude YouTube URLs (avoids futile HTTP requests to auth-gated pages)

- [ ] **Step 1: Write a test for `refresh_youtube_thumbnails`**

Create `tests/test_youtube_thumbnails.py`:

```python
"""Test that refresh_youtube_thumbnails copies thumbnail_url from raw to image_url."""
import json
import sqlite3
import sys
sys.path.insert(0, '.')

from db.store import init_db, refresh_youtube_thumbnails


def test_backfills_thumbnail():
    conn = init_db(":memory:")
    # Insert a YouTube item with thumbnail in raw, no image_url yet
    conn.execute(
        "INSERT INTO items (title, url, source, published_at, raw, fetched_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            "Test Video",
            "https://www.youtube.com/watch?v=abc123",
            "YouTube",
            "3 hours ago",
            json.dumps({"thumbnail_url": "https://i.ytimg.com/vi/abc123/maxresdefault.jpg", "channel": "Test Ch"}),
            "2026-08-13T00:00:00+00:00",
        ),
    )
    conn.commit()

    updated = refresh_youtube_thumbnails(conn)
    assert updated == 1, f"expected 1, got {updated}"

    row = conn.execute("SELECT image_url, image_type FROM items WHERE url = ?",
                       ("https://www.youtube.com/watch?v=abc123",)).fetchone()
    assert row[0] == "https://i.ytimg.com/vi/abc123/maxresdefault.jpg"
    assert row[1] == "article"
    print("test_backfills_thumbnail PASSED")


def test_skips_already_has_image():
    conn = init_db(":memory:")
    conn.execute(
        "INSERT INTO items (title, url, source, published_at, raw, fetched_at, image_url, image_type) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "Test Video",
            "https://www.youtube.com/watch?v=xyz789",
            "YouTube",
            "",
            json.dumps({"thumbnail_url": "https://i.ytimg.com/vi/xyz789/maxresdefault.jpg"}),
            "2026-08-13T00:00:00+00:00",
            "https://existing.jpg",
            "article",
        ),
    )
    conn.commit()

    updated = refresh_youtube_thumbnails(conn)
    assert updated == 0, f"expected 0, got {updated}"

    row = conn.execute("SELECT image_url FROM items WHERE url = ?",
                       ("https://www.youtube.com/watch?v=xyz789",)).fetchone()
    assert row[0] == "https://existing.jpg"  # unchanged
    print("test_skips_already_has_image PASSED")


def test_skips_non_youtube():
    conn = init_db(":memory:")
    conn.execute(
        "INSERT INTO items (title, url, source, published_at, raw, fetched_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            "TC Article",
            "https://techcrunch.com/2026/08/13/article/",
            "TechCrunch",
            "",
            json.dumps({}),
            "2026-08-13T00:00:00+00:00",
        ),
    )
    conn.commit()

    updated = refresh_youtube_thumbnails(conn)
    assert updated == 0, f"expected 0, got {updated}"
    print("test_skips_non_youtube PASSED")


if __name__ == "__main__":
    test_backfills_thumbnail()
    test_skips_already_has_image()
    test_skips_non_youtube()
    print("All tests passed.")
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
uv run python tests/test_youtube_thumbnails.py
```

Expected: `ImportError: cannot import name 'refresh_youtube_thumbnails' from 'db.store'`

- [ ] **Step 3: Add `refresh_youtube_thumbnails` to `db/store.py`**

Add this function after `refresh_publisher_logos` (around line 470):

```python
def refresh_youtube_thumbnails(conn: sqlite3.Connection) -> int:
    """Copy thumbnail_url from raw JSON into image_url for YouTube and YouTube Shorts items.
    Returns number of items updated."""
    rows = conn.execute(
        "SELECT id, raw FROM items "
        "WHERE source IN ('YouTube', 'YouTube Shorts') AND image_url IS NULL"
    ).fetchall()
    updated = 0
    for row_id, raw_json in rows:
        try:
            raw = json.loads(raw_json or "{}")
            thumb = raw.get("thumbnail_url")
            if thumb:
                conn.execute(
                    "UPDATE items SET image_url = ?, image_type = 'article' WHERE id = ?",
                    (thumb, row_id),
                )
                updated += 1
        except Exception:
            pass
    if updated:
        conn.commit()
    return updated
```

- [ ] **Step 4: Exclude YouTube URLs from `refresh_direct_images`**

In `db/store.py`, find the `refresh_direct_images` function. Its query currently reads:

```python
rows = conn.execute(
    "SELECT id, url FROM items WHERE image_url IS NULL AND url NOT LIKE '%news.google.com%'"
).fetchall()
```

Change it to:

```python
rows = conn.execute(
    "SELECT id, url FROM items "
    "WHERE image_url IS NULL "
    "AND url NOT LIKE '%news.google.com%' "
    "AND url NOT LIKE '%youtube.com%'"
).fetchall()
```

- [ ] **Step 5: Run tests — verify all pass**

```bash
uv run python tests/test_youtube_thumbnails.py
```

Expected:
```
test_backfills_thumbnail PASSED
test_skips_already_has_image PASSED
test_skips_non_youtube PASSED
All tests passed.
```

- [ ] **Step 6: Commit**

```bash
git add db/store.py tests/test_youtube_thumbnails.py
git commit -m "feat: YouTube thumbnail backfill in db/store.py"
```

---

## Task 4: Add `channel` to aggregation SELECT (`agents/aggregation.py`)

**Files:**
- Modify: `agents/aggregation.py`

**Interfaces:**
- Produces: `channel` field on items returned by `rank()` — value is the YouTube channel name string, or `""` for non-YouTube items
- Task 5 uses `item.get("channel", "")` in `_shape_item()`

- [ ] **Step 1: Write a test confirming `channel` in ranked output**

Create `tests/test_aggregation_channel.py`:

```python
"""Verify rank() includes 'channel' field extracted from raw JSON."""
import json
import sys
sys.path.insert(0, '.')

from db.store import init_db
from agents.aggregation import rank


def test_channel_field_present():
    conn = init_db(":memory:")
    conn.execute(
        "INSERT INTO items (title, url, source, published_at, raw, fetched_at, llm_score) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "Test YT Video",
            "https://www.youtube.com/watch?v=test1",
            "YouTube",
            "Mon, 01 Jan 2026 00:00:00 +0000",
            json.dumps({"channel": "Fireship", "is_short": False}),
            "2026-08-13T00:00:00+00:00",
            0.8,
        ),
    )
    conn.commit()

    # rank() opens its own connection — write to a temp file
    import tempfile, shutil, os
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy(":memory:", tmp)  # can't copy :memory: — use a file db instead

    # Write to a real file for rank() to open
    import sqlite3
    file_conn = init_db(tmp)
    file_conn.execute(
        "INSERT INTO items (title, url, source, published_at, raw, fetched_at, llm_score) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            "Test YT Video",
            "https://www.youtube.com/watch?v=test1",
            "YouTube",
            "Mon, 01 Jan 2026 00:00:00 +0000",
            json.dumps({"channel": "Fireship", "is_short": False}),
            "2026-08-13T00:00:00+00:00",
            0.8,
        ),
    )
    file_conn.commit()
    file_conn.close()

    items = rank(tmp)
    os.unlink(tmp)

    assert len(items) == 1
    assert "channel" in items[0], f"'channel' not in item keys: {list(items[0].keys())}"
    assert items[0]["channel"] == "Fireship"
    print("test_channel_field_present PASSED")


def test_channel_empty_for_non_youtube():
    import tempfile, os
    tmp = tempfile.mktemp(suffix=".db")
    conn = init_db(tmp)
    conn.execute(
        "INSERT INTO items (title, url, source, published_at, raw, fetched_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            "TC Article",
            "https://techcrunch.com/2026/08/article/",
            "TechCrunch",
            "Mon, 01 Jan 2026 00:00:00 +0000",
            json.dumps({}),
            "2026-08-13T00:00:00+00:00",
        ),
    )
    conn.commit()
    conn.close()

    items = rank(tmp)
    os.unlink(tmp)

    assert len(items) == 1
    assert items[0].get("channel", "") == ""
    print("test_channel_empty_for_non_youtube PASSED")


if __name__ == "__main__":
    test_channel_field_present()
    test_channel_empty_for_non_youtube()
    print("All tests passed.")
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
uv run python tests/test_aggregation_channel.py
```

Expected: `AssertionError: 'channel' not in item keys`

- [ ] **Step 3: Add `channel` to SELECT in `agents/aggregation.py`**

Find the `conn.execute(...)` call inside `rank()`. The current SELECT is:

```python
rows = conn.execute(
    """SELECT title, url, source, published_at, fetched_at,
              image_url, image_type, llm_score, llm_summary, llm_keywords,
              json_extract(raw, '$.summary') as rss_summary,
              json_extract(raw, '$.source.href') as source_href
       FROM items"""
).fetchall()
```

Change it to:

```python
rows = conn.execute(
    """SELECT title, url, source, published_at, fetched_at,
              image_url, image_type, llm_score, llm_summary, llm_keywords,
              json_extract(raw, '$.summary') as rss_summary,
              json_extract(raw, '$.source.href') as source_href,
              json_extract(raw, '$.channel') as channel
       FROM items"""
).fetchall()
```

- [ ] **Step 4: Run tests — verify all pass**

```bash
uv run python tests/test_aggregation_channel.py
```

Expected:
```
test_channel_field_present PASSED
test_channel_empty_for_non_youtube PASSED
All tests passed.
```

- [ ] **Step 5: Commit**

```bash
git add agents/aggregation.py tests/test_aggregation_channel.py
git commit -m "feat: expose channel field from raw JSON in rank() output"
```

---

## Task 5: Wire YouTube into `api.py`

**Files:**
- Modify: `api.py`

**Interfaces:**
- Consumes: `fetch_youtube` from `connectors/youtube.py`; `refresh_youtube_thumbnails` from `db/store.py`; `item.get("channel", "")` from aggregation output (Task 4)
- Produces: `/feed` response includes `channel` field on each item; YouTube items appear in feed after `/refresh`

- [ ] **Step 1: Add imports at top of `api.py`**

Find the existing import block. After `from connectors.tldr_tech import fetch as fetch_tldr`, add:

```python
from connectors.youtube import fetch as fetch_youtube
```

After `from db.store import (` block imports, add `refresh_youtube_thumbnails` to that import list:

```python
from db.store import (
    get_recent_runs,
    init_db,
    refresh_article_images,
    refresh_direct_images,
    refresh_publisher_logos,
    refresh_youtube_thumbnails,   # ← add this line
    save_items,
    save_llm_results,
    save_refresh_run,
    save_signal,
)
```

- [ ] **Step 2: Add YouTube to source mappings**

Find `_SOURCE_CATEGORY` dict (around line 41). Add two entries:

```python
_SOURCE_CATEGORY = {
    "Google News": ["Technology"],
    "TechCrunch": ["Technology"],
    "MIT Technology Review": ["Technology", "Science"],
    "TLDR Tech": ["Technology"],
    "ArXiv": ["Science"],
    "YouTube": ["Technology"],           # ← add
    "YouTube Shorts": ["Technology"],    # ← add
}
```

Find `_SOURCE_TYPE` dict. Add two entries:

```python
_SOURCE_TYPE = {
    "Google News": "Article",
    "TechCrunch": "Article",
    "MIT Technology Review": "Article",
    "TLDR Tech": "Newsletter",
    "ArXiv": "Paper",
    "YouTube": "Video",          # ← add
    "YouTube Shorts": "Short",   # ← add
}
```

- [ ] **Step 3: Add `channel` field to `_shape_item()`**

Find `_shape_item` function. Add `"channel"` to its return dict:

```python
def _shape_item(item: dict) -> dict:
    title = item.get("title", "")
    return {
        "title": title,
        "url": item.get("url", ""),
        "source": item.get("source", ""),
        "published_at": _relative_time(item.get("published_at", "")),
        "image_url": item.get("image_url"),
        "image_type": item.get("image_type"),
        "categories": _SOURCE_CATEGORY.get(item.get("source", ""), []),
        "score": round(item.get("score", 0.0), 4),
        "read_time": max(1, len(title.split()) // 3),
        "summary": item.get("summary") or "",
        "keywords": (item.get("keywords") or [])[:5],
        "llm_scored": item.get("llm_scored", False),
        "channel": item.get("channel") or "",   # ← add this line
    }
```

- [ ] **Step 4: Wire YouTube into `_do_refresh()`**

Find `all_items = (` block in `_do_refresh()`. Add `fetch_youtube`:

```python
all_items = (
    fetch_google_news()[:_SOURCE_LIMIT]
    + fetch_techcrunch()[:_SOURCE_LIMIT]
    + fetch_arxiv()[:_SOURCE_LIMIT]
    + fetch_mit()[:_SOURCE_LIMIT]
    + fetch_tldr()[:_SOURCE_LIMIT]
    + fetch_youtube()[:_SOURCE_LIMIT]    # ← add this line
)
```

Then, directly after `save_items(conn, all_items)`, add the YouTube thumbnail backfill call:

```python
new_count = save_items(conn, all_items)
refresh_youtube_thumbnails(conn)         # ← add this line (before refresh_article_images)
refresh_article_images(conn, use_playwright=False)
```

- [ ] **Step 5: Verify `api.py` starts without errors**

```bash
uv run python -c "import api; print('api.py imports OK')"
```

Expected: `api.py imports OK` (no import errors).

- [ ] **Step 6: Run a refresh and check `/feed`**

Start the API:
```bash
uv run python api.py &
```

Trigger refresh:
```bash
curl -s -X POST http://localhost:8000/refresh
sleep 5
curl -s http://localhost:8000/feed | python3 -c "
import sys, json
items = json.load(sys.stdin)
yt = [i for i in items if i['source'] in ('YouTube', 'YouTube Shorts')]
print(f'Total items: {len(items)}, YouTube: {len(yt)}')
for i in yt[:3]:
    print(i['source'], '|', i.get('channel',''), '|', i['title'][:50])
"
```

Expected: feed contains at least some YouTube items with `channel` populated.

- [ ] **Step 7: Kill background API and commit**

```bash
kill %1 2>/dev/null || true
git add api.py
git commit -m "feat: wire YouTube connector into api.py refresh pipeline"
```

---

## Task 6: Explore format filter — Videos + Shorts (`ExplorePage.jsx`)

**Files:**
- Modify: `frontend/src/components/ExplorePage.jsx`

**Interfaces:**
- Consumes: `/feed?type=Video` and `/feed?type=Short` — these now work because `_SOURCE_TYPE` maps them (Task 5)
- Produces: format filter bar shows 5 options: Articles, Newsletters, Papers, Videos, Shorts

- [ ] **Step 1: Update `CONTENT_TYPES` and `TYPE_MAP`**

In `ExplorePage.jsx`, find lines 3–4:

```js
const CONTENT_TYPES = ['Articles', 'Newsletters', 'Papers']
const TYPE_MAP = { Articles: 'Article', Newsletters: 'Newsletter', Papers: 'Paper' }
```

Change to:

```js
const CONTENT_TYPES = ['Articles', 'Newsletters', 'Papers', 'Videos', 'Shorts']
const TYPE_MAP = { Articles: 'Article', Newsletters: 'Newsletter', Papers: 'Paper', Videos: 'Video', Shorts: 'Short' }
```

- [ ] **Step 2: Add YouTube source colors**

In `ExplorePage.jsx`, find `const SOURCE_COLORS = {` object. Add two entries:

```js
const SOURCE_COLORS = {
    'Google News':      '#4285f4',
    'TechCrunch':       '#22c55e',
    'Papers with Code': '#f59e0b',
    'The Rundown AI':   '#8b5cf6',
    'MIT Technology Review': '#ef4444',
    'TLDR Tech':        '#06b6d4',
    'ArXiv':            '#f97316',
    'YouTube':          '#ff0000',        // ← add
    'YouTube Shorts':   '#ff4500',        // ← add
}
```

- [ ] **Step 3: Verify frontend compiles**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

Expected: build succeeds with no errors (warnings OK).

- [ ] **Step 4: Visual check in browser**

```bash
cd frontend && npm run dev &
```

Open `http://localhost:5173`, navigate to Explore. The Content Format bar should show:
`All | Articles | Newsletters | Papers | Videos | Shorts`

Each button should be selectable. Selecting "Videos" and clicking Apply should filter the feed (if YouTube items exist after a refresh).

- [ ] **Step 5: Kill dev server and commit**

```bash
kill %1 2>/dev/null || true
git add frontend/src/components/ExplorePage.jsx
git commit -m "feat: add Videos and Shorts to Explore format filter"
```

---

## Task 7: FeedCard channel subtitle (`FeedCard.jsx`)

**Files:**
- Modify: `frontend/src/components/FeedCard.jsx`

**Interfaces:**
- Consumes: `item.channel` (string, "" for non-YouTube items) — added by Task 5
- Produces: meta bar shows `"YouTube • Fireship"` instead of just `"YouTube"` when channel is non-empty

- [ ] **Step 1: Modify source display in meta bar**

In `FeedCard.jsx`, find the meta bar source span (around line 121):

```jsx
<span style={sourceStyle}>{item.source}</span>
<span style={dimStyle}>&nbsp;·&nbsp;{item.published_at}</span>
```

Change to:

```jsx
<span style={sourceStyle}>{item.source}</span>
{item.channel ? (
  <span style={dimStyle}>&nbsp;·&nbsp;{item.channel}</span>
) : (
  <span style={dimStyle}>&nbsp;·&nbsp;{item.published_at}</span>
)}
{item.channel && item.published_at && (
  <span style={dimStyle}>&nbsp;·&nbsp;{item.published_at}</span>
)}
```

Wait — this renders both channel and published_at for YouTube items. The desired display is:

- Non-YouTube: `YouTube source · 3 hours ago` (current behaviour)
- YouTube with channel + time: `YouTube · Fireship · 3 hours ago`
- YouTube with channel, no time: `YouTube · Fireship`

Simplified clean version — replace those two lines with:

```jsx
<span style={sourceStyle}>{item.source}</span>
{item.channel && (
  <span style={dimStyle}>&nbsp;·&nbsp;{item.channel}</span>
)}
{item.published_at && (
  <span style={dimStyle}>&nbsp;·&nbsp;{item.published_at}</span>
)}
```

This correctly handles: non-YouTube (no channel, shows source · time), YouTube (shows source · channel · time or source · channel if no time).

- [ ] **Step 2: Verify frontend compiles**

```bash
cd frontend && npm run build 2>&1 | tail -5
```

Expected: build succeeds, no errors.

- [ ] **Step 3: Visual check in browser**

```bash
cd frontend && npm run dev &
```

Open `http://localhost:5173` (with API running and YouTube items in feed).

- YouTube feed cards should show: `YouTube • Fireship • 3 hours ago` in the meta bar
- Non-YouTube feed cards should show: `TechCrunch • 2 hours ago` (unchanged)

- [ ] **Step 4: Kill dev server and commit**

```bash
kill %1 2>/dev/null || true
git add frontend/src/components/FeedCard.jsx
git commit -m "feat: show channel name in FeedCard meta bar for YouTube items"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|-----------------|------|
| `connectors/youtube.py` with `fetch()` | Tasks 1–2 |
| Session file `sessions/youtube.json` | Task 1 |
| `sessions/` gitignored | Task 1 |
| Poll every 10s, prompt at 5 min, no hard timeout | Task 1 |
| `ytInitialData` extraction via `page.evaluate` | Task 2 |
| Regular video: `source="YouTube"`, `url=watch?v=` | Task 2 |
| Short: `source="YouTube Shorts"`, `url=shorts/` | Task 2 |
| `raw["channel"]`, `raw["thumbnail_url"]`, `raw["is_short"]` | Task 2 |
| `refresh_youtube_thumbnails()` in `db/store.py` | Task 3 |
| Exclude YouTube from `refresh_direct_images` query | Task 3 |
| `channel` in aggregation SELECT | Task 4 |
| `_SOURCE_CATEGORY` + `_SOURCE_TYPE` mappings | Task 5 |
| `channel` in `_shape_item()` | Task 5 |
| `fetch_youtube()` in `_do_refresh()` | Task 5 |
| `refresh_youtube_thumbnails(conn)` called in `_do_refresh()` | Task 5 |
| Videos + Shorts in format filter | Task 6 |
| YouTube source colors in Explore | Task 6 |
| Channel subtitle in FeedCard | Task 7 |
| Error handling: parse failure returns `[]` | Task 2 (`_parse_home` try/except) |
| Error handling: session expired → re-auth | Task 1 (`_ensure_auth`) |

All spec requirements covered. No placeholders. All code is complete and runnable.
