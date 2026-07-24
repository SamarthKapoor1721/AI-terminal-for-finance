export function StatCard({
  label,
  value,
  sub,
  accent,
}: {
  label: string;
  value: string;
  sub?: string;
  accent?: string;
}) {
  return (
    <div className="panel p-4">
      <div className="stat-label">{label}</div>
      <div className={`stat-value mt-1.5 ${accent ?? ""}`}>{value}</div>
      {sub && <div className="mt-1 text-xs text-terminal-muted">{sub}</div>}
    </div>
  );
}
