import feedparser

_RSS_FEEDS = [
    "https://rss.arxiv.org/rss/cs.AI",
    "https://rss.arxiv.org/rss/cs.LG",
]
_API_URL = (
    "https://export.arxiv.org/api/query"
    "?search_query=cat:cs.AI+OR+cat:cs.LG"
    "&sortBy=submittedDate&sortOrder=descending&max_results=12"
)


def fetch() -> list[dict]:
    seen = set()
    items = []

    for url in _RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            link = entry.get("link", "")
            if link in seen:
                continue
            seen.add(link)
            items.append({
                "title": entry.get("title", ""),
                "url": link,
                "source": "ArXiv",
                "published_at": entry.get("published", ""),
                "raw": dict(entry),
            })

    if not items:
        feed = feedparser.parse(_API_URL)
        for entry in feed.entries:
            link = entry.get("link", "")
            if link in seen:
                continue
            seen.add(link)
            items.append({
                "title": entry.get("title", ""),
                "url": link,
                "source": "ArXiv",
                "published_at": entry.get("published", ""),
                "raw": dict(entry),
            })

    return items
