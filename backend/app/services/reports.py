"""AI company research reports (Phase 8).

Gathers structured context (quote, ratios, news sentiment) and prompts the local
LLM to write each report section, then renders to PDF with reportlab. Degrades
gracefully if the LLM is unavailable (sections show a notice instead of crashing).
"""

from __future__ import annotations

import io
import logging

from sqlalchemy.orm import Session

from app.models import NewsArticle, ResearchReport
from app.services import financials as financials_service
from app.services import llm, market_data
from app.services import news as news_service

logger = logging.getLogger(__name__)

SECTIONS = [
    ("Business Overview", "Summarize what the company does, its segments and competitive position."),
    ("Revenue Analysis", "Analyze revenue scale, growth trajectory and drivers."),
    ("Profitability Analysis", "Assess margins (gross, net), efficiency and earnings quality."),
    ("News Sentiment", "Interpret recent news sentiment and what it signals."),
    ("Risks", "Identify the key risks to the investment thesis."),
    ("Opportunities", "Identify the main growth opportunities and catalysts."),
    ("Bull Case", "Make the strongest concise bull argument."),
    ("Bear Case", "Make the strongest concise bear argument."),
]

_SYSTEM = (
    "You are an equity research analyst. Write concise, factual, professional prose "
    "grounded ONLY in the provided data. Do not invent numbers. If you have no "
    "reliable data or knowledge about this specific stock or company, clearly state "
    "that rather than making anything up. 2-4 sentences per section."
)


def _build_context(db: Session, ticker: str) -> str:
    parts: list[str] = []
    try:
        q = market_data.get_quote(ticker)
        parts.append(
            f"Quote: {q.name} ({q.ticker}) price={q.price} {q.currency}, "
            f"market_cap={q.market_cap}, P/E={q.pe_ratio}, EPS={q.eps}, "
            f"52w_high={q.week52_high}, 52w_low={q.week52_low}, sector={q.sector}."
        )
    except Exception:
        parts.append("Quote: unavailable.")

    try:
        r = financials_service.get_financials(ticker).ratios
        parts.append(
            f"Ratios: revenue_growth={r.revenue_growth}, gross_margin={r.gross_margin}, "
            f"net_margin={r.net_margin}, debt_to_equity={r.debt_to_equity}, "
            f"free_cash_flow={r.free_cash_flow}."
        )
    except Exception:
        parts.append("Ratios: unavailable.")

    news_service.fetch_and_store(db, ticker)
    arts = news_service.list_articles(db, ticker, limit=15)
    if arts:
        pos = sum(1 for a in arts if a.sentiment == "positive")
        neg = sum(1 for a in arts if a.sentiment == "negative")
        heads = "; ".join(a.headline for a in arts[:6])
        parts.append(f"News: {pos} positive / {neg} negative of {len(arts)}. Headlines: {heads}")

    return "\n".join(parts)


def generate_report(db: Session, *, user_id: int, ticker: str) -> ResearchReport:
    ticker = ticker.upper().strip()
    context = _build_context(db, ticker)

    body_lines = [f"# {ticker} — AI Research Report", ""]
    for title, instruction in SECTIONS:
        prompt = (
            f"Company data:\n{context}\n\n"
            f"Write the '{title}' section. {instruction}"
        )
        section_text = llm.generate(prompt, system=_SYSTEM)
        body_lines.append(f"## {title}")
        body_lines.append(section_text)
        body_lines.append("")

    content_md = "\n".join(body_lines)
    report = ResearchReport(
        user_id=user_id,
        ticker=ticker,
        title=f"{ticker} Research Report",
        content_md=content_md,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def render_pdf(report: ResearchReport) -> bytes:
    """Render a stored markdown report to a simple, clean PDF."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=0.8 * inch, bottomMargin=0.8 * inch,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1b", parent=styles["Title"], fontSize=20)
    h2 = ParagraphStyle("H2b", parent=styles["Heading2"], textColor="#b8860b")
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15)

    flow = []
    for raw in report.content_md.splitlines():
        line = raw.strip()
        if not line:
            flow.append(Spacer(1, 6))
        elif line.startswith("## "):
            flow.append(Spacer(1, 8))
            flow.append(Paragraph(line[3:], h2))
        elif line.startswith("# "):
            flow.append(Paragraph(line[2:], h1))
            flow.append(Spacer(1, 12))
        else:
            flow.append(Paragraph(line, body))

    doc.build(flow)
    return buf.getvalue()
