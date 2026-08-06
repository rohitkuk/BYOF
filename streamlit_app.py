import streamlit as st
from agents.aggregation import rank
from db.store import init_db

DB_PATH = "db/byof.db"

st.set_page_config(page_title="BYOF", layout="centered")
st.title("BYOF — Build Your Own Feed")

conn = init_db(DB_PATH)
conn.close()

ranked = rank(DB_PATH)

if not ranked:
    st.info("No items yet. Run `uv run python app.py` to fetch.")
else:
    st.caption(f"{len(ranked)} items · ranked by recency")
    for item in ranked:
        st.markdown(f"**[{item['title']}]({item['url']})**")
        st.caption(f"{item['source']} · {item['published_at']}")
        st.divider()
