import json
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from agents.aggregation import rank
from connectors.arxiv import fetch as fetch_arxiv
from connectors.google_news import fetch as fetch_google_news
from connectors.mit_tech_review import fetch as fetch_mit
from connectors.techcrunch import fetch as fetch_techcrunch
from connectors.tldr_tech import fetch as fetch_tldr
from db.store import init_db, refresh_article_images, refresh_publisher_logos, save_items

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

app = FastAPI()
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
    items = rank(DB_PATH, PREFS_PATH, limit=None)

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
    return shaped


@app.post("/refresh")
def post_refresh():
    conn = init_db(DB_PATH)
    all_items = (
        fetch_google_news()
        + fetch_techcrunch()
        + fetch_arxiv()
        + fetch_mit()
        + fetch_tldr()
    )
    new_count = save_items(conn, all_items)
    refresh_article_images(conn, use_playwright=False)
    refresh_publisher_logos(conn)
    conn.close()
    return {"status": "ok", "new_items": new_count}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
