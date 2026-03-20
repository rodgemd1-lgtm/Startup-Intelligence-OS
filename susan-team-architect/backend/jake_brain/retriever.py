"""Composite search across all 4 memory layers via jake_brain_search RPC."""
from __future__ import annotations

from datetime import datetime

from rag_engine.embedder import Embedder
from susan_core.config import config as susan_config
from supabase import create_client, Client
from jake_brain.store import BrainStore


class BrainRetriever:
    """Search Jake's brain with composite ranking across all memory layers."""

    def __init__(self, store: BrainStore | None = None):
        self.store = store or BrainStore()
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )
        self.embedder = Embedder()

    def search(
        self,
        query: str,
        project: str | None = None,
        people: list[str] | None = None,
        time_start: datetime | str | None = None,
        time_end: datetime | str | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        """Composite search across all 4 memory layers.

        Returns results ranked by: similarity x confidence x layer_weight x recency x access_boost
        """
        query_embedding = self.embedder.embed_query(query)

        if isinstance(time_start, datetime):
            time_start = time_start.isoformat()
        if isinstance(time_end, datetime):
            time_end = time_end.isoformat()

        result = self.supabase.rpc("jake_brain_search", {
            "query_embedding": query_embedding,
            "search_project": project,
            "search_people": people,
            "search_time_start": time_start,
            "search_time_end": time_end,
            "match_count": top_k,
        }).execute()

        memories = result.data or []

        # Bump access count for returned episodic memories
        for mem in memories:
            if mem["layer"] == "episodic":
                try:
                    self.store.bump_episodic_access(mem["id"])
                except Exception:
                    pass  # non-critical

        return memories

    def recall(
        self,
        query: str,
        project: str | None = None,
        top_k: int = 5,
    ) -> str:
        """High-level recall — returns a formatted string of relevant memories.

        Use this for injecting context into conversations.
        """
        memories = self.search(query, project=project, top_k=top_k)
        if not memories:
            return ""

        lines = []
        for mem in memories:
            layer = mem["layer"].upper()
            score = mem["composite_score"]
            content = mem["content"][:300]
            lines.append(f"[{layer} score={score:.3f}] {content}")

        return "\n".join(lines)

    def recall_about_person(self, person_name: str, top_k: int = 10) -> list[dict]:
        """Recall everything Jake knows about a person.

        Combines: entity lookup + graph traversal + memory search.
        """
        results = {
            "entity": None,
            "graph": [],
            "memories": [],
        }

        # Entity lookup
        entity = self.store.find_entity(person_name)
        if not entity:
            # Try title case
            entity = self.store.find_entity(person_name.title())
        results["entity"] = entity

        # Graph traversal
        if entity:
            results["graph"] = self.store.get_entity_graph(entity["id"], max_depth=2)

        # Memory search
        results["memories"] = self.search(
            query=f"about {person_name}",
            people=[person_name.lower()],
            top_k=top_k,
        )

        return results

    def recall_time_range(
        self,
        query: str,
        time_start: datetime | str,
        time_end: datetime | str,
        top_k: int = 10,
    ) -> list[dict]:
        """Recall memories from a specific time range.

        Enables: "what happened last Tuesday?" style queries.
        """
        return self.search(
            query=query,
            time_start=time_start,
            time_end=time_end,
            top_k=top_k,
        )

    def get_brain_summary(self) -> dict:
        """Get a summary of Jake's brain state."""
        stats = self.store.brain_stats()

        # Get top semantic facts
        top_facts = self.store.get_active_semantic(limit=10)

        return {
            "stats": stats,
            "top_facts": [f["content"][:100] for f in top_facts],
        }
