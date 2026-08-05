import json
import sqlite3
from datetime import datetime, timezone


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            url          TEXT    UNIQUE NOT NULL,
            source       TEXT,
            published_at TEXT,
            raw          TEXT,
            fetched_at   TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_items(conn: sqlite3.Connection, items: list[dict]) -> int:
    fetched_at = datetime.now(timezone.utc).isoformat()
    cursor = conn.executemany(
        """
        INSERT OR IGNORE INTO items (title, url, source, published_at, raw, fetched_at)
        VALUES (:title, :url, :source, :published_at, :raw, :fetched_at)
        """,
        [
            {
                "title": item["title"],
                "url": item["url"],
                "source": item["source"],
                "published_at": item["published_at"],
                "raw": json.dumps(item.get("raw", {})),
                "fetched_at": fetched_at,
            }
            for item in items
        ],
    )
    conn.commit()
    return cursor.rowcount
