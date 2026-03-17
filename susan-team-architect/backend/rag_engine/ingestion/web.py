"""Web scraping ingestion via Firecrawl — converts URLs to markdown and embeds."""
from __future__ import annotations
from pathlib import Path
from firecrawl import FirecrawlApp
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config


class WebIngestor(BaseIngestor):
    """Ingest web pages into the knowledge base via Firecrawl."""

    def __init__(self, retriever=None):
        super().__init__(retriever=retriever)

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
                result = app.scrape(url, formats=["markdown"])
                markdown = getattr(result, "markdown", "") or ""
                if not markdown:
                    continue

                title = ""
                if hasattr(result, "metadata") and result.metadata:
                    title = getattr(result.metadata, "title", "") or ""

                text_chunks = chunk_markdown(markdown, max_tokens=500)
                chunks = self._make_chunks(
                    texts=text_chunks,
                    data_type=data_type,
                    company_id=company_id,
                    agent_id=agent_id,
                    source=f"web:{url}",
                    source_url=url,
                    metadata={"title": title},
                )
                total += self.retriever.store_chunks(chunks)
            except Exception as e:
                print(f"  Warning: Failed to scrape {url}: {e}")

        return total

    def crawl(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        max_pages: int = 50,
        **kwargs,
    ) -> int:
        """Deep crawl a site via Firecrawl, following internal links.

        Args:
            source: Base URL to crawl.
            max_pages: Maximum number of pages to crawl.
        """
        app = FirecrawlApp(api_key=config.firecrawl_api_key)
        total = 0

        try:
            try:
                result = app.crawl(source, limit=max_pages, scrape_options={"formats": ["markdown"]})
            except AttributeError:
                result = app.crawl_url(source, params={"limit": max_pages})
            pages = self._extract_pages(result)
        except Exception as e:
            print(f"  Warning: Firecrawl crawl failed for {source}: {e}")
            return 0

        for page in pages:
            markdown = self._page_value(page, "markdown") or ""
            if not markdown.strip():
                continue

            metadata = self._page_value(page, "metadata") or {}
            title = self._metadata_value(metadata, "title")
            page_url = (
                self._metadata_value(metadata, "sourceURL")
                or self._metadata_value(metadata, "url")
                or source
            )

            text_chunks = chunk_markdown(markdown, max_tokens=500)
            chunks = self._make_chunks(
                texts=text_chunks,
                data_type=data_type,
                company_id=company_id,
                agent_id=agent_id,
                source=f"firecrawl-crawl:{page_url}",
                source_url=page_url,
                metadata={"title": title, "tool": "firecrawl-crawl", "base_url": source},
            )
            total += self.retriever.store_chunks(chunks)

        return total

    def _resolve_urls(self, source: str) -> list[str]:
        """Resolve source to a list of URLs."""
        path = Path(source)
        if path.is_file():
            return [line.strip() for line in path.read_text().splitlines() if line.strip()]
        return [source]

    def _extract_pages(self, result) -> list:
        if isinstance(result, dict):
            return result.get("data") or []
        return getattr(result, "data", None) or []

    def _page_value(self, page, field: str):
        if isinstance(page, dict):
            return page.get(field, "")
        return getattr(page, field, "")

    def _metadata_value(self, metadata, field: str) -> str:
        if isinstance(metadata, dict):
            return metadata.get(field, "") or ""
        return getattr(metadata, field, "") or ""
