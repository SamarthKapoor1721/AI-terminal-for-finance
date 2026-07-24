from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120), nullable=False, default="My Portfolio")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="portfolios")  # noqa: F821
    holdings: Mapped[list["PortfolioHolding"]] = relationship(
        back_populates="portfolio", cascade="all, delete-orphan"
    )


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE")
    )
    ticker: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    portfolio: Mapped["Portfolio"] = relationship(back_populates="holdings")
