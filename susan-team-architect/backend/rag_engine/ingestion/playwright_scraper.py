"""Playwright scraper -- navigates dynamic/JS-heavy pages and extracts content."""
from __future__ import annotations
from playwright.sync_api import sync_playwright
from markdownify import markdownify as md
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown


class PlaywrightIngestor(BaseIngestor):
    """Scrape JS-rendered pages via headless Chromium."""

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        wait_for: str | None = None,
        **kwargs,
    ) -> int:
        """Navigate to URL with Playwright, extract content as markdown.

        Args:
            source: URL to scrape.
            wait_for: Optional CSS selector to wait for before extraction.
        """
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                page.goto(source, wait_until="networkidle")

                if wait_for:
                    page.wait_for_selector(wait_for, timeout=15000)

                html = page.content()
                title = page.title()

                browser.close()
        except Exception as e:
            print(f"  Warning: Playwright failed for {source}: {e}")
            return 0

        markdown = md(html, strip=["script", "style", "nav", "footer", "header"])
        markdown = markdown.strip()
        if not markdown:
            return 0

        text_chunks = chunk_markdown(markdown, max_tokens=500)
        chunks = self._make_chunks(
            texts=text_chunks,
            data_type=data_type,
            company_id=company_id,
            agent_id=agent_id,
            source=f"playwright:{source}",
            source_url=source,
            metadata={"title": title, "tool": "playwright"},
        )
        return self.retriever.store_chunks(chunks)
