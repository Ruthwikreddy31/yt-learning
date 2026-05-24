from __future__ import annotations

from agents.quiz_agent import QuizAgent
from database.mongodb import mongo
from utils.text import clamp_transcript


class QuizService:
    def generate(self, video_id: str, provider: str = "gemini", difficulty: str = "adaptive", chapter: str = "full video") -> dict:
        video = mongo.find_one("videos", {"_id": video_id}) or {}
        transcript = mongo.find_one("transcripts", {"video_id": video_id})
        if not transcript:
            raise ValueError("Transcript not found.")
        quiz = QuizAgent(provider).generate(clamp_transcript(transcript["text"]), video.get("title", ""), difficulty, chapter)
        if "questions" not in quiz and "quizzes" in quiz:
            quiz["questions"] = quiz.get("quizzes", [])
        quiz.setdefault("questions", [])
        quiz["video_id"] = video_id
        mongo.upsert("quizzes", {"video_id": video_id, "difficulty": difficulty, "chapter": chapter}, quiz | {"difficulty": difficulty, "chapter": chapter})
        return quiz

    def grade(self, video_id: str, user_id: str, questions: list[dict], answers: dict[str, str]) -> dict:
        correct = 0
        weak_topics: list[str] = []
        for index, question in enumerate(questions):
            expected = str(question.get("answer", "")).strip().lower()
            actual = str(answers.get(str(index), "")).strip().lower()
            if actual == expected:
                correct += 1
            else:
                weak_topics.append(question.get("topic", "general"))
        total = len(questions) or 1
        score = round(correct / total * 100, 2)
        attempt = {"user_id": user_id, "video_id": video_id, "score": score, "total": total, "weak_topics": weak_topics, "answers": answers}
        mongo.insert("analytics", attempt)
        return attempt


quiz_service = QuizService()
