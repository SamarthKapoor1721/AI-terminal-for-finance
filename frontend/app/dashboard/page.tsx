"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TickerSearch } from "@/components/TickerSearch";
import { api, type StockQuote } from "@/lib/api";
import {
  fmtCompactCur,
  fmtNumber,
  fmtPercent,
  changeColor,
  currencySymbol,
} from "@/lib/format";

const MARKETS = {
  us: {
    label: "🇺🇸 US Stocks",
    tickers: [
      "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
      "JPM", "V", "MA", "UNH", "HD", "PG", "XOM", "JNJ", "WMT", "KO",
      "CRM", "NFLX", "AMD", "INTC", "ORCL", "ADBE", "CSCO", "PEP",
      "DIS", "BAC", "QCOM", "TXN",
    ],
  },
  india: {
    label: "🇮🇳 Indian Stocks",
    tickers: [
      "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
      "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
      "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS",
      "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
      "HCLTECH.NS", "TATAMOTORS.NS", "ADANIENT.NS", "POWERGRID.NS", "NTPC.NS",
      "ONGC.NS", "COALINDIA.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "TECHM.NS",
    ],
  },
} as const;

type MarketKey = keyof typeof MARKETS;
const BATCH_SIZE = 5; // load quotes in small batches to respect rate limits

export default function DashboardPage() {
  const [market, setMarket] = useState<MarketKey>("us");
  const [quotes, setQuotes] = useState<Record<string, StockQuote | null>>({});
  const [loadedCount, setLoadedCount] = useState(0);
  const reqId = useRef(0);

  const load = useCallback(async (key: MarketKey) => {
    const myId = ++reqId.current;
    const tickers = MARKETS[key].tickers;
    setQuotes({});
    setLoadedCount(0);

    for (let i = 0; i < tickers.length; i += BATCH_SIZE) {
      if (myId !== reqId.current) return; // a newer market switch superseded us
      const batch = tickers.slice(i, i + BATCH_SIZE);
      await Promise.all(
        batch.map(async (t) => {
          try {
            const q = await api.stock(t);
            if (myId === reqId.current) setQuotes((p) => ({ ...p, [t]: q }));
          } catch {
            if (myId === reqId.current) setQuotes((p) => ({ ...p, [t]: null }));
          }
        })
      );
      if (myId === reqId.current) setLoadedCount(Math.min(i + BATCH_SIZE, tickers.length));
    }
  }, []);

  useEffect(() => {
    load(market);
  }, [market, load]);

  const total = MARKETS[market].tickers.length;

  return (
    <AppShell>
      <div className="mb-6 flex items-end justify-between gap-4">
        <div>
          <h1 className="page-title">Market Dashboard</h1>
          <p className="mt-1 text-sm text-terminal-muted">
            Live quotes via yfinance. Click a row for full analysis.
          </p>
        </div>
        <div className="w-72">
          <TickerSearch placeholder="Search ticker (AAPL, TCS…)" />
        </div>
      </div>

      <div className="panel overflow-hidden">
        <div className="panel-header">
          <span>Watchlist</span>
          <span className="flex items-center gap-3">
            {loadedCount < total && (
              <span className="text-xs text-terminal-muted">
                loading {loadedCount}/{total}…
              </span>
            )}
            <span className="flex gap-1 rounded-md bg-terminal-bg p-0.5">
              {(Object.keys(MARKETS) as MarketKey[]).map((key) => (
                <button
                  key={key}
                  onClick={() => setMarket(key)}
                  className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
                    market === key
                      ? "bg-terminal-amber text-black"
                      : "text-terminal-muted hover:text-terminal-text"
                  }`}
                >
                  {MARKETS[key].label}
                </button>
              ))}
            </span>
          </span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Name</th>
              <th className="text-right">Price</th>
              <th className="text-right">Change</th>
              <th className="text-right">Mkt Cap</th>
              <th className="text-right">P/E</th>
            </tr>
          </thead>
          <tbody>
            {MARKETS[market].tickers.map((t) => (
              <WatchRow key={t} ticker={t} quote={quotes[t]} loaded={t in quotes} />
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}

function WatchRow({
  ticker,
  quote,
  loaded,
}: {
  ticker: string;
  quote: StockQuote | null | undefined;
  loaded: boolean;
}) {
  const display = ticker.replace(/\.(NS|BO)$/, "");
  const cur = currencySymbol(quote?.currency);

  return (
    <tr>
      <td>
        <Link
          href={`/stocks/${ticker}`}
          className="font-mono font-semibold text-terminal-amber hover:underline"
        >
          {display}
        </Link>
      </td>
      <td className="text-terminal-muted">
        {!loaded ? <span className="skeleton h-3 w-32" /> : quote?.name ?? "—"}
      </td>
      <td className="num text-right">
        {!loaded ? (
          <span className="skeleton h-3 w-14" />
        ) : quote?.price != null ? (
          `${cur}${fmtNumber(quote.price)}`
        ) : (
          "—"
        )}
      </td>
      <td className={`num text-right ${changeColor(quote?.change_percent)}`}>
        {quote?.change_percent != null ? fmtPercent(quote.change_percent) : "—"}
      </td>
      <td className="num text-right">
        {quote?.market_cap != null ? fmtCompactCur(quote.market_cap, quote.currency) : "—"}
      </td>
      <td className="num text-right">
        {quote?.pe_ratio != null ? fmtNumber(quote.pe_ratio) : "—"}
      </td>
    </tr>
  );
}
