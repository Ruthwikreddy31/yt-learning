from __future__ import annotations

from agents.chapter_agent import ChapterDetectionAgent
from agents.notes_agent import NotesAgent
from agents.summary_agent import SummaryAgent
from database.mongodb import mongo
from utils.text import clamp_transcript


class SummaryService:
    def generate_all(self, video_id: str, provider: str = "gemini") -> dict:
        video = mongo.find_one("videos", {"_id": video_id}) or {}
        transcript_doc = mongo.find_one("transcripts", {"video_id": video_id})
        if not transcript_doc:
            raise ValueError("Transcript not found.")
        text = clamp_transcript(transcript_doc["text"])
        summary = SummaryAgent(provider).generate(text, video.get("title", ""))
        chapters = ChapterDetectionAgent(provider).generate(transcript_doc.get("chunks", []), video.get("title", ""))
        notes = NotesAgent(provider).generate(text, video.get("title", ""))
        payload = {**summary, "chapters": chapters.get("chapters", []), "notes": notes, "video_id": video_id}
        mongo.upsert("summaries", {"video_id": video_id}, payload)
        return payload


summary_service = SummaryService()
