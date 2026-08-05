from connectors.google_news import fetch

items = fetch()
for item in items:
    print(f"[{item['source']}] {item['title']}")
    print(f"  {item['url']}")
    print(f"  {item['published_at']}")
    print()
