"""Batch manifest executor — runs scrape manifests across multiple tools."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml

from rag_engine.ingestion.exa_search import ExaSearchIngestor
from rag_engine.ingestion.jina_reader import JinaReaderIngestor
from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
from rag_engine.ingestion.web import WebIngestor


def parse_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load and validate a scrape manifest YAML file."""
    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    data.setdefault("manifest", {})
    data.setdefault("sources", [])
    return data


def execute_manifest(
    manifest_path: Path,
    dry_run: bool = False,
    resume: bool = False,
) -> dict[str, Any]:
    """Execute a scrape manifest YAML file.

    Manifest format:
        manifest:
          name: "Exercise Science Core"
          company: transformfit
          data_type: exercise_science
          priority: high
        sources:
          - tool: firecrawl
            url: https://example.com/article
          - tool: exa
            query: "progressive overload protocols"
            num_results: 10
          - tool: jina
            url: https://example.com/page
          - tool: playwright
            url: https://dynamic-site.com
            wait_for: ".content-loaded"

    Args:
        manifest_path: Path to the YAML manifest file.
        dry_run: If True, list sources without executing.
        resume: If True, skip URLs that have already been ingested.

    Returns:
        Summary dict with counts, errors, and per-source results.
    """
    data = parse_manifest(manifest_path)

    meta = data.get("manifest", {})
    sources = data.get("sources", [])
    company_id = meta.get("company", "shared")
    data_type = meta.get("data_type", "market_research")

    results: list[dict[str, Any]] = []
    total_chunks = 0
    errors: list[str] = []

    if dry_run:
        for src in sources:
            tool = src.get("tool", "firecrawl")
            target = src.get("url") or src.get("query", "")
            results.append({"tool": tool, "target": target, "status": "dry_run"})
        return {
            "manifest": meta.get("name", manifest_path.name),
            "dry_run": True,
            "total_chunks": 0,
            "sources_processed": 0,
            "sources_total": len(sources),
            "sources": results,
        }

    web = WebIngestor()
    exa = ExaSearchIngestor()
    jina = JinaReaderIngestor()
    pw = PlaywrightIngestor()

    existing_urls: set[str] = set()
    if resume:
        existing_urls = _get_existing_source_urls(company_id)

    for src in sources:
        tool = src.get("tool", "firecrawl")
        url = src.get("url", "")
        query = src.get("query", "")
        target = url or query

        if resume and url and url in existing_urls:
            results.append({"tool": tool, "target": target, "status": "skipped", "chunks": 0})
            continue

        try:
            if tool == "firecrawl" and src.get("mode") == "crawl":
                max_pages = src.get("max_pages", 50)
                count = web.crawl(source=url, company_id=company_id, data_type=data_type, max_pages=max_pages)
            elif tool == "firecrawl":
                count = web.ingest(source=url, company_id=company_id, data_type=data_type)
            elif tool == "firecrawl-crawl":
                max_pages = src.get("max_pages", 50)
                count = web.crawl(source=url, company_id=company_id, data_type=data_type, max_pages=max_pages)
            elif tool == "exa":
                num_results = src.get("num_results", 10)
                search_type = src.get("search_type", "autoprompt")
                count = exa.ingest(source=query, company_id=company_id, data_type=data_type,
                                    num_results=num_results, search_type=search_type)
            elif tool == "jina":
                count = jina.ingest(source=url, company_id=company_id, data_type=data_type)
            elif tool == "playwright":
                wait_for = src.get("wait_for")
                count = pw.ingest(source=url, company_id=company_id, data_type=data_type,
                                   wait_for=wait_for)
            else:
                errors.append(f"Unknown tool '{tool}' for {target}")
                results.append({"tool": tool, "target": target, "status": "error", "chunks": 0})
                continue

            total_chunks += count
            results.append({"tool": tool, "target": target, "status": "ok", "chunks": count})
        except Exception as e:
            errors.append(f"{tool}:{target} — {e}")
            results.append({"tool": tool, "target": target, "status": "error", "chunks": 0})

    return {
        "manifest": meta.get("name", manifest_path.name),
        "dry_run": False,
        "total_chunks": total_chunks,
        "sources_processed": sum(1 for r in results if r["status"] in {"ok", "error"}),
        "sources_total": len(sources),
        "completed": sum(1 for r in results if r["status"] == "ok"),
        "skipped": sum(1 for r in results if r["status"] == "skipped"),
        "errors": len(errors),
        "error_messages": errors,
        "sources": results,
    }


def _get_existing_source_urls(company_id: str) -> set[str]:
    """Query existing chunks to find already-ingested source URLs."""
    try:
        from rag_engine.retriever import Retriever
        retriever = Retriever()
        result = retriever.supabase.table("knowledge_chunks") \
            .select("source_url") \
            .eq("company_id", company_id) \
            .not_.is_("source_url", "null") \
            .execute()
        return {row["source_url"] for row in (result.data or []) if row.get("source_url")}
    except Exception:
        return set()
