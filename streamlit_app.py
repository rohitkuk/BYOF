import html
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import streamlit as st

from agents.aggregation import rank
from agents.weighing import CATEGORIES, load_prefs, save_prefs
from connectors.google_news import fetch
from db.store import init_db, refresh_article_images, refresh_publisher_logos, save_items

DB_PATH = "db/byof.db"
PREFS_PATH = "preferences.json"

_SOURCE_TYPE = {
    "Google News": "Article",
    # future: "YouTube": "Video", "Instagram Reels": "Reel", "Newsletter": "Newsletter"
}
_DEFAULT_TYPE = "Article"

_TAG_RE = re.compile(r"<[^>]+>")

_CAT_COLORS = {
    "AI & ML":           (79,  70, 229),
    "Technology":        (8,  145, 178),
    "Business":          (5,  150, 105),
    "Science":           (124,  58, 237),
    "Politics & Policy": (220,  38,  38),
    "Sports":            (217, 119,   6),
}
_DEFAULT_COLOR = (100, 116, 139)


def _content_type(source: str) -> str:
    return _SOURCE_TYPE.get(source, _DEFAULT_TYPE)


def _item_categories(item: dict) -> set[str]:
    title_lower = item["title"].lower()
    return {
        cat_name
        for cat_name, cat_data in CATEGORIES.items()
        if any(kw in title_lower for kw in cat_data["keywords"])
    }


def _item_subcategories(item: dict) -> set[str]:
    title_lower = item["title"].lower()
    result = set()
    for cat_data in CATEGORIES.values():
        for sub_name, sub_kws in cat_data["subcategories"].items():
            if any(kw in title_lower for kw in sub_kws):
                result.add(sub_name)
    return result


def _strip_html(text: str) -> str:
    return html.unescape(_TAG_RE.sub("", text or "")).strip()


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _item_image(item: dict) -> str | None:
    return item.get("image_url") or None


def _sort_images_first(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: 0 if x.get("image_url") else 1)


_CARD_H = 680


def _render_reel_feed(items: list[dict]) -> str:
    cards = ""
    for item in items:
        cats = sorted(_item_categories(item))
        cat_label = " · ".join(cats) or "General"
        r, g, b = _CAT_COLORS.get(cats[0] if cats else None, _DEFAULT_COLOR)
        summary = _strip_html(item.get("summary", ""))[:280]
        source = item.get("source", "")
        pub_date = item.get("published_at", "")
        img_url = _item_image(item)

        summary_html = (
            f'<p style="font-size:13px;color:#ccc;line-height:1.5;margin:0;'
            f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical">'
            f"{_esc(summary)}</p>"
        ) if summary else ""

        if img_url:
            media_box = (
                f'<div style="height:55%;flex-shrink:0;overflow:hidden;position:relative">'
                f'<img src="{_esc(img_url)}" style="width:100%;height:100%;object-fit:cover;display:block">'
                f'<div style="position:absolute;top:0;left:0;right:0;bottom:0;background:linear-gradient(to bottom,transparent 40%,rgba(0,0,0,0.8))">'
                f'<span style="position:absolute;bottom:14px;left:16px;background:rgba(255,255,255,0.18);'
                f'color:white;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;'
                f'letter-spacing:0.5px;text-transform:uppercase">'
                f'{_esc(cat_label)}</span>'
                f'</div></div>'
            )
        else:
            media_box = (
                f'<div style="height:55%;background:linear-gradient(135deg,rgb({r},{g},{b}),rgba({r},{g},{b},0.6));'
                f'flex-shrink:0;display:flex;align-items:flex-end;padding:16px">'
                f'<span style="background:rgba(0,0,0,0.4);color:white;padding:4px 12px;'
                f'border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.5px;'
                f'text-transform:uppercase">{_esc(cat_label)}</span>'
                f'</div>'
            )

        cards += (
            f'<div style="height:{_CARD_H}px;scroll-snap-align:start;display:flex;'
            f'flex-direction:column;overflow:hidden;border-bottom:1px solid #2a2a2a">'
            f'{media_box}'
            f'<div style="flex:1;background:#111;padding:18px 20px;overflow:hidden;'
            f'display:flex;flex-direction:column;gap:8px">'
            f'<h2 style="font-size:15px;font-weight:700;line-height:1.45;margin:0;color:#f0f0f0;'
            f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical">'
            f'<a href="{_esc(item["url"])}" target="_blank" style="color:inherit;text-decoration:none">'
            f'{_esc(item["title"])}</a></h2>'
            f'{summary_html}'
            f'<div style="margin-top:auto;display:flex;gap:10px;flex-wrap:wrap;align-items:center">'
            f'<span style="font-size:11px;color:#888;font-weight:600">{_esc(source)}</span>'
            f'<span style="font-size:10px;color:#555">{_esc(pub_date)}</span>'
            f'</div>'
            f'</div></div>\n'
        )

    return (
        f'<div style="height:{_CARD_H}px;overflow-y:scroll;scroll-snap-type:y mandatory;'
        f'background:#0d0d0d;border-radius:16px;font-family:-apple-system,system-ui,sans-serif">'
        f'{cards}'
        f'</div>'
    )


