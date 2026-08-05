import feedparser

QUERY = "AI"
_URL = f"https://news.google.com/rss/search?q={QUERY}&hl=en-US&gl=US&ceid=US:en"


def fetch() -> list[dict]:
    feed = feedparser.parse(_URL)
    items = []
    for entry in feed.entries:
        items.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "source": entry.get("source", {}).get("title", "Google News"),
            "published_at": entry.get("published", ""),
            "raw": dict(entry),
        })
    return items
