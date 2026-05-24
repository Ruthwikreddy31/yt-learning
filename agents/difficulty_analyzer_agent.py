from __future__ import annotations


class DifficultyAnalyzerAgent:
    def analyze(self, attempts: list[dict]) -> dict:
        weak_topics: dict[str, int] = {}
        for attempt in attempts:
            for topic in attempt.get("weak_topics", []):
                weak_topics[topic] = weak_topics.get(topic, 0) + 1
        level = "beginner" if not attempts else "intermediate"
        if attempts and sum(a.get("score", 0) for a in attempts) / len(attempts) >= 85:
            level = "advanced"
        return {"learner_level": level, "weak_topics": sorted(weak_topics, key=weak_topics.get, reverse=True)}