def _cutoff(date_filter: str) -> datetime | None:
    if date_filter == "All":
        return None
    now = datetime.now(timezone.utc)
    days = {"Today": 1, "Last 7 days": 7, "Last 30 days": 30}
    return now - timedelta(days=days[date_filter])


def _parse_dt(published_at: str) -> datetime | None:
    try:
        return parsedate_to_datetime(published_at)
    except Exception:
        return None


def _apply_filters(items, sel_cats, sel_subcats, date_filter, sel_types):
    cutoff = _cutoff(date_filter)
    out = []
    for item in items:
        if sel_cats and not (_item_categories(item) & set(sel_cats)):
            continue
        if sel_subcats and not (_item_subcategories(item) & set(sel_subcats)):
            continue
        if _content_type(item["source"]) not in sel_types:
            continue
        if cutoff:
            dt = _parse_dt(item.get("published_at", ""))
            if dt is None or dt < cutoff:
                continue
        out.append(item)
    return out


st.set_page_config(page_title="BYOF", layout="centered")

conn = init_db(DB_PATH)
conn.close()

prefs = load_prefs(PREFS_PATH)
has_prefs = bool(prefs.get("categories"))

# --- Setup / edit flow ---
if not has_prefs or st.session_state.get("editing_prefs"):
    st.title("What are you interested in?")

    selected_cats = st.multiselect(
        "Select categories",
        list(CATEGORIES.keys()),
        default=prefs.get("categories", []),
    )

    selected_subs = []
    if selected_cats:
        st.markdown("**Refine with subcategories** *(optional)*")
        for cat in selected_cats:
            subs = list(CATEGORIES[cat]["subcategories"].keys())
            default_subs = [s for s in prefs.get("subcategories", []) if s in subs]
            picked = st.multiselect(cat, subs, default=default_subs, key=f"sub_{cat}")
            selected_subs.extend(picked)

    if st.button("Save & view feed", disabled=not selected_cats):
        save_prefs({"categories": selected_cats, "subcategories": selected_subs}, PREFS_PATH)
        st.session_state["editing_prefs"] = False
        st.rerun()

    st.stop()

# --- Feed view ---
st.title("BYOF — Build Your Own Feed")

with st.sidebar:
    st.markdown(f"**Interests:** {', '.join(prefs['categories'])}")
    if st.button("Edit preferences"):
        st.session_state["editing_prefs"] = True
        st.rerun()

_, btn_col = st.columns([5, 1])
with btn_col:
    if st.button("Refresh", use_container_width=True):
        with st.spinner("Fetching articles + images..."):
            conn = init_db(DB_PATH)
            new_items = save_items(conn, fetch())
            refresh_article_images(conn)
            refresh_publisher_logos(conn)
            conn.close()
        st.toast(f"{new_items} new item(s) added")
        st.rerun()

FEED_LIMIT = 20
ranked = rank(DB_PATH, PREFS_PATH, limit=FEED_LIMIT)

if not ranked:
    st.info("No items yet. Run `uv run python app.py` to fetch.")
else:
    all_cats = list(CATEGORIES.keys())
    all_types = sorted({_content_type(item["source"]) for item in ranked})

    col1, col2, col3 = st.columns(3)
    with col1:
        sel_cats = st.multiselect("Category", all_cats, default=[])
    with col2:
        date_filter = st.selectbox("Date", ["All", "Today", "Last 7 days", "Last 30 days"])
    with col3:
        sel_types = st.multiselect("Type", all_types, default=all_types)

    sel_subcats = []
    if sel_cats:
        avail_subcats = []
        for cat in sel_cats:
            avail_subcats.extend(CATEGORIES[cat]["subcategories"].keys())
        sel_subcats = st.multiselect("Subcategory", avail_subcats, default=[])

    filtered = _apply_filters(ranked, sel_cats, sel_subcats, date_filter, sel_types)
    st.caption(f"{len(filtered)} of {FEED_LIMIT} · ranked by preference · refresh for new picks")

    if filtered:
        ordered = _sort_images_first(filtered)
        st.html(_render_reel_feed(ordered))
    else:
        st.info("No items match the current filters.")
