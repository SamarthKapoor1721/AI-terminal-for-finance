"use client";

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

export function AuthField({
  label,
  type,
  value,
  onChange,
  placeholder,
  minLength,
  autoComplete,
}: {
  label: string;
  type: "text" | "email" | "password";
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  minLength?: number;
  autoComplete?: string;
}) {
  const [show, setShow] = useState(false);
  const isPassword = type === "password";
  const inputType = isPassword && show ? "text" : type;

  return (
    <label className="block">
      <span className="stat-label">{label}</span>
      <div className="relative mt-1">
        <input
          type={inputType}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          minLength={minLength}
          autoComplete={autoComplete}
          required
          className="w-full rounded-md border border-terminal-border bg-terminal-bg px-3 py-2.5 text-sm outline-none transition-colors focus:border-terminal-amber focus:ring-1 focus:ring-terminal-amber/40"
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShow((s) => !s)}
            tabIndex={-1}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-terminal-muted hover:text-terminal-text"
            aria-label={show ? "Hide password" : "Show password"}
          >
            {show ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        )}
      </div>
    </label>
  );
}
