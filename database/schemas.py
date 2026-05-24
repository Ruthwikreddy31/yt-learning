from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TranscriptChunk(BaseModel):
    text: str
    start: float = 0
    end: float = 0
    chunk_index: int = 0


class Video(BaseModel):
    user_id: str
    youtube_url: HttpUrl | str
    youtube_id: str
    title: str = "YouTube video"
    status: Literal["queued", "processing", "ready", "failed"] = "queued"
    duration_seconds: float | None = None
    thumbnail_url: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)


class Transcript(BaseModel):
    video_id: str
    source: Literal["youtube", "whisper", "manual"]
    text: str
    chunks: list[TranscriptChunk]
    created_at: str = Field(default_factory=now_iso)


class Summary(BaseModel):
    video_id: str
    short_summary: str
    detailed_summary: str
    beginner_summary: str
    technical_summary: str
    key_insights: list[str] = []
    tags: list[str] = []
    chapters: list[dict[str, Any]] = []
    notes: dict[str, Any] = {}
    created_at: str = Field(default_factory=now_iso)


class QuizQuestion(BaseModel):
    question: str
    type: Literal["mcq", "true_false", "conceptual", "coding"] = "mcq"
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    options: list[str] = []
    answer: str
    explanation: str = ""
    topic: str = "general"


class QuizAttempt(BaseModel):
    user_id: str
    video_id: str
    score: float
    total: int
    weak_topics: list[str] = []
    answers: dict[str, Any] = {}
    created_at: str = Field(default_factory=now_iso)


class ChatTurn(BaseModel):
    user_id: str
    video_id: str
    role: Literal["user", "assistant"]
    content: str
    citations: list[dict[str, Any]] = []
    created_at: str = Field(default_factory=now_iso)
