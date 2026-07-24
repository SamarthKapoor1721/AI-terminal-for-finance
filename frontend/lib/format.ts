export function fmtNumber(n?: number | null, digits = 2): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function fmtCurrency(n?: number | null, currency = "USD"): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  });
}

export function fmtCompact(n?: number | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, {
    notation: "compact",
    maximumFractionDigits: 2,
  });
}

const CURRENCY_SYMBOL: Record<string, string> = {
  USD: "$",
  INR: "₹",
  EUR: "€",
  GBP: "£",
  JPY: "¥",
};

export function currencySymbol(currency?: string | null): string {
  return CURRENCY_SYMBOL[currency ?? "USD"] ?? "";
}

/** Compact number with a currency symbol prefix (e.g. ₹17.2T, $4.27T). */
export function fmtCompactCur(n?: number | null, currency?: string | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return `${currencySymbol(currency)}${fmtCompact(n)}`;
}

export function fmtPercent(n?: number | null): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}%`;
}

// Maps score [-1, 1] to a hex color interpolating red → gray → green
// using the terminal palette: red=#ef4444, neutral=#26282e, green=#22c55e.
export function sentimentColor(score: number): string {
  if (score > 0.1) {
    const t = Math.min(score / 0.6, 1); // 0→1 as score goes 0.1→0.6
    return interpolateColor("#26282e", "#22c55e", t);
  } else if (score < -0.1) {
    const t = Math.min(Math.abs(score) / 0.6, 1);
    return interpolateColor("#26282e", "#ef4444", t);
  }
  return "#26282e"; // neutral
}

function interpolateColor(c1: string, c2: string, t: number): string {
  const r1 = parseInt(c1.slice(1, 3), 16), g1 = parseInt(c1.slice(3, 5), 16), b1 = parseInt(c1.slice(5, 7), 16);
  const r2 = parseInt(c2.slice(1, 3), 16), g2 = parseInt(c2.slice(3, 5), 16), b2 = parseInt(c2.slice(5, 7), 16);
  const r = Math.round(r1 + (r2 - r1) * t).toString(16).padStart(2, "0");
  const g = Math.round(g1 + (g2 - g1) * t).toString(16).padStart(2, "0");
  const b = Math.round(b1 + (b2 - b1) * t).toString(16).padStart(2, "0");
  return `#${r}${g}${b}`;
}

export function changeColor(n?: number | null): string {
  if (n === null || n === undefined) return "text-terminal-muted";
  if (n > 0) return "text-terminal-green";
  if (n < 0) return "text-terminal-red";
  return "text-terminal-muted";
}
