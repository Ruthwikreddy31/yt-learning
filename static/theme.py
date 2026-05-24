from __future__ import annotations

from pathlib import Path

import streamlit as st


def inject_theme() -> None:
    css_path = Path(__file__).with_name("custom.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
