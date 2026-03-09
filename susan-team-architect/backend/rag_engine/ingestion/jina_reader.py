"""Jina AI reader mode -- clean text extraction from cluttered web pages."""
from __future__ import annotations
from pathlib import Path
import httpx
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config


class JinaReaderIngestor(BaseIngestor):
    """Extract clean markdown from URLs via Jina AI reader mode."""

    JINA_READER_URL = "https://r.jina.ai/"

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        **kwargs,
    ) -> int:
        """Ingest one URL or a file of URLs via Jina reader.

        Args:
            source: A URL string, or path to a file with one URL per line.
        """
        urls = self._resolve_urls(source)
        total = 0

        headers = {"Accept": "text/markdown"}
        if config.jina_api_key:
            headers["Authorization"] = f"Bearer {config.jina_api_key}"

        for url in urls:
            try:
                response = httpx.get(
                    f"{self.JINA_READER_URL}{url}",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                markdown = response.text.strip()
                if not markdown:
                    continue

                text_chunks = chunk_markdown(markdown, max_tokens=500)
                chunks = self._make_chunks(
                    texts=text_chunks,
                    data_type=data_type,
                    company_id=company_id,
                    agent_id=agent_id,
                    source=f"jina:{url}",
                    source_url=url,
                    metadata={"tool": "jina"},
                )
                total += self.retriever.store_chunks(chunks)
            except Exception as e:
                print(f"  Warning: Jina reader failed for {url}: {e}")

        return total

    def _resolve_urls(self, source: str) -> list[str]:
        """Resolve source to a list of URLs."""
        path = Path(source)
        if path.is_file():
            return [line.strip() for line in path.read_text().splitlines() if line.strip()]
        return [source]
