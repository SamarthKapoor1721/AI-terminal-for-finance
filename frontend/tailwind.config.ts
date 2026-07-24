import type { Config } from "tailwindcss";

// Bloomberg-inspired dark palette: near-black canvas, amber accents,
// terminal green/red for gains/losses.
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#0a0a0b",
          panel: "#121316",
          border: "#26282e",
          muted: "#8b8f99",
          text: "#e6e7ea",
          amber: "#ffb000",
          green: "#22c55e",
          red: "#ef4444",
          blue: "#3b82f6",
        },
      },
      fontFamily: {
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
