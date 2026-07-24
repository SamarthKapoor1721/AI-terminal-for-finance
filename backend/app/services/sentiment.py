"""FinBERT sentiment engine (Phase 5).

The model (~440MB) is loaded lazily on first use and cached for the process
lifetime. If torch/transformers aren't available the service degrades to a
neutral result so the rest of the API keeps working.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from threading import Lock

from app.core.config import settings

logger = logging.getLogger(__name__)

_LABELS = ["positive", "negative", "neutral"]
_pipeline = None
_lock = Lock()


@dataclass
class SentimentResult:
    sentiment: str
    confidence: float
    # signed score in [-1, 1]: +positive, -negative, 0 neutral
    score: float


def _load_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    with _lock:
        if _pipeline is not None:
            return _pipeline
        from transformers import pipeline  # heavy import, deferred

        logger.info("Loading FinBERT model: %s", settings.FINBERT_MODEL)
        _pipeline = pipeline(
            "text-classification",
            model=settings.FINBERT_MODEL,
            top_k=None,  # return all class scores
        )
        return _pipeline


def analyze(text: str) -> SentimentResult:
    text = (text or "").strip()
    if not text:
        return SentimentResult("neutral", 0.0, 0.0)

    try:
        clf = _load_pipeline()
    except Exception as exc:  # model missing / no torch
        logger.warning("FinBERT unavailable, returning neutral: %s", exc)
        return SentimentResult("neutral", 0.0, 0.0)

    # FinBERT has a 512-token limit; truncate generously by characters.
    scores = clf(text[:2000], truncation=True)[0]
    by_label = {s["label"].lower(): s["score"] for s in scores}
    label = max(by_label, key=by_label.get)
    confidence = by_label[label]
    signed = by_label.get("positive", 0.0) - by_label.get("negative", 0.0)

    return SentimentResult(sentiment=label, confidence=confidence, score=signed)
