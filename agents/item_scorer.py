from agents.llm_provider import call_structured

_TOOL_NAME = "score_article"
_TOOL_DESC = "Score article relevance and extract metadata"
_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "2-3 sentence summary of the article",
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "5-10 key topics or entities mentioned",
        },
        "categories": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Category names from user preferences that match this article",
        },
        "score": {
            "type": "number",
            "description": "Relevance score 0.0-1.0 based on user preferences. 1.0 = highly relevant, 0.0 = not relevant",
        },
    },
    "required": ["summary", "keywords", "categories", "score"],
}


def score_item(item: dict, prefs: dict) -> tuple[dict | None, dict]:
    """Score one item via configured LLM provider.
    Returns (result, usage). result has summary, keywords, categories, score.
    Returns (None, {}) on any failure."""
    body = (item.get("body") or "")[:2000]
    title = item.get("title", "")
    source = item.get("source", "")
    categories = prefs.get("categories", [])
    subcategories = prefs.get("subcategories", [])

    pref_text = ""
    if categories:
        pref_text += f"Categories: {', '.join(categories)}\n"
    if subcategories:
        pref_text += f"Topics: {', '.join(subcategories)}\n"
    if not pref_text:
        pref_text = "No specific preferences — score general tech/AI relevance."

    prompt = (
        f"User preferences:\n{pref_text}\n"
        f"Article:\nTitle: {title}\nSource: {source}\nContent: {body}\n\n"
        f"Score this article's relevance to the user's preferences and extract key metadata."
    )

    result, usage = call_structured(prompt, _TOOL_NAME, _TOOL_DESC, _SCHEMA)
    if result is not None:
        result["score"] = max(0.0, min(1.0, float(result.get("score", 0.5))))
    return result, usage
