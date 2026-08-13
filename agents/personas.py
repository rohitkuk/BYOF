import re as _re

_TOKEN_SPLIT = _re.compile(r'[^\w-]+')

SCORING_MODE = "reweight"

_BOOST_PER_MATCH = 0.15
_BOOST_CAP = 1.6
_DEFAULT_PERSONA = "generalist"

PERSONAS = {
    "researcher": {
        "source_weights": {
            "ArXiv": 2.0,
            "MIT Technology Review": 1.5,
            "TechCrunch": 0.7,
            "TLDR Tech": 0.8,
            "Google News": 0.9,
        },
        "keyword_affinities": [
            "paper", "model", "study", "research", "benchmark",
            "dataset", "neural", "training", "analysis", "arxiv",
        ],
    },
    "generalist": {
        "source_weights": {},
        "keyword_affinities": [],
    },
    "engineer": {
        "source_weights": {
            "TechCrunch": 1.8,
            "TLDR Tech": 1.8,
            "Google News": 1.0,
            "MIT Technology Review": 0.8,
            "ArXiv": 0.7,
        },
        "keyword_affinities": [
            "open-source", "tool", "api", "deploy", "build",
            "github", "library", "framework", "release", "launch",
        ],
    },
}


def _keyword_boost(item: dict, affinities: list[str]) -> float:
    if not affinities:
        return 1.0
    text = item.get("title", "").lower()
    kws = [k.lower() for k in (item.get("keywords") or [])]
    tokens: set[str] = set(_TOKEN_SPLIT.split(text))
    for kw in kws:
        tokens.update(_TOKEN_SPLIT.split(kw))
    tokens.discard("")
    count = sum(1 for aff in affinities if aff.lower() in tokens)
    return min(_BOOST_CAP, 1.0 + _BOOST_PER_MATCH * count)


def apply_persona(items: list[dict], persona_name: str) -> list[dict]:
    if SCORING_MODE == "rescore":
        return _rescore_persona(items, persona_name)

    persona = PERSONAS.get(persona_name) or PERSONAS[_DEFAULT_PERSONA]
    sw_map = persona["source_weights"]
    affinities = persona["keyword_affinities"]

    for item in items:
        sw = sw_map.get(item.get("source", ""), 1.0)
        kb = _keyword_boost(item, affinities)
        item["score"] = item["score"] * sw * kb

    return sorted(items, key=lambda x: x["score"], reverse=True)


def _rescore_persona(items: list[dict], persona_name: str) -> list[dict]:
    raise NotImplementedError(
        "rescore mode not implemented — set SCORING_MODE='reweight'"
    )
