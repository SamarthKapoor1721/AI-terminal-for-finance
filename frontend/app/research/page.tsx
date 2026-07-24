"use client";

import { useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api, type Filing } from "@/lib/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ResearchPage() {
  const [question, setQuestion] = useState("");
  const [ticker, setTicker] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function ask(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setAnswer(null);
    try {
      const { api } = await import("@/lib/api");
      const res = await api.ask(question, ticker || undefined);
      setAnswer(res.answer);
    } catch (err) {
      setAnswer(err instanceof Error ? err.message : "Failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-1 page-title">Research Assistant (RAG)</h1>
      <p className="mb-6 text-sm text-terminal-muted">
        Upload filings / transcripts, then ask questions answered from your documents
        (ChromaDB + bge embeddings + Qwen 3 via Ollama).
      </p>

      <EdgarPanel />

      <div className="grid gap-6 lg:grid-cols-2">
        <UploadPanel />

        <div className="panel p-4">
          <h2 className="mb-3 text-sm font-semibold">Ask a Question</h2>
          <form onSubmit={ask} className="space-y-3">
            <input
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="Ticker filter (optional)"
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm uppercase"
            />
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Summarize the key risks. What did management say about growth?"
              rows={3}
              className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm"
              required
            />
            <button
              disabled={busy}
              className="rounded bg-terminal-amber px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
            >
              {busy ? "Thinking…" : "Ask"}
            </button>
          </form>
          {answer && (
            <div className="mt-4 whitespace-pre-wrap rounded border border-terminal-border bg-terminal-bg p-3 text-sm">
              {answer}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

function EdgarPanel() {
  const [ticker, setTicker] = useState("");
  const [filings, setFilings] = useState<Filing[]>([]);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  async function load(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setStatus(null);
    setFilings([]);
    try {
      const res = await api.filings(ticker.toUpperCase());
      setFilings(res.filings);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "No filings found");
    } finally {
      setBusy(false);
    }
  }

  async function ingest(f: Filing) {
    setStatus(`Ingesting ${f.form}…`);
    try {
      const doc = await api.ingestFiling({
        ticker: ticker.toUpperCase(),
        url: f.url,
        form: f.form,
        date: f.date,
      });
      setStatus(`Indexed ${f.form} (${f.date}) — ask questions below.`);
      return doc;
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Ingest failed");
    }
  }

  return (
    <div className="panel mb-6 p-4">
      <h2 className="mb-3 text-sm font-semibold">
        Pull SEC Filings (EDGAR — no API key)
      </h2>
      <form onSubmit={load} className="mb-3 flex gap-2">
        <input
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="Ticker (e.g. AAPL)"
          className="w-40 rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm uppercase"
          required
        />
        <button
          disabled={busy}
          className="rounded bg-terminal-amber px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
        >
          {busy ? "Fetching…" : "List 10-K / 10-Q"}
        </button>
      </form>
      {status && <p className="mb-2 text-sm text-terminal-muted">{status}</p>}
      <div className="space-y-1">
        {filings.map((f) => (
          <div
            key={f.accession}
            className="flex items-center justify-between rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm"
          >
            <span className="font-mono">
              <span className="text-terminal-amber">{f.form}</span> · {f.date}
            </span>
            <button
              onClick={() => ingest(f)}
              className="rounded border border-terminal-border px-2 py-1 text-xs hover:border-terminal-amber"
            >
              Ingest → RAG
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function UploadPanel() {
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function upload(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    setBusy(true);
    setStatus(null);
    try {
      const { getToken } = await import("@/lib/api");
      const res = await fetch(`${API_URL}/research/documents`, {
        method: "POST",
        headers: { Authorization: `Bearer ${getToken()}` },
        body: fd,
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Upload failed");
      const doc = await res.json();
      setStatus(`Indexed "${doc.title}" — ${doc.chunk_count} chunks.`);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel p-4">
      <h2 className="mb-3 text-sm font-semibold">Upload Document</h2>
      <form onSubmit={upload} className="space-y-3">
        <input
          name="title"
          placeholder="Document title"
          className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm"
          required
        />
        <input
          name="ticker"
          placeholder="Ticker (optional)"
          className="w-full rounded border border-terminal-border bg-terminal-bg px-3 py-2 text-sm uppercase"
        />
        <input
          name="file"
          type="file"
          accept=".pdf,.txt"
          className="w-full text-sm text-terminal-muted file:mr-3 file:rounded file:border-0 file:bg-terminal-border file:px-3 file:py-1.5 file:text-terminal-text"
          required
        />
        <button
          disabled={busy}
          className="rounded bg-terminal-amber px-4 py-2 text-sm font-semibold text-black disabled:opacity-50"
        >
          {busy ? "Indexing…" : "Upload & Index"}
        </button>
      </form>
      {status && <p className="mt-3 text-sm text-terminal-muted">{status}</p>}
    </div>
  );
}
