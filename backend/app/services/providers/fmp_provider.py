"""Financial Modeling Prep provider (free tier, 250 req/day) — clean statements.

Docs: https://site.financialmodelingprep.com/developer/docs
"""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings
from app.schemas.financials import (
    FinancialRatios,
    FinancialsResponse,
    FinancialStatement,
    StatementLine,
)
from app.services.providers.base import DataProvider

logger = logging.getLogger(__name__)

_BASE = "https://financialmodelingprep.com/api/v3"


class FMPProvider(DataProvider):
    name = "fmp"

    @property
    def available(self) -> bool:
        return bool(settings.FMP_API_KEY)

    def _get(self, path: str, params: dict | None = None) -> list | None:
        params = {**(params or {}), "apikey": settings.FMP_API_KEY}
        try:
            with httpx.Client(timeout=20) as client:
                r = client.get(f"{_BASE}{path}", params=params)
                r.raise_for_status()
                data = r.json()
                return data if isinstance(data, list) else None
        except Exception as exc:
            logger.warning("FMP %s failed: %s", path, exc)
            return None

    @staticmethod
    def _statement(name: str, rows: list[dict], fields: dict[str, str]) -> FinancialStatement:
        periods = [r.get("date", "") for r in rows]
        lines = [
            StatementLine(
                label=label,
                values={r.get("date", ""): r.get(key) for r in rows},
            )
            for key, label in fields.items()
        ]
        return FinancialStatement(name=name, periods=periods, lines=lines)

    def get_financials(self, ticker: str) -> FinancialsResponse | None:
        ticker = ticker.upper()
        income = self._get(f"/income-statement/{ticker}", {"limit": 5})
        balance = self._get(f"/balance-sheet-statement/{ticker}", {"limit": 5})
        cash = self._get(f"/cash-flow-statement/{ticker}", {"limit": 5})
        if not income and not balance:
            return None
        income, balance, cash = income or [], balance or [], cash or []

        statements = [
            self._statement(
                "income_statement",
                income,
                {
                    "revenue": "Total Revenue",
                    "grossProfit": "Gross Profit",
                    "operatingIncome": "Operating Income",
                    "netIncome": "Net Income",
                    "eps": "EPS",
                },
            ),
            self._statement(
                "balance_sheet",
                balance,
                {
                    "totalAssets": "Total Assets",
                    "totalLiabilities": "Total Liabilities",
                    "totalDebt": "Total Debt",
                    "totalStockholdersEquity": "Stockholders Equity",
                    "cashAndCashEquivalents": "Cash & Equivalents",
                },
            ),
            self._statement(
                "cash_flow",
                cash,
                {
                    "operatingCashFlow": "Operating Cash Flow",
                    "capitalExpenditure": "Capital Expenditure",
                    "freeCashFlow": "Free Cash Flow",
                },
            ),
        ]

        ratios = FinancialRatios()
        if income:
            cur = income[0]
            rev = cur.get("revenue")
            if rev:
                if cur.get("netIncome") is not None:
                    ratios.net_margin = cur["netIncome"] / rev * 100
                if cur.get("grossProfit") is not None:
                    ratios.gross_margin = cur["grossProfit"] / rev * 100
            if len(income) >= 2 and income[1].get("revenue"):
                prior = income[1]["revenue"]
                ratios.revenue_growth = (rev - prior) / abs(prior) * 100
        if balance:
            eq = balance[0].get("totalStockholdersEquity")
            debt = balance[0].get("totalDebt")
            if eq and debt is not None:
                ratios.debt_to_equity = debt / eq
        if cash:
            ratios.free_cash_flow = cash[0].get("freeCashFlow")

        return FinancialsResponse(ticker=ticker, statements=statements, ratios=ratios)
