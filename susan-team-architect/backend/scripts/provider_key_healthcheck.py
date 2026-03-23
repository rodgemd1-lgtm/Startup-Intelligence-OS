"""Validate provider keys from the ignored backend .env without printing secrets."""
from __future__ import annotations

from pathlib import Path
import json
import os

import httpx

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = BACKEND_ROOT / ".env"


def load_env() -> None:
    if not ENV_PATH.exists():
        return
    for line in ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def first_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def check_exa() -> dict[str, object]:
    key = first_env("EXA_API_KEY")
    if not key:
        return {"provider": "exa", "status": "missing"}
    try:
        response = httpx.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": key, "Content-Type": "application/json"},
            json={"query": "healthcare AI enablement", "type": "auto", "numResults": 1},
            timeout=20.0,
        )
        response.raise_for_status()
        return {"provider": "exa", "status": "ok"}
    except Exception as exc:
        return {"provider": "exa", "status": "error", "error": str(exc)}


def check_brave() -> dict[str, object]:
    key = first_env("BRAVE_API_KEY", "BRAVE_SEARCH_API_KEY")
    if not key:
        return {"provider": "brave", "status": "missing"}
    try:
        response = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": key, "Accept": "application/json"},
            params={"q": "healthcare AI enablement", "count": 1},
            timeout=20.0,
        )
        response.raise_for_status()
        return {"provider": "brave", "status": "ok"}
    except Exception as exc:
        return {"provider": "brave", "status": "error", "error": str(exc)}


def check_firecrawl() -> dict[str, object]:
    key = first_env("FIRECRAWL_API_KEY")
    if not key:
        return {"provider": "firecrawl", "status": "missing"}
    try:
        response = httpx.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"url": "https://example.com", "formats": ["markdown"]},
            timeout=30.0,
        )
        response.raise_for_status()
        return {"provider": "firecrawl", "status": "ok"}
    except Exception as exc:
        err_msg = str(exc).lower()
        credit_keywords = ("402", "payment", "credit", "quota", "upgrade", "exceeded")
        if any(kw in err_msg for kw in credit_keywords):
            return {
                "provider": "firecrawl",
                "status": "out_of_credits",
                "error": str(exc),
                "fallback": "jina",
                "note": "Jina reader fallback is active — scraping will continue via https://r.jina.ai/",
            }
        return {"provider": "firecrawl", "status": "error", "error": str(exc)}


def check_jina() -> dict[str, object]:
    key = first_env("JINA_API_KEY", "JING_API_KEY")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    try:
        response = httpx.get("https://r.jina.ai/http://example.com", headers=headers, timeout=20.0)
        response.raise_for_status()
        return {"provider": "jina", "status": "ok", "authenticated": bool(key)}
    except Exception as exc:
        return {"provider": "jina", "status": "error", "error": str(exc)}


def check_apify() -> dict[str, object]:
    token = first_env("APIFY_TOKEN", "APIFY_API_TOKEN", "APIFY_API_KEY")
    if not token:
        return {"provider": "apify", "status": "missing"}
    try:
        response = httpx.get(
            "https://api.apify.com/v2/users/me",
            params={"token": token},
            timeout=20.0,
        )
        response.raise_for_status()
        return {"provider": "apify", "status": "ok"}
    except Exception as exc:
        return {"provider": "apify", "status": "error", "error": str(exc)}


def check_supabase() -> dict[str, object]:
    url = first_env("SUPABASE_URL")
    key = first_env("SUPABASE_KEY", "SUPABASE_SERVICE_KEY")
    if not url or not key:
        return {"provider": "supabase", "status": "missing"}
    try:
        response = httpx.get(
            f"{url.rstrip('/')}/rest/v1/",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            timeout=20.0,
        )
        if response.status_code in {200, 404}:
            return {"provider": "supabase", "status": "ok"}
        response.raise_for_status()
        return {"provider": "supabase", "status": "ok"}
    except Exception as exc:
        return {"provider": "supabase", "status": "error", "error": str(exc)}


def check_openai() -> dict[str, object]:
    key = first_env("OPENAI_API_KEY")
    if not key:
        return {"provider": "openai", "status": "missing"}
    try:
        response = httpx.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=20.0,
        )
        response.raise_for_status()
        return {"provider": "openai", "status": "ok"}
    except Exception as exc:
        return {"provider": "openai", "status": "error", "error": str(exc)}


def main() -> int:
    load_env()
    results = [
        check_exa(),
        check_brave(),
        check_firecrawl(),
        check_jina(),
        check_apify(),
        check_supabase(),
        check_openai(),
    ]
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
