from dotenv import load_dotenv

load_dotenv()

from agents.aggregation import rank
from agents.swarm import run_swarm
from connectors.arxiv import fetch as fetch_arxiv
from connectors.google_news import fetch as fetch_google_news
from connectors.mit_tech_review import fetch as fetch_mit
from connectors.techcrunch import fetch as fetch_techcrunch
from connectors.tldr_tech import fetch as fetch_tldr
from db.store import init_db, refresh_article_images, refresh_publisher_logos, save_items, save_llm_results

DB_PATH = "db/byof.db"
_SOURCE_LIMIT = 12


def _fetch_all() -> list[dict]:
    sources = [fetch_google_news, fetch_techcrunch, fetch_arxiv, fetch_mit, fetch_tldr]
    items = []
    for fn in sources:
        items.extend(fn()[:_SOURCE_LIMIT])
    return items


if __name__ == "__main__":
    conn = init_db(DB_PATH)

    print("Fetching articles...")
    items = _fetch_all()
    saved = save_items(conn, items)
    print(f"Saved {saved} new item(s) to {DB_PATH}")

    print("Fetching article-level images (slug + playwright fallback)...")
    article_updated = refresh_article_images(conn, verbose=True, use_playwright=True)
    print(f"Updated {article_updated} item(s) with article images")

    print("Fetching publisher logos (fallback)...")
    logo_updated = refresh_publisher_logos(conn, verbose=True)
    print(f"Updated {logo_updated} item(s) with publisher logos")

    print("Running V2 swarm (fetch content + LLM scoring)...")
    rows = conn.execute(
        "SELECT title, url, source, published_at FROM items WHERE llm_score IS NULL"
    ).fetchall()
    unscored = [{"title": r[0], "url": r[1], "source": r[2], "published_at": r[3]} for r in rows]
    swarm = run_swarm(unscored, "preferences.json")
    save_llm_results(conn, swarm.results)
    print(f"Scored {len(swarm.results)} item(s) ({swarm.failure_count} failures)")
    print(f"Tokens: {swarm.total_input_tokens} input, {swarm.total_output_tokens} output")

    conn.close()

    ranked = rank(DB_PATH)
    for item in ranked:
        print(f"[{item['source']}] {item['title']}")
        print(f"  {item['url']}")
        print(f"  {item['published_at']}")
        print()
