import feedparser

_URL = "https://tldr.tech/api/rss/tech"


def fetch() -> list[dict]:
    feed = feedparser.parse(_URL)
    items = []
    for entry in feed.entries:
        items.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "source": "TLDR Tech",
            "published_at": entry.get("published", ""),
            "raw": dict(entry),
        })
    return items
