import pytest
from agents.personas import apply_persona, _keyword_boost, PERSONAS, SCORING_MODE


def _item(title="", source="Google News", score=1.0, keywords=None):
    return {"title": title, "source": source, "score": score, "keywords": keywords or []}


def test_scoring_mode_is_reweight():
    assert SCORING_MODE == "reweight"


def test_generalist_leaves_scores_unchanged():
    items = [_item(source="ArXiv", score=2.0), _item(source="TechCrunch", score=1.0)]
    result = apply_persona(items, "generalist")
    assert abs(result[0]["score"] - 2.0) < 0.01
    assert abs(result[1]["score"] - 1.0) < 0.01


def test_researcher_boosts_arxiv_over_techcrunch():
    items = [_item(source="TechCrunch", score=1.0), _item(source="ArXiv", score=1.0)]
    result = apply_persona(items, "researcher")
    arxiv = next(i for i in result if i["source"] == "ArXiv")
    tech = next(i for i in result if i["source"] == "TechCrunch")
    assert arxiv["score"] > tech["score"]


def test_engineer_boosts_techcrunch_over_arxiv():
    items = [_item(source="ArXiv", score=1.0), _item(source="TechCrunch", score=1.0)]
    result = apply_persona(items, "engineer")
    tech = next(i for i in result if i["source"] == "TechCrunch")
    arxiv = next(i for i in result if i["source"] == "ArXiv")
    assert tech["score"] > arxiv["score"]


def test_keyword_boost_caps_at_1_6():
    affinities = PERSONAS["researcher"]["keyword_affinities"]
    item = _item(keywords=affinities)  # all keywords present
    boost = _keyword_boost(item, affinities)
    assert boost <= 1.6


def test_keyword_boost_title_match():
    item = _item(title="new research paper on neural training benchmarks")
    boost = _keyword_boost(item, PERSONAS["researcher"]["keyword_affinities"])
    assert boost > 1.0


def test_keyword_boost_no_affinities_returns_1():
    item = _item(title="some article", keywords=["foo", "bar"])
    boost = _keyword_boost(item, [])
    assert boost == 1.0


def test_unknown_persona_falls_back_to_generalist():
    items = [_item(source="ArXiv", score=1.0)]
    result = apply_persona(items, "not_a_real_persona")
    assert abs(result[0]["score"] - 1.0) < 0.01


def test_result_sorted_descending():
    items = [_item(source="TechCrunch", score=0.5), _item(source="ArXiv", score=1.0)]
    result = apply_persona(items, "researcher")
    scores = [i["score"] for i in result]
    assert scores == sorted(scores, reverse=True)


def test_rescore_mode_raises():
    import agents.personas as p
    original = p.SCORING_MODE
    p.SCORING_MODE = "rescore"
    try:
        with pytest.raises(NotImplementedError):
            apply_persona([_item()], "researcher")
    finally:
        p.SCORING_MODE = original
