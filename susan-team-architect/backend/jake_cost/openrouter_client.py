"""OpenRouter API client — unified gateway for GLM-5, MiniMax M2.7, GPT-4o.

V1.5 Cost Optimization: All agent operations route through OpenRouter.
Anthropic direct is reserved for Claude Code dev sessions only.

Uses the OpenAI-compatible API that OpenRouter exposes.
"""
from __future__ import annotations

import os
import time
import json
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")


@dataclass
class OpenRouterResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    raw: dict


class OpenRouterClient:
    """Minimal client for OpenRouter's OpenAI-compatible chat API."""

    def __init__(self, api_key: str | None = None, timeout: float = 120.0):
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not set. Add to ~/.jake-vault/secrets.env"
            )
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=OPENROUTER_BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://intelligence-os.local",
                "X-Title": "Startup Intelligence OS",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    def chat(
        self,
        model: str,
        messages: list[dict],
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> OpenRouterResponse:
        """Send a chat completion request to OpenRouter.

        Args:
            model: OpenRouter model ID (e.g. "zhipu/glm-5", "minimax/minimax-m2.7")
            messages: List of {"role": "user"/"assistant", "content": "..."}
            system: Optional system prompt (prepended as system message)
            max_tokens: Maximum output tokens
            temperature: Sampling temperature
        """
        if system:
            messages = [{"role": "system", "content": system}] + messages

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        start = time.time()
        try:
            resp = self._client.post("/chat/completions", json=payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter API error: {e.response.status_code} {e.response.text}")
            raise
        except httpx.TimeoutException:
            logger.error(f"OpenRouter API timeout after {self.timeout}s for model={model}")
            raise

        duration_ms = int((time.time() - start) * 1000)
        data = resp.json()

        # Extract response — handle both content and reasoning fields
        choices = data.get("choices", [])
        text = ""
        if choices:
            msg = choices[0].get("message", {})
            text = msg.get("content") or ""
            # Some reasoning models (MiniMax M2.7) put output in reasoning field
            if not text and msg.get("reasoning"):
                text = msg["reasoning"]

        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        # OpenRouter includes cost in the usage block
        cost = 0.0
        if "usage" in data:
            cost = data["usage"].get("cost", 0.0) or 0.0

        return OpenRouterResponse(
            text=text,
            model=data.get("model", model),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            duration_ms=duration_ms,
            raw=data,
        )

    def close(self):
        self._client.close()


# Singleton
_client: OpenRouterClient | None = None


def get_openrouter_client() -> OpenRouterClient:
    """Get or create the singleton OpenRouter client."""
    global _client
    if _client is None:
        _client = OpenRouterClient()
    return _client
