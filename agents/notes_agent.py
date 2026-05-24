from __future__ import annotations

from agents.base_agent import BaseAgent
from utils.learning_content import local_notes


class NotesAgent(BaseAgent):
    prompt_file = "notes_prompt.txt"
    system_instruction = "You create structured learning notes. Return valid JSON only."

    def generate(self, transcript: str, title: str = "") -> dict:
        return self.run_json(transcript=transcript, title=title)

    def fallback(self, transcript: str, **_) -> dict:
        return local_notes(transcript, _.get("title", ""))
