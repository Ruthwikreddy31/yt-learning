from __future__ import annotations

from database.mongodb import mongo
from services.chromadb_service import chromadb_service
from services.transcript_service import transcript_service
from services.youtube_service import extract_youtube_id, youtube_service


class VideoPipeline:
    def ingest(self, youtube_url: str, user_id: str) -> str:
        youtube_id = extract_youtube_id(youtube_url)
        existing = mongo.find_one("videos", {"user_id": user_id, "youtube_id": youtube_id})
        if existing and existing.get("status") == "ready":
            return str(existing["_id"])
        metadata = youtube_service.metadata(youtube_url)
        video = {
            "user_id": user_id,
            "youtube_url": youtube_url,
            "youtube_id": youtube_id,
            "title": metadata.get("title", "YouTube video"),
            "duration_seconds": metadata.get("duration_seconds"),
            "thumbnail_url": metadata.get("thumbnail_url"),
            "status": "processing",
        }
        video_id = str(existing["_id"]) if existing else mongo.insert("videos", video)
        if existing:
            mongo.update("videos", {"_id": video_id}, {"$set": video})
        try:
            transcript = transcript_service.extract(youtube_url)
            mongo.upsert(
                "transcripts",
                {"video_id": video_id},
                {"video_id": video_id, "source": transcript["source"], "text": transcript["text"], "chunks": transcript["chunks"]},
            )
            chromadb_service.upsert_chunks(video_id, transcript["chunks"])
            mongo.update("videos", {"_id": video_id}, {"$set": {"status": "ready"}})
        except Exception as exc:
            mongo.update(
                "videos",
                {"_id": video_id},
                {
                    "$set": {
                        "status": "transcript_failed",
                        "error": (
                            "Video link saved, but transcript extraction failed. "
                            "Use a video with captions, or install FFmpeg and Whisper support. "
                            f"Details: {exc}"
                        ),
                    }
                },
            )
        return video_id


video_pipeline = VideoPipeline()
