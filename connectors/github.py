import json
import re

import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
_PREFS_PATH = "preferences.json"
_TRENDING_BASE = "https://github.com/trending"


def _read_languages() -> list[str]:
    try:
        with open(_PREFS_PATH) as f:
            return json.load(f).get("github_languages", [])
    except Exception:
        return []


def _fetch_html(url: str) -> str | None:
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        return r.text if r.status_code == 200 else None
    except Exception:
        return None


def _parse_trending(html: str) -> list[dict]:
    items = []
    articles = re.split(r'<article\s[^>]*class="[^"]*Box-row[^"]*"', html)
    for chunk in articles[1:]:
        # Repo path from h2 > a href="/owner/repo" (a may have attrs before href)
        path_m = re.search(r'<h2[^>]*>.*?<a[^>]+href="/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)"', chunk, re.DOTALL)
        if not path_m:
            continue
        path = path_m.group(1).strip().split("?")[0]
        if "/" not in path:
            continue
        owner, repo = path.split("/", 1)

        # Description — p.col-9 inner text, strip tags
        desc_m = re.search(r'<p\s+class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', chunk, re.DOTALL)
        description = ""
        if desc_m:
            description = re.sub(r"<[^>]+>", "", desc_m.group(1))
            description = re.sub(r"\s+", " ", description).strip()

        # Language
        lang_m = re.search(r'itemprop="programmingLanguage"[^>]*>([^<]+)<', chunk)
        language = lang_m.group(1).strip() if lang_m else ""

        # Stars this week
        stars_m = re.search(r"([\d,]+)\s+stars\s+this\s+week", chunk)
        stars_this_week = int(stars_m.group(1).replace(",", "")) if stars_m else 0

        items.append({
            "title": f"{owner}/{repo}",
            "url": f"https://github.com/{owner}/{repo}",
            "source": "GitHub Trending",
            "published_at": "",
            "raw": {
                "description": description,
                "language": language,
                "stars_this_week": stars_this_week,
                "owner": owner,
                "repo": repo,
            },
        })
    return items


def fetch() -> list[dict]:
    languages = _read_languages()
    urls = (
        [f"{_TRENDING_BASE}/{lang.lower()}?since=weekly" for lang in languages]
        if languages
        else [f"{_TRENDING_BASE}?since=weekly"]
    )
    seen: set[str] = set()
    items: list[dict] = []
    for url in urls:
        html = _fetch_html(url)
        if html:
            for item in _parse_trending(html):
                if item["url"] not in seen:
                    seen.add(item["url"])
                    items.append(item)
    return items[:25]
