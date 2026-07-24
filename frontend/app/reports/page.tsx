"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Markdown } from "@/components/Markdown";
import { api, getToken, type Report } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ReportsPage() {
  const [ticker, setTicker] = useState("AAPL");
  const [reports, setReports] = useState<Report[]>([]);
  const [active, setActive] = useState<Report | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.reports().then((r) => {
      setReports(r);
      if (r.length) setActive(r[0]);
    });
  }, []);

  async function generate() {
    setBusy(true);
    try {
      const r = await api.generateReport(ticker.toUpperCase());
      setReports((prev) => [r, ...prev]);
      setActive(r);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-1 page-title">AI Research Reports</h1>
      <p className="mb-6 text-sm text-terminal-muted">
        Generates an 8-section analyst report (overview, revenue, profitability,
        sentiment, risks, opportunities, bull & bear) with Qwen 3. Export as PDF.
      </p>

      <div className="mb-6 flex gap-2">
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          className="w-40 rounded border border-terminal-border bg-terminal-panel px-3 py-2 text-sm uppercase"
        />
        <button
          onClick={generate}
          disabled={busy}
          className="rounded bg-terminal-amber px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
        >
          {busy ? "Generating… (LLM)" : "Generate Report"}
        </button>
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        <div className="panel p-3 lg:col-span-1">
          <div className="stat-label mb-2">History</div>
          {reports.length === 0 && (
            <p className="text-xs text-terminal-muted">No reports yet.</p>
          )}
          {reports.map((r) => (
            <button
              key={r.id}
              onClick={() => setActive(r)}
              className={`mb-1 block w-full rounded px-2 py-1.5 text-left text-sm ${
                active?.id === r.id
                  ? "bg-terminal-bg text-terminal-amber"
                  : "text-terminal-muted hover:bg-terminal-bg"
              }`}
            >
              {r.ticker} · {r.created_at.slice(0, 10)}
            </button>
          ))}
        </div>

        <div className="panel p-6 lg:col-span-3">
          {active ? (
            <>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="font-mono text-lg text-terminal-amber">{active.title}</h2>
                <a
                  href={`${API_URL}/reports/${active.id}/pdf`}
                  onClick={(e) => {
                    // attach auth token via fetch + blob since <a> can't set headers
                    e.preventDefault();
                    fetch(`${API_URL}/reports/${active.id}/pdf`, {
                      headers: { Authorization: `Bearer ${getToken()}` },
                    })
                      .then((res) => res.blob())
                      .then((blob) => {
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `${active.ticker}_report.pdf`;
                        a.click();
                        URL.revokeObjectURL(url);
                      });
                  }}
                  className="rounded border border-terminal-border px-3 py-1.5 text-xs hover:border-terminal-amber"
                >
                  ⬇ Download PDF
                </a>
              </div>
              <Markdown content={active.content_md} />
            </>
          ) : (
            <p className="text-sm text-terminal-muted">
              Generate a report to view it here.
            </p>
          )}
        </div>
      </div>
    </AppShell>
  );
}
