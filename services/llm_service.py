from __future__ import annotations

import logging

from services.gemini_service import gemini_service
from services.groq_service import groq_service
from services.openai_service import openai_service

logger = logging.getLogger(__name__)


class LLMRouter:
    def generate(self, provider: str, prompt: str, system_instruction: str | None = None, json_mode: bool = True, temperature: float = 0.2) -> str:
        provider = (provider or "gemini").lower()
        if provider == "local":
            return "{}" if json_mode else "I could not find this topic in the uploaded video."
        try:
            if provider == "openai":
                return openai_service.generate_text(prompt, system_instruction, json_mode, temperature)
            if provider == "groq":
                return groq_service.generate_text(prompt, system_instruction, json_mode, temperature)
            return gemini_service.generate_text(prompt, system_instruction, json_mode, temperature)
        except Exception as exc:
            logger.warning("LLM provider '%s' failed; using local fallback. Error: %s", provider, exc)
            return "{}" if json_mode else "I could not find this topic in the uploaded video."


llm_router = LLMRouter()
