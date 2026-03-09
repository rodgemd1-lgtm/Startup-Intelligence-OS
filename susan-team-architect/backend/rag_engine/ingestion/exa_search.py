"""Exa semantic search ingestion -- discovers and extracts thematically related content."""
from __future__ import annotations
from exa_py import Exa
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_markdown
from susan_core.config import config


class ExaSearchIngestor(BaseIngestor):
    """Semantic search via Exa, then ingest top results into knowledge base."""

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
        """Run Exa semantic search and ingest result content.

        Args:
            source: The search query string.
            num_results: Number of results to fetch (default 10).
            search_type: Exa search type -- autoprompt, keyword, or neural.
        """
        client = Exa(api_key=config.exa_api_key)
        total = 0

        try:
            response = client.search_and_contents(
                source,
                num_results=num_results,
                type=search_type,
                text=True,
                use_autoprompt=(search_type == "autoprompt"),
            )
        except Exception as e:
            print(f"  Warning: Exa search failed: {e}")
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
                source=f"exa:{source[:80]}",
                source_url=url,
                metadata={"title": title, "tool": "exa", "query": source},
            )
            total += self.retriever.store_chunks(chunks)

        return total
