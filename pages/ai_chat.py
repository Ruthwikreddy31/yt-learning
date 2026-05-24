from __future__ import annotations

import streamlit as st

from database.mongodb import mongo
from services.rag_service import rag_service
from utils.security import check_rate_limit
from utils.session import get_active_user
from utils.text import format_seconds
from utils.ui import empty_video_state


def render_ai_chat() -> None:
    user = get_active_user()
    video_id = st.session_state.get("selected_video_id")
    if not video_id:
        empty_video_state()
        return
    video = mongo.find_one("videos", {"_id": video_id}) or {}
    st.title("AI Tutor Chat")
    st.caption("Answers are generated only from retrieved transcript context.")

    query = st.text_input("Semantic search", placeholder="Where did the speaker explain APIs?")
    if query:
        hits = rag_service.retrieve(video_id, query)
        for hit in hits:
            st.markdown(
                f"<div class='search-hit'><b>{format_seconds(hit.get('start'))}</b> {hit.get('text', '')[:500]}</div>",
                unsafe_allow_html=True,
            )

    st.divider()
    for message in mongo.find("chat_history", {"user_id": user["id"], "video_id": video_id})[-20:]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input(f"Ask about {video.get('title', 'this video')}")
    if question:
        if not check_rate_limit("chat", limit=20, window_seconds=300):
            return
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving transcript context"):
                result = rag_service.answer(video_id, question, st.session_state.selected_ai_model, user["id"])
            st.write(result["answer"])
            if result["citations"]:
                with st.expander("Transcript citations"):
                    for citation in result["citations"]:
                        st.write(f"{format_seconds(citation.get('start'))}: {citation.get('text')[:500]}")
