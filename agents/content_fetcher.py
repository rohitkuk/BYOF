import hashlib
import re
import requests
from pathlib import Path
from urllib.parse import urljoin

_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
_META_IMG_RE = re.compile(
    r'(?:property|name)=["\'](?:og|twitter):image["\'][^>]+content=["\']([^"\']+)'
    r'|content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og|twitter):image["\']',
    re.I,
)
_SCRIPT_RE = re.compile(r'<(script|style)[^>]*>.*?</\1>', re.S | re.I)
_TAG_RE = re.compile(r'<[^>]+>')
_WS_RE = re.compile(r'\s+')
_SCREENSHOTS_DIR = Path("frontend/public/screenshots")


def _extract_text(html: str) -> str:
    html = _SCRIPT_RE.sub('', html)
    text = _TAG_RE.sub(' ', html)
    return _WS_RE.sub(' ', text).strip()


def _og_image(html: str, base_url: str) -> str | None:
    m = _META_IMG_RE.search(html)
    if m:
        img = m.group(1) or m.group(2)
        if img:
            return urljoin(base_url, img)
    return None


def _screenshot(url: str) -> str | None:
    try:
        from playwright.sync_api import sync_playwright
        _SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        fname = hashlib.md5(url.encode()).hexdigest()[:16] + ".jpg"
        path = _SCREENSHOTS_DIR / fname
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            ctx = browser.new_context(user_agent=_UA)
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.screenshot(
                path=str(path), type="jpeg", quality=75,
                clip={"x": 0, "y": 0, "width": 1280, "height": 720},
            )
            browser.close()
        return f"/screenshots/{fname}"
    except Exception:
        return None


def fetch_content(url: str, screenshot: bool = False) -> dict:
    """Returns {body, image_url, image_type}. Never raises.
    screenshot=False skips Playwright fallback (faster for swarm use)."""
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": _UA},
                         allow_redirects=True, stream=False)
        if r.status_code != 200:
            return {"body": "", "image_url": None, "image_type": None}
        html = r.text[:500_000]  # cap at 500KB to avoid regex slowdown on huge pages
        body = _extract_text(html)[:5000]
        image_url = _og_image(html, url)
        image_type = "article" if image_url else None
        if not image_url and screenshot:
            image_url = _screenshot(url)
            image_type = "screenshot" if image_url else None
        return {"body": body, "image_url": image_url, "image_type": image_type}
    except Exception:
        return {"body": "", "image_url": None, "image_type": None}
