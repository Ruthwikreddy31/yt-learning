from __future__ import annotations

from config import settings
from langsmith import traceable


class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key or settings.google_api_key
        self.is_configured = bool(self.api_key)
        self.sdk = None
        self._client = None
        self._types = None
        self._genai = None

    def _configure(self) -> None:
        if self.sdk or not self.is_configured:
            return
        try:
            from google import genai
            from google.genai import types

            self._client = genai.Client(api_key=self.api_key)
            self._types = types
            self.sdk = "google-genai"
        except Exception:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._genai = genai
                self.sdk = "google-generativeai"
            except ImportError as exc:
                raise RuntimeError("Google AI SDK is not installed. Run: pip install google-genai google-generativeai") from exc

    @traceable(run_type="llm", name="Gemini Generation")
    def generate_text(self, prompt: str, system_instruction: str | None = None, json_mode: bool = True, temperature: float = 0.2) -> str:
        if not self.is_configured:
            return "{}" if json_mode else "I could not find this topic in the uploaded video."
        self._configure()
        if self.sdk == "google-genai":
            config = self._types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json" if json_mode else None,
                system_instruction=system_instruction,
            )
            response = self._client.models.generate_content(model=settings.model_name, contents=prompt, config=config)
            return response.text or ("{}" if json_mode else "")
        generation_config = {"temperature": temperature, "max_output_tokens": 8192}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"
        model = self._genai.GenerativeModel(
            model_name=settings.model_name,
            system_instruction=system_instruction,
            generation_config=generation_config,
        )
        response = model.generate_content(prompt)
        return response.text or ("{}" if json_mode else "")


gemini_service = GeminiService()
