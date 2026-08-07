from agents.aggregation import rank
from connectors.google_news import fetch
from db.store import init_db, refresh_article_images, refresh_publisher_logos, save_items

DB_PATH = "db/byof.db"

if __name__ == "__main__":
    conn = init_db(DB_PATH)

    print("Fetching articles...")
    items = fetch()
    saved = save_items(conn, items)
    print(f"Saved {saved} new item(s) to {DB_PATH}")

    print("Fetching article-level images (slug + playwright fallback)...")
    article_updated = refresh_article_images(conn, verbose=True, use_playwright=True)
    print(f"Updated {article_updated} item(s) with article images")

    print("Fetching publisher logos (fallback)...")
    logo_updated = refresh_publisher_logos(conn, verbose=True)
    print(f"Updated {logo_updated} item(s) with publisher logos")

    conn.close()

    ranked = rank(DB_PATH)
    for item in ranked:
        print(f"[{item['source']}] {item['title']}")
        print(f"  {item['url']}")
        print(f"  {item['published_at']}")
        print()
