"""Web scraping ingestion via Firecrawl — converts URLs to markdown and embeds."""
from __future__ import annotations
from pathlib import Path
from firecrawl import FirecrawlApp
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config


class WebIngestor(BaseIngestor):
    """Ingest web pages into the knowledge base via Firecrawl."""

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        **kwargs,
    ) -> int:
        """Ingest a URL or list of URLs.

        Args:
            source: URL string, or path to a file with one URL per line
        """
        urls = self._resolve_urls(source)
        app = FirecrawlApp(api_key=config.firecrawl_api_key)
        total = 0

        for url in urls:
            try:
                result = app.scrape_url(url, params={"formats": ["markdown"]})
                markdown = result.get("markdown", "")
                if not markdown:
                    continue

                text_chunks = chunk_markdown(markdown, max_tokens=500)
                chunks = self._make_chunks(
                    texts=text_chunks,
                    data_type=data_type,
                    company_id=company_id,
                    agent_id=agent_id,
                    source=f"web:{url}",
                    source_url=url,
                    metadata={"title": result.get("metadata", {}).get("title", "")},
                )
                total += self.retriever.store_chunks(chunks)
            except Exception as e:
                print(f"  Warning: Failed to scrape {url}: {e}")

        return total

    def _resolve_urls(self, source: str) -> list[str]:
        """Resolve source to a list of URLs."""
        path = Path(source)
        if path.is_file():
            return [line.strip() for line in path.read_text().splitlines() if line.strip()]
        return [source]
