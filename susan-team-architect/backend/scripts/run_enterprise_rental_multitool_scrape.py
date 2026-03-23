"""Run Enterprise rental review scraping across Exa, Firecrawl, Brave, Jina/Jing, and Apify.

This runner is team-aware: it attempts to load API keys from Susan team env files first,
then from current process env, so Startup Intelligence operators can run the same command
without manually exporting every key each time.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import os

import httpx

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]
RUN_ROOT = (
    BACKEND_ROOT
    / "data"
    / "domains"
    / "enterprise_rental_intelligence"
    / "datasets"
    / "customer_review_training_seed"
    / "runs"
)

TEAM_ENV_CANDIDATES = [
    BACKEND_ROOT / ".env",
    REPO_ROOT / ".env",
    REPO_ROOT / ".startup-os" / ".env",
]

QUERIES = [
    "Enterprise Rent-A-Car customer reviews service quality themes",
    "Enterprise Rent-A-Car customer complaint patterns pickup dropoff billing",
    "Enterprise Rent-A-Car Trustpilot Better Business Bureau complaints",
]

TARGET_URLS = [
    "https://www.trustpilot.com/review/www.enterprise.com",
    "https://www.consumeraffairs.com/travel/enterprise.html",
    "https://www.sitejabber.com/reviews/enterprise.com",
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_dotenv_if_present(path: Path) -> bool:
    if not path.exists():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip())
    return True


def _bootstrap_team_env() -> list[str]:
    loaded: list[str] = []
    for env_path in TEAM_ENV_CANDIDATES:
        if _load_dotenv_if_present(env_path):
            loaded.append(str(env_path))
    return loaded


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def run_exa(query: str) -> dict:
    key = _first_env("EXA_API_KEY")
    if not key:
        return {"provider": "exa", "query": query, "status": "skipped", "reason": "EXA_API_KEY not set", "at": _now()}
    try:
        r = httpx.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": key, "Content-Type": "application/json"},
            json={"query": query, "type": "auto", "numResults": 5, "text": True},
            timeout=30.0,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        trimmed = [{"url": it.get("url"), "title": it.get("title"), "snippet": (it.get("text") or "")[:280]} for it in results]
        return {"provider": "exa", "query": query, "status": "ok", "count": len(trimmed), "results": trimmed, "at": _now()}
    except Exception as exc:
        return {"provider": "exa", "query": query, "status": "error", "error": str(exc), "at": _now()}


def run_brave(query: str) -> dict:
    key = _first_env("BRAVE_API_KEY", "BRAVE_SEARCH_API_KEY")
    if not key:
        return {
            "provider": "brave",
            "query": query,
            "status": "skipped",
            "reason": "BRAVE_API_KEY/BRAVE_SEARCH_API_KEY not set",
            "at": _now(),
        }
    try:
        r = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": key, "Accept": "application/json"},
            params={"q": query, "count": 5, "extra_snippets": True},
            timeout=30.0,
        )
        r.raise_for_status()
        results = r.json().get("web", {}).get("results", [])
        trimmed = [{"url": it.get("url"), "title": it.get("title"), "snippet": it.get("description")} for it in results]
        return {"provider": "brave", "query": query, "status": "ok", "count": len(trimmed), "results": trimmed, "at": _now()}
    except Exception as exc:
        return {"provider": "brave", "query": query, "status": "error", "error": str(exc), "at": _now()}


_FIRECRAWL_CREDIT_ERRORS = ("402", "payment", "credit", "quota", "upgrade", "exceeded")


def _is_credit_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(kw in msg for kw in _FIRECRAWL_CREDIT_ERRORS)


def run_firecrawl(url: str) -> dict:
    key = _first_env("FIRECRAWL_API_KEY")
    if not key:
        return {"provider": "firecrawl", "url": url, "status": "skipped", "reason": "FIRECRAWL_API_KEY not set", "at": _now()}
    try:
        r = httpx.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"url": url, "formats": ["markdown"]},
            timeout=45.0,
        )
        r.raise_for_status()
        data = r.json()
        md = ((data.get("data") or {}).get("markdown") or "")[:800]
        return {"provider": "firecrawl", "url": url, "status": "ok", "markdown_preview": md, "at": _now()}
    except Exception as exc:
        if _is_credit_error(exc):
            # Fall back to Jina reader
            print(f"  Firecrawl credits exhausted for {url} — falling back to Jina")
            return _run_jina_fallback(url)
        return {"provider": "firecrawl", "url": url, "status": "error", "error": str(exc), "at": _now()}


def _run_jina_fallback(url: str) -> dict:
    """Scrape a URL via Jina reader as a fallback for Firecrawl."""
    jina_key = _first_env("JINA_API_KEY")
    headers = {"Accept": "text/markdown"}
    if jina_key:
        headers["Authorization"] = f"Bearer {jina_key}"
    try:
        r = httpx.get(f"https://r.jina.ai/{url}", headers=headers, timeout=45.0, follow_redirects=True)
        r.raise_for_status()
        md = (r.text or "")[:800]
        return {"provider": "jina-fallback", "url": url, "status": "ok", "markdown_preview": md, "at": _now()}
    except Exception as exc:
        return {"provider": "jina-fallback", "url": url, "status": "error", "error": str(exc), "at": _now()}


def run_jina(url: str) -> dict:
    headers = {}
    jina_key = _first_env("JINA_API_KEY", "JING_API_KEY")
    if jina_key:
        headers["Authorization"] = f"Bearer {jina_key}"
    try:
        r = httpx.get(f"https://r.jina.ai/{url}", headers=headers, timeout=45.0, follow_redirects=True)
        r.raise_for_status()
        text = (r.text or "")[:800]
        return {"provider": "jina", "alias": "jing", "url": url, "status": "ok", "markdown_preview": text, "at": _now()}
    except Exception as exc:
        return {"provider": "jina", "alias": "jing", "url": url, "status": "error", "error": str(exc), "at": _now()}


def run_apify(url: str) -> dict:
    token = _first_env("APIFY_TOKEN", "APIFY_API_TOKEN", "APIFY_API_KEY")
    if not token:
        return {
            "provider": "apify",
            "url": url,
            "status": "skipped",
            "reason": "APIFY_TOKEN/APIFY_API_TOKEN/APIFY_API_KEY not set",
            "at": _now(),
        }
    endpoint = "https://api.apify.com/v2/acts/apify~website-content-crawler/run-sync-get-dataset-items"
    payload = {"startUrls": [{"url": url}], "maxCrawlPages": 1, "crawlerType": "playwright:adaptive", "saveMarkdown": True}
    try:
        r = httpx.post(endpoint, params={"token": token}, json=payload, timeout=120.0)
        r.raise_for_status()
        body = r.json()
        items = body if isinstance(body, list) else []
        first = items[0] if items else {}
        return {
            "provider": "apify",
            "url": url,
            "status": "ok",
            "item_count": len(items),
            "first_item_keys": sorted(first.keys())[:20],
            "at": _now(),
        }
    except Exception as exc:
        return {"provider": "apify", "url": url, "status": "error", "error": str(exc), "at": _now()}


def main() -> int:
    loaded_env_files = _bootstrap_team_env()
    run_id = f"enterprise_multitool_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir = RUN_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    provider_results = {
        "exa": [run_exa(q) for q in QUERIES],
        "brave": [run_brave(q) for q in QUERIES],
        "firecrawl": [run_firecrawl(u) for u in TARGET_URLS],
        "jina": [run_jina(u) for u in TARGET_URLS],
        "apify": [run_apify(u) for u in TARGET_URLS],
    }

    summary = {"run_id": run_id, "generated_at": _now(), "team_env_files_loaded": loaded_env_files, "providers": {}}
    for provider, rows in provider_results.items():
        summary["providers"][provider] = {
            "attempted": len(rows),
            "ok": sum(1 for row in rows if row.get("status") == "ok"),
            "skipped": sum(1 for row in rows if row.get("status") == "skipped"),
            "errored": sum(1 for row in rows if row.get("status") == "error"),
        }

    (out_dir / "results.json").write_text(json.dumps(provider_results, indent=2), encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md_lines = [
        "# Enterprise multi-tool scrape run",
        "",
        f"- run_id: `{run_id}`",
        f"- generated_at: `{summary['generated_at']}`",
        f"- team env files loaded: `{', '.join(loaded_env_files) if loaded_env_files else 'none'}`",
        "",
        "## Provider status",
    ]
    for p, s in summary["providers"].items():
        md_lines.append(f"- **{p}**: attempted={s['attempted']} ok={s['ok']} skipped={s['skipped']} errored={s['errored']}")
    (out_dir / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
