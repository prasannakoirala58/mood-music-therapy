"""
app.py  —  Streamlit UI  (Phase 5 — build after CLI is fully working)

Mood input → emotion detection → 3-song ISO journey display with Spotify links.
"""

import streamlit as st

# TODO: implement Phase 5 UI
# Imports from backend src will go here once wired up

st.set_page_config(
    page_title="Music Mood Therapy",
    page_icon="🎵",
    layout="centered",
)

st.title("🎵 Music Mood Therapy")
st.caption("Tell me how you feel. I'll find your path.")

st.info("Frontend coming in Phase 5 — run the CLI first via `docker-compose run backend`")
