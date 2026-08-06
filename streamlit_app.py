import streamlit as st
from agents.aggregation import rank
from agents.weighing import CATEGORIES, load_prefs, save_prefs
from db.store import init_db

DB_PATH = "db/byof.db"
PREFS_PATH = "preferences.json"

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

ranked = rank(DB_PATH, PREFS_PATH)

if not ranked:
    st.info("No items yet. Run `uv run python app.py` to fetch.")
else:
    st.caption(f"{len(ranked)} items · ranked by preference")
    for item in ranked:
        st.markdown(f"**[{item['title']}]({item['url']})**")
        st.caption(f"{item['source']} · {item['published_at']}")
        st.divider()
