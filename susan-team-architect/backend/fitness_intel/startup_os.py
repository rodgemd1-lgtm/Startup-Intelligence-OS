"""Compatibility exports for Startup-Intelligence-OS."""
from __future__ import annotations

from .schemas import DocumentChunk
from susan_core.schemas import KnowledgeChunk


def to_startup_os_knowledge_chunk(chunk: DocumentChunk) -> dict:
    return {
        "content": chunk.content,
        "company_id": "shared",
        "agent_id": None,
        "access_level": "public",
        "data_type": chunk.category or "fitness_intelligence",
        "source": chunk.source_type,
        "source_url": chunk.source_path,
        "metadata": {
            "entity_id": chunk.entity_id,
            "entity_type": chunk.entity_type,
            **chunk.metadata,
        },
    }


def to_susan_knowledge_chunk(chunk: DocumentChunk, company_id: str = "shared") -> KnowledgeChunk:
    payload = to_startup_os_knowledge_chunk(chunk)
    return KnowledgeChunk(
        content=payload["content"],
        company_id=company_id,
        agent_id=payload["agent_id"],
        access_level=payload["access_level"],
        data_type=payload["data_type"],
        source=payload["source"],
        source_url=payload["source_url"],
        metadata=payload["metadata"],
    )
