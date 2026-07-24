"""SEC EDGAR integration (Phase 7) — free, no API key.

Resolves a ticker to its CIK, lists recent filings, and extracts filing text so
it can be chunked + embedded into ChromaDB like any other RAG document. SEC
requires a descriptive User-Agent (configured via SEC_USER_AGENT).

Docs: https://www.sec.gov/os/accessing-edgar-data
"""

from __future__ import annotations

import logging
import re
from functools import lru_cache

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
_ARCHIVE = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{doc}"


def _headers() -> dict:
    return {"User-Agent": settings.SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"}


@lru_cache(maxsize=1)
def _ticker_map() -> dict[str, str]:
    """Map upper-case ticker -> zero-padded 10-digit CIK."""
    with httpx.Client(timeout=30, headers=_headers()) as client:
        data = client.get(_TICKERS_URL).raise_for_status().json()
    out: dict[str, str] = {}
    for row in data.values():
        out[row["ticker"].upper()] = str(row["cik_str"]).zfill(10)
    return out


def resolve_cik(ticker: str) -> str | None:
    return _ticker_map().get(ticker.upper())


def list_filings(ticker: str, form_types: tuple[str, ...] = ("10-K", "10-Q"), limit: int = 5) -> list[dict]:
    cik = resolve_cik(ticker)
    if not cik:
        return []
    with httpx.Client(timeout=30, headers=_headers()) as client:
        data = client.get(_SUBMISSIONS_URL.format(cik=cik)).raise_for_status().json()

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accns = recent.get("accessionNumber", [])
    docs = recent.get("primaryDocument", [])
    dates = recent.get("filingDate", [])

    out: list[dict] = []
    for form, accn, doc, date in zip(forms, accns, docs, dates):
        if form not in form_types:
            continue
        acc_nodash = accn.replace("-", "")
        url = _ARCHIVE.format(cik_int=int(cik), acc_nodash=acc_nodash, doc=doc)
        out.append({"form": form, "accession": accn, "date": date, "url": url, "document": doc})
        if len(out) >= limit:
            break
    return out


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def fetch_filing_text(url: str, max_chars: int = 400_000) -> str:
    """Download a filing's primary document and strip HTML to plain text."""
    with httpx.Client(timeout=60, headers=_headers(), follow_redirects=True) as client:
        html = client.get(url).raise_for_status().text
    text = _TAG_RE.sub(" ", html)
    text = _WS_RE.sub(" ", text)
    return text[:max_chars].strip()
