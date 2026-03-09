"""Shared runtime helpers for Susan phases."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
import yaml

from susan_core.clients import get_anthropic_client
from susan_core.config import config


def _cache_key(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_path(company: str, phase: str, payload: dict[str, Any]) -> Path:
    key = _cache_key(payload)
    return config.phase_cache_dir / company / f"{phase}-{key}.json"


def load_cache(company: str, phase: str, payload: dict[str, Any], refresh: bool = False) -> Any | None:
    if refresh:
        return None
    path = _cache_path(company, phase, payload)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_cache(company: str, phase: str, payload: dict[str, Any], value: Any) -> None:
    path = _cache_path(company, phase, payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str), encoding="utf-8")


def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        candidate = text[start:end]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            repaired = yaml.safe_load(candidate)
            if isinstance(repaired, dict):
                return repaired
    raise ValueError("Failed to parse JSON response")


def repair_json(text: str) -> dict:
    client = get_anthropic_client()
    repair_prompt = f"""Repair this malformed JSON and return ONLY valid JSON.

Malformed JSON:
{text}
"""
    response = client.messages.create(
        model=config.model_haiku,
        max_tokens=4096,
        messages=[{"role": "user", "content": repair_prompt}],
    )
    return extract_json(response.content[0].text)


def run_cached_json_phase(
    *,
    company: str,
    phase: str,
    cache_payload: dict[str, Any],
    prompt: str,
    model: str,
    max_tokens: int,
    refresh: bool = False,
) -> dict:
    cached = load_cache(company, phase, cache_payload, refresh=refresh)
    if cached is not None:
        return cached

    client = get_anthropic_client()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_text = response.content[0].text
    try:
        parsed = extract_json(raw_text)
    except Exception:
        parsed = repair_json(raw_text)
    save_cache(company, phase, cache_payload, parsed)
    return parsed


def run_cached_text_phase(
    *,
    company: str,
    phase: str,
    cache_payload: dict[str, Any],
    prompt: str,
    model: str,
    max_tokens: int,
    refresh: bool = False,
) -> str:
    cached = load_cache(company, phase, cache_payload, refresh=refresh)
    if cached is not None:
        return cached["text"]

    client = get_anthropic_client()
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text
    save_cache(company, phase, cache_payload, {"text": text})
    return text
