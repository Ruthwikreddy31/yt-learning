from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
        os.environ.setdefault(key.upper(), value)


def _env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name) or os.getenv(name.upper()) or os.getenv(name.lower()) or default


def _env_int(name: str, default: int) -> int:
    value = _env(name)
    try:
        return int(value) if value not in (None, "") else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    groq_api_key: str | None
    gemini_api_key: str | None
    google_api_key: str | None
    openai_api_key: str | None
    mongodb_uri: str | None
    mongodb_database: str
    chroma_host: str | None
    chroma_port: int | None
    chroma_persist_dir: str
    model_name: str
    groq_model_name: str
    openai_model_name: str
    embedding_model: str
    max_transcript_chars: int
    chunk_size_words: int
    chunk_overlap_words: int
    retrieval_top_k: int
    uploads_dir: str
    project_root: Path

    @property
    def upload_path(self) -> Path:
        path = self.project_root / self.uploads_dir
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    project_root = Path(__file__).resolve().parent
    _load_dotenv(project_root / ".env")
    return Settings(
        app_name=_env("APP_NAME", "AI YouTube Learning Assistant") or "AI YouTube Learning Assistant",
        environment=_env("ENVIRONMENT", "development") or "development",
        groq_api_key=_env("GROQ_API_KEY"),
        gemini_api_key=_env("GEMINI_API_KEY"),
        google_api_key=_env("GOOGLE_API_KEY"),
        openai_api_key=_env("OPENAI_API_KEY") or _env("openai_api_key"),
        mongodb_uri=_env("MONGODB_URI"),
        mongodb_database=_env("MONGODB_DATABASE", "ai_youtube_learning") or "ai_youtube_learning",
        chroma_host=_env("CHROMA_HOST"),
        chroma_port=_env_int("CHROMA_PORT", 0) or None,
        chroma_persist_dir=_env("CHROMA_PERSIST_DIR", "chromadb_data") or "chromadb_data",
        model_name=_env("MODEL_NAME", "gemini-1.5-flash") or "gemini-1.5-flash",
        groq_model_name=_env("GROQ_MODEL_NAME", "llama-3.1-70b-versatile") or "llama-3.1-70b-versatile",
        openai_model_name=_env("OPENAI_MODEL_NAME", "gpt-4o-mini") or "gpt-4o-mini",
        embedding_model=_env("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2") or "sentence-transformers/all-MiniLM-L6-v2",
        max_transcript_chars=_env_int("MAX_TRANSCRIPT_CHARS", 60000),
        chunk_size_words=_env_int("CHUNK_SIZE_WORDS", 220),
        chunk_overlap_words=_env_int("CHUNK_OVERLAP_WORDS", 45),
        retrieval_top_k=_env_int("RETRIEVAL_TOP_K", 5),
        uploads_dir=_env("UPLOADS_DIR", "uploads") or "uploads",
        project_root=project_root,
    )


settings = get_settings()
