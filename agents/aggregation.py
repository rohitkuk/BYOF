import json
import sqlite3
from datetime import datetime
from email.utils import parsedate_to_datetime

from agents.personas import apply_persona
from agents.weighing import weigh


def _parse_ts(published_at: str, fetched_at: str) -> float:
    for parse in (parsedate_to_datetime, datetime.fromisoformat):
        try:
            return parse(published_at).timestamp()
        except Exception:
            continue
    try:
        return datetime.fromisoformat(fetched_at).timestamp()
    except Exception:
        return 0.0


def rank(db_path: str, prefs_path: str = "preferences.json", limit: int | None = None, persona: str | None = None) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """SELECT title, url, source, published_at, fetched_at,
                  image_url, image_type, llm_score, llm_summary, llm_keywords,
                  json_extract(raw, '$.summary') as rss_summary,
                  json_extract(raw, '$.source.href') as source_href
           FROM items"""
    ).fetchall()
    conn.close()

    items = weigh([dict(row) for row in rows], prefs_path)

    for item in items:
        recency = _parse_ts(item["published_at"], item["fetched_at"])
        weight = item.pop("_weight", 1.0)
        llm_score = item.get("llm_score")
        if llm_score is not None:
            item["_score"] = recency * float(llm_score) * 10
            item["llm_scored"] = True
        else:
            item["_score"] = recency * weight
            item["llm_scored"] = False
        item["summary"] = item.get("llm_summary") or item.get("rss_summary") or ""
        item["keywords"] = json.loads(item.get("llm_keywords") or "[]")

    items.sort(key=lambda x: x["_score"], reverse=True)
    for item in items:
        item["score"] = item.pop("_score")
    if persona:
        items = apply_persona(items, persona)
    if limit is not None:
        items = items[:limit]
    return items
