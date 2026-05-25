from __future__ import annotations

from config import settings
from langsmith import traceable


class OpenAIService:
    def __init__(self):
        self.is_configured = bool(settings.openai_api_key)
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.is_configured:
            return None
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("The openai package is not installed. Run: pip install openai") from exc
        self._client = OpenAI(api_key=settings.openai_api_key)
        return self._client

    @traceable(run_type="llm", name="OpenAI Generation")
    def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        json_mode: bool = True,
        temperature: float = 0.2,
    ) -> str:
        if not self.is_configured:
            return "{}" if json_mode else "I could not find this topic in the uploaded video."
        client = self._get_client()
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=settings.openai_model_name,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"} if json_mode else None,
        )
        return response.choices[0].message.content or ("{}" if json_mode else "")


openai_service = OpenAIService()
