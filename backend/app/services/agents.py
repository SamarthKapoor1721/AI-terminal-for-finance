"""Multi-agent research system (Phase 12).

Five specialist agents gather evidence from the platform's own services and the
local LLM, then a coordinator synthesizes a final investment memo. This is a
lightweight orchestrator (no external framework) so it runs fully locally; it can
be swapped for LangGraph later without changing the API.

Workflow:  query -> agents run independently -> coordinator combines -> memo
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services import economics, financials as financials_service
from app.services import llm, market_data
from app.services import news as news_service
from app.services import portfolio as portfolio_service

logger = logging.getLogger(__name__)


@dataclass
class AgentFinding:
    agent: str
    summary: str


# Appended to every agent's system prompt to curb hallucination while still
# allowing useful qualitative context.
_GUARDRAIL = (
    " For SPECIFIC FINANCIAL FIGURES (prices, ratios, margins, growth rates), use "
    "ONLY the numbers in the provided data — never invent them. For qualitative or "
    "industry context not in the data (e.g. market share, competitors, products), "
    "you MAY use well-known general knowledge, but prefix any such statement with "
    "'(general knowledge)'. If you have NO reliable data or knowledge about this "
    "specific stock or company, do NOT make anything up — clearly state that you "
    "have no information about it. Be concise."
)


def _ask(role_system: str, prompt: str) -> str:
    out = llm.generate(prompt, system=role_system + _GUARDRAIL, temperature=0.2)
    return _strip_think(out)


def _strip_think(text: str) -> str:
    """Remove <think>…</think> reasoning blocks some models (e.g. Qwen 3) emit."""
    import re

    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _n(v, suffix="", pct=False) -> str:
    if v is None:
        return "unavailable"
    if pct:
        return f"{v:.1f}%"
    if abs(v) >= 1e9:
        return f"{v/1e9:.1f}B{suffix}"
    if abs(v) >= 1e6:
        return f"{v/1e6:.1f}M{suffix}"
    return f"{v:,.2f}{suffix}"


def _price_history_summary(ticker: str, period: str = "6mo") -> str:
    """Key stats from recent price history — the 'past' the agents analyze."""
    try:
        hist = market_data.get_history(ticker, period=period)
    except Exception:
        return ""
    pts = [p for p in hist.points if p.close is not None]
    if len(pts) < 5:
        return ""

    start, end = pts[0], pts[-1]
    low = min(pts, key=lambda p: p.close)
    high = max(pts, key=lambda p: p.close)
    change_pct = (end.close - start.close) / start.close * 100 if start.close else 0

    return (
        f"Price history ({period}): "
        f"start {start.close:.2f} on {start.date}, "
        f"latest {end.close:.2f} on {end.date} ({change_pct:+.1f}% over period). "
        f"Period LOW {low.close:.2f} on {low.date} (cheapest entry point). "
        f"Period HIGH {high.close:.2f} on {high.date}. "
        f"Latest is {(end.close - low.close) / low.close * 100:+.1f}% above the low."
    )


def technical_analyst(ticker: str) -> AgentFinding:
    summary = _price_history_summary(ticker)
    if not summary:
        return AgentFinding("Technical Analyst", "Price history unavailable.")
    out = _ask(
        "You are a technical analyst. Using the price history, describe the trend, "
        "identify when the best (lowest) buying opportunity was, and where the price "
        "stands now relative to its range — in 3-4 sentences.",
        f"{summary}\n\nGive your technical assessment.",
    )
    return AgentFinding("Technical Analyst", out)


def financial_analyst(ticker: str) -> AgentFinding:
    try:
        q = market_data.get_quote(ticker)
        r = financials_service.get_financials(ticker).ratios
        cur = q.currency or "USD"
        data = (
            f"{q.name} ({q.ticker}), prices in {cur}:\n"
            f"- Price: {_n(q.price)}\n"
            f"- Market cap: {_n(q.market_cap)}\n"
            f"- P/E ratio: {_n(q.pe_ratio)}\n"
            f"- EPS: {_n(q.eps)}\n"
            f"- Revenue growth YoY: {_n(r.revenue_growth, pct=True)}\n"
            f"- Gross margin: {_n(r.gross_margin, pct=True)}\n"
            f"- Net margin: {_n(r.net_margin, pct=True)}\n"
            f"- Debt-to-equity: {_n(r.debt_to_equity)}\n"
            f"- Free cash flow: {_n(r.free_cash_flow)}"
        )
    except Exception:
        data = "Financial data unavailable."
    out = _ask(
        "You are a financial analyst. Assess valuation, growth and balance-sheet health in 3-4 sentences.",
        f"Data:\n{data}\n\nGive your financial assessment.",
    )
    return AgentFinding("Financial Analyst", out)


def news_analyst(db: Session, ticker: str) -> AgentFinding:
    news_service.fetch_and_store(db, ticker)
    arts = news_service.list_articles(db, ticker, limit=15)
    if arts:
        pos = sum(1 for a in arts if a.sentiment == "positive")
        neg = sum(1 for a in arts if a.sentiment == "negative")
        heads = "; ".join(a.headline for a in arts[:6])
        data = f"{pos} positive / {neg} negative of {len(arts)}. Headlines: {heads}"
    else:
        data = "No recent news available."
    out = _ask(
        "You are a news analyst. Summarize the sentiment narrative and notable developments in 3-4 sentences.",
        f"News data:\n{data}\n\nGive your news assessment.",
    )
    return AgentFinding("News Analyst", out)


def risk_analyst(ticker: str) -> AgentFinding:
    try:
        r = financials_service.get_financials(ticker).ratios
        data = (
            f"- Debt-to-equity: {_n(r.debt_to_equity)}\n"
            f"- Net margin: {_n(r.net_margin, pct=True)}\n"
            f"- Free cash flow: {_n(r.free_cash_flow)}"
        )
    except Exception:
        data = "Risk metrics unavailable."
    out = _ask(
        "You are a risk analyst. Identify the top financial and market risks in 3-4 sentences.",
        f"Data:\n{data}\n\nGive your risk assessment.",
    )
    return AgentFinding("Risk Analyst", out)


def macro_analyst() -> AgentFinding:
    snapshot = economics.latest_snapshot()
    if snapshot:
        data = "\n".join(f"- {k}: {v}" for k, v in snapshot.items())
    else:
        data = "Macro data unavailable (FRED not configured)."
    out = _ask(
        "You are a macro analyst. The values below are already year-over-year "
        "percentages or rates. Explain how this macro backdrop affects equities "
        "in 3-4 sentences.",
        f"US economic indicators:\n{data}\n\nGive your macro assessment.",
    )
    return AgentFinding("Macro Analyst", out)


def portfolio_analyst(ticker: str) -> AgentFinding:
    out = _ask(
        "You are a portfolio analyst. Comment on position sizing, diversification and how this name "
        "fits a balanced portfolio in 3-4 sentences.",
        f"Consider adding {ticker.upper()} to a diversified equity portfolio. Give your assessment.",
    )
    return AgentFinding("Portfolio Analyst", out)


def _retrieve_context(db: Session, query: str, ticker: str) -> str:
    """Pull snippets from documents the user uploaded for this ticker.

    Skips entirely (and avoids loading the embedding model) when no documents
    exist, so memos stay fast for users who haven't uploaded anything.
    """
    from sqlalchemy import select

    from app.models import Document

    has_docs = db.scalar(
        select(Document.id).where(Document.ticker == ticker).limit(1)
    )
    if not has_docs:
        return ""

    try:
        from app.services import vectorstore

        hits = vectorstore.query(query, n_results=3, ticker=ticker)
    except Exception:
        return ""
    return "\n".join(f"- {h['text'][:300]}" for h in hits) if hits else ""


def coordinator(
    ticker: str,
    query: str,
    findings: list[AgentFinding],
    doc_context: str,
    price_summary: str = "",
) -> str:
    joined = "\n\n".join(f"### {f.agent}\n{f.summary}" for f in findings)
    docs = f"\nRelevant excerpts from uploaded documents:\n{doc_context}\n" if doc_context else ""
    price = f"\nPrice history facts:\n{price_summary}\n" if price_summary else ""
    prompt = (
        f"User's question: \"{query}\"\n\n"
        f"Analyst findings:\n{joined}\n{docs}{price}\n"
        f"Write the memo on {ticker.upper()} in this exact structure:\n"
        f"**Answer to your question:** Directly and specifically answer the user's "
        f"question first. If the answer isn't in the analyst data or documents, use "
        f"(general knowledge) and say it isn't from live data — do NOT just say "
        f"'unavailable'.\n\n"
        f"**Recommendation:** Buy / Hold / Sell with conviction.\n\n"
        f"**Synthesis:** one paragraph tying the findings together.\n\n"
        f"**Key takeaways:** 3 bullets."
    )
    return _ask(
        "You are the head of research. Answer the user's question first, then "
        "synthesize the analysts into a clear, decisive investment memo.",
        prompt,
    )


_OFF_TOPIC_MSG = (
    "**Please ask a relevant question.**\n\n"
    "This is a financial research assistant. Ask about the company, its stock, "
    "financials, news, risks, valuation, the economy, or whether to invest — "
    "for example:\n\n"
    "- *Is this stock overvalued?*\n"
    "- *What are the main risks?*\n"
    "- *How is revenue growing?*\n"
    "- *Should I buy, hold, or sell?*"
)


def is_relevant(query: str, ticker: str) -> bool:
    """Cheap single-call gate: is the question about finance/this company?

    Defaults to True if the classifier itself is unavailable, so legitimate
    questions are never blocked by an LLM outage.
    """
    query = (query or "").strip()
    if not query:
        return True
    verdict = llm.generate(
        f'Question about the stock {ticker}: "{query}"\n\n'
        "Is this question related to finance, investing, this company, stocks, "
        "markets, business, or the economy? Answer with ONLY the word YES or NO.",
        system="You are a strict topic classifier. Reply with exactly YES or NO.",
        temperature=0.0,
    )
    verdict = _strip_think(verdict).upper()
    if verdict.startswith("[LLM"):  # backend unavailable -> don't block
        return True
    return "NO" not in verdict[:6]


def _no_data_msg(ticker: str) -> str:
    return (
        f"**No data available for '{ticker}'.**\n\n"
        "This ticker could not be found, so there is nothing to analyze. "
        "Please check the symbol and try a valid stock (e.g. AAPL, MSFT, RELIANCE)."
    )


def run(db: Session, *, ticker: str, query: str) -> dict:
    ticker = ticker.upper().strip()

    # Reject off-topic questions before running the (expensive) agent pipeline.
    if not is_relevant(query, ticker):
        return {"ticker": ticker, "query": query, "findings": [], "memo": _OFF_TOPIC_MSG, "off_topic": True}

    # Reject unknown/invalid tickers — don't let the LLM speculate about a stock
    # that doesn't exist.
    try:
        market_data.get_quote(ticker)
    except Exception:
        return {"ticker": ticker, "query": query, "findings": [], "memo": _no_data_msg(ticker), "off_topic": True}

    findings = [
        financial_analyst(ticker),
        technical_analyst(ticker),
        news_analyst(db, ticker),
        risk_analyst(ticker),
        macro_analyst(),
        portfolio_analyst(ticker),
    ]
    doc_context = _retrieve_context(db, query, ticker)
    price_summary = _price_history_summary(ticker)
    memo = coordinator(ticker, query, findings, doc_context, price_summary)
    return {
        "ticker": ticker,
        "query": query,
        "findings": [{"agent": f.agent, "summary": f.summary} for f in findings],
        "memo": memo,
    }
