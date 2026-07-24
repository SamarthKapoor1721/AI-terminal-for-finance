from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    """An ingested document (annual report, transcript, SEC filing) for RAG."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ticker: Mapped[str | None] = mapped_column(String(16), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(32), default="other")  # transcript/filing/report
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/indexed/failed
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE")
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # The id used in ChromaDB so we can map vector hits back to rows.
    vector_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    document: Mapped["Document"] = relationship(back_populates="chunks")
