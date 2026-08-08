import html
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

import streamlit as st

from agents.aggregation import rank
from agents.weighing import CATEGORIES, load_prefs, save_prefs
from connectors.google_news import fetch as fetch_google_news
from connectors.techcrunch import fetch as fetch_techcrunch
from db.store import init_db, refresh_article_images, refresh_publisher_logos, save_items

DB_PATH = "db/byof.db"
PREFS_PATH = "preferences.json"
FEED_LIMIT = 20

_SOURCE_TYPE = {
    "Google News": "Article",
    "TechCrunch": "Article",
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

_BG      = "#0e0e0e"
_CARD_BG = "#1a1a1a"
_ACCENT  = "#e85d4a"
_TEXT    = "#f0f0f0"
_MUTED   = "#888"


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


def _is_meaningful_summary(summary: str, title: str) -> bool:
    if not summary or len(summary.strip()) < 20:
        return False
    s = summary.lower().strip()
    t = title.lower().strip()
    return s not in t and t not in s


def _relative_time(published_at: str) -> str:
    try:
        dt = parsedate_to_datetime(published_at)
        now = datetime.now(timezone.utc)
        seconds = (now - dt).total_seconds()
        if seconds < 3600:
            return "Just now"
        elif seconds < 86400:
            return f"{int(seconds // 3600)}h ago"
        elif seconds < 172800:
            return "Yesterday"
        elif seconds < 7 * 86400:
            return f"{int(seconds // 86400)} days ago"
        else:
            return dt.strftime("%b %-d")
    except Exception:
        return published_at or ""


def _favicon_url(item: dict) -> str:
    href = item.get("source_href", "") or ""
    if href:
        domain = urlparse(href).netloc
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=16"
    return ""


def _render_reel_feed(items: list[dict]) -> str:
    cards = ""
    for idx, item in enumerate(items):
        cats = sorted(_item_categories(item))
        cat_label = " · ".join(cats) or "General"
        r, g, b = _CAT_COLORS.get(cats[0] if cats else None, _DEFAULT_COLOR)
        summary = _strip_html(item.get("summary", ""))[:280]
        source = item.get("source", "")
        title_text = item.get("title", "")
        img_url = _item_image(item)
        rel_time = _relative_time(item.get("published_at", ""))
        fav_url = _favicon_url(item)

        fav_html = (
            f'<img src="{_esc(fav_url)}" '
            f'style="width:16px;height:16px;border-radius:2px;flex-shrink:0" '
            f'onerror="this.style.display=\'none\'">'
        ) if fav_url else ""

        meta_html = (
            f'<div style="margin-top:8px;display:flex;align-items:center;gap:6px">'
            f'{fav_html}'
            f'<span style="font-size:12px;color:#666">{_esc(source)} · {_esc(rel_time)}</span>'
            f'</div>'
        )

        summary_html = (
            f'<p style="font-size:13px;color:{_MUTED};line-height:1.5;margin:0;'
            f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">'
            f"{_esc(summary)}</p>"
        ) if _is_meaningful_summary(summary, title_text) else ""

        # Hidden checkboxes — siblings of card content for :has() to work
        checkboxes = (
            f'<input type="checkbox" class="like-toggle" id="like_{idx}" style="position:absolute;opacity:0;pointer-events:none">'
            f'<input type="checkbox" class="dislike-toggle" id="dislike_{idx}" style="position:absolute;opacity:0;pointer-events:none">'
            f'<input type="checkbox" class="save-toggle" id="save_{idx}" style="position:absolute;opacity:0;pointer-events:none">'
        )

        # Action rail — right side of media, vertically centered
        # TODO V2: persist like/dislike/save to db/store.py as user_signals table
        # keys: item_url, signal_type (like/dislike/save), timestamp
        # weighing agent will consume these as explicit preference signals in V2 swarm
        action_rail = (
            f'<div style="position:absolute;right:12px;top:50%;transform:translateY(-50%);'
            f'display:flex;flex-direction:column;gap:8px;z-index:3">'
            f'<label for="like_{idx}" class="action-btn like-btn">&#9825;</label>'
            f'<label for="dislike_{idx}" class="action-btn dislike-btn">&#10005;</label>'
            f'<label for="save_{idx}" class="action-btn save-btn">&#128278;</label>'
            f'</div>'
        )

        if img_url:
            media_box = (
                f'<div style="aspect-ratio:16/9;width:100%;overflow:hidden;position:relative;flex-shrink:0">'
                f'<img src="{_esc(img_url)}" style="width:100%;height:100%;object-fit:cover;display:block">'
                f'<div class="dislike-overlay" style="position:absolute;inset:0;'
                f'background:rgba(0,0,0,0.4);opacity:0;pointer-events:none;'
                f'transition:opacity 200ms;z-index:2"></div>'
                f'<div style="position:absolute;inset:0;'
                f'background:linear-gradient(to top,rgba(0,0,0,0.6) 0%,transparent 50%)">'
                f'<span style="position:absolute;bottom:10px;left:12px;'
                f'background:{_ACCENT};color:white;padding:3px 10px;border-radius:20px;'
                f'font-size:11px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase">'
                f'{_esc(cat_label)}</span>'
                f'</div>'
                f'{action_rail}'
                f'</div>'
            )
        else:
            media_box = (
                f'<div style="aspect-ratio:16/9;width:100%;overflow:hidden;position:relative;flex-shrink:0;'
                f'background:linear-gradient(135deg,rgb({r},{g},{b}),rgba({r},{g},{b},0.55));'
                f'display:flex;align-items:flex-end;padding:10px 12px">'
                f'<div class="dislike-overlay" style="position:absolute;inset:0;'
                f'background:rgba(0,0,0,0.4);opacity:0;pointer-events:none;'
                f'transition:opacity 200ms;z-index:2"></div>'
                f'<span style="background:{_ACCENT};color:white;padding:3px 10px;'
                f'border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.5px;'
                f'text-transform:uppercase;z-index:1;position:relative">{_esc(cat_label)}</span>'
                f'{action_rail}'
                f'</div>'
            )

        cards += (
            # Snap section fills viewport; card centered within it
            f'<div style="height:100svh;scroll-snap-align:start;display:flex;'
            f'flex-direction:column;justify-content:center;padding:56px 8px 8px">'
            f'<div class="card-wrapper" style="position:relative;width:100%;'
            f'border-radius:12px;overflow:hidden;'
            f'box-shadow:0 4px 24px rgba(0,0,0,0.5),0 0 0 1px rgba(255,255,255,0.06)">'
            f'{checkboxes}'
            f'{media_box}'
            f'<div style="background:{_CARD_BG};padding:14px 16px 16px">'
            f'<h2 style="font-size:17px;font-weight:800;line-height:1.35;margin:0 0 6px;color:{_TEXT};'
            f'overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical">'
            f'<a href="{_esc(item["url"])}" target="_blank" style="color:inherit;text-decoration:none">'
            f'{_esc(title_text)}</a></h2>'
            f'{summary_html}'
            f'{meta_html}'
            f'</div>'
            f'</div></div>\n'
        )

    return (
        f'<div style="position:fixed;top:0;left:50%;transform:translateX(-50%);'
        f'width:100%;max-width:680px;bottom:0;z-index:1;'
        f'overflow-y:scroll;scroll-snap-type:y mandatory;'
        f'background:{_BG};font-family:-apple-system,system-ui,sans-serif">'
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


def _apply_filters(items, sel_cats, sel_subcats, date_filter, sel_types, sel_sources):
    cutoff = _cutoff(date_filter)
    out = []
    for item in items:
        if sel_cats and not (_item_categories(item) & set(sel_cats)):
            continue
        if sel_subcats and not (_item_subcategories(item) & set(sel_subcats)):
            continue
        if _content_type(item["source"]) not in sel_types:
            continue
        if sel_sources and item.get("source") not in sel_sources:
            continue
        if cutoff:
            dt = _parse_dt(item.get("published_at", ""))
            if dt is None or dt < cutoff:
                continue
        out.append(item)
    return out


st.set_page_config(page_title="BYOF", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""<style>
header[data-testid="stHeader"]  { display: none !important; }
[data-testid="stToolbar"]       { display: none !important; }
footer                          { display: none !important; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
    min-height: 0 !important;
}
[data-testid="stMain"] { overflow: hidden !important; }

[data-testid="stSidebar"] { background-color: #111 !important; }
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem !important; }


.action-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(0,0,0,0.45);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 18px;
    color: white;
    transition: background 150ms, transform 150ms, color 150ms;
    user-select: none;
    -webkit-user-select: none;
    line-height: 1;
}
.action-btn:hover {
    background: rgba(255,255,255,0.15);
    transform: scale(1.1);
}
.card-wrapper:has(.like-toggle:checked) .like-btn    { color: #e85d4a !important; }
.card-wrapper:has(.dislike-toggle:checked) .dislike-btn { color: #888 !important; }
.card-wrapper:has(.save-toggle:checked) .save-btn    { color: #f0c040 !important; }
.card-wrapper:has(.dislike-toggle:checked) .dislike-overlay {
    opacity: 1 !important;
}

.byof-topbar {
    position: fixed;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 680px;
    z-index: 100;
    display: flex;
    align-items: center;
    padding: 14px 16px;
    pointer-events: none;
    font-family: -apple-system, system-ui, sans-serif;
    background: linear-gradient(to bottom, #0e0e0e 70%, transparent);
}
.byof-topbar-logo {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.18em;
    color: #e85d4a;
    text-transform: uppercase;
}
</style>""", unsafe_allow_html=True)

st.html("""<script>
(function() {
  var doc = window.parent.document;
  if (doc.getElementById('byof-sidebar-fab')) return;
  var btn = doc.createElement('button');
  btn.id = 'byof-sidebar-fab';
  btn.innerHTML = '&#9776;';
  btn.style.cssText = 'position:fixed;top:10px;right:16px;width:40px;height:40px;' +
    'border-radius:50%;background:#e85d4a;color:white;border:none;' +
    'box-shadow:0 2px 8px rgba(0,0,0,0.4);z-index:99999;' +
    'display:flex;align-items:center;justify-content:center;' +
    'cursor:pointer;font-size:18px;line-height:1;' +
    'font-family:-apple-system,system-ui,sans-serif;';
  btn.addEventListener('click', function() {
    var toggle = doc.querySelector('[data-testid="stExpandSidebarButton"]') ||
                 doc.querySelector('[data-testid="stSidebarCollapseButton"]') ||
                 doc.querySelector('[data-testid="collapsedControl"]');
    if (toggle) toggle.click();
  });
  doc.body.appendChild(btn);
})();
</script>""", unsafe_allow_javascript=True)

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
interests_str = " · ".join(prefs["categories"])
ranked = rank(DB_PATH, PREFS_PATH, limit=FEED_LIMIT)
all_cats = list(CATEGORIES.keys())
all_types = sorted({_content_type(item["source"]) for item in ranked}) if ranked else ["Article"]
all_sources = ["Google News", "TechCrunch"]

with st.sidebar:
    st.markdown(
        f'<h2 style="color:{_TEXT};margin:0 0 4px;font-size:20px;font-weight:800">BYOF</h2>'
        f'<p style="color:{_MUTED};font-size:13px;margin:0 0 16px">'
        f'Interests: <span style="color:{_TEXT};font-weight:600">{_esc(interests_str)}</span></p>',
        unsafe_allow_html=True,
    )
    if st.button("Edit preferences", key="edit_prefs_btn"):
        st.session_state["editing_prefs"] = True
        st.rerun()
    st.divider()
    sel_cats = st.multiselect("Category", all_cats, default=[], placeholder="All categories")
    date_filter = st.selectbox("Date", ["All", "Today", "Last 7 days", "Last 30 days"])
    sel_types = st.multiselect("Type", all_types, default=all_types)
    sel_sources = st.multiselect("Source", all_sources, default=all_sources)
    sel_subcats = []
    if sel_cats:
        avail_subcats = []
        for cat in sel_cats:
            avail_subcats.extend(CATEGORIES[cat]["subcategories"].keys())
        sel_subcats = st.multiselect("Subcategory", avail_subcats, default=[])
    st.divider()
    if st.button("↻ Refresh", key="refresh_btn", use_container_width=True):
        with st.spinner("Fetching..."):
            conn = init_db(DB_PATH)
            new_items = save_items(conn, fetch_google_news() + fetch_techcrunch())
            refresh_article_images(conn)
            refresh_publisher_logos(conn)
            conn.close()
        st.toast(f"{new_items} new item(s) added")
        st.rerun()

if not ranked:
    st.info("No items yet. Run `uv run python app.py` to fetch.")
else:
    filtered = _apply_filters(ranked, sel_cats, sel_subcats, date_filter, sel_types, sel_sources)
    if filtered:
        ordered = _sort_images_first(filtered)
        st.markdown('<div class="byof-topbar"><span class="byof-topbar-logo">BYOF</span></div>', unsafe_allow_html=True)
        st.markdown(_render_reel_feed(ordered), unsafe_allow_html=True)
    else:
        st.info("No items match the current filters.")
