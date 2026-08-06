import json
from pathlib import Path

PREFS_PATH = "preferences.json"
_BOOST_PER_MATCH = 1.5

CATEGORIES = {
    "AI & ML": {
        "keywords": ["ai", "artificial intelligence", "machine learning", "deep learning", "neural"],
        "subcategories": {
            "LLMs & Chatbots": ["llm", "gpt", "claude", "chatgpt", "openai", "anthropic", "gemini", "llama", "chatbot"],
            "Computer Vision": ["computer vision", "image recognition", "stable diffusion", "midjourney"],
            "Robotics": ["robotics", "robot", "autonomous vehicle", "drone"],
            "AI Safety & Ethics": ["ai safety", "ai ethics", "alignment", "bias", "responsible ai"],
        },
    },
    "Technology": {
        "keywords": ["tech", "technology", "software", "developer"],
        "subcategories": {
            "Startups & VC": ["startup", "venture capital", "funding", "series a", "series b"],
            "Cybersecurity": ["cybersecurity", "hack", "vulnerability", "breach", "ransomware"],
            "Cloud & Infrastructure": ["cloud", "aws", "azure", "google cloud", "kubernetes"],
            "Mobile & Apps": ["mobile", "ios", "android", "app store"],
        },
    },
    "Business": {
        "keywords": ["business", "economy", "market", "company", "corporate"],
        "subcategories": {
            "Markets & Finance": ["stock market", "nasdaq", "wall street", "earnings", "ipo"],
            "Crypto & Web3": ["crypto", "bitcoin", "ethereum", "blockchain", "defi"],
            "Leadership": ["ceo", "founder", "executive", "acquisition", "merger"],
        },
    },
    "Science": {
        "keywords": ["science", "research", "study", "discovery"],
        "subcategories": {
            "Space": ["space", "nasa", "spacex", "satellite", "mars", "astronomy"],
            "Climate & Energy": ["climate", "environment", "carbon", "renewable", "solar", "ev"],
            "Health & Medicine": ["health", "medicine", "drug", "vaccine", "cancer", "clinical trial"],
        },
    },
    "Politics & Policy": {
        "keywords": ["politics", "government", "policy", "legislation", "regulation"],
        "subcategories": {
            "US Politics": ["congress", "senate", "white house", "democrat", "republican", "election"],
            "Tech Policy": ["antitrust", "privacy", "gdpr", "data protection", "big tech"],
            "International": ["china", "europe", "nato", "geopolitics", "sanctions"],
        },
    },
    "Sports": {
        "keywords": ["sports", "game", "championship", "athlete", "tournament", "league"],
        "subcategories": {
            "American Football": ["nfl", "super bowl", "quarterback", "touchdown"],
            "Basketball": ["nba", "basketball", "playoffs"],
            "Soccer": ["soccer", "premier league", "fifa", "world cup", "champions league"],
            "Tennis": ["tennis", "wimbledon", "us open", "grand slam"],
        },
    },
}


def load_prefs(prefs_path: str = PREFS_PATH) -> dict:
    try:
        return json.loads(Path(prefs_path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"categories": [], "subcategories": []}


def save_prefs(prefs: dict, prefs_path: str = PREFS_PATH) -> None:
    Path(prefs_path).write_text(json.dumps(prefs, indent=2))


def _keywords_for_prefs(prefs: dict) -> list[str]:
    selected_cats = prefs.get("categories", [])
    selected_subs = set(prefs.get("subcategories", []))
    keywords = []
    for cat_name, cat_data in CATEGORIES.items():
        if cat_name not in selected_cats:
            continue
        keywords.extend(cat_data["keywords"])
        for sub_name, sub_kws in cat_data["subcategories"].items():
            if sub_name in selected_subs:
                keywords.extend(sub_kws)
    return list(set(kw.lower() for kw in keywords))


def weigh(items: list[dict], prefs_path: str = PREFS_PATH) -> list[dict]:
    prefs = load_prefs(prefs_path)
    keywords = _keywords_for_prefs(prefs)

    for item in items:
        if not keywords:
            item["_weight"] = 1.0
        else:
            title_lower = item["title"].lower()
            matches = sum(1 for kw in keywords if kw in title_lower)
            item["_weight"] = _BOOST_PER_MATCH ** matches if matches else 1.0

    return items
