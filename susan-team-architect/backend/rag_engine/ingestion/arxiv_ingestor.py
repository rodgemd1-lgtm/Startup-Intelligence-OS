"""arXiv paper ingestion — searches for recent papers and embeds abstracts."""
from __future__ import annotations
import arxiv
from rag_engine.ingestion.base import BaseIngestor
from rag_engine.chunker import chunk_text


class ArxivIngestor(BaseIngestor):
    """Ingest arXiv paper abstracts into the knowledge base."""

    def ingest(
        self,
        source: str,
        company_id: str = "shared",
        data_type: str = "ai_ml_research",
        agent_id: str | None = None,
        max_results: int = 50,
        **kwargs,
    ) -> int:
        """Search arXiv and ingest paper abstracts.

        Args:
            source: Search query (e.g., "multi-agent systems fitness")
            max_results: Maximum papers to fetch
        """
        search = arxiv.Search(
            query=source,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )

        total = 0
        for paper in search.results():
            abstract = f"**{paper.title}**\n\nAuthors: {', '.join(a.name for a in paper.authors[:5])}\n\n{paper.summary}"

            text_chunks = chunk_text(abstract, max_tokens=500, overlap=0)
            chunks = self._make_chunks(
                texts=text_chunks,
                data_type=data_type,
                company_id=company_id,
                agent_id=agent_id,
                source=f"arxiv:{paper.entry_id}",
                source_url=paper.pdf_url,
                metadata={
                    "title": paper.title,
                    "authors": [a.name for a in paper.authors[:5]],
                    "categories": paper.categories,
                    "published": str(paper.published.date()),
                },
            )
            total += self.retriever.store_chunks(chunks)

        return total
