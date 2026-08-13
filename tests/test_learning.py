import math

import pytest
from db.store import init_db, save_signal, get_signals_with_items, save_items


def test_save_signal_inserts_row(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    save_signal(conn, "http://example.com", "liked")
    rows = get_signals_with_items(conn)
    assert len(rows) == 1
    assert rows[0]["url"] == "http://example.com"
    assert rows[0]["action"] == "liked"
    assert rows[0]["created_at"] is not None


def test_get_signals_joins_items(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    save_items(conn, [{"title": "T", "url": "http://a.com", "source": "ArXiv",
                       "published_at": "", "raw": {}}])
    conn.execute("UPDATE items SET llm_keywords = ? WHERE url = ?",
                 ('["neural"]', "http://a.com"))
    conn.commit()
    save_signal(conn, "http://a.com", "liked")
    rows = get_signals_with_items(conn)
    assert rows[0]["source"] == "ArXiv"
    assert rows[0]["llm_keywords"] == '["neural"]'


def test_multiple_signals_same_url(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    save_signal(conn, "http://a.com", "liked")
    save_signal(conn, "http://a.com", "saved")
    rows = get_signals_with_items(conn)
    assert len(rows) == 2


def test_signal_unknown_url_source_is_none(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    save_signal(conn, "http://unknown.com", "skipped")
    rows = get_signals_with_items(conn)
    assert rows[0]["source"] is None
    assert rows[0]["llm_keywords"] is None


# ── Task 2: agents/learning.py tests ─────────────────────────────────────────

from agents.learning import compute_learned_weights, apply_learned_weights


def test_liked_boosts_source(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    conn.execute("""INSERT INTO items (title, url, source, published_at, fetched_at, raw)
                    VALUES ('T', 'http://a.com', 'ArXiv', '', datetime('now'), '{}')""")
    conn.execute("UPDATE items SET llm_keywords = '[]' WHERE url = 'http://a.com'")
    conn.commit()
    save_signal(conn, "http://a.com", "liked")
    result = compute_learned_weights(conn)
    assert result["source_boosts"].get("ArXiv", 1.0) > 1.0


def test_skipped_demotes_source_and_adds_to_skipped_urls(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    conn.execute("""INSERT INTO items (title, url, source, published_at, fetched_at, raw)
                    VALUES ('T', 'http://a.com', 'TechCrunch', '', datetime('now'), '{}')""")
    conn.execute("UPDATE items SET llm_keywords = '[]' WHERE url = 'http://a.com'")
    conn.commit()
    save_signal(conn, "http://a.com", "skipped")
    result = compute_learned_weights(conn)
    assert result["source_boosts"].get("TechCrunch", 1.0) < 1.0
    assert "http://a.com" in result["skipped_urls"]


def test_saved_outweighs_liked(tmp_path):
    conn_l = init_db(str(tmp_path / "liked.db"))
    conn_s = init_db(str(tmp_path / "saved.db"))
    for conn in (conn_l, conn_s):
        conn.execute("""INSERT INTO items (title, url, source, published_at, fetched_at, raw)
                        VALUES ('T', 'http://a.com', 'ArXiv', '', datetime('now'), '{}')""")
        conn.execute("UPDATE items SET llm_keywords = '[]' WHERE url = 'http://a.com'")
        conn.commit()
    save_signal(conn_l, "http://a.com", "liked")
    save_signal(conn_s, "http://a.com", "saved")
    liked_boost = compute_learned_weights(conn_l)["source_boosts"]["ArXiv"]
    saved_boost = compute_learned_weights(conn_s)["source_boosts"]["ArXiv"]
    assert saved_boost > liked_boost


def test_boost_clamped_to_max(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    conn.execute("""INSERT INTO items (title, url, source, published_at, fetched_at, raw)
                    VALUES ('T', 'http://a.com', 'ArXiv', '', datetime('now'), '{}')""")
    conn.execute("UPDATE items SET llm_keywords = '[]' WHERE url = 'http://a.com'")
    conn.commit()
    for _ in range(30):
        save_signal(conn, "http://a.com", "liked")
    result = compute_learned_weights(conn)
    assert result["source_boosts"]["ArXiv"] <= 2.5


def test_boost_clamped_to_min(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    conn.execute("""INSERT INTO items (title, url, source, published_at, fetched_at, raw)
                    VALUES ('T', 'http://a.com', 'ArXiv', '', datetime('now'), '{}')""")
    conn.execute("UPDATE items SET llm_keywords = '[]' WHERE url = 'http://a.com'")
    conn.commit()
    for _ in range(30):
        save_signal(conn, "http://a.com", "skipped")
    result = compute_learned_weights(conn)
    assert result["source_boosts"]["ArXiv"] >= 0.4


def test_keyword_boost_from_liked_item(tmp_path):
    conn = init_db(str(tmp_path / "test.db"))
    conn.execute("""INSERT INTO items (title, url, source, published_at, fetched_at, raw)
                    VALUES ('T', 'http://a.com', 'ArXiv', '', datetime('now'), '{}')""")
    conn.execute("UPDATE items SET llm_keywords = ? WHERE url = ?",
                 ('["neural", "benchmark"]', "http://a.com"))
    conn.commit()
    save_signal(conn, "http://a.com", "liked")
    result = compute_learned_weights(conn)
    assert result["keyword_boosts"].get("neural", 1.0) > 1.0
    assert result["keyword_boosts"].get("benchmark", 1.0) > 1.0


def test_apply_learned_filters_skipped():
    items = [
        {"url": "http://a.com", "source": "ArXiv", "score": 1.0, "keywords": []},
        {"url": "http://b.com", "source": "TechCrunch", "score": 1.0, "keywords": []},
    ]
    learned = {"source_boosts": {}, "keyword_boosts": {}, "skipped_urls": ["http://a.com"]}
    result = apply_learned_weights(items, learned)
    assert len(result) == 1
    assert result[0]["url"] == "http://b.com"


def test_apply_learned_multiplies_score():
    items = [{"url": "http://a.com", "source": "ArXiv", "score": 1.0, "keywords": ["neural"]}]
    learned = {"source_boosts": {"ArXiv": 2.0}, "keyword_boosts": {"neural": 1.5}, "skipped_urls": []}
    result = apply_learned_weights(items, learned)
    assert result[0]["score"] == pytest.approx(1.0 * 2.0 * 1.5)


def test_apply_learned_empty_dict_returns_items_unchanged():
    items = [{"url": "http://a.com", "source": "ArXiv", "score": 1.0, "keywords": []}]
    result = apply_learned_weights(items, {})
    assert result[0]["score"] == pytest.approx(1.0)


def test_apply_learned_sorts_descending():
    items = [
        {"url": "http://a.com", "source": "ArXiv", "score": 1.0, "keywords": []},
        {"url": "http://b.com", "source": "TechCrunch", "score": 0.5, "keywords": []},
    ]
    learned = {"source_boosts": {"TechCrunch": 3.0}, "keyword_boosts": {}, "skipped_urls": []}
    result = apply_learned_weights(items, learned)
    assert result[0]["url"] == "http://b.com"
