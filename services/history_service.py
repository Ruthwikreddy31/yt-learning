from __future__ import annotations

from database.mongodb import mongo
from services.chromadb_service import chromadb_service


RELATED_COLLECTIONS = [
    "transcripts",
    "summaries",
    "quizzes",
    "flashcards",
    "notes",
    "analytics",
    "chat_history",
]


class HistoryService:
    def delete_source(self, video_id: str) -> None:
        mongo.delete_many("videos", {"_id": video_id})
        for collection in RELATED_COLLECTIONS:
            mongo.delete_many(collection, {"video_id": video_id})
        chromadb_service.delete_video(video_id)

    def delete_all_for_user(self, user_id: str) -> None:
        videos = mongo.find("videos", {"user_id": user_id})
        for video in videos:
            self.delete_source(str(video["_id"]))
        mongo.delete_many("analytics", {"user_id": user_id})
        mongo.delete_many("chat_history", {"user_id": user_id})


history_service = HistoryService()
