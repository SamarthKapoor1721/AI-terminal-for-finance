from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResearchReport(Base):
    """A generated AI research report (Phase 8 / Phase 12 memo)."""

    __tablename__ = "research_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    ticker: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)  # markdown body
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
