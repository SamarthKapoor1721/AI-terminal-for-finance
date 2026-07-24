"""LLM access with pluggable backend and online/offline auto-selection.

Backend selection (LLM_MODE=auto, the default):
  • online + GROQ_API_KEY set  -> Groq cloud (fast)        [when reachable]
  • offline / no key           -> local Ollama (Qwen 3)    [always available locally]

LLM_MODE can be forced to "groq" or "ollama". Groq reachability is probed at
most once per _REACHABLE_TTL seconds so it adds no per-call latency.

Used by RAG (Phase 7), reports (Phase 8), earnings (Phase 6) and the multi-agent
system (Phase 12). Returns a clear message if no backend is reachable.
"""

from __future__ import annotations

import logging
import time

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_REACHABLE_TTL = 60.0  # seconds to cache the Groq connectivity probe
_groq_probe = {"at": 0.0, "ok": False}


def _groq_reachable() -> bool:
    """True if a key is set and Groq responds (cached)."""
    if not settings.GROQ_API_KEY:
        return False
    now = time.time()
    if now - _groq_probe["at"] < _REACHABLE_TTL:
        return _groq_probe["ok"]
    ok = False
    try:
        with httpx.Client(timeout=3) as client:
            r = client.get(
                f"{settings.GROQ_BASE_URL}/models",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            )
            ok = r.status_code == 200
    except Exception:
        ok = False  # offline or unreachable -> fall back to local
    _groq_probe.update(at=now, ok=ok)
    return ok


def active_backend() -> str:
    """Resolve which backend a call would use right now."""
    mode = settings.LLM_MODE.lower()
    if mode == "groq":
        return "groq"
    if mode == "ollama":
        return "ollama"
    # auto: prefer Groq when online + configured, else local Ollama
    return "groq" if _groq_reachable() else "ollama"


def _generate_groq(prompt: str, system: str | None, temperature: float) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{settings.GROQ_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:300]
        logger.warning("Groq error %s: %s", exc.response.status_code, detail)
        return f"[LLM error] Groq returned {exc.response.status_code}: {detail}"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Groq unavailable: %s", exc)
        return f"[LLM unavailable] Could not reach Groq: {exc}"


def _generate_ollama(prompt: str, system: str | None, temperature: float) -> str:
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system
    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Ollama unavailable: %s", exc)
        return (
            "[LLM unavailable] Could not reach Ollama at "
            f"{settings.OLLAMA_BASE_URL}. Ensure Ollama is running and the model "
            f"'{settings.OLLAMA_MODEL}' is pulled, or set GROQ_API_KEY to use Groq."
        )


def generate(prompt: str, system: str | None = None, temperature: float = 0.2) -> str:
    """Single-shot completion via the auto-selected backend."""
    if active_backend() == "groq":
        return _generate_groq(prompt, system, temperature)
    return _generate_ollama(prompt, system, temperature)


def is_available() -> bool:
    if active_backend() == "groq":
        return True
    try:
        with httpx.Client(timeout=5) as client:
            return client.get(f"{settings.OLLAMA_BASE_URL}/api/tags").status_code == 200
    except Exception:
        return False
