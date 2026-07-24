"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

export function TickerSearch({ placeholder = "Search ticker (AAPL, TSLA, NVDA…)" }) {
  const [q, setQ] = useState("");
  const router = useRouter();

  function go(e: React.FormEvent) {
    e.preventDefault();
    const t = q.trim().toUpperCase();
    if (t) router.push(`/stocks/${t}`);
  }

  return (
    <form onSubmit={go} className="relative">
      <Search
        size={16}
        className="absolute left-3 top-1/2 -translate-y-1/2 text-terminal-muted"
      />
      <input
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded border border-terminal-border bg-terminal-panel py-2 pl-9 pr-3 text-sm uppercase outline-none focus:border-terminal-amber"
      />
    </form>
  );
}
