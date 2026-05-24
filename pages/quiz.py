from __future__ import annotations

import streamlit as st

from database.mongodb import mongo
from services.quiz_service import quiz_service
from utils.security import check_rate_limit
from utils.session import get_active_user
from utils.ui import empty_video_state


def render_quiz() -> None:
    user = get_active_user()
    video_id = st.session_state.get("selected_video_id")
    if not video_id:
        empty_video_state()
        return
    video = mongo.find_one("videos", {"_id": video_id}) or {}
    st.title("Adaptive Quiz")
    st.caption(video.get("title", "Selected video"))

    left, right = st.columns([1, 1])
    with left:
        difficulty = st.selectbox("Difficulty", ["adaptive", "easy", "medium", "hard"])
    with right:
        chapter = st.text_input("Chapter scope", "full video")

    quiz = mongo.find_one("quizzes", {"video_id": video_id, "difficulty": difficulty, "chapter": chapter})
    has_questions = bool((quiz or {}).get("questions") or (quiz or {}).get("quizzes"))
    if st.button("Generate quiz" if not has_questions else "Regenerate quiz", use_container_width=True):
        if not check_rate_limit("generate_quiz", limit=8, window_seconds=300):
            return
        with st.spinner("Creating transcript-grounded questions"):
            try:
                quiz = quiz_service.generate(video_id, st.session_state.selected_ai_model, difficulty, chapter)
                st.session_state.quiz_answers = {}
            except Exception as exc:
                st.error(f"Could not generate quiz: {exc}")
                return

    if not quiz:
        st.info("Generate a quiz to begin.")
        return

    questions = quiz.get("questions") or quiz.get("quizzes", [])
    with st.form("quiz_form"):
        answers: dict[str, str] = {}
        for index, question in enumerate(questions):
            st.markdown(f"### {index + 1}. {question.get('question')}")
            options = question.get("options") or (["True", "False"] if question.get("type") == "true_false" else [])
            if options:
                answers[str(index)] = st.radio(
                    "Select your answer",
                    options,
                    key=f"q_{video_id}_{index}",
                    index=None,
                    label_visibility="collapsed",
                )
            else:
                answers[str(index)] = st.text_area("Your answer", key=f"q_{video_id}_{index}")
        submitted = st.form_submit_button("Submit quiz", use_container_width=True)

    if submitted:
        unanswered = [str(index + 1) for index in range(len(questions)) if not answers.get(str(index))]
        if unanswered:
            st.warning("Please answer every question before submitting. Missing: " + ", ".join(unanswered))
            return
        result = quiz_service.grade(video_id, user["id"], questions, answers)
        st.success(f"Score: {result['score']}%")
        if result["weak_topics"]:
            st.warning("Weak topics: " + ", ".join(sorted(set(result["weak_topics"]))))
        for index, question in enumerate(questions):
            with st.expander(f"Review question {index + 1}"):
                st.write("Answer:", question.get("answer"))
                st.write(question.get("explanation", ""))
