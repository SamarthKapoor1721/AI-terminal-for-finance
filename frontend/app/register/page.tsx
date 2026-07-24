"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, AlertCircle } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { AuthShowcase } from "@/components/AuthShowcase";
import { AuthField } from "@/components/AuthField";

export default function RegisterPage() {
  const { register } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await register(email, name, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  const strength = passwordStrength(password);

  return (
    <div className="flex min-h-screen bg-terminal-bg">
      <AuthShowcase />

      <div className="flex w-full items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-sm">
          <Link href="/" className="mb-8 flex items-center gap-2 lg:hidden">
            <div className="pulse-dot h-2.5 w-2.5 rounded-full bg-terminal-amber" />
            <span className="font-mono text-sm font-bold tracking-tight">AI TERMINAL</span>
          </Link>

          <h1 className="text-2xl font-bold">Create your account</h1>
          <p className="mt-1 text-sm text-terminal-muted">
            Free forever. No credit card required.
          </p>

          <form onSubmit={onSubmit} className="mt-8 space-y-4">
            <AuthField label="Name" type="text" value={name} onChange={setName} placeholder="Jane Doe" autoComplete="name" />
            <AuthField label="Email" type="email" value={email} onChange={setEmail} placeholder="you@example.com" autoComplete="email" />
            <AuthField
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              placeholder="At least 8 characters"
              minLength={8}
              autoComplete="new-password"
            />

            {password.length > 0 && (
              <div className="flex items-center gap-2">
                <div className="flex flex-1 gap-1">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className={`h-1 flex-1 rounded-full ${
                        i < strength.level ? strength.color : "bg-terminal-border"
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs text-terminal-muted">{strength.label}</span>
              </div>
            )}

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
              {busy ? "Creating…" : "Create account"}
              {!busy && <ArrowRight size={16} />}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-terminal-muted">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-terminal-amber hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

function passwordStrength(pw: string): { level: number; label: string; color: string } {
  if (pw.length === 0) return { level: 0, label: "", color: "" };
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/\d/.test(pw) || /[^A-Za-z0-9]/.test(pw)) score++;
  if (score <= 1) return { level: 1, label: "Weak", color: "bg-terminal-red" };
  if (score === 2) return { level: 2, label: "Fair", color: "bg-terminal-amber" };
  return { level: 3, label: "Strong", color: "bg-terminal-green" };
}
