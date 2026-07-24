"""ChromaDB vector store wrapper (Phase 7 RAG).

Persists embeddings to disk at settings.CHROMA_PATH. One collection holds all
document chunks; each chunk carries metadata (document_id, ticker) so we can
filter retrieval by company.
"""

from __future__ import annotations

import logging
from threading import Lock

from app.core.config import settings
from app.services.embeddings import BGEEmbeddingFunction, embed_query

logger = logging.getLogger(__name__)

_COLLECTION = "documents"
_client = None
_lock = Lock()


def _get_collection():
    global _client
    with _lock:
        if _client is None:
            import chromadb

            _client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        return _client.get_or_create_collection(
            name=_COLLECTION,
            embedding_function=BGEEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )


def add_chunks(
    ids: list[str],
    texts: list[str],
    metadatas: list[dict],
) -> None:
    if not ids:
        return
    _get_collection().add(ids=ids, documents=texts, metadatas=metadatas)


def query(
    text: str,
    n_results: int = 5,
    ticker: str | None = None,
) -> list[dict]:
    where = {"ticker": ticker.upper()} if ticker else None
    res = _get_collection().query(
        query_embeddings=[embed_query(text)],
        n_results=n_results,
        where=where,
    )
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    return [
        {"text": d, "metadata": m, "distance": dist}
        for d, m, dist in zip(docs, metas, dists)
    ]


def delete_document(document_id: int) -> None:
    _get_collection().delete(where={"document_id": document_id})
