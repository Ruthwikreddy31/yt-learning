from __future__ import annotations

from typing import Any

from config import settings
from services.embedding_service import embedding_service


class ChromaDBService:
    def __init__(self):
        self.client = None
        self.transcript_embeddings = None
        self.semantic_chunks = None
        self.quiz_embeddings = None
        try:
            # Override sqlite3 with pysqlite3 if available (crucial for older SQLite versions on Streamlit Cloud/Linux)
            try:
                __import__('pysqlite3')
                import sys
                sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
            except ImportError:
                pass

            import chromadb

            self.client = chromadb.PersistentClient(path=str(settings.project_root / settings.chroma_persist_dir))
            self.transcript_embeddings = self.client.get_or_create_collection("transcript_embeddings", metadata={"hnsw:space": "cosine"})
            self.semantic_chunks = self.client.get_or_create_collection("semantic_chunks", metadata={"hnsw:space": "cosine"})
            self.quiz_embeddings = self.client.get_or_create_collection("quiz_embeddings", metadata={"hnsw:space": "cosine"})
        except Exception:
            self.memory: dict[str, list[dict[str, Any]]] = {}

    @property
    def is_configured(self) -> bool:
        return self.semantic_chunks is not None

    def upsert_chunks(self, video_id: str, chunks: list[dict[str, Any]]) -> None:
        if not chunks:
            return
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.embed_many(texts)
        if self.is_configured:
            ids = [f"{video_id}:{chunk.get('chunk_index', i)}" for i, chunk in enumerate(chunks)]
            metadatas = [
                {
                    "video_id": video_id,
                    "start": float(chunk.get("start", 0)),
                    "end": float(chunk.get("end", 0)),
                    "chunk_index": int(chunk.get("chunk_index", i)),
                }
                for i, chunk in enumerate(chunks)
            ]
            self.semantic_chunks.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
            self.transcript_embeddings.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
            return
        self.memory[video_id] = [{**chunk, "embedding": embeddings[i]} for i, chunk in enumerate(chunks)]

    def query(self, video_id: str, query: str, top_k: int | None = None) -> list[dict[str, Any]]:
        top_k = top_k or settings.retrieval_top_k
        query_embedding = embedding_service.embed(query)
        if self.is_configured:
            result = self.semantic_chunks.query(query_embeddings=[query_embedding], n_results=top_k, where={"video_id": video_id})
            docs = result.get("documents", [[]])[0]
            metas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0] if result.get("distances") else [0] * len(docs)
            return [{"text": docs[i], **metas[i], "score": float(distances[i])} for i in range(len(docs))]
        return sorted(
            [
                {k: v for k, v in chunk.items() if k != "embedding"} | {"score": _cosine(query_embedding, chunk["embedding"])}
                for chunk in self.memory.get(video_id, [])
            ],
            key=lambda row: row["score"],
            reverse=True,
        )[:top_k]

    def delete_video(self, video_id: str) -> None:
        if self.is_configured:
            for collection in [self.semantic_chunks, self.transcript_embeddings, self.quiz_embeddings]:
                try:
                    collection.delete(where={"video_id": video_id})
                except Exception:
                    pass
            return
        self.memory.pop(video_id, None)


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


chromadb_service = ChromaDBService()
