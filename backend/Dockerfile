# syntax=docker/dockerfile:1

# --- Stage 1: build wheels + models (has compilers, dropped from final) ---
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# The cache mount keeps downloaded wheels (~2GB: torch, spacy, …) on the host
# between builds, so re-running this layer resolves from disk, not the network.
# The cpu wheel index keeps torch CUDA-free on x86 builds (no-op on arm64).
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# spaCy NER model for geo risk heatmap (must be baked in at build time)
RUN python -m spacy download en_core_web_sm

# --- Stage 2: runtime (no build-essential: ~400MB lighter) ---
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps (incl. console scripts like uvicorn/celery) from the builder
COPY --from=builder /usr/local /usr/local

WORKDIR /app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
