import json
import os
import time as _time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from agents.aggregation import rank
from agents.swarm import run_swarm
from connectors.arxiv import fetch as fetch_arxiv
from connectors.google_news import fetch as fetch_google_news
from connectors.mit_tech_review import fetch as fetch_mit
from connectors.techcrunch import fetch as fetch_techcrunch
from connectors.tldr_tech import fetch as fetch_tldr
from db.store import (
    get_recent_runs,
    init_db,
    refresh_article_images,
    refresh_direct_images,
    refresh_publisher_logos,
    save_items,
    save_llm_results,
    save_refresh_run,
)

DB_PATH = "db/byof.db"
PREFS_PATH = "preferences.json"

_SOURCE_CATEGORY = {
    "Google News": ["Technology"],
    "TechCrunch": ["Technology"],
    "MIT Technology Review": ["Technology", "Science"],
    "TLDR Tech": ["Technology"],
    "ArXiv": ["Science"],
}

_SOURCE_TYPE = {
    "Google News": "Article",
    "TechCrunch": "Article",
    "MIT Technology Review": "Article",
    "TLDR Tech": "Newsletter",
    "ArXiv": "Paper",
}

Path("frontend/public/screenshots").mkdir(parents=True, exist_ok=True)

# In-memory refresh state — tracks running/last-completed job
_refresh_state: dict = {"status": "idle", "last": None}

# Feed cache — unfiltered /feed responses, 30s TTL, keyed by persona
_feed_cache: dict = {}  # persona_name -> {"data": list, "ts": float}
_FEED_CACHE_TTL = 30


def _invalidate_feed_cache():
    _feed_cache.clear()


app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_ts(published_at: str) -> float | None:
    if not published_at:
        return None
    for parse in (parsedate_to_datetime, datetime.fromisoformat):
        try:
            dt = parse(published_at)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except Exception:
            continue
    return None


def _relative_time(published_at: str) -> str:
    ts = _parse_ts(published_at)
    if ts is None:
        return published_at
    now = datetime.now(timezone.utc).timestamp()
    diff = now - ts
    if diff < 60:
        return "Just now"
    if diff < 3600:
        h = int(diff // 60)
        return f"{h}m ago"
    if diff < 86400:
        h = int(diff // 3600)
        return f"{h}h ago"
    if diff < 172800:
        return "Yesterday"
    days = int(diff // 86400)
    return f"{days} days ago"


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
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/preferences")
def get_preferences():
    if not os.path.exists(PREFS_PATH):
        return {"categories": [], "subcategories": []}
    with open(PREFS_PATH) as f:
        return json.load(f)


@app.post("/preferences")
def post_preferences(body: dict):
    with open(PREFS_PATH, "w") as f:
        json.dump(body, f, indent=2)
    return {"status": "ok"}


@app.get("/feed")
def get_feed(
    category: str | None = Query(default=None),
    date: str | None = Query(default=None),
    type: str | None = Query(default=None),
    source: str | None = Query(default=None),
):
    has_filters = any([category, date, type, source])

    _prefs = json.load(open(PREFS_PATH)) if os.path.exists(PREFS_PATH) else {}
    persona = _prefs.get("persona", "generalist")

    if not has_filters:
        cached = _feed_cache.get(persona)
        if cached and (_time.time() - cached["ts"]) < _FEED_CACHE_TTL:
            return cached["data"]

    items = rank(DB_PATH, PREFS_PATH, limit=None, persona=persona)

    if source:
        items = [i for i in items if i.get("source") == source]
    if category:
        items = [
            i for i in items
            if category in _SOURCE_CATEGORY.get(i.get("source", ""), [])
        ]
    if type:
        items = [
            i for i in items
            if _SOURCE_TYPE.get(i.get("source", "")) == type
        ]
    if date:
        now = datetime.now(timezone.utc).timestamp()
        cutoffs = {"Today": 86400, "This week": 604800, "This month": 2592000}
        cutoff = cutoffs.get(date)
        if cutoff:
            items = [
                i for i in items
                if (_parse_ts(i.get("published_at", "")) or 0) >= now - cutoff
            ]

    shaped = [_shape_item(i) for i in items[:20]]

    if not has_filters:
        _feed_cache[persona] = {"data": shaped, "ts": _time.time()}

    return shaped


_SOURCE_LIMIT = 12   # items fetched per connector per refresh
_SWARM_LIMIT = 60    # max items sent to LLM swarm per refresh


def _do_refresh():
    _refresh_state["status"] = "running"
    try:
        conn = init_db(DB_PATH)
        all_items = (
            fetch_google_news()[:_SOURCE_LIMIT]
            + fetch_techcrunch()[:_SOURCE_LIMIT]
            + fetch_arxiv()[:_SOURCE_LIMIT]
            + fetch_mit()[:_SOURCE_LIMIT]
            + fetch_tldr()[:_SOURCE_LIMIT]
        )
        new_count = save_items(conn, all_items)
        refresh_article_images(conn, use_playwright=False)
        refresh_direct_images(conn)
        refresh_publisher_logos(conn)

        rows = conn.execute(
            "SELECT title, url, source, published_at FROM items "
            "WHERE llm_score IS NULL ORDER BY fetched_at DESC LIMIT ?",
            (_SWARM_LIMIT,),
        ).fetchall()
        unscored = [{"title": r[0], "url": r[1], "source": r[2], "published_at": r[3]} for r in rows]
        swarm = run_swarm(unscored, PREFS_PATH)
        save_llm_results(conn, swarm.results)
        run_record = {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "item_count": len(all_items),
            "scored_count": len(swarm.results),
            "input_tokens": swarm.total_input_tokens,
            "output_tokens": swarm.total_output_tokens,
            "failure_count": swarm.failure_count,
        }
        save_refresh_run(conn, run_record)
        conn.close()
        _invalidate_feed_cache()
        _refresh_state["last"] = {
            **run_record,
            "new_items": new_count,
            "status": "ok",
        }
    except Exception as e:
        _refresh_state["last"] = {"status": "error", "error": str(e)}
    finally:
        _refresh_state["status"] = "idle"


@app.post("/refresh")
def post_refresh(background_tasks: BackgroundTasks):
    if _refresh_state["status"] == "running":
        return {"status": "already_running"}
    background_tasks.add_task(_do_refresh)
    return {"status": "started"}


@app.get("/refresh/status")
def get_refresh_status():
    return {"status": _refresh_state["status"], "last": _refresh_state["last"]}


@app.get("/runs")
def get_runs():
    conn = init_db(DB_PATH)
    runs = get_recent_runs(conn)
    conn.close()
    return runs


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
