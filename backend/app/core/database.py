from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings

engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables. For real migrations use Alembic; this is for first boot."""
    # Import models so they register on Base.metadata before create_all.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
