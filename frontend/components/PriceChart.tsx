"use client";

import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PricePoint } from "@/lib/api";

export function PriceChart({ points }: { points: PricePoint[] }) {
  const data = points.map((p) => ({ date: p.date, close: p.close }));
  const positive =
    data.length > 1 &&
    (data[data.length - 1].close ?? 0) >= (data[0].close ?? 0);
  const color = positive ? "#22c55e" : "#ef4444";

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.3} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis
          dataKey="date"
          tick={{ fill: "#8b8f99", fontSize: 11 }}
          minTickGap={40}
          stroke="#26282e"
        />
        <YAxis
          domain={["auto", "auto"]}
          tick={{ fill: "#8b8f99", fontSize: 11 }}
          stroke="#26282e"
          width={56}
          tickFormatter={(v) => `$${Number(v).toFixed(0)}`}
        />
        <Tooltip
          contentStyle={{
            background: "#121316",
            border: "1px solid #26282e",
            borderRadius: 6,
            fontSize: 12,
          }}
          labelStyle={{ color: "#8b8f99" }}
          formatter={(v) => [`$${Number(v).toFixed(2)}`, "Close"]}
        />
        <Area
          type="monotone"
          dataKey="close"
          stroke={color}
          strokeWidth={1.5}
          fill="url(#priceFill)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
