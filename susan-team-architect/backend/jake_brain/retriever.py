"""Composite search across all 4 memory layers via jake_brain_search RPC."""
from __future__ import annotations

from datetime import datetime, timezone

from rag_engine.embedder import Embedder
from susan_core.config import config as susan_config
from supabase import create_client, Client
from jake_brain.store import BrainStore

DECAY_MAX_DAYS = 90  # Memories not accessed in 90+ days get 0.7x weight


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

        # Apply memory decay to composite_score before ranking
        memories = self._apply_decay(memories)

        # Bump access count for returned memories (2d: access tracking)
        for mem in memories:
            try:
                if mem["layer"] == "episodic":
                    self.store.bump_episodic_access(mem["id"])
                elif mem["layer"] == "semantic":
                    self.store.bump_semantic_access(mem["id"])
            except Exception:
                pass  # non-critical

        # Corrections always win — pin them to the top regardless of composite_score
        # This ensures Mike's explicit corrections override any conflicting memories
        # "rule" category = corrections (permanently override other memories)
        corrections = [
            m for m in memories
            if m.get("category") == "rule"
            and m.get("metadata", {}).get("source") == "mike_explicit"
        ]
        non_corrections = [m for m in memories if m not in corrections]
        if corrections:
            # Pin corrections first, then the rest by original ranking
            memories = corrections + non_corrections

        return memories

    def _apply_decay(self, memories: list[dict]) -> list[dict]:
        """Apply recency-based decay to composite_score.

        Formula: score = composite_score * (0.7 + 0.3 * recency_factor)
        recency_factor = max(0, 1 - days_since_access / DECAY_MAX_DAYS)

        Memories not accessed in 90+ days get 0.7x weight.
        Freshly accessed memories keep full weight.
        """
        now = datetime.now(timezone.utc)

        for mem in memories:
            # Use last_accessed_at if available, else fall back to created_at
            ts = mem.get("last_accessed_at") or mem.get("created_at") or mem.get("occurred_at")
            if not ts:
                mem["composite_score"] = mem.get("composite_score", 0.5) * 0.7
                continue

            try:
                # Parse timestamp (handle Z suffix)
                ts_str = str(ts).replace("Z", "+00:00")
                last_access = datetime.fromisoformat(ts_str)
                if last_access.tzinfo is None:
                    last_access = last_access.replace(tzinfo=timezone.utc)
                days_since = (now - last_access).total_seconds() / 86400
                recency_factor = max(0.0, 1.0 - days_since / DECAY_MAX_DAYS)
                decay_multiplier = 0.7 + 0.3 * recency_factor
                mem["composite_score"] = mem.get("composite_score", 0.5) * decay_multiplier
                mem["decay_applied"] = round(decay_multiplier, 3)
            except (ValueError, TypeError):
                mem["composite_score"] = mem.get("composite_score", 0.5) * 0.7

        # Re-sort by adjusted score (keep corrections at top, handled after)
        memories.sort(key=lambda m: m.get("composite_score", 0), reverse=True)
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
