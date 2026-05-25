from __future__ import annotations

import streamlit as st

from config import settings
from database.mongodb import mongo
from pages.ai_chat import render_ai_chat
from pages.analytics import render_analytics
from pages.dashboard import render_dashboard
from pages.flashcards import render_flashcards
from pages.quiz import render_quiz
from pages.summary import render_summary
from pages.upload_video import render_upload_video
from services.history_service import history_service
from static.theme import inject_theme
from utils.session import get_active_user


st.set_page_config(
    page_title="AI YouTube Learning Assistant",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

PAGES = {
    "Dashboard": render_dashboard,
    "Upload Source": render_upload_video,
    "Summary": render_summary,
    "Quiz": render_quiz,
    "Flashcards": render_flashcards,
    "AI Chat": render_ai_chat,
    "Analytics": render_analytics,
}


def bootstrap_state() -> None:
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("selected_video_id", None)
    st.session_state.setdefault("selected_ai_model", "gemini")
    st.session_state.setdefault("chat_messages", [])
    st.session_state.setdefault("quiz_answers", {})


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## AI Learning Studio")
        st.caption("No login required. Your work is stored locally unless MongoDB is configured.")

        page = st.radio(
            "Workspace",
            list(PAGES.keys()),
            index=list(PAGES.keys()).index(st.session_state.page if st.session_state.page in PAGES else "Dashboard"),
        )
        st.session_state.page = page

        st.selectbox(
            "AI provider",
            options=["gemini", "openai", "local", "groq"],
            key="selected_ai_model",
            help="Use Gemini as default. Local works offline. Groq is optional.",
        )

        st.divider()
        st.caption("History")
        current_user = get_active_user()
        history = mongo.find("videos", {"user_id": current_user["id"]})
        for video in history[-8:][::-1]:
            label = video.get("title") or video.get("youtube_id") or "Untitled video"
            open_col, delete_col = st.columns([5, 1])
            with open_col:
                if st.button(label[:42], key=f"history_{video['_id']}", use_container_width=True):
                    st.session_state.selected_video_id = str(video["_id"])
                    st.session_state.page = "Summary"
                    st.rerun()
            with delete_col:
                if st.button("x", key=f"delete_{video['_id']}", help="Delete this source"):
                    history_service.delete_source(str(video["_id"]))
                    if st.session_state.get("selected_video_id") == str(video["_id"]):
                        st.session_state.selected_video_id = None
                        st.session_state.page = "Dashboard"
                    st.rerun()

        if history:
            st.divider()
            confirm_clear = st.checkbox("Confirm clear all history")
            if st.button("Delete all history", use_container_width=True, disabled=not confirm_clear):
                history_service.delete_all_for_user(current_user["id"])
                st.session_state.selected_video_id = None
                st.session_state.page = "Dashboard"
                st.rerun()

        st.divider()
        st.caption("Settings")
        st.write(f"MongoDB: {'connected' if mongo.is_connected else 'local fallback'}")
        st.write(f"Chroma path: `{settings.chroma_persist_dir}`")


def main() -> None:
    bootstrap_state()
    render_sidebar()
    PAGES[st.session_state.page]()


if __name__ == "__main__":
    main()
