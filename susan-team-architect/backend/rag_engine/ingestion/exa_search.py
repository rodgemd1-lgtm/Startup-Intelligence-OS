"""Exa semantic search ingestion — discovers and ingests thematically related content."""
from __future__ import annotations
from exa_py import Exa
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config


class ExaSearchIngestor(BaseIngestor):
    """Discover and ingest content via Exa semantic search."""

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "market_research",
        agent_id: str | None = None,
        num_results: int = 10,
        search_type: str = "autoprompt",
        **kwargs,
    ) -> int:
        """Run an Exa semantic search and ingest the results.

        Args:
            source: The search query string.
            num_results: Number of results to discover and ingest.
            search_type: One of 'autoprompt', 'keyword', 'neural'.
        """
        client = Exa(api_key=config.exa_api_key)
        total = 0

        use_autoprompt = search_type == "autoprompt"
        exa_type = "auto" if search_type == "autoprompt" else search_type

        try:
            response = client.search_and_contents(
                source,
                num_results=num_results,
                type=exa_type,
                use_autoprompt=use_autoprompt,
                text=True,
            )
        except Exception as e:
            print(f"  Warning: Exa search failed for '{source}': {e}")
            return 0

        for result in response.results:
            text = getattr(result, "text", "") or ""
            if not text.strip():
                continue

            title = getattr(result, "title", "") or ""
            url = getattr(result, "url", "") or ""

            text_chunks = chunk_markdown(text, max_tokens=500)
            chunks = self._make_chunks(
                texts=text_chunks,
                data_type=data_type,
                company_id=company_id,
                agent_id=agent_id,
                source=f"exa:{url}",
                source_url=url,
                metadata={
                    "title": title,
                    "tool": "exa",
                    "query": source,
                    "search_type": search_type,
                },
            )
            total += self.retriever.store_chunks(chunks)

        return total
