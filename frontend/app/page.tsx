"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  LineChart,
  Newspaper,
  FileSearch,
  Bot,
  Briefcase,
  Filter,
  FileText,
  TrendingUp,
  ShieldCheck,
  Cpu,
  Lock,
  Zap,
} from "lucide-react";
import { getToken } from "@/lib/api";

const TICKER_TAPE = [
  ["AAPL", "+1.2%", true],
  ["TSLA", "-2.4%", false],
  ["NVDA", "+3.1%", true],
  ["MSFT", "+0.6%", true],
  ["GOOGL", "-0.4%", false],
  ["AMZN", "+1.8%", true],
  ["META", "+2.2%", true],
  ["AMD", "-1.1%", false],
] as const;

const FEATURES = [
  { icon: LineChart, title: "Live Market Data", desc: "Real-time prices, market cap, P/E, EPS and interactive charts for any ticker." },
  { icon: FileText, title: "Financial Statements", desc: "Income, balance sheet & cash flow — with growth, margins and key ratios computed for you." },
  { icon: Newspaper, title: "AI News Sentiment", desc: "FinBERT reads every headline and labels it positive, negative or neutral." },
  { icon: FileSearch, title: "Document Q&A (RAG)", desc: "Upload annual reports or pull SEC filings, then ask questions in plain English." },
  { icon: Bot, title: "Multi-Agent Memo", desc: "Five AI analysts research independently; a coordinator delivers a Buy/Hold/Sell memo." },
  { icon: Briefcase, title: "Portfolio Analytics", desc: "Track gains, volatility, Sharpe ratio and allocation across your holdings." },
  { icon: Filter, title: "Stock Screener", desc: "Filter the market by market cap, P/E, revenue growth and debt." },
  { icon: TrendingUp, title: "Economic Dashboard", desc: "Inflation, interest rates, GDP and unemployment trends that move markets." },
];

const TRUST = [
  { icon: Lock, label: "Private by default", desc: "AI runs locally — your research never leaves your machine." },
  { icon: Cpu, label: "Powered by local AI", desc: "Qwen 3, FinBERT & embeddings — no expensive subscriptions." },
  { icon: Zap, label: "Optional cloud speed", desc: "Plug in a free Groq key for 10× faster generation when online." },
  { icon: ShieldCheck, label: "100% free & open", desc: "Works with zero paid API keys. Yours to run and extend." },
];

