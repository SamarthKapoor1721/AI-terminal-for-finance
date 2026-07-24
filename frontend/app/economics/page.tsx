"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AppShell } from "@/components/AppShell";
import { api, type EconomicsResponse, type EconomicsSeries } from "@/lib/api";

type Point = { date: string; value: number | null };
type RangeKey = "1Y" | "5Y" | "Max";
const RANGE_YEARS: Record<RangeKey, number> = { "1Y": 1, "5Y": 5, Max: 100 };

// Series featured in the headline strip, in display order.
const HEADLINE = ["CPIAUCSL", "FEDFUNDS", "GDPC1", "UNRATE"];

/** Year-over-year % change, matched by date so it works for any frequency. */
function toYoY(points: Point[]): Point[] {
  return points.map((p, i) => {
    if (p.value == null) return { date: p.date, value: null };
    const target = new Date(p.date);
    target.setFullYear(target.getFullYear() - 1);
    let base: Point | null = null;
    for (let j = i - 1; j >= 0; j--) {
      if (points[j].value == null) continue;
      if (new Date(points[j].date) <= target) {
        base = points[j];
        break;
      }
    }
    const v0 = base?.value ?? null;
    return {
      date: p.date,
      value: v0 ? (p.value / v0 - 1) * 100 : null,
    };
  });
}

function filterRange(points: Point[], years: number): Point[] {
  if (years >= 100) return points;
  const cutoff = new Date();
  cutoff.setFullYear(cutoff.getFullYear() - years);
  return points.filter((p) => new Date(p.date) >= cutoff);
}

function lastValid(points: Point[]): Point | null {
  for (let i = points.length - 1; i >= 0; i--) {
    if (points[i].value != null) return points[i];
  }
  return null;
}

function fmtVal(v: number | null | undefined, suffix = ""): string {
  if (v == null) return "—";
  return `${v.toFixed(2)}${suffix}`;
}

