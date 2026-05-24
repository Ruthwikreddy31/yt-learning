from __future__ import annotations

from collections import Counter

from database.mongodb import mongo


class AnalyticsService:
    def dashboard(self, user_id: str) -> dict:
        videos = mongo.find("videos", {"user_id": user_id})
        attempts = mongo.find("analytics", {"user_id": user_id})
        average_score = round(sum(a.get("score", 0) for a in attempts) / len(attempts), 2) if attempts else 0
        weak_counter = Counter(topic for attempt in attempts for topic in attempt.get("weak_topics", []))
        ready_videos = [video for video in videos if video.get("status") == "ready"]
        return {
            "videos_total": len(videos),
            "videos_ready": len(ready_videos),
            "quiz_attempts": len(attempts),
            "average_score": average_score,
            "weak_topics": weak_counter.most_common(8),
            "recent_attempts": attempts[-10:],
        }


analytics_service = AnalyticsService()
