"""Local embeddings via sentence-transformers (BAAI/bge-large-en-v1.5).

Wrapped to satisfy ChromaDB's EmbeddingFunction protocol. Lazy-loaded so the
API boots without the model downloaded.
"""

from __future__ import annotations

import logging
from threading import Lock

from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None
_lock = Lock()

# bge models recommend this prefix for retrieval queries.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def _load():
    global _model
    if _model is not None:
        return _model
    with _lock:
        if _model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
            _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return _model


def embed_documents(texts: list[str]) -> list[list[float]]:
    model = _load()
    return model.encode(texts, normalize_embeddings=True).tolist()


def embed_query(text: str) -> list[float]:
    model = _load()
    return model.encode([QUERY_PREFIX + text], normalize_embeddings=True)[0].tolist()


class BGEEmbeddingFunction:
    """ChromaDB-compatible embedding function."""

    def __call__(self, input: list[str]) -> list[list[float]]:  # noqa: A002 (chroma API)
        return embed_documents(input)

    # ChromaDB >=0.5 calls .name() for telemetry
    @staticmethod
    def name() -> str:
        return "bge-large-en-v1.5"
