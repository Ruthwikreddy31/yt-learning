from __future__ import annotations

from agents.tutor_agent import TutorChatAgent
from config import settings
from database.mongodb import mongo
from services.chromadb_service import chromadb_service
from utils.text import format_seconds


class RAGService:
    def retrieve(self, video_id: str, question: str, top_k: int | None = None) -> list[dict]:
        return chromadb_service.query(video_id, question, top_k or settings.retrieval_top_k)

    def answer(self, video_id: str, question: str, provider: str = "gemini", user_id: str | None = None) -> dict:
        chunks = self.retrieve(video_id, question)
        if not chunks:
            answer = "I could not find this topic in the uploaded video."
        else:
            context = "\n\n".join(
                f"[{format_seconds(chunk.get('start'))}] {chunk.get('text', '')}" for chunk in chunks
            )
            answer = TutorChatAgent(provider=provider).answer(context, question)
        if user_id:
            mongo.insert("chat_history", {"user_id": user_id, "video_id": video_id, "role": "user", "content": question})
            mongo.insert("chat_history", {"user_id": user_id, "video_id": video_id, "role": "assistant", "content": answer, "citations": chunks})
        return {"answer": answer, "citations": chunks}


rag_service = RAGService()
