from pydantic import BaseModel


class StatementLine(BaseModel):
    """One row of a financial statement across reporting periods."""

    label: str
    values: dict[str, float | None]  # period (e.g. "2023-12-31") -> value


class FinancialStatement(BaseModel):
    name: str  # income_statement | balance_sheet | cash_flow
    periods: list[str]
    lines: list[StatementLine]


class FinancialRatios(BaseModel):
    revenue_growth: float | None = None  # YoY %
    gross_margin: float | None = None
    net_margin: float | None = None
    debt_to_equity: float | None = None
    free_cash_flow: float | None = None


class FinancialsResponse(BaseModel):
    ticker: str
    statements: list[FinancialStatement]
    ratios: FinancialRatios
