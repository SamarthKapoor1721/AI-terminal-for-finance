"""Celery app for background jobs (news ingestion, document indexing).

Tasks are intentionally thin wrappers around the services so the same logic
runs synchronously from the API or async from the worker.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "finance",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.update(task_track_started=True, result_expires=3600)


@celery_app.task(name="news.refresh")
def refresh_news_task(ticker: str) -> int:
    from app.core.database import SessionLocal
    from app.services import news as news_service

    db = SessionLocal()
    try:
        articles = news_service.fetch_and_store(db, ticker)
        return len(articles)
    finally:
        db.close()
