"use client";

import { AppShell } from "@/components/AppShell";
import { useAuth } from "@/lib/auth";

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <AppShell>
      <h1 className="mb-6 page-title">Settings</h1>

      <div className="panel max-w-lg space-y-4 p-6">
        <h2 className="text-sm font-semibold">Profile</h2>
        <Row label="Name" value={user?.name ?? "—"} />
        <Row label="Email" value={user?.email ?? "—"} />
        <Row
          label="Member since"
          value={user?.created_at?.slice(0, 10) ?? "—"}
        />
      </div>
    </AppShell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-terminal-border pb-2">
      <span className="text-sm text-terminal-muted">{label}</span>
      <span className="font-mono text-sm">{value}</span>
    </div>
  );
}
