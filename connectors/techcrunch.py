import feedparser

_URL = "https://techcrunch.com/feed/"


def fetch() -> list[dict]:
    feed = feedparser.parse(_URL)
    items = []
    for entry in feed.entries:
        items.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "source": entry.get("source", {}).get("title", "TechCrunch"),
            "published_at": entry.get("published", ""),
            "raw": dict(entry),
        })
    return items
