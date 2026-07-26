import socket
from collections.abc import Generator
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings


def _connect_args() -> dict:
    """Pin psycopg to the host's IPv4 address.

    Some deployment platforms (e.g. Railway) advertise IPv6 egress but can't
    actually route it, while DNS for managed Postgres hosts (e.g. Neon's
    pooler) can return an IPv6 record. Left alone, psycopg picks that
    unreachable address and every query fails with "Network is unreachable".
    Resolving to IPv4 ourselves and passing it via `hostaddr` sidesteps the
    platform's routing entirely.
    """
    host = urlparse(settings.sqlalchemy_url.replace("postgresql+psycopg", "postgresql")).hostname
    if not host:
        return {}
    try:
        ipv4 = socket.getaddrinfo(host, None, socket.AF_INET)[0][4][0]
    except socket.gaierror:
        return {}
    return {"hostaddr": ipv4}


engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,
    future=True,
    connect_args=_connect_args(),
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
