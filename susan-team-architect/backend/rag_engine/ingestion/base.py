"""Base ingestion pipeline — all sources inherit from this."""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from rag_engine.retriever import Retriever
from rag_engine.chunker import chunk_text, chunk_markdown
from susan_core.schemas import KnowledgeChunk


class BaseIngestor(ABC):
    """Base class for all data ingestion pipelines."""

    def __init__(self, retriever: Retriever | None = None):
        self.retriever = retriever or Retriever()

    @abstractmethod
    def ingest(self, source: str, company_id: str = "shared", **kwargs) -> int:
        """Ingest data from source. Returns number of chunks stored."""
        ...

    def _make_chunks(
        self,
        texts: list[str],
        data_type: str,
        company_id: str = "shared",
        agent_id: str | None = None,
        source: str | None = None,
        source_url: str | None = None,
        metadata: dict | None = None,
    ) -> list[KnowledgeChunk]:
        """Convert text list to KnowledgeChunk objects."""
        return [
            KnowledgeChunk(
                content=text,
                company_id=company_id,
                agent_id=agent_id,
                data_type=data_type,
                source=source,
                source_url=source_url,
                metadata=metadata or {},
            )
            for text in texts
        ]
