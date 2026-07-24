"""RAG ingestion + retrieval-augmented Q&A (Phase 7).

Pipeline: upload -> extract text -> chunk -> embed -> store in ChromaDB.
Queries embed the question, retrieve top-k chunks, and ask Ollama to answer
grounded strictly in those chunks.
"""

from __future__ import annotations

import io
import uuid

from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.services import llm, vectorstore


def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    # default: treat as UTF-8 text
    return data.decode("utf-8", errors="ignore")


def chunk_text(text: str, size: int = 1000, overlap: int = 150) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def ingest(
    db: Session,
    *,
    user_id: int,
    title: str,
    filename: str,
    data: bytes,
    ticker: str | None = None,
    doc_type: str = "other",
) -> Document:
    doc = Document(
        user_id=user_id,
        ticker=ticker.upper() if ticker else None,
        title=title,
        doc_type=doc_type,
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        text = extract_text(filename, data)
        chunks = chunk_text(text)

        ids, texts, metadatas = [], [], []
        for i, chunk in enumerate(chunks):
            vector_id = f"doc{doc.id}-{uuid.uuid4().hex[:8]}"
            db.add(
                DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk,
                    vector_id=vector_id,
                )
            )
            ids.append(vector_id)
            texts.append(chunk)
            metadatas.append(
                {
                    "document_id": doc.id,
                    "chunk_index": i,
                    "ticker": doc.ticker or "",
                    "title": title,
                }
            )

        vectorstore.add_chunks(ids, texts, metadatas)
        doc.chunk_count = len(chunks)
        doc.status = "indexed"
    except Exception:
        doc.status = "failed"
        db.commit()
        raise

    db.commit()
    db.refresh(doc)
    return doc


_SYSTEM = (
    "You are a financial research assistant. Answer ONLY using the provided "
    "context excerpts from the user's documents. If the answer is not in the "
    "context, say you don't have enough information. Cite excerpt numbers."
)


def answer(question: str, ticker: str | None = None, k: int = 5) -> dict:
    hits = vectorstore.query(question, n_results=k, ticker=ticker)
    if not hits:
        return {
            "answer": "No relevant documents found. Upload documents first.",
            "sources": [],
        }

    context = "\n\n".join(
        f"[Excerpt {i + 1}] {h['text']}" for i, h in enumerate(hits)
    )
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    response = llm.generate(prompt, system=_SYSTEM)

    return {
        "answer": response,
        "sources": [
            {
                "excerpt": i + 1,
                "document_id": h["metadata"].get("document_id"),
                "title": h["metadata"].get("title"),
                "snippet": h["text"][:240],
            }
            for i, h in enumerate(hits)
        ],
    }
