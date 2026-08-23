import time
from pathlib import Path

from playwright.sync_api import sync_playwright

SESSION_PATH = Path("sessions/linkedin.json")

_EXTRACT_JS = """
(() => {
  const posts = [...document.querySelectorAll('[data-id]')];
  return posts.map(el => {
    const urn = el.getAttribute('data-id') || '';
    const textEl = el.querySelector(
      '.update-components-text, .feed-shared-update-v2__description, .attributed-text-segment-list__content'
    );
    const text = textEl ? textEl.innerText.trim() : '';
    const authorEl = el.querySelector(
      '.update-components-actor__name, .feed-shared-actor__name, .update-components-actor__name span[aria-hidden="true"]'
    );
    const author = authorEl ? authorEl.innerText.trim() : '';
    const timeEl = el.querySelector('time');
    const publishedAt = timeEl
      ? (timeEl.getAttribute('datetime') || timeEl.innerText.trim())
      : '';
    const articleEl = el.querySelector(
      '.update-components-article a, .feed-shared-article__content a'
    );
    const articleUrl = articleEl ? articleEl.href : null;
    const isJob = urn.includes(':job') || urn.includes(':jobPosting');
    return { urn, text, author, publishedAt, articleUrl, isJob };
  }).filter(p => p.urn && (p.text || p.isJob));
})()
"""


def _session_exists() -> bool:
    return SESSION_PATH.exists()


def _is_on_feed(page) -> bool:
    return "/feed" in page.url


def _is_logged_in_headless(page) -> bool:
    time.sleep(3)
    return "/feed" in page.url or (
        "linkedin.com" in page.url and "/login" not in page.url and "/authwall" not in page.url
    )


def _ensure_auth(p):
    SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)

    if _session_exists():
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state=str(SESSION_PATH))
        page = ctx.new_page()
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        if _is_logged_in_headless(page):
            return browser, ctx, page
        page.close()
        ctx.close()
        browser.close()

    print("[LinkedIn] Session missing or expired — opening browser for login.")
    print("[LinkedIn] Please sign in. Browser will close automatically once you reach the feed.")
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")

    deadline = time.time() + 600
    while time.time() < deadline:
        time.sleep(2)
        if _is_on_feed(page):
            print("[LinkedIn] Login done! Saving session...")
            ctx.storage_state(path=str(SESSION_PATH))
            print(f"[LinkedIn] Session saved to {SESSION_PATH}")
            break
    else:
        raise TimeoutError("LinkedIn login timed out after 10 minutes.")

    page.close()
    ctx.close()
    browser.close()
    print("[LinkedIn] Browser closed. Running headless...")

    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state=str(SESSION_PATH))
    page = ctx.new_page()
    page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    return browser, ctx, page


def fetch() -> list[dict]:
    items: list[dict] = []
    with sync_playwright() as p:
        browser, ctx, page = _ensure_auth(p)
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

        for _ in range(4):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(1.5)

        try:
            posts = page.evaluate(_EXTRACT_JS)
        except Exception:
            posts = []

        for post in posts:
            urn = post.get("urn", "")
            text = post.get("text", "") or ""
            title = text[:120] if text else (urn if post.get("isJob") else "")
            if not title:
                continue
            items.append({
                "title": title,
                "url": f"https://www.linkedin.com/feed/update/{urn}/",
                "source": "LinkedIn",
                "published_at": post.get("publishedAt", ""),
                "raw": {
                    "author": post.get("author", ""),
                    "full_text": text,
                    "article_url": post.get("articleUrl"),
                    "is_job": post.get("isJob", False),
                    "urn": urn,
                },
            })

        ctx.close()
        browser.close()

    return items
