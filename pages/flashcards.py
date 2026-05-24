from __future__ import annotations

import streamlit as st

from database.mongodb import mongo
from services.flashcard_service import flashcard_service
from utils.security import check_rate_limit
from utils.session import get_active_user
from utils.ui import empty_video_state


def render_flashcards() -> None:
    get_active_user()
    video_id = st.session_state.get("selected_video_id")
    if not video_id:
        empty_video_state()
        return
    video = mongo.find_one("videos", {"_id": video_id}) or {}
    st.title("Flashcards")
    st.caption(video.get("title", "Selected video"))

    deck = mongo.find_one("flashcards", {"video_id": video_id})
    has_cards = bool((deck or {}).get("flashcards") or (deck or {}).get("cards"))
    if st.button("Generate flashcards" if not has_cards else "Regenerate flashcards", use_container_width=True):
        if not check_rate_limit("generate_flashcards", limit=8, window_seconds=300):
            return
        with st.spinner("Creating study cards"):
            try:
                deck = flashcard_service.generate(video_id, st.session_state.selected_ai_model)
            except Exception as exc:
                st.error(f"Could not generate flashcards: {exc}")
                return

    cards = (deck or {}).get("flashcards") or (deck or {}).get("cards", [])
    if not cards:
        st.info("Generate flashcards to study key concepts.")
        return
    for card in cards:
        with st.container(border=True):
            st.markdown(f"<div class='flashcard'><h3>{card.get('front')}</h3><p>{card.get('back')}</p><span class='muted'>{card.get('topic', '')}</span></div>", unsafe_allow_html=True)
