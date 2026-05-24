from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse


def extract_youtube_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.hostname in {"youtu.be", "www.youtu.be"}:
        return parsed.path.strip("/")
    if parsed.hostname and "youtube" in parsed.hostname:
        query_id = parse_qs(parsed.query).get("v", [None])[0]
        if query_id:
            return query_id
        match = re.search(r"/(?:embed|shorts)/([^/?]+)", parsed.path)
        if match:
            return match.group(1)
    raise ValueError("Please paste a valid YouTube URL.")


class YouTubeService:
    def metadata(self, url: str) -> dict:
        video_id = extract_youtube_id(url)
        data = {"youtube_id": video_id, "title": f"YouTube video {video_id}", "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"}
        try:
            import yt_dlp

            with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                data.update(
                    {
                        "title": info.get("title") or data["title"],
                        "duration_seconds": info.get("duration"),
                        "thumbnail_url": info.get("thumbnail") or data["thumbnail_url"],
                    }
                )
        except Exception:
            pass
        return data


youtube_service = YouTubeService()
