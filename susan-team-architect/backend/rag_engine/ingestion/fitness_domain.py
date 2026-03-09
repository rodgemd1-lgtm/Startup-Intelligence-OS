"""Fitness domain ingestion for Susan's shared RAG knowledge base."""
from __future__ import annotations

from pathlib import Path

from fitness_intel.pipeline import CorpusBuilder
from fitness_intel.startup_os import to_susan_knowledge_chunk
from rag_engine.ingestion.base import BaseIngestor
from susan_core.config import config


class FitnessDomainIngestor(BaseIngestor):
    """Ingest the merged fitness intelligence domain into the shared retriever."""

    def ingest(
        self,
        source: str = "",
        company_id: str = "shared",
        data_type: str = "fitness_intelligence",
        agent_id: str | None = None,
        limit: int | None = None,
        **kwargs,
    ) -> int:
        domain_root = Path(source) if source else config.fitness_domain_dir / "editorial"
        builder = CorpusBuilder(domain_root)
        chunks = builder.build_chunks(limit=limit)
        knowledge_chunks = []

        for chunk in chunks:
            knowledge_chunk = to_susan_knowledge_chunk(chunk, company_id=company_id)
            if knowledge_chunk.data_type == "docs":
                knowledge_chunk.data_type = "fitness_docs"
            elif knowledge_chunk.data_type == "analysis":
                knowledge_chunk.data_type = "fitness_analysis"
            elif knowledge_chunk.data_type in {"fitness", "nutrition", "recovery", "mindfulness"}:
                knowledge_chunk.data_type = "fitness_app_profile"
            else:
                knowledge_chunk.data_type = data_type
            knowledge_chunk.agent_id = agent_id
            knowledge_chunks.append(knowledge_chunk)

        return self.retriever.store_chunks(knowledge_chunks)
