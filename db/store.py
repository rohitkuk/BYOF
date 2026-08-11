import json
import re
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin

import requests

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
_META_IMG_RE = re.compile(
    r'(?:property|name)=["\'](?:og|twitter):image["\'][^>]+content=["\']([^"\']+)'
    r'|content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og|twitter):image["\']',
    re.I,
)
_TOUCH_ICON_RE = re.compile(
    r'<link[^>]+rel=["\'][^"\']*apple-touch-icon[^"\']*["\'][^>]+href=["\']([^"\']+)["\']'
    r'|<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*apple-touch-icon[^"\']*["\']',
    re.I,
)
_GOOGLE_IMG_RE = re.compile(r'(?:google(?:apis|user)?|gstatic|lh\d\.google)\.com', re.I)
# Strip trailing publisher suffix from title, e.g. " - TechCrunch" or " | Wired"
_PUB_SUFFIX_RE = re.compile(r'\s*[-|–—]\s*\w[\w\s&.]*$')


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS publisher_logos (
            source_href TEXT PRIMARY KEY,
            logo_url    TEXT,
            fetched_at  TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS refresh_runs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at        TEXT NOT NULL,
            item_count    INTEGER,
            scored_count  INTEGER,
            input_tokens  INTEGER,
            output_tokens INTEGER,
            failure_count INTEGER
        )
    """)
    for col, definition in [
        ("image_url", "TEXT"),
        ("image_type", "TEXT"),
        ("article_url", "TEXT"),
        ("body", "TEXT"),
        ("llm_summary", "TEXT"),
        ("llm_keywords", "TEXT"),
        ("llm_categories", "TEXT"),
        ("llm_score", "REAL"),
        ("scored_at", "TEXT"),
    ]:
        try:
            conn.execute(f"ALTER TABLE items ADD COLUMN {col} {definition}")
        except Exception:
            pass
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_llm_score ON items(llm_score)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_fetched_at ON items(fetched_at DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_source ON items(source)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_items_published_at ON items(published_at)")
    conn.commit()
    return conn


def save_items(conn: sqlite3.Connection, items: list[dict]) -> int:
    fetched_at = datetime.now(timezone.utc).isoformat()
    cursor = conn.executemany(
        """INSERT OR IGNORE INTO items (title, url, source, published_at, raw, fetched_at)
           VALUES (:title, :url, :source, :published_at, :raw, :fetched_at)""",
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


def update_image_urls(conn: sqlite3.Connection, updates: dict[str, str]) -> None:
    conn.executemany(
        "UPDATE items SET image_url = ? WHERE url = ? AND image_url IS NULL",
        [(img_url, item_url) for item_url, img_url in updates.items()],
    )
    conn.commit()


# ── helpers ──────────────────────────────────────────────────────────────────

def _fetch_html(url: str, timeout: int = 6) -> str | None:
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": _UA}, allow_redirects=True)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None


def _og_image_from_html(html: str, base_url: str) -> str | None:
    m = _META_IMG_RE.search(html)
    if m:
        img = m.group(1) or m.group(2)
        if img and not _GOOGLE_IMG_RE.search(img):
            return urljoin(base_url, img)
    return None


def _slugify(title: str) -> str:
    clean = _PUB_SUFFIX_RE.sub("", title)
    clean = re.sub(r"['’‘“”]", "", clean)
    clean = clean.lower()
    clean = re.sub(r"[^a-z0-9]+", "-", clean)
    return clean.strip("-")


def _construct_article_url(source_href: str, title: str, published_at: str) -> str | None:
    try:
        dt = parsedate_to_datetime(published_at)
        slug = _slugify(title)
        if not slug:
            return None
        return f"{source_href.rstrip('/')}/{dt.year}/{dt.month:02d}/{dt.day:02d}/{slug}/"
    except Exception:
        return None


# ── article-level image refresh ───────────────────────────────────────────────

def _resolve_gn_url_and_image(gn_url: str) -> tuple[str | None, str | None]:
    """Resolve Google News URL to actual article URL + og:image via Playwright.
    Returns (article_url, og_image) or (None, None) if unavailable."""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        return None, None

    navigate_url = gn_url.replace('/rss/articles/', '/articles/').split('?')[0]
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto(navigate_url, wait_until="domcontentloaded", timeout=15000)
            try:
                page.wait_for_url(lambda u: "news.google.com" not in u, timeout=10000)
            except PWTimeout:
                pass
            article_url = page.url
            if "news.google.com" in article_url:
                browser.close()
                return None, None
            # Extract og:image from the rendered page
            og_image = page.evaluate("""() => {
                const m = document.querySelector('meta[property="og:image"], meta[name="og:image"]');
                return m ? m.getAttribute('content') : null;
            }""")
            browser.close()
            # Filter Google-hosted images
            if og_image and _GOOGLE_IMG_RE.search(og_image):
                og_image = None
            return article_url, og_image or None
    except Exception:
        return None, None


def refresh_article_images(
    conn: sqlite3.Connection,
    verbose: bool = False,
    max_workers: int = 8,
    use_playwright: bool = False,
) -> int:
    """Fetch article-specific og:image.
    Phase 1 (concurrent): try title+date+slug URL construction.
    Phase 2 (sequential, optional): Playwright resolution for remaining items.
    Updates only items where image_type IS NULL."""
    rows = conn.execute("""
        SELECT id, title, url, published_at,
               json_extract(raw, '$.source.href') AS source_href
        FROM items
        WHERE image_type IS NULL
          AND published_at IS NOT NULL
          AND json_extract(raw, '$.source.href') IS NOT NULL
    """).fetchall()

    # Phase 1: fast concurrent slug-based resolution
    def process_slug(row):
        item_id, title, gn_url, published_at, source_href = row
        article_url = _construct_article_url(source_href, title, published_at)
        if not article_url:
            return None
        html = _fetch_html(article_url)
        if not html:
            return None
        og = _og_image_from_html(html, article_url)
        if og:
            return (item_id, article_url, og)
        return None

    slug_failed = []
    updated = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_slug, row): row for row in rows}
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception:
                result = None
            row = futures[future]
            if result:
                item_id, article_url, og = result
                conn.execute(
                    "UPDATE items SET image_url = ?, image_type = 'article', article_url = ? WHERE id = ?",
                    (og, article_url, item_id),
                )
                updated += 1
                if verbose:
                    print(f"  [slug] {row[1][:55]} → ok")
            else:
                slug_failed.append(row)

    conn.commit()

    # Phase 2: Playwright for items slug resolution couldn't handle
    if use_playwright and slug_failed:
        if verbose:
            print(f"  [playwright] resolving {len(slug_failed)} articles...")
        for row in slug_failed:
            item_id, title, gn_url, published_at, source_href = row
            try:
                article_url, og = _resolve_gn_url_and_image(gn_url)
                if article_url and og:
                    conn.execute(
                        "UPDATE items SET image_url = ?, image_type = 'article', article_url = ? WHERE id = ?",
                        (og, article_url, item_id),
                    )
                    updated += 1
                    if verbose:
                        print(f"  [playwright] {title[:55]} → ok")
                elif article_url:
                    # Have URL but no og:image — try requests fallback
                    html = _fetch_html(article_url)
                    og = _og_image_from_html(html, article_url) if html else None
                    if og:
                        conn.execute(
                            "UPDATE items SET image_url = ?, image_type = 'article', article_url = ? WHERE id = ?",
                            (og, article_url, item_id),
                        )
                        updated += 1
                        if verbose:
                            print(f"  [playwright+fetch] {title[:55]} → ok")
            except Exception:
                continue
        conn.commit()

    return updated


# ── publisher logo refresh ────────────────────────────────────────────────────

def _url_ok(url: str) -> bool:
    try:
        r = requests.head(url, timeout=5, headers={"User-Agent": _UA}, allow_redirects=True)
        return r.status_code < 400
    except Exception:
        return False


def _fetch_logo_url(source_href: str) -> str | None:
    html = _fetch_html(source_href)
    if not html:
        return None
    # Try og:image first, validate it's actually accessible
    og = _og_image_from_html(html, source_href)
    if og and _url_ok(og):
        return og
    # Fall back to apple-touch-icon
    m2 = _TOUCH_ICON_RE.search(html)
    if m2:
        icon = m2.group(1) or m2.group(2)
        icon_url = urljoin(source_href, icon)
        if _url_ok(icon_url):
            return icon_url
    return None


def refresh_direct_images(
    conn: sqlite3.Connection,
    max_workers: int = 8,
    timeout: int = 12,
) -> int:
    """Fetch og:image directly from item.url for every item still missing an image.
    Skips news.google.com URLs (those require Playwright to resolve the redirect).
    Returns number of items updated."""
    rows = conn.execute(
        "SELECT id, url FROM items WHERE image_url IS NULL AND url NOT LIKE '%news.google.com%'"
    ).fetchall()

    def fetch_one(row):
        item_id, url = row
        try:
            r = requests.get(
                url, timeout=timeout, headers={"User-Agent": _UA}, allow_redirects=True
            )
            if r.status_code != 200:
                return None
            og = _og_image_from_html(r.text[:300_000], url)
            if og:
                return (item_id, og)
        except Exception:
            pass
        return None

    updated = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, row): row for row in rows}
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    item_id, og = result
                    conn.execute(
                        "UPDATE items SET image_url = ?, image_type = 'article' WHERE id = ?",
                        (og, item_id),
                    )
                    updated += 1
            except Exception:
                pass
    conn.commit()
    return updated


def save_llm_results(conn: sqlite3.Connection, results: list[dict]) -> None:
    if not results:
        return
    conn.executemany(
        """UPDATE items SET
               body           = :body,
               image_url      = COALESCE(image_url, :image_url),
               image_type     = COALESCE(image_type, :image_type),
               llm_summary    = :llm_summary,
               llm_keywords   = :llm_keywords,
               llm_categories = :llm_categories,
               llm_score      = :llm_score,
               scored_at      = :scored_at
           WHERE url = :url""",
        results,
    )
    conn.commit()


def save_refresh_run(conn: sqlite3.Connection, run: dict) -> None:
    conn.execute(
        """INSERT INTO refresh_runs
               (run_at, item_count, scored_count, input_tokens, output_tokens, failure_count)
           VALUES (:run_at, :item_count, :scored_count, :input_tokens, :output_tokens, :failure_count)""",
        run,
    )
    conn.commit()


def get_recent_runs(conn: sqlite3.Connection, limit: int = 10) -> list[dict]:
    cursor = conn.execute(
        "SELECT id, run_at, item_count, scored_count, input_tokens, output_tokens, failure_count "
        "FROM refresh_runs ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def refresh_publisher_logos(conn: sqlite3.Connection, verbose: bool = False) -> int:
    """Fetch logos for publishers not yet cached. Only fills items with NULL image_url.
    Returns number of items updated."""
    new_pubs = conn.execute("""
        SELECT DISTINCT json_extract(raw, '$.source.href') AS src
        FROM items
        WHERE json_extract(raw, '$.source.href') IS NOT NULL
          AND json_extract(raw, '$.source.href') NOT IN (SELECT source_href FROM publisher_logos)
    """).fetchall()

    fetched_at = datetime.now(timezone.utc).isoformat()
    for (src,) in new_pubs:
        if verbose:
            print(f"  Fetching logo: {src}", end=" ... ", flush=True)
        logo_url = _fetch_logo_url(src)
        conn.execute(
            "INSERT OR REPLACE INTO publisher_logos (source_href, logo_url, fetched_at) VALUES (?, ?, ?)",
            (src, logo_url, fetched_at),
        )
        if verbose:
            print("ok" if logo_url else "none")
    conn.commit()

    # Mark items with legacy image_url (before image_type column existed) as 'logo'
    conn.execute("""
        UPDATE items SET image_type = 'logo'
        WHERE image_type IS NULL AND image_url IS NOT NULL
    """)

    # Apply logos only to items still missing an image
    cursor = conn.execute("""
        UPDATE items
        SET image_url = (
                SELECT logo_url FROM publisher_logos
                WHERE source_href = json_extract(items.raw, '$.source.href')
            ),
            image_type = 'logo'
        WHERE image_url IS NULL
          AND json_extract(raw, '$.source.href') IN (
              SELECT source_href FROM publisher_logos WHERE logo_url IS NOT NULL
          )
    """)
    conn.commit()
    return cursor.rowcount
