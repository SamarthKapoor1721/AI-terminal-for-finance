"use client";

import { useEffect, useState } from "react";
import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { AppShell } from "@/components/AppShell";
import { StatCard } from "@/components/StatCard";
import { api, type Portfolio, type PortfolioSummary } from "@/lib/api";
import {
  changeColor,
  fmtCompact,
  fmtCurrency,
  fmtNumber,
  fmtPercent,
} from "@/lib/format";

const COLORS = ["#ffb000", "#3b82f6", "#22c55e", "#ef4444", "#a855f7", "#14b8a6"];

export default function PortfolioPage() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [active, setActive] = useState<number | null>(null);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [form, setForm] = useState({ ticker: "", quantity: "", price: "" });

  async function load() {
    const ps = await api.portfolios();
    setPortfolios(ps);
    if (ps.length && active == null) setActive(ps[0].id);
  }
  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (active != null) api.portfolio(active).then(setSummary);
  }, [active]);

  async function createPortfolio() {
    const p = await api.createPortfolio("My Portfolio");
    await load();
    setActive(p.id);
  }

  async function addHolding(e: React.FormEvent) {
    e.preventDefault();
    if (active == null) return;
    await api.addHolding(active, {
      ticker: form.ticker.toUpperCase(),
      quantity: Number(form.quantity),
      purchase_price: Number(form.price),
    });
    setForm({ ticker: "", quantity: "", price: "" });
    api.portfolio(active).then(setSummary);
  }

  const pieData =
    summary?.holdings
      .filter((h) => h.weight != null)
      .map((h) => ({ name: h.ticker, value: h.weight! })) ?? [];

  return (
    <AppShell>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="page-title">Portfolio</h1>
        {portfolios.length === 0 && (
          <button
            onClick={createPortfolio}
            className="rounded bg-terminal-amber px-3 py-2 text-sm font-semibold text-black"
          >
            Create Portfolio
          </button>
        )}
      </div>

      {summary && (
        <>
          <div className="mb-6 grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-6">
            <StatCard label="Total Value" value={fmtCurrency(summary.total_value)} />
            <StatCard label="Total Cost" value={fmtCurrency(summary.total_cost)} />
            <StatCard
              label="Total Gain"
              value={summary.total_gain != null ? fmtCurrency(summary.total_gain) : "—"}
              accent={changeColor(summary.total_gain)}
            />
            <StatCard
              label="Return"
              value={fmtPercent(summary.total_gain_percent)}
              accent={changeColor(summary.total_gain_percent)}
            />
            <StatCard
              label="Volatility (ann.)"
              value={summary.volatility != null ? fmtPercent(summary.volatility * 100) : "—"}
            />
            <StatCard label="Sharpe" value={fmtNumber(summary.sharpe_ratio)} />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="panel p-4 lg:col-span-2">
              <h2 className="mb-3 text-sm font-semibold">Holdings</h2>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-terminal-border text-left text-xs uppercase text-terminal-muted">
                    <th className="py-2">Ticker</th>
                    <th className="py-2 text-right">Qty</th>
                    <th className="py-2 text-right">Cost</th>
                    <th className="py-2 text-right">Price</th>
                    <th className="py-2 text-right">Value</th>
                    <th className="py-2 text-right">Gain</th>
                    <th className="py-2 text-right">Weight</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.holdings.map((h) => (
                    <tr key={h.id} className="border-b border-terminal-border/50">
                      <td className="py-2 font-mono text-terminal-amber">{h.ticker}</td>
                      <td className="py-2 text-right font-mono">{fmtNumber(h.quantity, 0)}</td>
                      <td className="py-2 text-right font-mono">{fmtCurrency(h.purchase_price)}</td>
                      <td className="py-2 text-right font-mono">{fmtCurrency(h.current_price)}</td>
                      <td className="py-2 text-right font-mono">{fmtCurrency(h.market_value)}</td>
                      <td className={`py-2 text-right font-mono ${changeColor(h.gain)}`}>
                        {fmtPercent(h.gain_percent)}
                      </td>
                      <td className="py-2 text-right font-mono">
                        {h.weight != null ? `${h.weight.toFixed(1)}%` : "—"}
                      </td>
                    </tr>
                  ))}
                  {summary.holdings.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-6 text-center text-terminal-muted">
                        No holdings yet. Add one below.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>

              <form onSubmit={addHolding} className="mt-4 flex flex-wrap gap-2">
                <input
                  placeholder="Ticker"
                  value={form.ticker}
                  onChange={(e) => setForm({ ...form, ticker: e.target.value })}
                  className="w-28 rounded border border-terminal-border bg-terminal-bg px-2 py-1.5 text-sm uppercase"
                  required
                />
                <input
                  placeholder="Quantity"
                  type="number"
                  step="any"
                  value={form.quantity}
                  onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                  className="w-28 rounded border border-terminal-border bg-terminal-bg px-2 py-1.5 text-sm"
                  required
                />
                <input
                  placeholder="Buy price"
                  type="number"
                  step="any"
                  value={form.price}
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
                  className="w-28 rounded border border-terminal-border bg-terminal-bg px-2 py-1.5 text-sm"
                  required
                />
                <button className="rounded bg-terminal-amber px-3 py-1.5 text-sm font-semibold text-black">
                  Add
                </button>
              </form>
            </div>

            <div className="panel p-4">
              <h2 className="mb-3 text-sm font-semibold">Allocation</h2>
              {pieData.length ? (
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={90}>
                      {pieData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: "#121316", border: "1px solid #26282e" }}
                      formatter={(v) => `${Number(v).toFixed(1)}%`}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-sm text-terminal-muted">Add holdings to see allocation.</p>
              )}
            </div>
          </div>
        </>
      )}
    </AppShell>
  );
}
