from __future__ import annotations

import streamlit as st


def card(body: str) -> None:
    st.markdown(f"<div class='ai-card'>{body}</div>", unsafe_allow_html=True)


def metric_card(label: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="muted">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="muted">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_video_state() -> None:
    st.info("Upload or select a YouTube video to start learning from transcript-grounded AI.")
