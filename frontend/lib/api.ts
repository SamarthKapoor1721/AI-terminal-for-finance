// Thin typed client for the FastAPI backend. Token is kept in localStorage
// (fine for a local terminal; use httpOnly cookies for real deployments).

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/+$/, "");

const TOKEN_KEY = "abt_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (!(options.body instanceof FormData) && options.body) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export const api = {
  // --- auth ---
  register: (body: { email: string; name: string; password: string }) =>
    request<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  login: async (email: string, password: string) => {
    // OAuth2 password flow expects form-encoded username/password.
    const form = new URLSearchParams({ username: email, password });
    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new ApiError(res.status, data.detail || "Login failed");
    }
    return (await res.json()) as TokenResponse;
  },

  me: () => request<User>("/auth/me"),

  // --- market data ---
  stock: (ticker: string) => request<StockQuote>(`/stocks/${ticker}`),
  history: (ticker: string, period = "1y") =>
    request<PriceHistory>(`/stocks/${ticker}/history?period=${period}`),

  // --- financials ---
  financials: (ticker: string) =>
    request<FinancialsResponse>(`/financials/${ticker}`),

  // --- news ---
  news: (ticker: string, refresh = false) =>
    request<NewsArticle[]>(`/news/${ticker}?refresh=${refresh}`),
  sentiment: (ticker: string) =>
    request<SentimentSummary>(`/news/${ticker}/sentiment`),

  // --- portfolios ---
  portfolios: () => request<Portfolio[]>("/portfolios"),
  createPortfolio: (name: string) =>
    request<Portfolio>(`/portfolios?name=${encodeURIComponent(name)}`, {
      method: "POST",
    }),
  portfolio: (id: number) => request<PortfolioSummary>(`/portfolios/${id}`),
  addHolding: (
    id: number,
    body: { ticker: string; quantity: number; purchase_price: number }
  ) =>
    request(`/portfolios/${id}/holdings`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // --- screener ---
  screen: (body: Record<string, unknown>) =>
    request<{ count: number; results: ScreenResult[] }>("/screener", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // --- research / RAG ---
  ask: (question: string, ticker?: string) =>
    request<{ answer: string; sources: unknown[] }>("/research/ask", {
      method: "POST",
      body: JSON.stringify({ question, ticker }),
    }),
  filings: (ticker: string) =>
    request<{ ticker: string; filings: Filing[] }>(`/research/filings/${ticker}`),
  ingestFiling: (body: { ticker: string; url: string; form: string; date?: string }) =>
    request("/research/filings/ingest", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // --- reports (Phase 8) ---
  generateReport: (ticker: string) =>
    request<Report>("/reports", {
      method: "POST",
      body: JSON.stringify({ ticker }),
    }),
  reports: () => request<Report[]>("/reports"),

  // --- multi-agent (Phase 12) ---
  runAgents: (ticker: string, query: string) =>
    request<AgentResult>("/agents/research", {
      method: "POST",
      body: JSON.stringify({ ticker, query }),
    }),

  // --- economics (Phase 11) ---
  economics: () => request<EconomicsResponse>("/economics"),

  // --- geo risk heatmap ---
  geoHeatmap: (refresh = false) =>
    request<CountryRisk[]>(`/geo/heatmap?refresh=${refresh}`),
};

export interface Filing {
  form: string;
  accession: string;
  date: string;
  url: string;
  document: string;
}
export interface Report {
  id: number;
  ticker: string;
  title: string;
  content_md: string;
  created_at: string;
}
export interface AgentFinding {
  agent: string;
  summary: string;
}
export interface AgentResult {
  ticker: string;
  query: string;
  findings: AgentFinding[];
  memo: string;
  off_topic?: boolean;
}
export interface EconomicsSeries {
  label: string;
  series_id: string;
  units: string;
  frequency?: "daily" | "weekly" | "monthly" | "quarterly";
  yoy_default?: boolean;
  points: { date: string; value: number | null }[];
}
export interface EconomicsResponse {
  available: boolean;
  series: EconomicsSeries[];
}

export interface HeadlineMini {
  headline: string;
  url: string;
  source: string | null;
  ticker: string;
  sentiment_score: number | null;
}
export interface CountryRisk {
  iso2: string;
  name: string;
  score: number;
  article_count: number;
  headlines: HeadlineMini[];
}

// ---- types (mirror backend schemas) ----
export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}
export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}
export interface StockQuote {
  ticker: string;
  name?: string;
  price?: number;
  currency?: string;
  change?: number;
  change_percent?: number;
  market_cap?: number;
  pe_ratio?: number;
  eps?: number;
  volume?: number;
  week52_high?: number;
  week52_low?: number;
  sector?: string;
  industry?: string;
}
export interface PricePoint {
  date: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
}
export interface PriceHistory {
  ticker: string;
  period: string;
  interval: string;
  points: PricePoint[];
}
export interface StatementLine {
  label: string;
  values: Record<string, number | null>;
}
export interface FinancialStatement {
  name: string;
  periods: string[];
  lines: StatementLine[];
}
export interface FinancialsResponse {
  ticker: string;
  statements: FinancialStatement[];
  ratios: {
    revenue_growth?: number;
    gross_margin?: number;
    net_margin?: number;
    debt_to_equity?: number;
    free_cash_flow?: number;
  };
}
export interface NewsArticle {
  id: number;
  company_ticker: string;
  headline: string;
  source?: string;
  url: string;
  published_at?: string;
  sentiment?: string;
  sentiment_score?: number;
  confidence?: number;
}
export interface SentimentSummary {
  ticker: string;
  article_count: number;
  positive: number;
  negative: number;
  neutral: number;
  overall_score?: number;
}
export interface Portfolio {
  id: number;
  name: string;
  created_at: string;
}
export interface HoldingValuation {
  id: number;
  ticker: string;
  quantity: number;
  purchase_price: number;
  current_price?: number;
  cost_basis: number;
  market_value?: number;
  gain?: number;
  gain_percent?: number;
  weight?: number;
}
export interface PortfolioSummary {
  portfolio: Portfolio;
  holdings: HoldingValuation[];
  total_cost: number;
  total_value?: number;
  total_gain?: number;
  total_gain_percent?: number;
  volatility?: number;
  sharpe_ratio?: number;
}
export interface ScreenResult {
  ticker: string;
  name?: string;
  currency?: string;
  market_cap?: number;
  pe_ratio?: number;
  revenue_growth?: number;
  debt_to_equity?: number;
  sector?: string;
  industry?: string;
}
