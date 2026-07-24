"""Economic indicators via FRED (Phase 11).

Requires a free FRED_API_KEY. Without it, endpoints return an `available: false`
payload instead of failing, so the dashboard renders a clear "connect FRED" state.

Docs: https://fred.stlouisfed.org/docs/api/fred/
"""

from __future__ import annotations

import logging
from threading import Lock

from app.core.config import settings

logger = logging.getLogger(__name__)

# label -> (FRED series id, units, frequency, yoy_default)
#   frequency  : how often FRED publishes (drives YoY math / chart density)
#   yoy_default: True when the raw level is not meaningful to chart (e.g. a CPI
#                index of ~310) and year-over-year % is the number people read.
SERIES: dict[str, tuple[str, str, str, bool]] = {
    "Inflation (CPI)":     ("CPIAUCSL",     "index", "monthly",   True),
    "Fed Funds Rate":      ("FEDFUNDS",     "%",     "monthly",   False),
    "Real GDP":            ("GDPC1",        "$B",    "quarterly", True),
    "Unemployment Rate":   ("UNRATE",       "%",     "monthly",   False),
    "10Y Treasury Yield":  ("DGS10",        "%",     "daily",     False),
    "30Y Mortgage Rate":   ("MORTGAGE30US", "%",     "weekly",    False),
    "Consumer Sentiment":  ("UMCSENT",      "index", "monthly",   False),
    "Retail Sales":        ("RSAFS",        "$M",    "monthly",   True),
}

_fred = None
_lock = Lock()


def is_available() -> bool:
    return bool(settings.FRED_API_KEY)


def _client():
    global _fred
    if _fred is not None:
        return _fred
    with _lock:
        if _fred is None:
            from fredapi import Fred

            _fred = Fred(api_key=settings.FRED_API_KEY)
        return _fred


def get_series(series_id: str, observation_start: str = "2015-01-01") -> list[dict]:
    if not is_available():
        return []
    try:
        s = _client().get_series(series_id, observation_start=observation_start)
    except Exception as exc:  # noqa: BLE001
        logger.warning("FRED series %s failed: %s", series_id, exc)
        return []
    return [
        {"date": idx.strftime("%Y-%m-%d"), "value": (None if v != v else float(v))}
        for idx, v in s.items()
    ]


def dashboard() -> dict:
    if not is_available():
        return {"available": False, "series": []}
    out = []
    for label, (sid, units, freq, yoy) in SERIES.items():
        points = get_series(sid)
        out.append(
            {
                "label": label,
                "series_id": sid,
                "units": units,
                "frequency": freq,
                "yoy_default": yoy,
                "points": points,
            }
        )
    return {"available": True, "series": out}


def _yoy(series_id: str, periods_per_year: int, start: str) -> float | None:
    """Year-over-year % change. `periods_per_year` = 12 for monthly, 4 for quarterly."""
    vals = [p["value"] for p in get_series(series_id, observation_start=start) if p["value"] is not None]
    if len(vals) <= periods_per_year:
        return None
    prior = vals[-(periods_per_year + 1)]
    return (vals[-1] / prior - 1) * 100 if prior else None


def latest_snapshot() -> dict[str, float]:
    """Interpreted macro figures for the macro agent.

    CPI (monthly) and GDP (quarterly) are reported as **year-over-year % change**
    — the meaningful number — not their raw index/dollar levels. Rates are
    already percentages.
    """
    snap: dict[str, float] = {}
    if not is_available():
        return snap

    cpi = _yoy("CPIAUCSL", 12, "2022-01-01")        # monthly index -> YoY %
    if cpi is not None:
        snap["Inflation (CPI YoY %)"] = round(cpi, 2)

    gdp = _yoy("GDPC1", 4, "2021-01-01")            # quarterly real GDP -> YoY %
    if gdp is not None:
        snap["Real GDP growth (YoY %)"] = round(gdp, 2)

    for label, sid in (("Fed Funds Rate (%)", "FEDFUNDS"), ("Unemployment (%)", "UNRATE")):
        vals = [p["value"] for p in get_series(sid, observation_start="2024-01-01") if p["value"] is not None]
        if vals:
            snap[label] = round(vals[-1], 2)

    return snap
