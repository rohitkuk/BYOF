from connectors.google_news import fetch
from db.store import init_db, save_items
from agents.aggregation import rank

DB_PATH = "db/byof.db"

conn = init_db(DB_PATH)
items = fetch()
saved = save_items(conn, items)
conn.close()

print(f"Saved {saved} new item(s) to {DB_PATH}\n")

ranked = rank(DB_PATH)
for item in ranked:
    print(f"[{item['source']}] {item['title']}")
    print(f"  {item['url']}")
    print(f"  {item['published_at']}")
    print()
