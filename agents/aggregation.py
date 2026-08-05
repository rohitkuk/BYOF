import sqlite3
from datetime import datetime
from email.utils import parsedate_to_datetime

SOURCE_WEIGHTS = {
    "Google News": 1.0,
}
_DEFAULT_WEIGHT = 1.0


def _parse_ts(published_at: str, fetched_at: str) -> float:
    try:
        return parsedate_to_datetime(published_at).timestamp()
    except Exception:
        try:
            return datetime.fromisoformat(fetched_at).timestamp()
        except Exception:
            return 0.0


def rank(db_path: str) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT title, url, source, published_at, fetched_at FROM items"
    ).fetchall()
    conn.close()

    items = [dict(row) for row in rows]
    for item in items:
        recency = _parse_ts(item["published_at"], item["fetched_at"])
        weight = SOURCE_WEIGHTS.get(item["source"], _DEFAULT_WEIGHT)
        item["_score"] = recency * weight

    items.sort(key=lambda x: x["_score"], reverse=True)
    for item in items:
        del item["_score"]
    return items
