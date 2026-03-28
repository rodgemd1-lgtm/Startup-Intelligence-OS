"""Ollama Client — local LLM inference via Ollama on M5 Max.

Zero-cost inference for background tasks, formatting, embed prep.
Optimized for Apple Silicon M5 Max with 48GB unified memory.

Qwen2.5-Coder:32b uses ~20GB RAM, leaving ~28GB for OS + other apps.
Metal GPU acceleration is automatic on Apple Silicon.
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
# Default model — set OLLAMA_MODEL env var to override per machine:
#   M4 Pro 24GB:  OLLAMA_MODEL=qwen2.5-coder:14b  (uses ~9GB)
#   M5 Max 48GB:  OLLAMA_MODEL=qwen2.5-coder:32b  (uses ~20GB)
OLLAMA_DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:14b")


@dataclass
class OllamaResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    cost_usd: float = 0.0  # always zero — local inference


def is_ollama_running() -> bool:
    """Check if Ollama is running and responsive."""
    try:
        resp = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def has_model(model: str = OLLAMA_DEFAULT_MODEL) -> bool:
    """Check if the specified model is pulled and available."""
    try:
        resp = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2.0)
        if resp.status_code != 200:
            return False
        models = resp.json().get("models", [])
        return any(m.get("name", "").startswith(model.split(":")[0]) for m in models)
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


class OllamaClient:
    """Thin wrapper around Ollama's HTTP API for local inference."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_DEFAULT_MODEL):
        self.base_url = base_url
        self.model = model
        self._client = httpx.Client(base_url=base_url, timeout=120.0)

    def chat(
        self,
        messages: list[dict],
        system: str = "",
        model: str | None = None,
        max_tokens: int = 8192,
    ) -> OllamaResponse:
        """Send a chat completion request to Ollama."""
        model = model or self.model

        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "num_gpu": 99,  # use all GPU layers (Metal on M5 Max)
            },
        }

        if system:
            payload["messages"] = [{"role": "system", "content": system}] + messages

        start = time.time()
        resp = self._client.post("/api/chat", json=payload)
        duration_ms = int((time.time() - start) * 1000)

        resp.raise_for_status()
        data = resp.json()

        text = data.get("message", {}).get("content", "")
        eval_count = data.get("eval_count", 0)
        prompt_eval_count = data.get("prompt_eval_count", 0)

        return OllamaResponse(
            text=text,
            model=model,
            input_tokens=prompt_eval_count,
            output_tokens=eval_count,
            duration_ms=duration_ms,
            cost_usd=0.0,
        )


# Singleton
_client: OllamaClient | None = None


def get_ollama_client() -> OllamaClient:
    """Get or create singleton Ollama client."""
    global _client
    if _client is None:
        _client = OllamaClient()
    return _client
