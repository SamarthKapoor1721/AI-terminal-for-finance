from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NewsArticle(Base):
    __tablename__ = "news_articles"
    __table_args__ = (UniqueConstraint("url", name="uq_news_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    company_ticker: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(String(120))
    url: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # FinBERT output (Phase 4/5)
    sentiment: Mapped[str | None] = mapped_column(String(16))  # positive/negative/neutral
    sentiment_score: Mapped[float | None] = mapped_column(Float)  # signed: +pos / -neg
    confidence: Mapped[float | None] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
