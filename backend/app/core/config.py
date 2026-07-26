from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Postgres
    POSTGRES_USER: str = "finance"
    POSTGRES_PASSWORD: str = "finance"
    POSTGRES_DB: str = "finance"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI — LLM backend.
    #   LLM_MODE = "auto"   -> Groq if a key is set AND Groq is reachable (online),
    #                          else local Ollama (offline-friendly). [default]
    #   LLM_MODE = "groq"   -> force Groq
    #   LLM_MODE = "ollama" -> force local Ollama
    LLM_MODE: str = "auto"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # AI — embeddings + sentiment
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"
    FINBERT_MODEL: str = "ProsusAI/finbert"

    # Vector store
    CHROMA_PATH: str = "./data/chroma"

    # Economic data
    FRED_API_KEY: str = ""

    # Optional data providers (free tiers). Empty => use free yfinance fallback.
    FINNHUB_API_KEY: str = ""
    FMP_API_KEY: str = ""

    # SEC EDGAR requires a descriptive User-Agent (no key). Set to your email.
    SEC_USER_AGENT: str = "AI Bloomberg Terminal contact@example.com"

    # CORS. Comma-separated string in env, e.g.
    # "https://my-app.vercel.app,https://foo.com". Kept as a plain str field
    # (not list[str]) because pydantic-settings tries json.loads() on complex
    # env fields before any validator runs, which breaks on a bare comma list.
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def sqlalchemy_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
