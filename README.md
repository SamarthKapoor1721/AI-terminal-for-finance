<div align="center">

# 📊 AI Bloomberg Terminal

### A professional-grade financial research platform that runs on your own computer — powered by local AI.

*Research any public company, read its financials in plain charts, gauge the mood of the news, ask an AI questions about official filings, build a portfolio, and get an AI-written investment memo — all for free, with no data leaving your machine.*

`Next.js 15` · `FastAPI` · `PostgreSQL` · `Local AI (Qwen 3 + FinBERT)` · `ChromaDB` · `Docker`

</div>

---

## 🧭 Table of Contents
1. [What is this? (in plain English)](#-what-is-this-in-plain-english)
2. [Who is it for?](#-who-is-it-for)
3. [What can you actually do with it?](#-what-can-you-actually-do-with-it)
4. [A tour of every page](#-a-tour-of-every-page)
5. [How the AI works (no jargon)](#-how-the-ai-works-no-jargon)
6. [Getting started](#-getting-started)
7. [Optional free upgrades (API keys)](#-optional-free-upgrades-api-keys)
8. [The technology, explained](#-the-technology-explained)
9. [Project structure](#-project-structure)
10. [Glossary for non-finance readers](#-glossary-for-non-finance-readers)
11. [Troubleshooting](#-troubleshooting)
12. [Disclaimer](#-disclaimer)

---

## 💡 What is this? (in plain English)

A **"Bloomberg Terminal"** is the famous, expensive software (think ~$25,000/year) that professional investors on Wall Street use to research companies and markets. It puts prices, company financials, news, and analytics all in one place.

**This project is a free, open version of that idea** — a website you run on your own laptop. You type in a company's ticker symbol (like `AAPL` for Apple or `TSLA` for Tesla) and it shows you everything you'd want to know to understand that company as an investment: its stock price, how much money it makes, whether the news is positive or negative, and more.

The twist: it has **Artificial Intelligence built in** that runs **locally on your computer** (no expensive cloud bills, no sending your data to anyone). The AI can read a company's 100-page official reports and answer your questions about them, write a full research report, and even simulate a *team of analysts* debating whether a stock is a good buy.

> **You do not need to be a finance expert to use it.** Every number comes with context, and this README explains the finance terms as we go (and there's a [glossary](#-glossary-for-non-finance-readers) at the bottom).

---

## 👥 Who is it for?

| You are… | You'll use it to… |
|---|---|
| 🧑‍🎓 **A curious beginner** | Learn how companies are valued, in a real tool, without paying anything |
| 💻 **A developer** | Study a full-stack app: Next.js + FastAPI + Postgres + local LLMs + RAG + multi-agent AI |
| 📈 **A retail investor** | Do real research on stocks you're considering, and track a portfolio |
| 🔬 **An AI/ML learner** | See FinBERT sentiment, embeddings, a vector database, and an agent system working together |

---

## 🚀 What can you actually do with it?

Here's the full feature list — each one explained simply.

### 1. 🔐 Your own private account
Sign up with an email and password. Your portfolios and uploaded documents are private to you. (Behind the scenes this uses secure password hashing and JWT tokens — standard login technology.)

### 2. 📈 Look up any stock
Type a ticker (`AAPL`, `MSFT`, `NVDA`, `TSLA`…) and instantly see:
- **Price** and today's change (green = up, red = down)
- **Market Cap** — the total value of the whole company
- **P/E Ratio** — roughly, how "expensive" the stock is relative to its profits
- **EPS** — how much profit the company makes per share
- **52-week high/low** — the highest and lowest price over the past year
- An **interactive price chart** you can switch between 1 month, 6 months, 1 year, 5 years

### 3. 📑 Read the financials as charts
Every public company must publish three core reports. We fetch them and calculate the important ratios for you:
- **Income Statement** — "How much did they sell and earn?"
- **Balance Sheet** — "What do they own vs. owe?"
- **Cash Flow Statement** — "How much real cash moved in and out?"
- Auto-calculated: **Revenue Growth**, **Profit Margins**, **Debt-to-Equity** (how much debt they carry), **Free Cash Flow** (spare cash after expenses).

### 4. 📰 See if the news is good or bad (AI sentiment)
We pull recent news headlines about the company and an AI model called **FinBERT** (trained specifically on financial language) labels each one **Positive**, **Negative**, or **Neutral**, with a confidence score. You get an at-a-glance "mood meter" for the company.

### 5. 🎙️ Analyze an earnings call
Four times a year, companies hold "earnings calls" where executives discuss results. Upload the transcript (PDF or TXT) and the AI extracts:
- **Growth mentions** and **Risk mentions**
- **Guidance changes** (when they raise/lower future expectations)
- An **Executive Confidence Score** and a **Risk Score** (0–100)
- A plain-English summary

### 6. 🤖 Ask an AI about official documents (RAG)
Upload a company's **annual report or SEC filing** (or pull one automatically from the government's free **SEC EDGAR** database), and then just *ask questions in plain English*:
> *"Summarize the main risks."*
> *"What did management say about growth?"*
> *"How has revenue changed?"*

The AI answers using **only the actual document** — so it won't make things up. (This technique is called **RAG**, explained [below](#-how-the-ai-works-no-jargon).)

### 7. 📄 Generate a full research report (and export to PDF)
Click one button and the AI writes a complete 8-section equity research report — Business Overview, Revenue Analysis, Profitability, News Sentiment, Risks, Opportunities, **Bull Case**, and **Bear Case** — then download it as a clean **PDF**.

### 8. 🧠 Get a "team of AI analysts" verdict (multi-agent)
This is the showpiece. Five specialist AI agents each research independently:
- **Financial Analyst** (the numbers) · **News Analyst** (the headlines) · **Risk Analyst** (what could go wrong) · **Macro Analyst** (the broader economy) · **Portfolio Analyst** (how it fits a portfolio)

Then a **Coordinator** combines their findings into a single **Investment Memo** with a clear **Buy / Hold / Sell** recommendation.

### 9. 💼 Build and track a portfolio
Add your holdings (ticker, quantity, price you paid). The app calculates:
- **Total value** and **gains/losses** (live)
- **Volatility** (how bumpy the ride is) and **Sharpe Ratio** (return earned per unit of risk)
- A pie chart of how your money is **allocated**

### 10. 🔍 Screen for stocks
Set filters like *"Revenue Growth > 20%, Debt-to-Equity < 0.5, Market Cap > $10B"* and get back a list of companies that match.

### 11. 🌍 Track the economy
A dashboard of the big-picture indicators that move all markets — **Inflation, Interest Rates, GDP, Unemployment** — with historical charts (via the free FRED government data API).

---

## 🖥️ A tour of every page

| Page | What you see |
|------|--------------|
| **Landing** (`/`) | The welcome page introducing the platform |
| **Dashboard** (`/dashboard`) | A live watchlist of popular stocks + a search bar |
| **Stock** (`/stocks/AAPL`) | Everything about one company: price, chart, ratios, news mood |
| **News** (`/news`) | Headlines color-coded by AI sentiment |
| **Portfolio** (`/portfolio`) | Your holdings, gains/losses, risk metrics, allocation pie |
| **Screener** (`/screener`) | Filter the market by your criteria |
| **Research** (`/research`) | Upload docs / pull SEC filings, then ask the AI questions |
| **Reports** (`/reports`) | Generate & download AI research reports as PDF |
| **AI Memo** (`/memo`) | Run the multi-agent analyst team |
| **Economics** (`/economics`) | Inflation, rates, GDP, unemployment charts |
| **Settings** (`/settings`) | Your profile |

The whole interface uses a **dark, Bloomberg-style theme** — black background, amber highlights, monospace numbers — so it looks and feels like a professional trading terminal.

---

## 🧠 How the AI works (no jargon)

This platform uses **four AI components, all running locally and free**:

1. **The Language Model (Qwen 3, via Ollama)** — the "brain" that writes reports, memos, and answers. Think of it as a private ChatGPT running on your machine. *(Optionally, you can plug in Groq's free cloud API to make it much faster — see below.)*

2. **FinBERT** — a smaller AI specialized in reading *financial* text and judging if it's positive or negative. It scores every news headline.

3. **Embeddings (bge-large)** — converts text into lists of numbers that capture *meaning*, so the computer can find which paragraphs of a 100-page document are relevant to your question.

4. **ChromaDB (a vector database)** — stores those number-lists and searches them lightning-fast.

**RAG, explained simply:** When you ask *"What are the risks?"*, the system (1) finds the most relevant paragraphs from your uploaded document using embeddings, then (2) hands *only those paragraphs* to the language model and says "answer using these." This stops the AI from inventing facts — it can only use what's actually in the document. **R**etrieval-**A**ugmented **G**eneration = "look it up first, then answer."

---

## 🏁 Getting started

### What you need installed
- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (runs everything in containers — you don't install Python/Postgres manually)
- **[Ollama](https://ollama.com)** (runs the local AI) — *optional but recommended for the AI features*

### Step-by-step

```bash
# 1. Go to the project folder
cd FInance

# 2. Create your settings file from the template
cp .env.example .env

# 3. (For AI features) start Ollama and download the AI model — one time
ollama serve &
ollama pull qwen3:8b

# 4. Start the whole platform (first run takes a few minutes to build)
docker compose up --build
```

### Open it
- 🌐 **The app:** http://localhost:3000
- 📖 **API documentation:** http://localhost:8000/docs
- 🔑 **Account:** open http://localhost:3000/register and create one (tables are created automatically on first boot)

> **First AI request is slow** because it downloads the FinBERT/embedding models (~1.5 GB, one time) and the local language model is CPU-bound. Everything else (prices, charts, portfolio) is instant.

### To stop it
```bash
docker compose down          # stop everything
docker compose down -v       # ...and also erase the database
```

---

## 🧾 Commands cheat sheet

### First-time setup
```bash
cd FInance                                  # 1. enter the project
cp .env.example .env                         # 2. create your config (once)
ollama serve &                               # 3. start local AI
ollama pull qwen3:8b                          #    download the model (once, ~5 GB)
docker compose up --build                     # 4. build + start everything
```
Then open **http://localhost:3000** and create an account at `/register`.

### Everyday use (after the first build)
| Goal | Command |
|------|---------|
| Start | `docker compose up` |
| Start in the background | `docker compose up -d` |
| Stop | `docker compose down` |
| Stop **and wipe the database** | `docker compose down -v` |
| See what's running | `docker compose ps` |
| Watch backend logs | `docker compose logs -f backend` |
| Watch frontend logs | `docker compose logs -f frontend` |
| Open a shell in the backend | `docker compose exec backend bash` |

### After changing things
| You changed… | Run this |
|--------------|----------|
| `.env` (e.g. added an API key) | `docker compose restart backend` |
| Python code in `backend/` | nothing — it auto-reloads |
| Frontend code in `frontend/` | nothing — it hot-reloads |
| `backend/requirements.txt` | `docker compose build backend && docker compose up -d --force-recreate backend` |
| `frontend/package.json` | `docker compose build frontend && docker compose up -d --force-recreate frontend` |

> **Tip:** use `docker compose up -d` to run it in the background so you get your terminal back, then `docker compose logs -f` to watch output when you need it.

---

## 🔓 Optional free upgrades (API keys)

**The platform works with zero API keys.** These free keys just make it faster or more reliable. Add any of them to your `.env` file and restart — the app automatically uses them, and falls back gracefully if they're missing.

| Key | Free? | What it improves | Get it |
|-----|:----:|------------------|--------|
| `GROQ_API_KEY` | ✅ | **Makes AI ~10× faster** (cloud LLM instead of local CPU). Auto-used when online, falls back to local Ollama when offline. | [console.groq.com](https://console.groq.com/keys) |
| `FINNHUB_API_KEY` | ✅ | More reliable stock quotes & news (avoids free-data rate limits) | [finnhub.io](https://finnhub.io/register) |
| `FMP_API_KEY` | ✅ | Cleaner financial statements | [FMP](https://site.financialmodelingprep.com) |
| `FRED_API_KEY` | ✅ | Real data on the Economics page | [FRED](https://fred.stlouisfed.org/docs/api/api_key.html) |
| *SEC EDGAR* | ✅ | Real company filings — **no key needed**, just an email in `SEC_USER_AGENT` | built-in |

**Smart LLM switching:** With `LLM_MODE=auto` (the default), the app uses **Groq when you're online** (fast) and **local Ollama when you're offline** (private, always works). Force either with `LLM_MODE=groq` or `LLM_MODE=ollama`.

---

## ⚙️ The technology, explained

| Layer | Tools | In plain terms |
|-------|-------|----------------|
| **Frontend** (what you see) | Next.js 15, React, TypeScript, Tailwind CSS, Recharts | The website and its charts |
| **Backend** (the engine) | FastAPI, Python 3.12, SQLAlchemy | Handles requests, talks to the database and AI |
| **Database** | PostgreSQL | Stores users, portfolios, news, documents |
| **Cache / jobs** | Redis, Celery | Background tasks & speed |
| **AI** | Ollama (Qwen 3), FinBERT, bge embeddings, ChromaDB | The intelligence layer |
| **Data** | yfinance, SEC EDGAR, FRED, Finnhub/FMP | Where the financial numbers come from |
| **Packaging** | Docker, Docker Compose | Runs it all with one command |

### Architecture at a glance
```
   You (browser)
        │
        ▼
  ┌───────────────┐      ┌──────────────────────┐     ┌─────────────┐
  │  Next.js 15   │ ───▶ │   FastAPI backend     │ ──▶ │ PostgreSQL  │
  │  (dark UI)    │      │   (Python)            │     │  + Redis    │
  └───────────────┘      └──────────┬───────────┘     └─────────────┘
                                    │
              ┌─────────────────────┼──────────────────────┐
              ▼                     ▼                       ▼
       FinBERT (mood)       ChromaDB + embeddings     Qwen 3 / Groq
                            (document search)          (writes answers)
```

---

## 📁 Project structure

```
FInance/
├── docker-compose.yml        # one command runs the whole stack
├── .env.example              # all configuration options (copy to .env)
├── backend/                  # FastAPI app (Python)
│   ├── app/
│   │   ├── main.py           # entry point
│   │   ├── core/             # config, database, security
│   │   ├── models/           # database tables
│   │   ├── schemas/          # request/response shapes
│   │   ├── api/routes/       # the API endpoints
│   │   └── services/         # the real logic:
│   │       ├── market_data, financials, news, sentiment
│   │       ├── portfolio, screener, economics
│   │       ├── rag, edgar, embeddings, vectorstore   # document AI
│   │       ├── reports, earnings, agents             # AI features
│   │       ├── llm.py        # smart Groq/Ollama switching
│   │       └── providers/    # swappable data sources (yfinance/Finnhub/FMP)
└── frontend/                 # Next.js app (TypeScript)
    ├── app/                  # one folder per page
    ├── components/           # reusable UI (sidebar, charts, cards)
    └── lib/                  # API client, auth, formatting
```

---

## 📘 Glossary for non-finance readers

| Term | Plain meaning |
|------|---------------|
| **Ticker** | A company's short stock-market code (Apple = `AAPL`) |
| **Market Cap** | Total value of the company = share price × number of shares |
| **P/E Ratio** | Price ÷ earnings. Higher = investors expect more growth (or it's pricey) |
| **EPS** | Earnings Per Share — profit divided by number of shares |
| **Revenue** | Total sales (the "top line") |
| **Margin** | What % of sales becomes profit |
| **Debt-to-Equity** | How much the company borrows vs. owns. Lower is usually safer |
| **Free Cash Flow** | Spare cash left after running and investing in the business |
| **Volatility** | How much a price swings up and down — a measure of risk |
| **Sharpe Ratio** | Return earned for each unit of risk taken (higher is better) |
| **Bull / Bear case** | The optimistic / pessimistic argument for a stock |
| **Sentiment** | Whether text (like news) is positive, negative, or neutral |
| **SEC filing** | Official reports companies must legally publish (e.g. 10-K = annual) |
| **LLM** | Large Language Model — the AI that understands and writes text |
| **RAG** | "Look it up, then answer" — AI grounded in real documents |
| **Embedding** | Turning text into numbers that capture meaning |

---

## 🩹 Troubleshooting

| Problem | Fix |
|---------|-----|
| `service "backend" is not running` | The build isn't finished — wait, or run `docker compose ps` to check |
| Stock prices show "—" or errors | Free data source (Yahoo) is rate-limiting; wait a moment and retry, or add a free `FINNHUB_API_KEY` |
| AI features say "LLM unavailable" | Start Ollama (`ollama serve`) and pull the model, **or** add a `GROQ_API_KEY` |
| Reports/memos are slow | Normal on CPU — add a free `GROQ_API_KEY` to make them ~10× faster |
| Economics page is empty | Add a free `FRED_API_KEY` to `.env` and restart the backend |

---

## ⚠️ Disclaimer

This software is for **educational and research purposes only**. It is **not financial advice**. The data comes from free third-party sources and may be delayed or inaccurate. AI-generated reports and memos can be wrong. **Always do your own research and consult a licensed professional before investing.**

---

<div align="center">

**Built with local-first AI — your research stays on your machine.**

</div>
