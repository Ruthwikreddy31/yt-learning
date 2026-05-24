from __future__ import annotations

from agents.flashcard_agent import FlashcardAgent
from database.mongodb import mongo
from utils.text import clamp_transcript


class FlashcardService:
    def generate(self, video_id: str, provider: str = "gemini") -> dict:
        video = mongo.find_one("videos", {"_id": video_id}) or {}
        transcript = mongo.find_one("transcripts", {"video_id": video_id})
        if not transcript:
            raise ValueError("Transcript not found.")
        cards = FlashcardAgent(provider).generate(clamp_transcript(transcript["text"]), video.get("title", ""))
        if "flashcards" not in cards and "cards" in cards:
            cards["flashcards"] = cards.get("cards", [])
        cards.setdefault("flashcards", [])
        cards["video_id"] = video_id
        mongo.upsert("flashcards", {"video_id": video_id}, cards)
        return cards


flashcard_service = FlashcardService()
