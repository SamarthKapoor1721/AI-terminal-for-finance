"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { api, type ScreenResult } from "@/lib/api";
import { fmtCompactCur, fmtNumber, fmtPercent } from "@/lib/format";

export default function ScreenerPage() {
  const [filters, setFilters] = useState({
    min_market_cap: "10",
    max_pe: "",
    min_revenue_growth: "",
    max_debt_to_equity: "",
  });
  const [market, setMarket] = useState<"us" | "india" | "all">("us");
  const [results, setResults] = useState<ScreenResult[]>([]);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    try {
      const body: Record<string, unknown> = { market };
      if (filters.min_market_cap)
        body.min_market_cap = Number(filters.min_market_cap) * 1e9;
      if (filters.max_pe) body.max_pe = Number(filters.max_pe);
      if (filters.min_revenue_growth)
        body.min_revenue_growth = Number(filters.min_revenue_growth);
      if (filters.max_debt_to_equity)
        body.max_debt_to_equity = Number(filters.max_debt_to_equity);
      const res = await api.screen(body);
      setResults(res.results);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-1 page-title">Stock Screener</h1>
      <p className="mb-6 text-sm text-terminal-muted">
        Filters run against a seeded large/mid-cap universe (fundamentals via yfinance).
      </p>

      <div className="mb-4 flex gap-1">
        {([
          ["us", "🇺🇸 US"],
          ["india", "🇮🇳 India"],
          ["all", "🌐 All"],
        ] as const).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setMarket(key)}
            className={`rounded px-3 py-1.5 text-sm font-medium transition-colors ${
              market === key
                ? "bg-terminal-amber text-black"
                : "text-terminal-muted hover:bg-terminal-panel hover:text-terminal-text"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="panel mb-6 grid grid-cols-2 gap-4 p-4 md:grid-cols-4">
        <Filter
          label="Min Market Cap ($B)"
          value={filters.min_market_cap}
          onChange={(v) => setFilters({ ...filters, min_market_cap: v })}
        />
        <Filter
          label="Max P/E"
          value={filters.max_pe}
          onChange={(v) => setFilters({ ...filters, max_pe: v })}
        />
        <Filter
          label="Min Rev Growth (%)"
          value={filters.min_revenue_growth}
          onChange={(v) => setFilters({ ...filters, min_revenue_growth: v })}
        />
        <Filter
          label="Max Debt/Equity"
          value={filters.max_debt_to_equity}
          onChange={(v) => setFilters({ ...filters, max_debt_to_equity: v })}
        />
      </div>

      <button
        onClick={run}
        disabled={busy}
        className="mb-6 rounded bg-terminal-amber px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
      >
        {busy ? "Screening…" : "Run Screen"}
      </button>

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-terminal-border text-left text-xs uppercase text-terminal-muted">
              <th className="px-4 py-3">Ticker</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3 text-right">Mkt Cap</th>
              <th className="px-4 py-3 text-right">P/E</th>
              <th className="px-4 py-3 text-right">Rev Growth</th>
              <th className="px-4 py-3 text-right">D/E</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.ticker} className="border-b border-terminal-border/50">
                <td className="px-4 py-3">
                  <Link
                    href={`/stocks/${r.ticker}`}
                    className="font-mono text-terminal-amber hover:underline"
                  >
                    {r.ticker.replace(/\.(NS|BO)$/, "")}
                  </Link>
                </td>
                <td className="px-4 py-3 text-terminal-muted">{r.name}</td>
                <td className="px-4 py-3 text-right font-mono">{fmtCompactCur(r.market_cap, r.currency)}</td>
                <td className="px-4 py-3 text-right font-mono">{fmtNumber(r.pe_ratio)}</td>
                <td className="px-4 py-3 text-right font-mono">{fmtPercent(r.revenue_growth)}</td>
                <td className="px-4 py-3 text-right font-mono">{fmtNumber(r.debt_to_equity)}</td>
              </tr>
            ))}
            {results.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-terminal-muted">
                  Run a screen to see matching companies.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}

function Filter({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className="block">
      <span className="stat-label">{label}</span>
      <input
        type="number"
        step="any"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded border border-terminal-border bg-terminal-bg px-2 py-1.5 text-sm"
      />
    </label>
  );
}
