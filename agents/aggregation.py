import sqlite3
from datetime import datetime
from email.utils import parsedate_to_datetime

from agents.weighing import weigh


def _parse_ts(published_at: str, fetched_at: str) -> float:
    try:
        return parsedate_to_datetime(published_at).timestamp()
    except Exception:
        try:
            return datetime.fromisoformat(fetched_at).timestamp()
        except Exception:
            return 0.0


def rank(db_path: str, prefs_path: str = "preferences.json") -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT title, url, source, published_at, fetched_at FROM items"
    ).fetchall()
    conn.close()

    items = weigh([dict(row) for row in rows], prefs_path)

    for item in items:
        recency = _parse_ts(item["published_at"], item["fetched_at"])
        weight = item.pop("_weight", 1.0)
        item["_score"] = recency * weight

    items.sort(key=lambda x: x["_score"], reverse=True)
    for item in items:
        del item["_score"]
    return items
