import json
import math
from datetime import datetime, timezone

from db.store import get_signals_with_items

_SIGNAL_VALUES = {"liked": 1.0, "saved": 1.5, "skipped": -1.0}
_HALF_LIFE_DAYS = 7
_WEIGHT_SCALE = 0.15
_BOOST_MIN = 0.4
_BOOST_MAX = 2.5


def _decay(created_at: str) -> float:
    try:
        ts = datetime.fromisoformat(created_at)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        days_ago = (datetime.now(timezone.utc) - ts).total_seconds() / 86400
        return math.exp(-math.log(2) / _HALF_LIFE_DAYS * days_ago)
    except Exception:
        return 0.0


def _to_boost(raw: float) -> float:
    return max(_BOOST_MIN, min(_BOOST_MAX, 1.0 + raw * _WEIGHT_SCALE))


def compute_learned_weights(conn) -> dict:
    rows = get_signals_with_items(conn)
    source_raw: dict[str, float] = {}
    keyword_raw: dict[str, float] = {}
    skipped_urls: list[str] = []

    for row in rows:
        action = row["action"]
        if action == "skipped":
            skipped_urls.append(row["url"])

        sv = _SIGNAL_VALUES.get(action, 0.0)
        if sv == 0.0:
            continue

        w = sv * _decay(row["created_at"])
        source = row["source"]
        if source:
            source_raw[source] = source_raw.get(source, 0.0) + w

        kws = json.loads(row["llm_keywords"] or "[]")
        for kw in kws:
            keyword_raw[kw] = keyword_raw.get(kw, 0.0) + w

    return {
        "source_boosts": {s: _to_boost(v) for s, v in source_raw.items()},
        "keyword_boosts": {k: _to_boost(v) for k, v in keyword_raw.items()},
        "skipped_urls": list(set(skipped_urls)),
    }


def apply_learned_weights(items: list[dict], learned: dict) -> list[dict]:
    if not learned:
        return items

    skipped = set(learned.get("skipped_urls", []))
    source_boosts = learned.get("source_boosts", {})
    keyword_boosts = learned.get("keyword_boosts", {})

    result = []
    for item in items:
        if item.get("url") in skipped:
            continue
        sb = source_boosts.get(item.get("source", ""), 1.0)
        kws = item.get("keywords") or []
        kb = (sum(keyword_boosts.get(kw, 1.0) for kw in kws) / len(kws)) if kws and keyword_boosts else 1.0
        item["score"] = item["score"] * sb * kb
        result.append(item)

    return sorted(result, key=lambda x: x["score"], reverse=True)
