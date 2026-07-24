import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finance")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup. For production, run Alembic migrations instead.
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as exc:  # don't crash if DB is briefly unavailable
        logger.error("DB init failed: %s", exc)
    yield


app = FastAPI(
    title="AI Bloomberg Terminal API",
    description="Finance intelligence platform — market data, financials, news "
    "sentiment, RAG research, portfolios, and screening.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    from app.services import llm

    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "llm_backend": llm.active_backend(),
        "llm_available": llm.is_available(),
    }


@app.get("/", tags=["meta"])
def root() -> dict:
    return {"name": "AI Bloomberg Terminal API", "docs": "/docs"}
