from __future__ import annotations

from agents.base_agent import BaseAgent
from utils.learning_content import local_summary


class SummaryAgent(BaseAgent):
    prompt_file = "summary_prompt.txt"
    system_instruction = "You are an expert AI educator. Return valid JSON only and use only the transcript."

    def generate(self, transcript: str, title: str = "") -> dict:
        return self.run_json(transcript=transcript, title=title)

    def fallback(self, transcript: str, title: str = "", **_) -> dict:
        return local_summary(transcript, title)