export default function EconomicsPage() {
  const [data, setData] = useState<EconomicsResponse | null>(null);

  useEffect(() => {
    api.economics().then(setData).catch(() => setData({ available: false, series: [] }));
  }, []);

  const seriesById = useMemo(
    () => Object.fromEntries((data?.series ?? []).map((s) => [s.series_id, s])),
    [data]
  );

  return (
    <AppShell>
      <h1 className="mb-1 page-title">Economic Indicators</h1>
      <p className="mb-6 text-sm text-terminal-muted">
        Inflation, rates, growth and the labor market — live from the FRED API.
      </p>

      {data && !data.available && (
        <div className="panel mb-6 p-4 text-sm text-terminal-muted">
          FRED not connected. Add a free{" "}
          <code className="text-terminal-amber">FRED_API_KEY</code> to{" "}
          <code>.env</code> and restart the backend to populate these charts.
          (Get one at fred.stlouisfed.org)
        </div>
      )}

      {data?.available && (
        <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {HEADLINE.map((id) => {
            const s = seriesById[id];
            if (!s) return null;
            return <HeadlineTile key={id} series={s} />;
          })}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {(data?.series ?? []).map((s) => (
          <SeriesCard key={s.series_id} series={s} />
        ))}

        {data && !data.available &&
          ["Inflation (CPI)", "Fed Funds Rate", "Real GDP", "Unemployment"].map((label) => (
            <div key={label} className="panel p-4">
              <div className="stat-label">{label}</div>
              <div className="mt-4 flex h-32 items-center justify-center rounded border border-dashed border-terminal-border text-xs text-terminal-muted">
                Connect FRED to populate
              </div>
            </div>
          ))}
      </div>
    </AppShell>
  );
}

function HeadlineTile({ series }: { series: EconomicsSeries }) {
  const useYoY = series.yoy_default;
  const pts = useYoY ? toYoY(series.points) : series.points;
  const last = lastValid(pts);
  const prev = (() => {
    const idx = pts.findIndex((p) => p === last);
    for (let i = idx - 1; i >= 0; i--) if (pts[i].value != null) return pts[i];
    return null;
  })();
  const delta = last?.value != null && prev?.value != null ? last.value - prev.value : null;
  const suffix = useYoY ? "%" : series.units === "%" ? "%" : "";

  return (
    <div className="panel p-4">
      <div className="stat-label">
        {series.label}
        {useYoY && <span className="ml-1 normal-case text-terminal-muted/60">YoY</span>}
      </div>
      <div className="mt-1.5 flex items-baseline gap-2">
        <span className="stat-value text-terminal-amber">{fmtVal(last?.value, suffix)}</span>
        {delta != null && (
          <span className="font-mono text-xs text-terminal-muted">
            {delta >= 0 ? "▲" : "▼"} {Math.abs(delta).toFixed(2)}
          </span>
        )}
      </div>
      <div className="mt-1 text-[11px] text-terminal-muted">
        as of {last?.date ?? "—"}
      </div>
    </div>
  );
}

function SeriesCard({ series }: { series: EconomicsSeries }) {
  const [yoy, setYoy] = useState(!!series.yoy_default);
  const [range, setRange] = useState<RangeKey>("5Y");
  const canToggle = series.units === "index" || series.units === "$B" || series.units === "$M";

  const points = useMemo(() => {
    const transformed = yoy ? toYoY(series.points) : series.points;
    return filterRange(transformed, RANGE_YEARS[range]);
  }, [series.points, yoy, range]);

  const last = lastValid(points);
  const suffix = yoy ? "%" : series.units === "%" ? "%" : "";

  return (
    <div className="panel p-4">
      <div className="mb-3 flex items-start justify-between gap-2">
        <div>
          <div className="text-sm font-medium text-terminal-text">{series.label}</div>
          <div className="font-mono text-[11px] text-terminal-muted">
            {series.series_id} · updated {last?.date ?? "—"}
          </div>
        </div>
        <div className="text-right">
          <div className="font-mono text-xl text-terminal-amber">
            {fmtVal(last?.value, suffix)}
          </div>
          <div className="text-[11px] text-terminal-muted">
            {yoy ? "% YoY" : series.units}
          </div>
        </div>
      </div>

      <div className="mb-2 flex items-center justify-between">
        {canToggle ? (
          <div className="flex gap-0.5 rounded-md bg-terminal-bg p-0.5 text-[11px]">
            <button
              onClick={() => setYoy(true)}
              className={`rounded px-2 py-0.5 transition-colors ${
                yoy ? "bg-terminal-amber text-black" : "text-terminal-muted hover:text-terminal-text"
              }`}
            >
              YoY %
            </button>
            <button
              onClick={() => setYoy(false)}
              className={`rounded px-2 py-0.5 transition-colors ${
                !yoy ? "bg-terminal-amber text-black" : "text-terminal-muted hover:text-terminal-text"
              }`}
            >
              Level
            </button>
          </div>
        ) : (
          <span />
        )}
        <div className="flex gap-0.5 rounded-md bg-terminal-bg p-0.5 text-[11px]">
          {(Object.keys(RANGE_YEARS) as RangeKey[]).map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={`rounded px-2 py-0.5 transition-colors ${
                range === r ? "bg-terminal-amber text-black" : "text-terminal-muted hover:text-terminal-text"
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={160}>
        <AreaChart data={points} margin={{ top: 4, right: 4, bottom: 0, left: -16 }}>
          <defs>
            <linearGradient id={`grad-${series.series_id}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ffb000" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#ffb000" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#26282e" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "#8b8f99", fontSize: 10 }}
            tickFormatter={(d: string) => d.slice(0, 4)}
            minTickGap={40}
            stroke="#26282e"
          />
          <YAxis
            tick={{ fill: "#8b8f99", fontSize: 10 }}
            width={44}
            domain={["auto", "auto"]}
            stroke="#26282e"
          />
          <Tooltip
            contentStyle={{
              background: "#121316",
              border: "1px solid #26282e",
              borderRadius: 6,
              fontSize: 12,
            }}
            labelStyle={{ color: "#8b8f99" }}
            formatter={(v: number) => [`${v.toFixed(2)}${suffix}`, yoy ? "YoY" : series.units]}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#ffb000"
            strokeWidth={1.5}
            fill={`url(#grad-${series.series_id})`}
            dot={false}
            connectNulls
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
