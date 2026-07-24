"use client";

import { use, useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { PriceChart } from "@/components/PriceChart";
import { StatCard } from "@/components/StatCard";
import { TickerSearch } from "@/components/TickerSearch";
import {
  api,
  type FinancialsResponse,
  type PriceHistory,
  type SentimentSummary,
  type StockQuote,
} from "@/lib/api";
import {
  changeColor,
  fmtCompact,
  fmtCompactCur,
  fmtCurrency,
  fmtNumber,
  fmtPercent,
} from "@/lib/format";

const PERIODS = ["1mo", "6mo", "1y", "5y"];

export default function StockPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = use(params);
  const sym = ticker.toUpperCase();

  const [quote, setQuote] = useState<StockQuote | null>(null);
  const [history, setHistory] = useState<PriceHistory | null>(null);
  const [period, setPeriod] = useState("1y");
  const [financials, setFinancials] = useState<FinancialsResponse | null>(null);
  const [sentiment, setSentiment] = useState<SentimentSummary | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    setErr(null);
    api.stock(sym).then(setQuote).catch((e) => setErr(e.message));
    api.financials(sym).then(setFinancials).catch(() => {});
    api
      .news(sym, true)
      .then(() => api.sentiment(sym).then(setSentiment))
      .catch(() => {});
  }, [sym]);

  useEffect(() => {
    api.history(sym, period).then(setHistory).catch(() => {});
  }, [sym, period]);

  return (
    <AppShell>
      <div className="mb-6 max-w-md">
        <TickerSearch />
      </div>

      {err && <p className="text-terminal-red">{err}</p>}

      {quote && (
        <>
          <div className="mb-6 flex flex-wrap items-baseline gap-x-4 gap-y-1">
            <h1 className="font-mono text-3xl font-bold text-terminal-amber">
              {quote.ticker}
            </h1>
            <span className="text-terminal-muted">{quote.name}</span>
            <span className="ml-auto font-mono text-3xl">
              {fmtCurrency(quote.price, quote.currency)}
            </span>
            <span className={`font-mono text-lg ${changeColor(quote.change)}`}>
              {quote.change != null ? fmtNumber(quote.change) : "—"} (
              {fmtPercent(quote.change_percent)})
            </span>
          </div>

          <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-7">
            <StatCard label="Market Cap" value={fmtCompactCur(quote.market_cap, quote.currency)} />
            <StatCard label="P/E" value={fmtNumber(quote.pe_ratio)} />
            <StatCard label="EPS" value={fmtNumber(quote.eps)} />
            <StatCard label="Volume" value={fmtCompact(quote.volume)} />
            <StatCard label="52W High" value={fmtCurrency(quote.week52_high, quote.currency)} />
            <StatCard label="52W Low" value={fmtCurrency(quote.week52_low, quote.currency)} />
            <StatCard label="Sector" value={quote.sector ?? "—"} />
          </div>

          <div className="panel mb-6 p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold">Price History</h2>
              <div className="flex gap-1">
                {PERIODS.map((p) => (
                  <button
                    key={p}
                    onClick={() => setPeriod(p)}
                    className={`rounded px-2 py-1 text-xs font-mono ${
                      period === p
                        ? "bg-terminal-amber text-black"
                        : "text-terminal-muted hover:text-terminal-text"
                    }`}
                  >
                    {p.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            {history ? (
              <PriceChart points={history.points} />
            ) : (
              <div className="flex h-80 items-center justify-center text-terminal-muted">
                Loading chart…
              </div>
            )}
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <RatiosPanel financials={financials} currency={quote.currency} />
            <SentimentPanel sentiment={sentiment} />
          </div>
        </>
      )}
    </AppShell>
  );
}

function RatiosPanel({
  financials,
  currency,
}: {
  financials: FinancialsResponse | null;
  currency?: string;
}) {
  const r = financials?.ratios;
  return (
    <div className="panel p-4">
      <h2 className="mb-3 text-sm font-semibold">Key Financial Ratios</h2>
      {r ? (
        <div className="grid grid-cols-2 gap-3">
          <Ratio label="Revenue Growth (YoY)" value={fmtPercent(r.revenue_growth)} />
          <Ratio label="Gross Margin" value={fmtPercent(r.gross_margin)} />
          <Ratio label="Net Margin" value={fmtPercent(r.net_margin)} />
          <Ratio label="Debt / Equity" value={fmtNumber(r.debt_to_equity)} />
          <Ratio
            label="Free Cash Flow"
            value={fmtCompactCur(r.free_cash_flow, currency)}
          />
        </div>
      ) : (
        <p className="text-sm text-terminal-muted">Loading financials…</p>
      )}
    </div>
  );
}

function Ratio({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="stat-label">{label}</div>
      <div className="font-mono text-base">{value}</div>
    </div>
  );
}

function SentimentPanel({ sentiment }: { sentiment: SentimentSummary | null }) {
  return (
    <div className="panel p-4">
      <h2 className="mb-3 text-sm font-semibold">News Sentiment (FinBERT)</h2>
      {sentiment && sentiment.article_count > 0 ? (
        <>
          <div className="mb-3 flex items-center gap-4">
            <div className="font-mono text-2xl">
              {sentiment.overall_score != null
                ? sentiment.overall_score.toFixed(2)
                : "—"}
            </div>
            <div className="text-xs text-terminal-muted">
              overall score across {sentiment.article_count} articles (-1…+1)
            </div>
          </div>
          <div className="flex gap-3 text-sm">
            <Pill label="Positive" n={sentiment.positive} color="text-terminal-green" />
            <Pill label="Neutral" n={sentiment.neutral} color="text-terminal-muted" />
            <Pill label="Negative" n={sentiment.negative} color="text-terminal-red" />
          </div>
        </>
      ) : (
        <p className="text-sm text-terminal-muted">
          No scored news yet (or FinBERT/Ollama not running).
        </p>
      )}
    </div>
  );
}

function Pill({ label, n, color }: { label: string; n: number; color: string }) {
  return (
    <div className="flex-1 rounded border border-terminal-border bg-terminal-bg p-3 text-center">
      <div className={`font-mono text-xl ${color}`}>{n}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
