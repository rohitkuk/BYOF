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