export default function LandingPage() {
  const [loggedIn, setLoggedIn] = useState(false);
  useEffect(() => setLoggedIn(!!getToken()), []);

  const primaryHref = loggedIn ? "/dashboard" : "/register";
  const primaryLabel = loggedIn ? "Open Terminal" : "Get Started Free";

  return (
    <div className="min-h-screen bg-terminal-bg text-terminal-text">
      {/* Nav */}
      <header className="sticky top-0 z-20 border-b border-terminal-border bg-terminal-bg/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="pulse-dot h-2.5 w-2.5 rounded-full bg-terminal-amber" />
            <span className="font-mono text-sm font-bold tracking-tight">AI&nbsp;TERMINAL</span>
          </div>
          <nav className="flex items-center gap-3 text-sm">
            <Link href="/login" className="text-terminal-muted hover:text-terminal-text">
              Sign in
            </Link>
            <Link
              href={primaryHref}
              className="rounded bg-terminal-amber px-4 py-2 font-semibold text-black hover:opacity-90"
            >
              {primaryLabel}
            </Link>
          </nav>
        </div>
      </header>

      {/* Ticker tape */}
      <div className="overflow-hidden border-b border-terminal-border bg-terminal-panel py-2">
        <div className="marquee flex w-max gap-8 whitespace-nowrap font-mono text-xs">
          {[...TICKER_TAPE, ...TICKER_TAPE].map(([sym, chg, up], i) => (
            <span key={i} className="flex items-center gap-2">
              <span className="text-terminal-muted">{sym}</span>
              <span className={up ? "text-terminal-green" : "text-terminal-red"}>{chg}</span>
            </span>
          ))}
        </div>
      </div>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="grid-bg hero-glow absolute inset-0" />
        <div className="relative mx-auto max-w-6xl px-6 pb-20 pt-20 text-center">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-terminal-border bg-terminal-panel px-3 py-1 text-xs text-terminal-muted">
            <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-terminal-green" />
            Local-first AI · No data leaves your machine
          </div>
          <h1 className="mx-auto max-w-3xl text-4xl font-bold leading-tight md:text-6xl">
            The <span className="gradient-text">AI Bloomberg Terminal</span> for everyone
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-base text-terminal-muted md:text-lg">
            Professional-grade financial research — live market data, AI sentiment,
            document Q&A, and a team of AI analysts — running free on your own computer.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link
              href={primaryHref}
              className="inline-flex items-center gap-2 rounded bg-terminal-amber px-6 py-3 font-semibold text-black hover:opacity-90"
            >
              {primaryLabel} <ArrowRight size={18} />
            </Link>
            <Link
              href="/login"
              className="rounded border border-terminal-border px-6 py-3 font-semibold text-terminal-text hover:border-terminal-amber"
            >
              Sign in
            </Link>
          </div>

          {/* Terminal mockup */}
          <div className="mx-auto mt-14 max-w-3xl">
            <TerminalMock />
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="mb-10 text-center">
          <h2 className="text-2xl font-bold md:text-3xl">Everything in one terminal</h2>
          <p className="mt-2 text-terminal-muted">Twelve integrated modules, from raw data to AI verdict.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div
              key={title}
              className="panel group p-5 transition-colors hover:border-terminal-amber/50"
            >
              <Icon size={22} className="mb-3 text-terminal-amber" />
              <h3 className="mb-1 font-semibold">{title}</h3>
              <p className="text-sm text-terminal-muted">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-terminal-border bg-terminal-panel/40">
        <div className="mx-auto max-w-6xl px-6 py-16">
          <div className="mb-10 text-center">
            <h2 className="text-2xl font-bold md:text-3xl">How it works</h2>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              { n: "01", t: "Search a company", d: "Type a ticker like AAPL. Get price, financials and news instantly." },
              { n: "02", t: "Let the AI dig in", d: "Read filings, score sentiment, and run a team of analysts on the name." },
              { n: "03", t: "Decide with confidence", d: "Get a clear research report and a Buy/Hold/Sell memo, export to PDF." },
            ].map((s) => (
              <div key={s.n} className="panel p-6">
                <div className="font-mono text-3xl font-bold text-terminal-amber/30">{s.n}</div>
                <h3 className="mt-2 font-semibold">{s.t}</h3>
                <p className="mt-1 text-sm text-terminal-muted">{s.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust / AI */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {TRUST.map(({ icon: Icon, label, desc }) => (
            <div key={label} className="text-center">
              <div className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-full border border-terminal-border bg-terminal-panel">
                <Icon size={18} className="text-terminal-amber" />
              </div>
              <h3 className="font-semibold">{label}</h3>
              <p className="mt-1 text-sm text-terminal-muted">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-3xl px-6 pb-20 text-center">
        <div className="panel hero-glow relative overflow-hidden p-10">
          <h2 className="text-2xl font-bold md:text-3xl">Start your research in seconds</h2>
          <p className="mx-auto mt-3 max-w-md text-terminal-muted">
            Free, private and runs on your machine. No credit card, no subscriptions.
          </p>
          <Link
            href={primaryHref}
            className="mt-6 inline-flex items-center gap-2 rounded bg-terminal-amber px-6 py-3 font-semibold text-black hover:opacity-90"
          >
            {primaryLabel} <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-terminal-border">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-6 py-6 text-xs text-terminal-muted md:flex-row">
          <div className="flex items-center gap-2">
            <div className="h-1.5 w-1.5 rounded-full bg-terminal-amber" />
            <span className="font-mono">AI BLOOMBERG TERMINAL</span>
          </div>
          <p>For educational use only · Not financial advice</p>
        </div>
      </footer>
    </div>
  );
}

/** A static, styled mock of the stock page to showcase the UI. */
function TerminalMock() {
  return (
    <div className="panel overflow-hidden text-left shadow-2xl">
      <div className="flex items-center gap-2 border-b border-terminal-border bg-terminal-panel px-4 py-2">
        <span className="h-2.5 w-2.5 rounded-full bg-terminal-red/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-terminal-amber/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-terminal-green/70" />
        <span className="ml-3 font-mono text-xs text-terminal-muted">stocks/AAPL</span>
      </div>
      <div className="bg-terminal-bg p-5">
        <div className="flex items-baseline justify-between">
          <div>
            <div className="font-mono text-2xl font-bold text-terminal-amber">AAPL</div>
            <div className="text-xs text-terminal-muted">Apple Inc.</div>
          </div>
          <div className="text-right">
            <div className="font-mono text-2xl">$290.55</div>
            <div className="font-mono text-sm text-terminal-red">-3.64%</div>
          </div>
        </div>

        {/* faux chart */}
        <svg viewBox="0 0 400 90" className="mt-4 w-full" preserveAspectRatio="none">
          <defs>
            <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22c55e" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#22c55e" stopOpacity="0" />
            </linearGradient>
          </defs>
          <polyline
            points="0,70 40,60 80,65 120,45 160,50 200,35 240,40 280,25 320,30 360,18 400,22"
            fill="none"
            stroke="#22c55e"
            strokeWidth="1.5"
          />
          <polygon
            points="0,70 40,60 80,65 120,45 160,50 200,35 240,40 280,25 320,30 360,18 400,22 400,90 0,90"
            fill="url(#g)"
          />
        </svg>

        <div className="mt-4 grid grid-cols-4 gap-2 text-center">
          {[
            ["Mkt Cap", "$4.27T"],
            ["P/E", "35.18"],
            ["EPS", "8.26"],
            ["52W H", "$317.40"],
          ].map(([l, v]) => (
            <div key={l} className="rounded border border-terminal-border bg-terminal-panel p-2">
              <div className="stat-label">{l}</div>
              <div className="font-mono text-sm">{v}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
