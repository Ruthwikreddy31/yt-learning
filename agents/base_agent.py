from __future__ import annotations

from pathlib import Path
from typing import Any

from services.llm_service import llm_router
from utils.text import parse_json_object


class BaseAgent:
    prompt_file: str = ""
    system_instruction: str = "Return valid JSON only."

    def __init__(self, provider: str = "gemini"):
        self.provider = provider

    def load_prompt(self, **kwargs: Any) -> str:
        template = (Path(__file__).resolve().parents[1] / "prompts" / self.prompt_file).read_text(encoding="utf-8")
        return template.format(**kwargs)

    def run_json(self, **kwargs: Any) -> dict[str, Any]:
        prompt = self.load_prompt(**kwargs)
        try:
            raw = llm_router.generate(self.provider, prompt, self.system_instruction, json_mode=True)
        except Exception:
            return self.fallback(**kwargs)
        parsed = parse_json_object(raw, fallback={})
        if not parsed or parsed.get("error"):
            return self.fallback(**kwargs)
        return parsed

    def run_text(self, **kwargs: Any) -> str:
        prompt = self.load_prompt(**kwargs)
        try:
            return llm_router.generate(self.provider, prompt, self.system_instruction, json_mode=False)
        except Exception:
            return "I could not find this topic in the uploaded video."

    def fallback(self, **_: Any) -> dict[str, Any]:
        return {}
