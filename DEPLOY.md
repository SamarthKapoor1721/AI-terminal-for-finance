# Deploying AI Terminal

## What deploys, and what doesn't

| Component | Deployable? | Notes |
|---|---|---|
| **FastAPI backend** | ✅ Yes | Needs ~3 GB RAM (FinBERT + bge-large models load into memory). This is the main constraint. |
| **Next.js frontend** | ✅ Yes | Static + SSR; deploys anywhere. `NEXT_PUBLIC_API_URL` must be set **at build time**. |
| **Postgres** | ✅ Yes | Managed (Neon/Supabase) or the compose container. |
| **LLM (Groq)** | ✅ Yes | `GROQ_API_KEY` already works. Set `LLM_MODE=groq` in prod. |
| **LLM (Ollama)** | ❌ No | Points at `host.docker.internal` — a local-only address. Use Groq in the cloud. |
| **Celery worker** | ⏭️ Dropped | Nothing in the code dispatches a task (no `.delay()` / `.apply_async`). Verified dead weight. |
| **Redis** | ⏭️ Dropped | Only existed for Celery. Not needed. |
| **ChromaDB (RAG)** | ⚠️ Partial | Persists to local disk. Fine on a VPS volume; **ephemeral on free HF Spaces** (re-ingest filings after a rebuild). |
| **yfinance quotes** | ⚠️ Flaky | Rate-limited from datacenter IPs. Finnhub key is set and tried first, so mostly OK with the occasional 429 fallback. |

---

## Option A — Free (Vercel + Hugging Face Spaces + Neon)

Best for a demo/portfolio. $0, no credit card. Caveat: the free Space **sleeps after ~48 h idle** and cold-starts in ~1–2 min.

### 1. Database — Neon (free)
1. Create a project at neon.tech → copy the connection string.
2. Convert the driver prefix: `postgresql://…` → `postgresql+psycopg://…`
   Keep it for `DATABASE_URL` below.

### 2. Backend — Hugging Face Spaces (free, 16 GB RAM)
1. Push this repo to GitHub (`git remote add origin … && git push -u origin main`).
2. Create a new **Space** → SDK: **Docker** → **Blank**.
3. In the Space, point it at `backend/Dockerfile.hf` (rename it to `Dockerfile`, or set it as the Dockerfile path). It listens on port **7860** as HF requires.
4. Space **Settings → Secrets**, add:
   ```
   DATABASE_URL       = postgresql+psycopg://…   (from Neon)
   SECRET_KEY         = <a long random string — do NOT reuse the dev one>
   LLM_MODE           = groq
   GROQ_API_KEY       = <your key>
   FRED_API_KEY       = <your key>
   FINNHUB_API_KEY    = <your key>
   CORS_ORIGINS       = https://<your-app>.vercel.app
   SEC_USER_AGENT     = AI Terminal you@email.com
   ```
5. The Space builds and gives you a URL like `https://<user>-<space>.hf.space`. That's your API base.

### 3. Frontend — Vercel (free)
1. vercel.com → New Project → import the GitHub repo → **Root Directory: `frontend`**.
2. Environment variable:
   ```
   NEXT_PUBLIC_API_URL = https://<user>-<space>.hf.space
   ```
3. Deploy. Copy the resulting `https://<your-app>.vercel.app` back into the Space's `CORS_ORIGINS` secret and restart the Space.

Done. Open the Vercel URL, log in with the demo account after seeding (below).

---

## Option B — Always-on VPS (Oracle Always-Free, Hetzner, DigitalOcean)

Best if you don't want sleeping. Oracle's Always-Free ARM VM (4 cores / 24 GB RAM) runs this for $0 forever (needs a card for identity check). Files provided: `docker-compose.prod.yml`, `backend/Dockerfile`, `frontend/Dockerfile.prod`, `Caddyfile`.

1. Point two DNS records at the server: `app.yourdomain.com` and `api.yourdomain.com`.
2. Edit **`Caddyfile`** — replace the two example domains.
3. Create **`.env`** on the server (copy `.env.example`) and set: strong `POSTGRES_PASSWORD`, `SECRET_KEY`, `LLM_MODE=groq`, `GROQ_API_KEY`, `FRED_API_KEY`, `FINNHUB_API_KEY`, `CORS_ORIGINS=https://app.yourdomain.com`, and `PUBLIC_API_URL=https://api.yourdomain.com`.
4. Deploy:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
   Caddy fetches HTTPS certs automatically.

---

## After first deploy (either option)

Seed the demo user against the production DB:
```bash
# Option A: run locally with DATABASE_URL pointed at Neon
# Option B: docker compose -f docker-compose.prod.yml exec backend python -m scripts.seed
```
Login: `demo@terminal.ai` / `demo12345` (change it for anything public).

## Security checklist before going public
- [ ] `SECRET_KEY` is a fresh long random string (not the dev value)
- [ ] `CORS_ORIGINS` is your real frontend domain, not `*` or localhost
- [ ] DB password is strong (VPS) / DB is the managed instance (free)
- [ ] Consider disabling `/docs` or the open `register` endpoint for a public demo
