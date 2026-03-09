"""Research prompt and meta-prompt intelligence via Exa, Brave, and Firecrawl.

Outputs:
  artifacts/prompt_intelligence/search_results.json
  artifacts/prompt_intelligence/scraped_pages.jsonl
  artifacts/prompt_intelligence/summary.md

Usage:
  cd susan-team-architect/backend
  python3 -m scripts.ingest_prompt_intelligence
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import json
import os

import httpx
import yaml

try:
    from firecrawl import Firecrawl
except Exception:  # pragma: no cover - optional runtime dependency behavior
    Firecrawl = None


@dataclass
class SearchHit:
    provider: str
    topic: str
    query: str
    title: str
    url: str
    snippet: str | None = None
    published_at: str | None = None


def load_dotenv(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    return yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}


def search_exa(query: str, topic: str, api_key: str, top_k: int) -> list[SearchHit]:
    response = httpx.post(
        "https://api.exa.ai/search",
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "type": "auto",
            "text": True,
            "numResults": top_k,
        },
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    hits: list[SearchHit] = []
    for result in payload.get("results", []):
        text = result.get("text") or ""
        hits.append(
            SearchHit(
                provider="exa",
                topic=topic,
                query=query,
                title=result.get("title") or result.get("url", ""),
                url=result.get("url", ""),
                snippet=text[:400] if text else None,
                published_at=result.get("publishedDate"),
            )
        )
    return hits


def search_brave(query: str, topic: str, api_key: str, top_k: int) -> list[SearchHit]:
    response = httpx.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={
            "X-Subscription-Token": api_key,
            "Accept": "application/json",
        },
        params={
            "q": query,
            "count": top_k,
            "extra_snippets": True,
        },
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    hits: list[SearchHit] = []
    for result in payload.get("web", {}).get("results", []):
        snippet = result.get("description")
        extra = result.get("extra_snippets") or []
        if extra:
            snippet = " ".join([snippet or "", *extra]).strip()
        hits.append(
            SearchHit(
                provider="brave",
                topic=topic,
                query=query,
                title=result.get("title") or result.get("url", ""),
                url=result.get("url", ""),
                snippet=snippet,
                published_at=result.get("age"),
            )
        )
    return hits


def scrape_firecrawl(url: str, api_key: str, formats: list[str]) -> dict[str, Any]:
    if Firecrawl is None:
        raise RuntimeError("firecrawl-py is not installed in the active environment.")
    client = Firecrawl(api_key=api_key)
    result = client.scrape(
        url,
        formats=formats or ["markdown"],
        maxAge=0,
    )
    return result if isinstance(result, dict) else result.model_dump()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def main() -> int:
    backend_root = Path(__file__).resolve().parents[1]
    load_dotenv(backend_root / ".env")
    manifest = load_manifest(backend_root / "data" / "prompt_library" / "source_manifest.yaml")
    artifacts_root = backend_root / "artifacts" / "prompt_intelligence"
    providers = manifest.get("providers", {})
    queries = manifest.get("queries", [])

    all_hits: list[SearchHit] = []
    for entry in queries:
        query = entry["query"]
        topic = entry["topic"]

        exa_key = os.getenv(providers.get("exa", {}).get("enabled_env", ""))
        if exa_key:
            try:
                all_hits.extend(search_exa(query, topic, exa_key, int(providers.get("exa", {}).get("top_k", 5))))
            except Exception as exc:
                all_hits.append(SearchHit(provider="exa", topic=topic, query=query, title="EXA_ERROR", url="", snippet=str(exc)))

        brave_key = os.getenv(providers.get("brave", {}).get("enabled_env", ""))
        if brave_key:
            try:
                all_hits.extend(search_brave(query, topic, brave_key, int(providers.get("brave", {}).get("top_k", 5))))
            except Exception as exc:
                all_hits.append(SearchHit(provider="brave", topic=topic, query=query, title="BRAVE_ERROR", url="", snippet=str(exc)))

    deduped_urls: dict[str, SearchHit] = {}
    for hit in all_hits:
        if hit.url and hit.url not in deduped_urls:
            deduped_urls[hit.url] = hit

    firecrawl_key = os.getenv(providers.get("firecrawl", {}).get("enabled_env", ""))
    scrape_limit = int(providers.get("firecrawl", {}).get("scrape_limit", 10))
    scrape_formats = list(providers.get("firecrawl", {}).get("formats", ["markdown"]))
    scraped_rows: list[dict[str, Any]] = []
    if firecrawl_key:
        for hit in list(deduped_urls.values())[:scrape_limit]:
            try:
                scraped = scrape_firecrawl(hit.url, firecrawl_key, scrape_formats)
                scraped_rows.append(
                    {
                        "provider": hit.provider,
                        "topic": hit.topic,
                        "query": hit.query,
                        "title": hit.title,
                        "url": hit.url,
                        "scrape": scraped,
                    }
                )
            except Exception as exc:
                scraped_rows.append(
                    {
                        "provider": hit.provider,
                        "topic": hit.topic,
                        "query": hit.query,
                        "title": hit.title,
                        "url": hit.url,
                        "error": str(exc),
                    }
                )

    hits_payload = [asdict(hit) for hit in all_hits]
    write_json(artifacts_root / "search_results.json", hits_payload)
    write_jsonl(artifacts_root / "scraped_pages.jsonl", scraped_rows)

    summary_lines = [
        "# Prompt Intelligence Harvest",
        "",
        f"- Generated at: {datetime.now(UTC).isoformat()}",
        f"- Total search hits: {len(all_hits)}",
        f"- Unique URLs: {len(deduped_urls)}",
        f"- Firecrawl scrapes attempted: {len(scraped_rows)}",
        "",
        "## Providers",
        f"- Exa configured: {'yes' if os.getenv(providers.get('exa', {}).get('enabled_env', '')) else 'no'}",
        f"- Brave configured: {'yes' if os.getenv(providers.get('brave', {}).get('enabled_env', '')) else 'no'}",
        f"- Firecrawl configured: {'yes' if firecrawl_key else 'no'}",
        f"- Firecrawl formats: {', '.join(scrape_formats)}",
        "",
        "## Topics",
    ]
    topic_counts = {}
    for hit in all_hits:
        topic_counts[hit.topic] = topic_counts.get(hit.topic, 0) + 1
    for topic, count in sorted(topic_counts.items()):
        summary_lines.append(f"- {topic}: {count} hits")

    (artifacts_root / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    print(json.dumps({"hits": len(all_hits), "unique_urls": len(deduped_urls), "scrapes": len(scraped_rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
