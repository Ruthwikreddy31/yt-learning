from __future__ import annotations

from agents.base_agent import BaseAgent
from utils.learning_content import local_quiz


class QuizAgent(BaseAgent):
    prompt_file = "quiz_prompt.txt"
    system_instruction = (
        "You are a careful quiz author. Return valid JSON only. "
        "Create topic-based questions from the uploaded learning content. "
        "Do not quote subtitles or reveal the answer in the question."
    )

    def generate(self, transcript: str, title: str = "", difficulty: str = "adaptive", chapter: str = "full video") -> dict:
        return self.run_json(transcript=transcript, title=title, difficulty=difficulty, chapter=chapter)

    def fallback(self, transcript: str, **_) -> dict:
        return local_quiz(transcript, _.get("title", ""))
