from __future__ import annotations

import streamlit as st

from database.mongodb import mongo
from services.summary_service import summary_service
from utils.security import check_rate_limit
from utils.session import get_active_user
from utils.text import format_seconds
from utils.ui import empty_video_state


def render_summary() -> None:
    get_active_user()
    video_id = st.session_state.get("selected_video_id")
    if not video_id:
        empty_video_state()
        return
    video = mongo.find_one("videos", {"_id": video_id}) or {}
    st.title(video.get("title", "Video learning view"))

    if video.get("youtube_id"):
        st.video(f"https://www.youtube.com/watch?v={video['youtube_id']}")

    transcript = mongo.find_one("transcripts", {"video_id": video_id})
    if not transcript:
        st.warning(video.get("error", "This video is saved, but no transcript is available yet. Try a video with captions enabled, or install FFmpeg and Whisper dependencies for audio transcription."))
        return

    existing = mongo.find_one("summaries", {"video_id": video_id})
    needs_generation = not existing or not existing.get("short_summary")
    button_label = "Generate summaries, chapters, and notes" if needs_generation else "Regenerate summaries, chapters, and notes"
    if st.button(button_label, use_container_width=True):
        if not check_rate_limit("generate_summary", limit=6, window_seconds=300):
            return
        with st.spinner("Generating transcript-grounded learning materials"):
            try:
                existing = summary_service.generate_all(video_id, st.session_state.selected_ai_model)
                st.success("Generated.")
            except Exception as exc:
                st.error(f"Could not generate summary: {exc}")
                return

    if not existing or not existing.get("short_summary"):
        st.info("Generate learning materials to view summaries, chapters, notes, and insights.")
        return

    tabs = st.tabs(["Summary", "Chapters", "Notes", "Insights"])
    with tabs[0]:
        st.subheader("Short summary")
        st.write(existing.get("short_summary", ""))
        st.subheader("Beginner explanation")
        st.write(existing.get("beginner_summary", ""))
        st.subheader("Technical summary")
        st.write(existing.get("technical_summary", ""))
        st.subheader("Detailed summary")
        st.write(existing.get("detailed_summary", ""))
    with tabs[1]:
        for chapter in existing.get("chapters", []):
            st.markdown(
                f"<div class='chapter-row'><b>{format_seconds(chapter.get('start'))}</b> {chapter.get('title', '')}<br><span class='muted'>{chapter.get('summary', '')}</span></div>",
                unsafe_allow_html=True,
            )
    with tabs[2]:
        notes = existing.get("notes", {})
        for section in notes.get("sections", []):
            st.markdown(f"### {section.get('heading', 'Section')}")
            for bullet in section.get("bullets", []):
                st.markdown(f"- {bullet}")
    with tabs[3]:
        st.write(existing.get("key_insights", []))
        st.write("Tags:", ", ".join(existing.get("tags", [])))
