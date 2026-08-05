from connectors.google_news import fetch
from db.store import init_db, save_items

conn = init_db("db/byof.db")
items = fetch()
saved = save_items(conn, items)
conn.close()

for item in items:
    print(f"[{item['source']}] {item['title']}")
    print(f"  {item['url']}")
    print(f"  {item['published_at']}")
    print()

print(f"Saved {saved} new item(s) to db/byof.db")
