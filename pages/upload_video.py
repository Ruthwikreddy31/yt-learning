from __future__ import annotations

import streamlit as st

from database.mongodb import mongo
from services.document_service import document_service
from services.flashcard_service import flashcard_service
from services.quiz_service import quiz_service
from services.summary_service import summary_service
from services.video_pipeline import video_pipeline
from utils.security import check_rate_limit
from utils.session import get_active_user


def render_upload_video() -> None:
    user = get_active_user()
    st.title("Upload Learning Source")
    st.caption("Use a YouTube link or upload a PDF/document. The app indexes the content for summaries, quizzes, flashcards, semantic search, and AI chat.")

    youtube_tab, document_tab = st.tabs(["YouTube link", "Document / PDF"])

    with youtube_tab:
        with st.form("youtube_upload"):
            url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
            submitted = st.form_submit_button("Process video", use_container_width=True)

        if submitted:
            if not url:
                st.error("Paste a YouTube URL first.")
                return
            if not check_rate_limit("ingest_video", limit=4, window_seconds=300):
                return
            progress = st.progress(0, text="Reading video metadata")
            try:
                progress.progress(25, text="Extracting transcript or preparing Whisper fallback")
                video_id = video_pipeline.ingest(url, user["id"])
                st.session_state.selected_video_id = video_id
                video = mongo.find_one("videos", {"_id": video_id}) or {}
                if video.get("status") == "ready":
                    progress.progress(65, text="Generating summary, quiz, and flashcards")
                    _generate_study_assets(video_id)
                    progress.progress(100, text="Ready")
                    st.success("Video is ready with summary, quiz, and flashcards.")
                else:
                    progress.progress(100, text="Saved")
                    st.warning(video.get("error", "Video was saved, but transcript extraction needs attention."))
                st.session_state.page = "Summary"
                st.rerun()
            except Exception as exc:
                st.error(f"Could not process this video: {exc}")

    with document_tab:
        uploaded = st.file_uploader("Upload PDF, DOCX, TXT, or Markdown", type=["pdf", "docx", "txt", "md"])
        if st.button("Process document", use_container_width=True, disabled=uploaded is None):
            if not check_rate_limit("ingest_document", limit=8, window_seconds=300):
                return
            progress = st.progress(0, text="Reading document")
            try:
                video_id = document_service.ingest(uploaded, user["id"])
                st.session_state.selected_video_id = video_id
                progress.progress(65, text="Generating summary, quiz, and flashcards")
                _generate_study_assets(video_id)
                progress.progress(100, text="Ready")
                st.success("Document is ready with summary, quiz, and flashcards.")
                st.session_state.page = "Summary"
                st.rerun()
            except Exception as exc:
                st.error(f"Could not process this document: {exc}")


def _generate_study_assets(video_id: str) -> None:
    provider = st.session_state.get("selected_ai_model", "gemini")
    generators = [
        lambda active_provider: summary_service.generate_all(video_id, active_provider),
        lambda active_provider: quiz_service.generate(video_id, active_provider),
        lambda active_provider: flashcard_service.generate(video_id, active_provider),
    ]
    for generate in generators:
        try:
            generate(provider)
        except Exception:
            generate("local")
