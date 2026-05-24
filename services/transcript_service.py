from __future__ import annotations

from pathlib import Path

from config import settings
from services.youtube_service import extract_youtube_id
from utils.text import chunk_transcript, transcript_to_text


class TranscriptService:
    def extract(self, youtube_url: str) -> dict:
        video_id = extract_youtube_id(youtube_url)
        transcript_errors: list[str] = []
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            segments = self._fetch_youtube_transcript(YouTubeTranscriptApi, video_id)
            return {"source": "youtube", "segments": segments, "text": transcript_to_text(segments), "chunks": chunk_transcript(segments)}
        except Exception as exc:
            transcript_errors.append(f"YouTube captions failed: {exc}")

        try:
            return self._whisper_fallback(youtube_url)
        except Exception as exc:
            transcript_errors.append(f"Whisper fallback failed: {exc}")
            raise RuntimeError(" ".join(transcript_errors))

    def _fetch_youtube_transcript(self, api_class, video_id: str) -> list[dict]:
        languages = ["en", "en-US", "en-GB", "hi"]
        if hasattr(api_class, "get_transcript"):
            return api_class.get_transcript(video_id, languages=languages)

        api = api_class()
        fetched = api.fetch(video_id, languages=languages)
        segments = []
        for item in fetched:
            if isinstance(item, dict):
                segments.append(item)
            else:
                start = float(getattr(item, "start", 0))
                duration = float(getattr(item, "duration", 0))
                text = str(getattr(item, "text", ""))
                segments.append({"text": text, "start": start, "duration": duration})
        return segments

    def _whisper_fallback(self, youtube_url: str) -> dict:
        audio_file = self._download_audio(youtube_url)
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(str(audio_file))
        segments = [
            {"text": item.get("text", ""), "start": float(item.get("start", 0)), "duration": float(item.get("end", 0)) - float(item.get("start", 0))}
            for item in result.get("segments", [])
        ]
        return {"source": "whisper", "segments": segments, "text": result.get("text", transcript_to_text(segments)), "chunks": chunk_transcript(segments)}

    def _download_audio(self, youtube_url: str) -> Path:
        import yt_dlp

        output = settings.upload_path / "%(id)s.%(ext)s"
        opts = {
            "format": "bestaudio/best",
            "outtmpl": str(output),
            "quiet": True,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
        return settings.upload_path / f"{info['id']}.mp3"


transcript_service = TranscriptService()
