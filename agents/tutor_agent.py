from __future__ import annotations

from agents.base_agent import BaseAgent


class TutorChatAgent(BaseAgent):
    prompt_file = "tutor_prompt.txt"
    system_instruction = (
        "You are an AI tutor. Answer only using retrieved transcript context. "
        "If information is unavailable, say: I could not find this topic in the uploaded video."
    )

    def answer(self, retrieved_chunks: str, user_question: str) -> str:
        if not retrieved_chunks.strip():
            return "I could not find this topic in the uploaded video."
        return self.run_text(retrieved_chunks=retrieved_chunks, user_question=user_question)


TutorAgent = TutorChatAgent
