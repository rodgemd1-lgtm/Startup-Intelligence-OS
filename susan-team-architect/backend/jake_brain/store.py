"""CRUD operations for all 6 brain tables."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from supabase import create_client, Client

from rag_engine.embedder import Embedder
from susan_core.config import config as susan_config
from jake_brain.config import brain_config


class BrainStore:
    """Handles storage and retrieval for Jake's cognitive memory tables."""

    def __init__(self):
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )
        self.embedder = Embedder()

    # ------------------------------------------------------------------
    # Working Memory
    # ------------------------------------------------------------------

    def store_working(
        self,
        content: str,
        session_id: str,
        memory_type: str = "note",
        importance: float = 0.5,
        metadata: dict | None = None,
    ) -> dict:
        """Store a working memory item (current session buffer)."""
        embedding = self.embedder.embed_query(content)
        row = {
            "content": content,
            "embedding": embedding,
            "session_id": session_id,
            "memory_type": memory_type,
            "importance": importance,
            "metadata": metadata or {},
        }
        result = self.supabase.table("jake_working").insert(row).execute()
        return result.data[0] if result.data else {}

    def get_session_working(self, session_id: str) -> list[dict]:
        """Get all working memories for a session."""
        result = (
            self.supabase.table("jake_working")
            .select("*")
            .eq("session_id", session_id)
            .eq("promoted", False)
            .order("created_at", desc=False)
            .execute()
        )
        return result.data or []

    def promote_working(self, working_id: str, target: str, promoted_id: str) -> None:
        """Mark a working memory as promoted."""
        self.supabase.table("jake_working").update({
            "promoted": True,
            "promoted_to": target,
            "promoted_id": promoted_id,
        }).eq("id", working_id).execute()

    # ------------------------------------------------------------------
    # Episodic Memory
    # ------------------------------------------------------------------

    def store_episodic(
        self,
        content: str,
        occurred_at: datetime | str,
        memory_type: str = "conversation",
        project: str | None = None,
        importance: float = 0.5,
        people: list[str] | None = None,
        topics: list[str] | None = None,
        session_id: str | None = None,
        source: str | None = None,
        source_type: str = "hermes",
        metadata: dict | None = None,
    ) -> dict:
        """Store an episodic memory (time-stamped event)."""
        if isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at)

        embedding = self.embedder.embed_query(content)
        row = {
            "content": content,
            "embedding": embedding,
            "occurred_at": occurred_at.isoformat(),
            "session_id": session_id,
            "memory_type": memory_type,
            "project": project,
            "importance": importance,
            "people": people or [],
            "topics": topics or [],
            "source": source,
            "source_type": source_type,
            "metadata": metadata or {},
        }
        result = self.supabase.table("jake_episodic").insert(row).execute()
        return result.data[0] if result.data else {}

    def store_episodic_batch(self, memories: list[dict]) -> int:
        """Store multiple episodic memories. Each dict must have 'content' and 'occurred_at'."""
        if not memories:
            return 0

        texts = [m["content"] for m in memories]
        embeddings = self.embedder.embed(texts, input_type="document")

        rows = []
        for mem, emb in zip(memories, embeddings):
            occurred = mem["occurred_at"]
            if isinstance(occurred, str):
                occurred = datetime.fromisoformat(occurred)
            rows.append({
                "content": mem["content"],
                "embedding": emb,
                "occurred_at": occurred.isoformat(),
                "session_id": mem.get("session_id"),
                "memory_type": mem.get("memory_type", "conversation"),
                "project": mem.get("project"),
                "importance": mem.get("importance", 0.5),
                "people": mem.get("people", []),
                "topics": mem.get("topics", []),
                "source": mem.get("source"),
                "source_type": mem.get("source_type", "hermes"),
                "metadata": mem.get("metadata", {}),
            })

        stored = 0
        for i in range(0, len(rows), brain_config.store_batch_size):
            batch = rows[i : i + brain_config.store_batch_size]
            self.supabase.table("jake_episodic").insert(batch).execute()
            stored += len(batch)
        return stored

    def bump_episodic_access(self, episodic_id: str) -> None:
        """Increment access count and update last_accessed_at when recalled."""
        existing = (
            self.supabase.table("jake_episodic")
            .select("access_count")
            .eq("id", episodic_id)
            .execute()
        )
        if not existing.data:
            return
        current_count = existing.data[0].get("access_count") or 0
        self.supabase.table("jake_episodic").update({
            "access_count": current_count + 1,
            "last_accessed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", episodic_id).execute()

    def bump_semantic_access(self, semantic_id: str) -> None:
        """Update last_accessed_at for a semantic fact when recalled."""
        self.supabase.table("jake_semantic").update({
            "last_accessed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", semantic_id).execute()

    def get_unpromoted_episodic(self, limit: int = 100) -> list[dict]:
        """Get episodic memories that haven't been promoted to semantic yet."""
        result = (
            self.supabase.table("jake_episodic")
            .select("*")
            .eq("promoted_to_semantic", False)
            .order("occurred_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    # ------------------------------------------------------------------
    # Semantic Memory
    # ------------------------------------------------------------------

    def check_contradiction(self, content: str, category: str) -> list[dict]:
        """Check if new semantic content contradicts existing active facts.

        Returns list of contradicting facts. Each has a 'contradiction_type' field.
        Contradiction = high similarity (similar topic) but opposing assertions.
        """
        similar = self.find_similar_semantic(
            content, threshold=brain_config.contradiction_similarity_threshold
        )
        contradictions = []
        content_lower = content.lower()

        # Negation markers — simple heuristic for contradiction detection
        negation_words = {"not", "never", "no", "don't", "doesn't", "isn't", "aren't", "won't", "can't", "shouldn't"}

        for fact in similar:
            if fact.get("category") != category:
                continue  # Different categories, less likely to contradict
            fact_lower = fact["content"].lower()

            # Check for negation asymmetry: one has negation words, other doesn't
            content_negated = bool(negation_words & set(content_lower.split()))
            fact_negated = bool(negation_words & set(fact_lower.split()))

            if content_negated != fact_negated:
                # One is negated, the other isn't — likely contradiction
                contradictions.append({
                    **fact,
                    "contradiction_type": "negation_asymmetry",
                })
            elif fact.get("confidence", 0) > 0.8 and len(content_lower) > 20:
                # High-confidence existing fact — flag for review
                contradictions.append({
                    **fact,
                    "contradiction_type": "high_confidence_conflict",
                })

        return contradictions

    def store_semantic(
        self,
        content: str,
        category: str,
        confidence: float = 0.7,
        source_episodes: list[str] | None = None,
        project: str | None = None,
        topics: list[str] | None = None,
        supersedes: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Store a semantic fact (abstracted knowledge).

        Automatically checks for contradictions before storing.
        If contradictions found, adds 'contradicted_by' metadata.
        Does NOT overwrite — contradictions are flagged, not suppressed.
        """
        embedding = self.embedder.embed_query(content)

        # Contradiction check before insert
        contradictions = self.check_contradiction(content, category)
        contradiction_ids = [c["id"] for c in contradictions]

        final_metadata = metadata or {}
        if contradiction_ids:
            final_metadata = {
                **final_metadata,
                "contradicted_by": contradiction_ids,
                "contradiction_types": [c["contradiction_type"] for c in contradictions],
                "contradiction_flagged_at": datetime.now(timezone.utc).isoformat(),
            }

        row = {
            "content": content,
            "embedding": embedding,
            "category": category,
            "confidence": confidence,
            "source_episodes": source_episodes or [],
            "evidence_count": len(source_episodes) if source_episodes else 1,
            "last_reinforced_at": datetime.now(timezone.utc).isoformat(),
            "project": project,
            "topics": topics or [],
            "supersedes": supersedes,
            "metadata": final_metadata,
        }
        result = self.supabase.table("jake_semantic").insert(row).execute()

        # If superseding, mark old fact
        if supersedes:
            self.supabase.table("jake_semantic").update({
                "superseded_by": result.data[0]["id"],
                "is_active": False,
            }).eq("id", supersedes).execute()

        return result.data[0] if result.data else {}

    def reinforce_semantic(self, semantic_id: str, new_episode_id: str) -> None:
        """Add evidence to an existing semantic fact."""
        existing = (
            self.supabase.table("jake_semantic")
            .select("source_episodes, evidence_count, confidence")
            .eq("id", semantic_id)
            .execute()
        )
        if not existing.data:
            return

        current = existing.data[0]
        episodes = current["source_episodes"] or []
        if new_episode_id not in episodes:
            episodes.append(new_episode_id)

        new_count = len(episodes)
        # Confidence increases with evidence, asymptotically approaching 1.0
        new_confidence = min(0.95, current["confidence"] + 0.05 * (1 - current["confidence"]))

        self.supabase.table("jake_semantic").update({
            "source_episodes": episodes,
            "evidence_count": new_count,
            "confidence": new_confidence,
            "last_reinforced_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", semantic_id).execute()

    def find_similar_semantic(self, content: str, threshold: float = 0.85) -> list[dict]:
        """Find semantic facts similar to given content (for dedup/contradiction)."""
        embedding = self.embedder.embed_query(content)
        result = self.supabase.rpc("jake_brain_search", {
            "query_embedding": embedding,
            "match_count": 5,
        }).execute()

        return [
            r for r in (result.data or [])
            if r["layer"] == "semantic" and r["similarity"] >= threshold
        ]

    def get_active_semantic(self, category: str | None = None, limit: int = 50) -> list[dict]:
        """Get active semantic facts, optionally filtered by category."""
        query = (
            self.supabase.table("jake_semantic")
            .select("*")
            .eq("is_active", True)
            .order("confidence", desc=True)
            .limit(limit)
        )
        if category:
            query = query.eq("category", category)
        return query.execute().data or []

    # ------------------------------------------------------------------
    # Procedural Memory
    # ------------------------------------------------------------------

    def store_procedural(
        self,
        content: str,
        pattern_type: str,
        domain: str | None = None,
        confidence: float = 0.6,
        source_episodes: list[str] | None = None,
        approved: bool = False,
        metadata: dict | None = None,
    ) -> dict:
        """Store a procedural pattern (learned workflow/rule)."""
        embedding = self.embedder.embed_query(content)
        row = {
            "content": content,
            "embedding": embedding,
            "pattern_type": pattern_type,
            "domain": domain,
            "confidence": confidence,
            "source_episodes": source_episodes or [],
            "approved": approved,
            "approved_at": datetime.now(timezone.utc).isoformat() if approved else None,
            "metadata": metadata or {},
        }
        result = self.supabase.table("jake_procedural").insert(row).execute()
        return result.data[0] if result.data else {}

    def approve_procedural(self, procedural_id: str) -> None:
        """Mike approves a learned pattern."""
        self.supabase.table("jake_procedural").update({
            "approved": True,
            "approved_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", procedural_id).execute()

    def record_outcome(self, procedural_id: str, success: bool) -> None:
        """Record whether applying this pattern succeeded or failed."""
        existing = (
            self.supabase.table("jake_procedural")
            .select("success_count, failure_count")
            .eq("id", procedural_id)
            .execute()
        )
        if not existing.data:
            return
        current = existing.data[0]
        field = "success_count" if success else "failure_count"
        self.supabase.table("jake_procedural").update({
            field: current[field] + 1,
            "last_applied_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", procedural_id).execute()

    # ------------------------------------------------------------------
    # Entities (Knowledge Graph Nodes)
    # ------------------------------------------------------------------

    def upsert_entity(
        self,
        name: str,
        entity_type: str,
        properties: dict | None = None,
        importance: float = 0.5,
        metadata: dict | None = None,
    ) -> dict:
        """Create or update an entity. Returns the entity row."""
        # Check if exists
        existing = (
            self.supabase.table("jake_entities")
            .select("*")
            .eq("name", name)
            .eq("entity_type", entity_type)
            .execute()
        )

        now = datetime.now(timezone.utc).isoformat()

        if existing.data:
            entity = existing.data[0]
            # Merge properties
            merged_props = {**(entity.get("properties") or {}), **(properties or {})}
            self.supabase.table("jake_entities").update({
                "properties": merged_props,
                "importance": max(entity["importance"], importance),
                "last_mentioned_at": now,
                "mention_count": entity["mention_count"] + 1,
                "metadata": {**(entity.get("metadata") or {}), **(metadata or {})},
            }).eq("id", entity["id"]).execute()
            entity["properties"] = merged_props
            return entity

        # Create new
        embed_text = f"{name} ({entity_type})"
        if properties:
            embed_text += " " + " ".join(f"{k}: {v}" for k, v in properties.items() if v)
        embedding = self.embedder.embed_query(embed_text)

        row = {
            "name": name,
            "entity_type": entity_type,
            "properties": properties or {},
            "embedding": embedding,
            "importance": importance,
            "last_mentioned_at": now,
            "mention_count": 1,
            "metadata": metadata or {},
        }
        result = self.supabase.table("jake_entities").insert(row).execute()
        return result.data[0] if result.data else {}

    def find_entity(self, name: str, entity_type: str | None = None) -> dict | None:
        """Find an entity by name (and optionally type)."""
        query = self.supabase.table("jake_entities").select("*").eq("name", name)
        if entity_type:
            query = query.eq("entity_type", entity_type)
        result = query.execute()
        return result.data[0] if result.data else None

    def search_entities(self, query: str, entity_type: str | None = None, limit: int = 10) -> list[dict]:
        """Semantic search for entities."""
        embedding = self.embedder.embed_query(query)
        # Use direct vector search on entities table
        # For now, use a simple approach — search by name pattern
        q = (
            self.supabase.table("jake_entities")
            .select("*")
            .eq("is_active", True)
            .order("importance", desc=True)
            .limit(limit)
        )
        if entity_type:
            q = q.eq("entity_type", entity_type)
        return q.execute().data or []

    def get_entity_graph(self, entity_id: str, max_depth: int = 2) -> list[dict]:
        """Traverse the knowledge graph from an entity."""
        result = self.supabase.rpc("jake_entity_graph", {
            "root_entity_id": entity_id,
            "max_depth": max_depth,
        }).execute()
        return result.data or []

    # ------------------------------------------------------------------
    # Relationships (Knowledge Graph Edges)
    # ------------------------------------------------------------------

    def upsert_relationship(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str,
        properties: dict | None = None,
        confidence: float = 0.8,
        source_episode_id: str | None = None,
    ) -> dict:
        """Create or update a relationship between entities."""
        existing = (
            self.supabase.table("jake_relationships")
            .select("*")
            .eq("source_entity_id", source_entity_id)
            .eq("target_entity_id", target_entity_id)
            .eq("relationship_type", relationship_type)
            .execute()
        )

        if existing.data:
            rel = existing.data[0]
            episodes = rel.get("source_episodes") or []
            if source_episode_id and source_episode_id not in episodes:
                episodes.append(source_episode_id)
            merged_props = {**(rel.get("properties") or {}), **(properties or {})}
            self.supabase.table("jake_relationships").update({
                "properties": merged_props,
                "confidence": max(rel["confidence"], confidence),
                "source_episodes": episodes,
            }).eq("id", rel["id"]).execute()
            return rel

        row = {
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relationship_type": relationship_type,
            "properties": properties or {},
            "confidence": confidence,
            "source_episodes": [source_episode_id] if source_episode_id else [],
        }
        result = self.supabase.table("jake_relationships").insert(row).execute()
        return result.data[0] if result.data else {}

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def brain_stats(self) -> dict:
        """Get counts across all brain tables."""
        tables = ["jake_working", "jake_episodic", "jake_semantic", "jake_procedural",
                  "jake_entities", "jake_relationships"]
        stats = {}
        for table in tables:
            result = self.supabase.table(table).select("id", count="exact").execute()
            stats[table.replace("jake_", "")] = result.count or 0
        return stats
