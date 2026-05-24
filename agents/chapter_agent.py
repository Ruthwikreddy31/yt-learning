from __future__ import annotations

from agents.base_agent import BaseAgent
from utils.text import format_seconds


class ChapterDetectionAgent(BaseAgent):
    prompt_file = "chapter_prompt.txt"
    system_instruction = "You create accurate transcript-grounded chapters. Return valid JSON only."

    def generate(self, chunks: list[dict], title: str = "") -> dict:
        transcript_with_timestamps = "\n".join(
            f"[{format_seconds(chunk.get('start'))}] {chunk.get('text', '')[:700]}" for chunk in chunks[:80]
        )
        result = self.run_json(transcript_with_timestamps=transcript_with_timestamps, title=title, chunks=chunks)
        if not result.get("chapters"):
            return self.fallback(chunks=chunks)
        return result

    def fallback(self, chunks: list[dict] | None = None, **_) -> dict:
        chunks = chunks or []
        chapters = [
            {
                "title": f"Section {index + 1}",
                "start": chunk.get("start", 0),
                "end": chunk.get("end", 0),
                "summary": chunk.get("text", "")[:220],
                "important_moment": False,
            }
            for index, chunk in enumerate(chunks[:8])
        ]
        return {"chapters": chapters}


ChapterAgent = ChapterDetectionAgent
