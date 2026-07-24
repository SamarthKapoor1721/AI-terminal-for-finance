"""Financial statements + ratio calculations (Phase 3), sourced from yfinance."""

from __future__ import annotations

import math

import pandas as pd
import yfinance as yf

from app.schemas.financials import (
    FinancialRatios,
    FinancialsResponse,
    FinancialStatement,
    StatementLine,
)


def _clean(value) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None


def _frame_to_statement(name: str, df: pd.DataFrame) -> FinancialStatement:
    if df is None or df.empty:
        return FinancialStatement(name=name, periods=[], lines=[])

    periods = [c.strftime("%Y-%m-%d") if hasattr(c, "strftime") else str(c) for c in df.columns]
    lines: list[StatementLine] = []
    for label, row in df.iterrows():
        values = {
            period: _clean(row.iloc[i]) for i, period in enumerate(periods)
        }
        lines.append(StatementLine(label=str(label), values=values))
    return FinancialStatement(name=name, periods=periods, lines=lines)


def _row(df: pd.DataFrame, *names: str) -> pd.Series | None:
    """Return the first matching row (yfinance label names vary by version)."""
    if df is None or df.empty:
        return None
    for n in names:
        if n in df.index:
            return df.loc[n]
    return None


def _ratios(income: pd.DataFrame, balance: pd.DataFrame, cashflow: pd.DataFrame) -> FinancialRatios:
    ratios = FinancialRatios()

    revenue = _row(income, "Total Revenue", "TotalRevenue")
    net_income = _row(income, "Net Income", "NetIncome")
    gross_profit = _row(income, "Gross Profit", "GrossProfit")

    # Columns are ordered most-recent first in yfinance.
    if revenue is not None and len(revenue) >= 2:
        latest, prior = _clean(revenue.iloc[0]), _clean(revenue.iloc[1])
        if latest is not None and prior:
            ratios.revenue_growth = (latest - prior) / abs(prior) * 100

    if revenue is not None and len(revenue):
        rev0 = _clean(revenue.iloc[0])
        if rev0:
            if net_income is not None:
                ni0 = _clean(net_income.iloc[0])
                if ni0 is not None:
                    ratios.net_margin = ni0 / rev0 * 100
            if gross_profit is not None:
                gp0 = _clean(gross_profit.iloc[0])
                if gp0 is not None:
                    ratios.gross_margin = gp0 / rev0 * 100

    total_debt = _row(balance, "Total Debt", "TotalDebt")
    equity = _row(
        balance,
        "Stockholders Equity",
        "Total Stockholder Equity",
        "StockholdersEquity",
    )
    if total_debt is not None and equity is not None:
        debt0, eq0 = _clean(total_debt.iloc[0]), _clean(equity.iloc[0])
        if debt0 is not None and eq0:
            ratios.debt_to_equity = debt0 / eq0

    op_cf = _row(cashflow, "Operating Cash Flow", "Total Cash From Operating Activities")
    capex = _row(cashflow, "Capital Expenditure", "Capital Expenditures")
    if op_cf is not None and capex is not None:
        ocf0, cx0 = _clean(op_cf.iloc[0]), _clean(capex.iloc[0])
        if ocf0 is not None and cx0 is not None:
            ratios.free_cash_flow = ocf0 + cx0  # capex is negative in yfinance

    return ratios


def _yfinance_financials(ticker: str) -> FinancialsResponse | None:
    """yfinance implementation, called by YFinanceProvider.get_financials."""
    ticker = ticker.upper().strip()
    t = yf.Ticker(ticker)

    income = t.financials
    balance = t.balance_sheet
    cashflow = t.cashflow

    if (income is None or income.empty) and (balance is None or balance.empty):
        return None

    statements = [
        _frame_to_statement("income_statement", income),
        _frame_to_statement("balance_sheet", balance),
        _frame_to_statement("cash_flow", cashflow),
    ]
    return FinancialsResponse(
        ticker=ticker,
        statements=statements,
        ratios=_ratios(income, balance, cashflow),
    )


def get_financials(ticker: str) -> FinancialsResponse:
    """Resolve through the provider chain (FMP → yfinance)."""
    from app.services.providers import get_financials_providers
    from app.services.market_data import resolve_symbol

    ticker = ticker.upper().strip()
    symbol = resolve_symbol(ticker)  # handles .NS/.BO for Indian names
    for provider in get_financials_providers():
        try:
            result = provider.get_financials(symbol)
        except Exception:  # noqa: BLE001
            continue
        if result is not None:
            return result
    raise ValueError(f"No financial statements found for '{ticker}'")
