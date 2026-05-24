from __future__ import annotations

from agents.notes_agent import NotesAgent
from database.mongodb import mongo
from utils.text import clamp_transcript


class NotesService:
    def generate(self, video_id: str, provider: str = "gemini") -> dict:
        video = mongo.find_one("videos", {"_id": video_id}) or {}
        transcript = mongo.find_one("transcripts", {"video_id": video_id})
        if not transcript:
            raise ValueError("Transcript not found.")
        notes = NotesAgent(provider).generate(clamp_transcript(transcript["text"]), video.get("title", ""))
        mongo.upsert("notes", {"video_id": video_id}, notes | {"video_id": video_id})
        return notes


notes_service = NotesService()
