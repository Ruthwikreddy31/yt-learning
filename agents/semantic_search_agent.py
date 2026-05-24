from __future__ import annotations

from services.chromadb_service import chromadb_service


class SemanticSearchAgent:
    def search(self, video_id: str, query: str, top_k: int = 5) -> list[dict]:
        return chromadb_service.query(video_id, query, top_k)
