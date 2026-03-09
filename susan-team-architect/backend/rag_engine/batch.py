"""Batch manifest parser and executor for systematic data scraping."""
from __future__ import annotations
from pathlib import Path
import yaml

from rag_engine.ingestion.exa_search import ExaSearchIngestor
from rag_engine.ingestion.jina_reader import JinaReaderIngestor
from rag_engine.ingestion.playwright_scraper import PlaywrightIngestor
from rag_engine.ingestion.web import WebIngestor


def parse_manifest(path: Path) -> dict:
    """Parse a scrape manifest YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def execute_manifest(
    manifest_path: Path,
    dry_run: bool = False,
    resume: bool = False,
) -> dict:
    """Execute all sources in a manifest.

    Args:
        manifest_path: Path to the YAML manifest file.
        dry_run: If True, list sources without executing.
        resume: If True, skip already-ingested source_urls (not yet implemented).

    Returns:
        Summary dict with total_chunks, sources_processed, errors.
    """
    data = parse_manifest(manifest_path)
    meta = data.get("manifest", {})
    sources = data.get("sources", [])
    company = meta.get("company", "shared")
    data_type = meta.get("data_type", "market_research")

    if dry_run:
        print(f"DRY RUN: {meta.get('name', 'Unnamed')} ({len(sources)} sources)")
        for i, src in enumerate(sources, 1):
            tool = src.get("tool", "unknown")
            target = src.get("query") or src.get("url") or src.get("url_file", "")
            print(f"  [{i}/{len(sources)}] {tool}: {target}")
        return {"total_chunks": 0, "sources_processed": 0, "sources_total": len(sources), "errors": 0}

    exa = ExaSearchIngestor()
    jina = JinaReaderIngestor()
    playwright = PlaywrightIngestor()
    web = WebIngestor()

    total_chunks = 0
    processed = 0
    errors = 0

    for i, src in enumerate(sources, 1):
        tool = src.get("tool", "firecrawl")
        target = src.get("query") or src.get("url") or src.get("url_file", "")
        print(f"  [{i}/{len(sources)}] {tool}: {target[:80]}...")

        try:
            if tool == "exa":
                count = exa.ingest(
                    source=src["query"],
                    company_id=company,
                    data_type=data_type,
                    num_results=src.get("num_results", 10),
                    search_type=src.get("search_type", "autoprompt"),
                )
            elif tool == "jina":
                count = jina.ingest(
                    source=src.get("url") or src.get("url_file", ""),
                    company_id=company,
                    data_type=data_type,
                )
            elif tool == "playwright":
                count = playwright.ingest(
                    source=src["url"],
                    company_id=company,
                    data_type=data_type,
                    wait_for=src.get("wait_for"),
                )
            elif tool == "firecrawl":
                mode = src.get("mode", "single")
                if mode == "crawl":
                    count = web.crawl(
                        source=src["url"],
                        company_id=company,
                        data_type=data_type,
                        max_pages=src.get("max_pages", 50),
                    )
                else:
                    count = web.ingest(
                        source=src.get("url") or src.get("url_file", ""),
                        company_id=company,
                        data_type=data_type,
                    )
            else:
                print(f"    Unknown tool: {tool}")
                errors += 1
                continue

            total_chunks += count
            processed += 1
            print(f"    -> {count} chunks")

        except Exception as e:
            print(f"    ERROR: {e}")
            errors += 1

    return {
        "total_chunks": total_chunks,
        "sources_processed": processed,
        "sources_total": len(sources),
        "errors": errors,
    }
