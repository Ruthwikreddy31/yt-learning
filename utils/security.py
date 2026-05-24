from __future__ import annotations

import time

import streamlit as st


def check_rate_limit(action: str, limit: int = 8, window_seconds: int = 60) -> bool:
    bucket_key = f"rate_limit_{action}"
    now = time.time()
    bucket = [stamp for stamp in st.session_state.get(bucket_key, []) if now - stamp < window_seconds]
    if len(bucket) >= limit:
        st.error("Too many requests. Please wait a moment and try again.")
        st.session_state[bucket_key] = bucket
        return False
    bucket.append(now)
    st.session_state[bucket_key] = bucket
    return True
