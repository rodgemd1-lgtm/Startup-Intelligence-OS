"""Supabase pgvector retrieval and storage."""
from __future__ import annotations
import json
from supabase import create_client, Client
from rag_engine.embedder import Embedder
from susan_core.config import config
from susan_core.schemas import KnowledgeChunk


class Retriever:
    """Handles vector storage and similarity search via Supabase pgvector."""

    def __init__(self):
        self.supabase: Client = create_client(config.supabase_url, config.supabase_key)
        self.embedder = Embedder()

    def store_chunks(self, chunks: list[KnowledgeChunk]) -> int:
        """Embed and store chunks in Supabase. Returns count stored."""
        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed(texts)

        rows = []
        for chunk, embedding in zip(chunks, embeddings):
            rows.append({
                "content": chunk.content,
                "embedding": embedding,
                "company_id": chunk.company_id,
                "agent_id": chunk.agent_id,
                "access_level": chunk.access_level,
                "data_type": chunk.data_type,
                "source": chunk.source,
                "source_url": chunk.source_url,
                "metadata": chunk.metadata,
            })

        # Insert in batches of 100
        stored = 0
        for i in range(0, len(rows), 100):
            batch = rows[i:i + 100]
            self.supabase.table("knowledge_chunks").insert(batch).execute()
            stored += len(batch)

        return stored

    def search(
        self,
        query: str,
        company_id: str,
        data_types: list[str] | None = None,
        agent_id: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Similarity search against the knowledge base."""
        query_embedding = self.embedder.embed_query(query)

        result = self.supabase.rpc("search_knowledge", {
            "query_embedding": query_embedding,
            "filter_company": company_id,
            "filter_access": ["public", "company"],
            "filter_types": data_types,
            "filter_agent": agent_id,
            "match_count": top_k,
        }).execute()

        return result.data if result.data else []

    def count_chunks(self, company_id: str | None = None) -> int:
        """Count total chunks, optionally filtered by company."""
        query = self.supabase.table("knowledge_chunks").select("id", count="exact")
        if company_id:
            query = query.eq("company_id", company_id)
        result = query.execute()
        return result.count or 0

    def delete_chunks(
        self,
        company_id: str,
        data_type: str | None = None,
    ) -> int:
        """Delete chunks by company and optionally data type."""
        query = self.supabase.table("knowledge_chunks").delete().eq("company_id", company_id)
        if data_type:
            query = query.eq("data_type", data_type)
        result = query.execute()
        return len(result.data) if result.data else 0
