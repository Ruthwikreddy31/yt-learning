from __future__ import annotations

from agents.base_agent import BaseAgent
from utils.learning_content import local_flashcards


class FlashcardAgent(BaseAgent):
    prompt_file = "flashcard_prompt.txt"
    system_instruction = "You create concise study flashcards. Return valid JSON only."

    def generate(self, transcript: str, title: str = "") -> dict:
        return self.run_json(transcript=transcript, title=title)

    def fallback(self, transcript: str, **_) -> dict:
        return local_flashcards(transcript, _.get("title", ""))
