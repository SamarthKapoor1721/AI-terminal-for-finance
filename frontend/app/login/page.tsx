"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, AlertCircle } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { AuthShowcase } from "@/components/AuthShowcase";
import { AuthField } from "@/components/AuthField";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen bg-terminal-bg">
      <AuthShowcase />

      {/* Form side */}
      <div className="flex w-full items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-sm">
          {/* mobile logo */}
          <Link href="/" className="mb-8 flex items-center gap-2 lg:hidden">
            <div className="pulse-dot h-2.5 w-2.5 rounded-full bg-terminal-amber" />
            <span className="font-mono text-sm font-bold tracking-tight">AI TERMINAL</span>
          </Link>

          <h1 className="text-2xl font-bold">Welcome back</h1>
          <p className="mt-1 text-sm text-terminal-muted">
            Sign in to your research terminal.
          </p>

          <form onSubmit={onSubmit} className="mt-8 space-y-4">
            <AuthField
              label="Email"
              type="email"
              value={email}
              onChange={setEmail}
              placeholder="you@example.com"
              autoComplete="email"
            />
            <AuthField
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              placeholder="••••••••"
              autoComplete="current-password"
            />

            {error && (
              <div className="flex items-center gap-2 rounded-md border border-terminal-red/40 bg-terminal-red/10 px-3 py-2 text-sm text-terminal-red">
                <AlertCircle size={15} /> {error}
              </div>
            )}

            <button
              type="submit"
              disabled={busy}
              className="flex w-full items-center justify-center gap-2 rounded-md bg-terminal-amber py-2.5 text-sm font-semibold text-black transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {busy ? "Signing in…" : "Sign in"}
              {!busy && <ArrowRight size={16} />}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-terminal-muted">
            New here?{" "}
            <Link href="/register" className="font-medium text-terminal-amber hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
