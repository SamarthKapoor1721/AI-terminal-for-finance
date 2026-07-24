"use client";

import { useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { api, ApiError, type CountryRisk } from "@/lib/api";
import { sentimentColor } from "@/lib/format";

// react-simple-maps touches browser APIs; skip SSR to avoid hydration errors.
const WorldMap = dynamic(() => import("./WorldMap"), { ssr: false });

function flagEmoji(iso2: string): string {
  return String.fromCodePoint(
    ...Array.from(iso2).map((c) => 0x1f1e6 - 65 + c.charCodeAt(0))
  );
}

export default function GeoPage() {
  const [data, setData] = useState<CountryRisk[]>([]);
  const [selected, setSelected] = useState<CountryRisk | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const riskByIso2 = useMemo(
    () => Object.fromEntries(data.map((c) => [c.iso2, c])),
    [data]
  );

  async function load(refresh = false) {
    setBusy(true);
    setError(null);
    try {
      setData(await api.geoHeatmap(refresh));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load heatmap");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AppShell>
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h1 className="mb-1 page-title">Geopolitical Risk</h1>
          <p className="text-sm text-terminal-muted">
            Countries colored by FinBERT sentiment of recent financial news.
            Click a country for details.
          </p>
        </div>
        <div className="text-right">
          <button
            onClick={() => load(true)}
            disabled={busy}
            className="rounded bg-terminal-amber px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
          >
            {busy ? "Loading…" : "Refresh"}
          </button>
          <div className="mt-1 text-xs text-terminal-muted">
            Takes ~1 min — fetches fresh news for 40+ country ETFs
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded border border-terminal-red/50 bg-terminal-red/10 px-4 py-2 text-sm text-terminal-red">
          {error}
        </div>
      )}

      <div className="flex flex-col gap-4 lg:flex-row">
        <div className="panel relative p-2 lg:w-[65%]">
          <WorldMap riskByIso2={riskByIso2} onSelect={setSelected} />
          {!busy && data.length === 0 && !error && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="rounded border border-terminal-border bg-terminal-panel px-6 py-4 text-sm text-terminal-muted">
                No data — click Refresh to fetch market news
              </div>
            </div>
          )}
        </div>

        <div className="lg:w-[35%]">
          {selected ? (
            <DetailPanel country={selected} onClose={() => setSelected(null)} />
          ) : (
            <SummaryPanel data={data} onSelect={setSelected} />
          )}
        </div>
      </div>
    </AppShell>
  );
}

function ScoreBadge({ score }: { score: number }) {
  return (
    <span
      className="rounded px-2 py-0.5 font-mono text-xs text-white"
      style={{ backgroundColor: sentimentColor(score) }}
    >
      {score > 0 ? "+" : ""}
      {score.toFixed(2)}
    </span>
  );
}

function DetailPanel({
  country,
  onClose,
}: {
  country: CountryRisk;
  onClose: () => void;
}) {
  return (
    <div className="panel p-4">
      <div className="mb-3 flex items-start justify-between">
        <h2 className="text-lg font-semibold">
          {flagEmoji(country.iso2)} {country.name}
        </h2>
        <button
          onClick={onClose}
          className="text-sm text-terminal-muted hover:text-terminal-text"
        >
          ✕
        </button>
      </div>

      <div className="mb-4 flex items-center gap-3 text-sm">
        <ScoreBadge score={country.score} />
        <span className="text-terminal-muted">
          {country.article_count} article{country.article_count === 1 ? "" : "s"}
        </span>
      </div>

      <div className="space-y-2">
        {country.headlines.map((h) => (
          <a
            key={h.url}
            href={h.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block rounded border border-terminal-border p-3 hover:border-terminal-amber/50"
          >
            <div className="flex items-start gap-2">
              <span
                className="mt-1.5 h-2 w-2 shrink-0 rounded-full"
                style={{ backgroundColor: sentimentColor(h.sentiment_score ?? 0) }}
              />
              <div className="min-w-0">
                <div className="text-sm">
                  {h.headline.length > 80
                    ? `${h.headline.slice(0, 80)}…`
                    : h.headline}
                </div>
                <div className="mt-1 flex items-center gap-2 text-xs text-terminal-muted">
                  {h.source && <span>{h.source}</span>}
                  <span className="rounded bg-terminal-amber/15 px-1.5 py-0.5 font-mono text-terminal-amber">
                    {h.ticker}
                  </span>
                </div>
              </div>
            </div>
          </a>
        ))}
      </div>

      {country.headlines[0] && (
        <Link
          href={`/news?ticker=${country.headlines[0].ticker}`}
          className="mt-4 inline-block text-sm text-terminal-amber hover:underline"
        >
          View full news →
        </Link>
      )}
    </div>
  );
}

function SummaryPanel({
  data,
  onSelect,
}: {
  data: CountryRisk[];
  onSelect: (c: CountryRisk) => void;
}) {
  // build_heatmap returns ascending by score, so the head is most negative.
  const worst = data.slice(0, 5);
  return (
    <div className="panel p-4">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-terminal-muted">
        Legend
      </h2>
      <div className="mb-1 h-2 w-full rounded bg-gradient-to-r from-terminal-red via-terminal-border to-terminal-green" />
      <div className="mb-5 flex justify-between text-xs text-terminal-muted">
        <span>Negative</span>
        <span>Neutral</span>
        <span>Positive</span>
      </div>

      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-terminal-muted">
        Highest Risk
      </h2>
      <div className="space-y-1">
        {worst.map((c) => (
          <button
            key={c.iso2}
            onClick={() => onSelect(c)}
            className="flex w-full items-center justify-between rounded px-2 py-2 text-left text-sm hover:bg-terminal-bg"
          >
            <span>
              {flagEmoji(c.iso2)} {c.name}
              <span className="ml-2 text-xs text-terminal-muted">
                {c.article_count} articles
              </span>
            </span>
            <ScoreBadge score={c.score} />
          </button>
        ))}
        {worst.length === 0 && (
          <p className="text-sm text-terminal-muted">No countries scored yet.</p>
        )}
      </div>
    </div>
  );
}
