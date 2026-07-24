"use client";

import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Markdown } from "@/components/Markdown";
import { api, type AgentResult } from "@/lib/api";

const AGENT_ORDER = [
  "Financial Analyst",
  "Technical Analyst",
  "News Analyst",
  "Risk Analyst",
  "Macro Analyst",
  "Portfolio Analyst",
];

export default function MemoPage() {
  const [ticker, setTicker] = useState("AAPL");
  const [query, setQuery] = useState("Should I invest in this company?");
  const [result, setResult] = useState<AgentResult | null>(null);
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    setResult(null);
    try {
      setResult(await api.runAgents(ticker.toUpperCase(), query));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-1 page-title">Multi-Agent Investment Memo</h1>
      <p className="mb-6 text-sm text-terminal-muted">
        Six specialist agents (Financial, Technical, News, Risk, Macro, Portfolio)
        research independently, then a Coordinator synthesizes a final memo.
      </p>

      <div className="mb-6 flex flex-wrap gap-2">
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          className="w-32 rounded border border-terminal-border bg-terminal-panel px-3 py-2 text-sm uppercase"
        />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="min-w-[280px] flex-1 rounded border border-terminal-border bg-terminal-panel px-3 py-2 text-sm"
        />
        <button
          onClick={run}
          disabled={busy}
          className="rounded bg-terminal-amber px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
        >
          {busy ? "Agents running… (~30-60s)" : "Run Research"}
        </button>
      </div>

      {busy && (
        <div className="panel p-4 text-sm text-terminal-muted">
          Running 5 agents + coordinator on the local LLM. This takes a bit on CPU…
        </div>
      )}

      {result?.off_topic && (
        <div className="panel mx-auto max-w-xl border-terminal-amber/40 p-6 text-center">
          <div className="mb-3 text-3xl">🚫</div>
          <Markdown content={result.memo} />
        </div>
      )}

      {result && !result.off_topic && (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-3 lg:col-span-2">
            <div className="panel border-terminal-amber/40 p-5">
              <div className="stat-label mb-2 text-terminal-amber">Final Investment Memo</div>
              <Markdown content={result.memo} />
            </div>
          </div>
          <div className="space-y-3">
            {AGENT_ORDER.map((name) => {
              const f = result.findings.find((x) => x.agent === name);
              if (!f) return null;
              return (
                <div key={name} className="panel p-4">
                  <div className="stat-label mb-1">{f.agent}</div>
                  <p className="text-sm text-terminal-text/85">{f.summary}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </AppShell>
  );
}
