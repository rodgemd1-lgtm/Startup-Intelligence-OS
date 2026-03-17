"""Playwright ingestion — scrapes dynamic/JS-heavy pages via headless Chromium."""
from __future__ import annotations
from pathlib import Path
from markdownify import markdownify as md
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown

try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover - keeps module importable without Playwright.
    sync_playwright = None


class PlaywrightIngestor(BaseIngestor):
    """Ingest dynamic web pages via Playwright headless browser."""

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        wait_for: str | None = None,
        **kwargs,
    ) -> int:
        """Ingest a URL or list of URLs via Playwright.

        Args:
            source: URL string, or path to a file with one URL per line.
            wait_for: Optional CSS selector to wait for before extracting content.
        """
        if sync_playwright is None:
            return 0

        urls = self._resolve_urls(source)
        total = 0

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()

                for url in urls:
                    try:
                        page.goto(url, wait_until="networkidle")

                        if wait_for:
                            page.wait_for_selector(wait_for, timeout=15000)

                        title = page.title() or ""
                        html = page.content()

                        if not html or not html.strip():
                            continue

                        markdown = md(html, heading_style="ATX", strip=["script", "style", "nav", "footer"])
                        if not markdown.strip():
                            continue

                        text_chunks = chunk_markdown(markdown, max_tokens=500)
                        chunks = self._make_chunks(
                            texts=text_chunks,
                            data_type=data_type,
                            company_id=company_id,
                            agent_id=agent_id,
                            source=f"playwright:{url}",
                            source_url=url,
                            metadata={"title": title, "tool": "playwright", "wait_for": wait_for or ""},
                        )
                        total += self.retriever.store_chunks(chunks)
                    except Exception as e:
                        print(f"  Warning: Playwright failed for {url}: {e}")

                context.close()
                browser.close()
        except Exception as e:
            print(f"  Warning: Playwright bootstrap failed: {e}")
            return 0

        return total

    def _resolve_urls(self, source: str) -> list[str]:
        """Resolve source to a list of URLs."""
        path = Path(source)
        if path.is_file():
            return [line.strip() for line in path.read_text().splitlines() if line.strip()]
        return [source]
