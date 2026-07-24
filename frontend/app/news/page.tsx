"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { api, type NewsArticle, type SentimentSummary } from "@/lib/api";

const SENTIMENT_COLOR: Record<string, string> = {
  positive: "text-terminal-green",
  negative: "text-terminal-red",
  neutral: "text-terminal-muted",
};

export default function NewsPage() {
  return (
    <Suspense>
      <NewsPageInner />
    </Suspense>
  );
}

function NewsPageInner() {
  const searchParams = useSearchParams();
  const [ticker, setTicker] = useState(searchParams.get("ticker") || "AAPL");
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [summary, setSummary] = useState<SentimentSummary | null>(null);
  const [busy, setBusy] = useState(false);

  async function load(e?: React.FormEvent) {
    e?.preventDefault();
    setBusy(true);
    try {
      const sym = ticker.toUpperCase();
      const list = await api.news(sym, true);
      setArticles(list);
      setSummary(await api.sentiment(sym));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-1 page-title">News Intelligence</h1>
      <p className="mb-6 text-sm text-terminal-muted">
        Headlines scored with FinBERT sentiment.
      </p>

      <form onSubmit={load} className="mb-6 flex gap-2">
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          className="w-40 rounded border border-terminal-border bg-terminal-panel px-3 py-2 text-sm uppercase"
        />
        <button
          disabled={busy}
          className="rounded bg-terminal-amber px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
        >
          {busy ? "Loading…" : "Fetch News"}
        </button>
      </form>

      {summary && (
        <div className="mb-6 flex gap-3">
          <Tile label="Positive" n={summary.positive} color="text-terminal-green" />
          <Tile label="Neutral" n={summary.neutral} color="text-terminal-muted" />
          <Tile label="Negative" n={summary.negative} color="text-terminal-red" />
          <Tile
            label="Overall"
            n={summary.overall_score != null ? Number(summary.overall_score.toFixed(2)) : 0}
            color="text-terminal-amber"
          />
        </div>
      )}

      <div className="space-y-2">
        {articles.map((a) => (
          <a
            key={a.id}
            href={a.url}
            target="_blank"
            rel="noopener noreferrer"
            className="panel block p-4 hover:border-terminal-amber/50"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-sm font-medium">{a.headline}</div>
                <div className="mt-1 text-xs text-terminal-muted">
                  {a.source} · {a.published_at?.slice(0, 10) ?? "—"}
                </div>
              </div>
              {a.sentiment && (
                <span
                  className={`shrink-0 font-mono text-xs uppercase ${
                    SENTIMENT_COLOR[a.sentiment] ?? ""
                  }`}
                >
                  {a.sentiment}
                  {a.confidence != null && ` ${(a.confidence * 100).toFixed(0)}%`}
                </span>
              )}
            </div>
          </a>
        ))}
        {articles.length === 0 && (
          <p className="text-sm text-terminal-muted">
            Enter a ticker and fetch news to begin.
          </p>
        )}
      </div>
    </AppShell>
  );
}

function Tile({ label, n, color }: { label: string; n: number; color: string }) {
  return (
    <div className="panel flex-1 p-3 text-center">
      <div className={`font-mono text-2xl ${color}`}>{n}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
