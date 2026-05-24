from __future__ import annotations

import json
import re
from typing import Any

from config import settings


def parse_json_object(raw: str, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    fallback = fallback or {}
    if not raw:
        return fallback
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if not match:
            return fallback
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return fallback


def format_seconds(seconds: float | int | None) -> str:
    seconds = int(seconds or 0)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def transcript_to_text(segments: list[dict[str, Any]]) -> str:
    return " ".join(segment.get("text", "").strip() for segment in segments if segment.get("text"))


def chunk_transcript(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    words: list[str] = []
    start = 0.0
    end = 0.0
    for segment in segments:
        segment_words = segment.get("text", "").split()
        if not words:
            start = float(segment.get("start", 0))
        words.extend(segment_words)
        end = float(segment.get("start", 0)) + float(segment.get("duration", 0))
        if len(words) >= settings.chunk_size_words:
            chunks.append({"text": " ".join(words), "start": start, "end": end, "chunk_index": len(chunks)})
            words = words[-settings.chunk_overlap_words :]
            start = max(start, end - 45)
    if words:
        chunks.append({"text": " ".join(words), "start": start, "end": end, "chunk_index": len(chunks)})
    return chunks


def chunk_plain_text(text: str) -> list[dict[str, Any]]:
    words = re.sub(r"\s+", " ", text or "").strip().split()
    chunks: list[dict[str, Any]] = []
    step = max(1, settings.chunk_size_words - settings.chunk_overlap_words)
    for index, start in enumerate(range(0, len(words), step)):
        piece = words[start:start + settings.chunk_size_words]
        if not piece:
            continue
        chunks.append(
            {
                "text": " ".join(piece),
                "start": float(index),
                "end": float(index + 1),
                "chunk_index": index,
            }
        )
    return chunks


def clamp_transcript(text: str) -> str:
    return text[: settings.max_transcript_chars]
