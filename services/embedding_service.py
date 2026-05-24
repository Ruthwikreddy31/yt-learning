from __future__ import annotations

import hashlib
import math
from functools import lru_cache

from config import settings


class EmbeddingService:
    def __init__(self):
        self.model = None
        self._attempted_load = False

    def _load_model(self) -> None:
        if self._attempted_load:
            return
        self._attempted_load = True
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(settings.embedding_model)
        except Exception:
            self.model = None

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        self._load_model()
        if self.model is not None:
            vectors = self.model.encode(texts, normalize_embeddings=True)
            return [vector.tolist() for vector in vectors]
        return [_hash_embedding(text) for text in texts]


@lru_cache(maxsize=4096)
def _hash_embedding(text: str, dims: int = 384) -> list[float]:
    vector = [0.0] * dims
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:4], "big") % dims
        vector[index] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


embedding_service = EmbeddingService()
