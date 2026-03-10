"""Jina Reader ingestion — clean markdown extraction from cluttered web pages."""
from __future__ import annotations
from pathlib import Path
import httpx
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config


class JinaReaderIngestor(BaseIngestor):
    """Ingest web pages via Jina Reader API for clean text extraction."""

    JINA_READER_URL = "https://r.jina.ai/"

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        **kwargs,
    ) -> int:
        """Ingest a URL or list of URLs via Jina Reader.

        Args:
            source: URL string, or path to a file with one URL per line.
        """
        urls = self._resolve_urls(source)
        total = 0

        headers = {
            "Accept": "text/markdown",
        }
        if config.jina_api_key:
            headers["Authorization"] = f"Bearer {config.jina_api_key}"

        for url in urls:
            try:
                response = httpx.get(
                    f"{self.JINA_READER_URL}{url}",
                    headers=headers,
                    timeout=30.0,
                    follow_redirects=True,
                )
                response.raise_for_status()
                markdown = response.text

                if not markdown.strip():
                    continue

                # Extract title from first markdown heading if present
                title = ""
                for line in markdown.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("# "):
                        title = stripped[2:].strip()
                        break

                text_chunks = chunk_markdown(markdown, max_tokens=500)
                chunks = self._make_chunks(
                    texts=text_chunks,
                    data_type=data_type,
                    company_id=company_id,
                    agent_id=agent_id,
                    source=f"jina:{url}",
                    source_url=url,
                    metadata={"title": title, "tool": "jina"},
                )
                total += self.retriever.store_chunks(chunks)
            except Exception as e:
                print(f"  Warning: Jina Reader failed for {url}: {e}")

        return total

    def _resolve_urls(self, source: str) -> list[str]:
        """Resolve source to a list of URLs."""
        path = Path(source)
        if path.is_file():
            return [line.strip() for line in path.read_text().splitlines() if line.strip()]
        return [source]
