from __future__ import annotations

import pandas as pd
import streamlit as st

from services.analytics_service import analytics_service
from utils.session import get_active_user
from utils.ui import metric_card


def render_analytics() -> None:
    user = get_active_user()
    data = analytics_service.dashboard(user["id"])
    st.title("Learning Analytics")

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Average quiz score", f"{data['average_score']}%")
    with c2:
        metric_card("Attempts", str(data["quiz_attempts"]))
    with c3:
        metric_card("Ready videos", str(data["videos_ready"]))

    if data["recent_attempts"]:
        df = pd.DataFrame(data["recent_attempts"])
        st.subheader("Score trend")
        st.line_chart(df[["score"]])
    else:
        st.info("Complete a quiz to see score trends.")

    st.subheader("Weak topics")
    if data["weak_topics"]:
        st.bar_chart(pd.DataFrame(data["weak_topics"], columns=["topic", "count"]).set_index("topic"))
    else:
        st.caption("No weak topics yet.")
