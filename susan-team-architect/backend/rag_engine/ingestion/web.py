"""Web scraping ingestion via Firecrawl with Jina reader fallback."""
from __future__ import annotations
from pathlib import Path
import urllib.request
from firecrawl import FirecrawlApp
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config

_FIRECRAWL_CREDIT_ERRORS = ("402", "payment", "credit", "quota", "upgrade", "exceeded")


def _is_credit_error(exc: Exception) -> bool:
    """Return True if exception looks like an out-of-credits / quota error."""
    msg = str(exc).lower()
    return any(kw in msg for kw in _FIRECRAWL_CREDIT_ERRORS)


def _jina_scrape(url: str) -> str:
    """Fetch a URL via Jina reader (https://r.jina.ai/{url}) and return markdown text."""
    jina_url = f"https://r.jina.ai/{url}"
    req = urllib.request.Request(jina_url, headers={"Accept": "text/markdown"})
    jina_key = config.jina_api_key if hasattr(config, "jina_api_key") else ""
    if jina_key:
        req.add_header("Authorization", f"Bearer {jina_key}")
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", errors="replace")


class WebIngestor(BaseIngestor):
    """Ingest web pages — tries Firecrawl first, falls back to Jina reader on credit/quota errors."""

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
        total = 0

        for url in urls:
            markdown = ""
            title = ""
            tool_used = "firecrawl"

            # --- Try Firecrawl first ---
            try:
                app = FirecrawlApp(api_key=config.firecrawl_api_key)
                result = app.scrape(url, formats=["markdown"])
                markdown = getattr(result, "markdown", "") or ""
                if hasattr(result, "metadata") and result.metadata:
                    title = getattr(result.metadata, "title", "") or ""
            except Exception as e:
                if _is_credit_error(e):
                    print(f"  Firecrawl credits exhausted for {url} — falling back to Jina")
                else:
                    print(f"  Firecrawl failed for {url}: {e} — falling back to Jina")
                markdown = ""

            # --- Fall back to Jina if Firecrawl returned nothing ---
            if not markdown:
                try:
                    markdown = _jina_scrape(url)
                    tool_used = "jina"
                except Exception as e:
                    print(f"  Warning: Jina fallback also failed for {url}: {e}")
                    continue

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
                metadata={"title": title, "scrape_tool": tool_used},
            )
            total += self.retriever.store_chunks(chunks)

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
        Falls back to a single Jina scrape of the base URL on credit/quota errors.

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
            if _is_credit_error(e):
                print(f"  Firecrawl credits exhausted for crawl of {source} — falling back to Jina single-page scrape")
            else:
                print(f"  Warning: Firecrawl crawl failed for {source}: {e} — falling back to Jina single-page scrape")
            # Fallback: scrape just the base URL via Jina
            try:
                markdown = _jina_scrape(source)
                if markdown:
                    text_chunks = chunk_markdown(markdown, max_tokens=500)
                    chunks = self._make_chunks(
                        texts=text_chunks,
                        data_type=data_type,
                        company_id=company_id,
                        agent_id=agent_id,
                        source=f"jina-crawl-fallback:{source}",
                        source_url=source,
                        metadata={"title": "", "tool": "jina-crawl-fallback", "base_url": source},
                    )
                    total += self.retriever.store_chunks(chunks)
            except Exception as je:
                print(f"  Warning: Jina fallback also failed for {source}: {je}")
            return total

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
