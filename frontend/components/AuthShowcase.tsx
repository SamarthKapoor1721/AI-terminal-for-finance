import Link from "next/link";
import { Check, TrendingUp, TrendingDown } from "lucide-react";

const BULLETS = [
  "Live market data, financials & interactive charts",
  "AI news sentiment with FinBERT",
  "Ask questions of SEC filings (RAG)",
  "A team of AI analysts → investment memo",
];

const MINI_TAPE = [
  ["AAPL", "290.55", "-3.6%", false],
  ["NVDA", "208.19", "+2.1%", true],
  ["MSFT", "418.30", "+0.6%", true],
] as const;

/** Branded left panel shared by the login & register screens. */
export function AuthShowcase() {
  return (
    <div className="relative hidden overflow-hidden border-r border-terminal-border bg-terminal-panel/40 lg:flex lg:w-1/2 lg:flex-col">
      <div className="grid-bg hero-glow absolute inset-0" />

      <div className="relative flex h-full flex-col justify-between p-12">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 w-fit">
          <div className="pulse-dot h-2.5 w-2.5 rounded-full bg-terminal-amber" />
          <span className="font-mono text-sm font-bold tracking-tight">AI&nbsp;TERMINAL</span>
        </Link>

        {/* Pitch */}
        <div>
          <h2 className="max-w-md text-3xl font-bold leading-tight">
            The <span className="gradient-text">AI Bloomberg Terminal</span> for everyone
          </h2>
          <ul className="mt-6 space-y-3">
            {BULLETS.map((b) => (
              <li key={b} className="flex items-start gap-2 text-sm text-terminal-text/85">
                <Check size={16} className="mt-0.5 shrink-0 text-terminal-green" />
                {b}
              </li>
            ))}
          </ul>

          {/* Mini live-style quote panel */}
          <div className="panel mt-8 max-w-sm p-4">
            <div className="stat-label mb-2">Watchlist</div>
            <div className="space-y-2 font-mono text-sm">
              {MINI_TAPE.map(([sym, px, chg, up]) => (
                <div key={sym} className="flex items-center justify-between">
                  <span className="text-terminal-amber">{sym}</span>
                  <span className="text-terminal-muted">${px}</span>
                  <span
                    className={`flex items-center gap-1 ${
                      up ? "text-terminal-green" : "text-terminal-red"
                    }`}
                  >
                    {up ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
                    {chg}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <p className="text-xs text-terminal-muted">
          Local-first AI · Your research never leaves your machine
        </p>
      </div>
    </div>
  );
}
