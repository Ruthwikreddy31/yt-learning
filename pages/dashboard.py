from __future__ import annotations

import streamlit as st

from database.mongodb import mongo
from services.analytics_service import analytics_service
from utils.session import get_active_user
from utils.ui import metric_card


def render_dashboard() -> None:
    user = get_active_user()
    data = analytics_service.dashboard(user["id"])
    st.title("AI YouTube Learning Assistant")
    st.caption("A transcript-grounded study workspace for summaries, quizzes, flashcards, semantic search, and AI tutoring.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Videos", str(data["videos_total"]), "Uploaded learning sources")
    with c2:
        metric_card("Ready", str(data["videos_ready"]), "Indexed for RAG")
    with c3:
        metric_card("Quiz attempts", str(data["quiz_attempts"]), "Assessment history")
    with c4:
        metric_card("Avg score", f"{data['average_score']}%", "Across attempts")

    st.subheader("Recent videos")
    videos = mongo.find("videos", {"user_id": user["id"]})
    if not videos:
        st.info("Start by uploading a YouTube link.")
        if st.button("Upload a source"):
            st.session_state.page = "Upload Source"
            st.rerun()
        return
    for video in videos[-6:][::-1]:
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"### {video.get('title', 'Untitled')}")
                st.caption(f"Status: {video.get('status')} | YouTube ID: {video.get('youtube_id')}")
            with right:
                if st.button("Open", key=f"open_dash_{video['_id']}", use_container_width=True):
                    st.session_state.selected_video_id = str(video["_id"])
                    st.session_state.page = "Summary"
                    st.rerun()
