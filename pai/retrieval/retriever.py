"""Unified memory retrieval — replaces broken brain_search Python wrapper.

Search strategy:
1. Supabase RPC jake_brain_search — composite vector search across all layers
2. Supabase keyword search — full-text fallback for when no embeddings available
3. Entity graph traversal — jake_entity_graph RPC for knowledge graph queries

The jake_brain_search RPC in Supabase is well-designed (composite ranking with
recency decay, importance weighting, cross-layer search). The bug was in the
Python wrapper that called it (JSON serialization of embeddings). This module
fixes the wrapper while preserving the RPC.
"""
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

from supabase import create_client, Client


def _load_env():
    """Load .env from susan backend if not already in environment."""
    if os.environ.get("SUPABASE_URL"):
        return
    env_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "susan-team-architect", "backend", ".env"
    )
    if os.path.exists(env_path):
        for line in open(env_path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


class PAIRetriever:
    """Unified retrieval across all memory tiers.

    Uses the jake_brain_search Supabase RPC for vector similarity search
    with composite ranking. Falls back to keyword search when no Voyage
    API key is available for query embedding.
    """

    def __init__(self, supabase_client: Optional[Client] = None):
        _load_env()
        self.client = supabase_client or create_client(
            os.environ["SUPABASE_URL"],
            os.environ.get("SUPABASE_SERVICE_KEY", os.environ.get("SUPABASE_KEY", "")),
        )
        self._embedder = None

    @property
    def embedder(self):
        """Lazy-load embedder (requires Voyage AI key)."""
        if self._embedder is None:
            try:
                sys.path.insert(0, os.path.join(
                    os.path.dirname(__file__), "..", "..", "susan-team-architect", "backend"
                ))
                from rag_engine.embedder import Embedder
                self._embedder = Embedder()
            except Exception:
                self._embedder = False  # Mark as unavailable
        return self._embedder if self._embedder is not False else None

    def search(
        self,
        query: str,
        limit: int = 10,
        project: Optional[str] = None,
        people: Optional[list] = None,
        recency_days: Optional[int] = None,
    ) -> list:
        """Search across all memory tiers.

        Tries vector search first (requires Voyage AI key for query embedding).
        Falls back to keyword search if embeddings unavailable.

        Returns list of dicts with: id, content, layer, similarity, importance,
        composite_score, metadata
        """
        results = []

        # Try vector search via RPC
        if self.embedder:
            results = self._vector_search(query, limit, project, people, recency_days)

        # Fall back to keyword search
        if not results:
            results = self._keyword_search(query, limit, project, recency_days)

        return results

    def _vector_search(
        self, query: str, limit: int, project: Optional[str],
        people: Optional[list], recency_days: Optional[int]
    ) -> list:
        """Vector search using jake_brain_search RPC."""
        try:
            query_embedding = self.embedder.embed_query(query)

            # Build RPC params — the key fix: ensure embedding is a plain list
            params = {
                "query_embedding": list(query_embedding) if hasattr(query_embedding, '__iter__') else query_embedding,
                "match_count": limit,
            }
            if project:
                params["search_project"] = project
            if people:
                params["search_people"] = people
            if recency_days:
                params["search_time_start"] = (
                    datetime.utcnow() - timedelta(days=recency_days)
                ).isoformat()

            result = self.client.rpc("jake_brain_search", params).execute()
            return result.data or []

        except Exception as e:
            print(f"[PAIRetriever] Vector search error: {e}")
            return []

    def _keyword_search(
        self, query: str, limit: int, project: Optional[str],
        recency_days: Optional[int]
    ) -> list:
        """Keyword search fallback — searches content across all tables."""
        results = []
        search_term = f"%{query}%"

        tables = [
            ("jake_episodic", "episodic"),
            ("jake_semantic", "semantic"),
            ("jake_procedural", "procedural"),
        ]

        for table, layer in tables:
            try:
                q = (
                    self.client.table(table)
                    .select("id, content, metadata, created_at")
                    .ilike("content", search_term)
                    .limit(limit)
                )
                if project and table == "jake_episodic":
                    q = q.eq("project", project)
                if recency_days:
                    cutoff = (datetime.utcnow() - timedelta(days=recency_days)).isoformat()
                    q = q.gte("created_at", cutoff)

                data = q.order("created_at", desc=True).execute()

                for row in data.data or []:
                    results.append({
                        "id": row["id"],
                        "content": row["content"],
                        "layer": layer,
                        "similarity": 0.5,  # No vector similarity for keyword
                        "importance": 0.5,
                        "composite_score": 0.5,
                        "metadata": row.get("metadata", {}),
                    })
            except Exception as e:
                print(f"[PAIRetriever] Keyword search error on {table}: {e}")

        return results[:limit]

    def search_entities(self, name: str) -> list:
        """Search entity graph by name."""
        try:
            result = (
                self.client.table("jake_entities")
                .select("id, name, entity_type, properties, importance")
                .ilike("name", f"%{name}%")
                .eq("is_active", True)
                .execute()
            )
            return result.data or []
        except Exception as e:
            print(f"[PAIRetriever] Entity search error: {e}")
            return []

    def traverse_graph(self, entity_id: str, max_depth: int = 2) -> list:
        """Traverse knowledge graph from an entity."""
        try:
            result = self.client.rpc("jake_entity_graph", {
                "root_entity_id": entity_id,
                "max_depth": max_depth,
            }).execute()
            return result.data or []
        except Exception as e:
            print(f"[PAIRetriever] Graph traversal error: {e}")
            return []

    def get_stats(self) -> dict:
        """Get memory statistics across all tables."""
        stats = {}
        for table in ["jake_episodic", "jake_semantic", "jake_procedural",
                       "jake_entities", "jake_relationships", "jake_goals"]:
            try:
                r = self.client.table(table).select("id", count="exact").limit(1).execute()
                stats[table] = r.count
            except:
                stats[table] = "error"
        return stats
