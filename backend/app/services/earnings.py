"""Earnings-call intelligence (Phase 6).

Takes a transcript (PDF/TXT), extracts growth/risk/guidance mentions, scores
management tone with FinBERT, and asks the LLM for an executive summary. Produces
an Executive Confidence Score and a Risk Score (0-100).
"""

from __future__ import annotations

import re

from app.services import llm
from app.services import sentiment as sentiment_service
from app.services.rag import extract_text

_GROWTH = re.compile(r"\b(growth|increase|expand|record|strong|accelerat|momentum|outperform)\w*", re.I)
_RISK = re.compile(r"\b(risk|decline|decrease|headwind|challeng|uncertain|weak|pressure|litigation|lawsuit)\w*", re.I)
_GUIDANCE = re.compile(r"\b(guidance|outlook|forecast|expect|anticipate|raise|lower|reaffirm)\w*", re.I)

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _sentences_with(pattern: re.Pattern, text: str, limit: int = 8) -> list[str]:
    out = []
    for sent in _SENT_SPLIT.split(text):
        if pattern.search(sent):
            cleaned = sent.strip()
            if 20 <= len(cleaned) <= 400:
                out.append(cleaned)
        if len(out) >= limit:
            break
    return out


def analyze_transcript(filename: str, data: bytes) -> dict:
    text = extract_text(filename, data)
    if not text.strip():
        raise ValueError("No extractable text in transcript")

    growth = _sentences_with(_GROWTH, text)
    risks = _sentences_with(_RISK, text)
    guidance = _sentences_with(_GUIDANCE, text)

    # Management confidence: FinBERT over the most salient (growth+guidance) lines.
    sample = " ".join((growth + guidance)[:10]) or text[:1500]
    tone = sentiment_service.analyze(sample)
    # Map signed score [-1,1] -> 0..100
    confidence_score = round((tone.score + 1) / 2 * 100, 1)

    # Risk score: density of risk vs growth mentions.
    g, r = len(growth), len(risks)
    risk_score = round(min(100, (r / max(1, g + r)) * 100 + r * 2), 1)

    summary = llm.generate(
        f"Earnings call excerpts:\nGROWTH: {growth[:5]}\nRISKS: {risks[:5]}\n"
        f"GUIDANCE: {guidance[:5]}\n\nWrite a 4-5 sentence executive summary of this "
        f"earnings call covering tone, growth, risks and guidance.",
        system="You are an equity analyst summarizing an earnings call factually.",
    )

    return {
        "executive_confidence_score": confidence_score,
        "risk_score": risk_score,
        "management_tone": tone.sentiment,
        "growth_mentions": growth,
        "risk_mentions": risks,
        "guidance_mentions": guidance,
        "summary": summary,
    }
