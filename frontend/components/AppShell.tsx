"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Sidebar } from "./Sidebar";

/** Layout for authenticated pages: redirects to /login when no session. */
export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex h-screen items-center justify-center text-terminal-muted">
        <span className="text-sm">Loading terminal…</span>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-terminal-bg p-6">
        <div className="mx-auto max-w-6xl">{children}</div>
      </main>
    </div>
  );
}
