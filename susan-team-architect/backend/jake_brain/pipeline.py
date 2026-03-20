"""End-to-end brain pipeline: text in → extract → embed → store → graph → consolidate.

This is the main entry point for feeding Jake's brain.
"""
from __future__ import annotations

from datetime import datetime, timezone

from jake_brain.store import BrainStore
from jake_brain.extractor import Extractor
from jake_brain.graph import KnowledgeGraph
from jake_brain.retriever import BrainRetriever
from jake_brain.consolidator import Consolidator


class BrainPipeline:
    """Orchestrates the full brain pipeline."""

    def __init__(self):
        self.store = BrainStore()
        self.extractor = Extractor()
        self.graph = KnowledgeGraph(self.store)
        self.retriever = BrainRetriever(self.store)
        self.consolidator = Consolidator(self.store)

    def ingest_conversation(
        self,
        text: str,
        session_id: str | None = None,
        source: str | None = None,
        source_type: str = "hermes",
        occurred_at: datetime | str | None = None,
    ) -> dict:
        """Ingest a conversation chunk into Jake's brain.

        This is the primary entry point. Call after every Hermes conversation.

        Returns summary of what was stored and extracted.
        """
        if not occurred_at:
            occurred_at = datetime.now(timezone.utc)
        if isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at)

        # 1. EXTRACT — pull entities, decisions, patterns from text
        extraction = self.extractor.extract(text)

        # 2. STORE — write to episodic memory
        episodic = self.store.store_episodic(
            content=text,
            occurred_at=occurred_at,
            memory_type="conversation",
            project=extraction.project,
            importance=extraction.importance,
            people=extraction.people,
            topics=extraction.topics,
            session_id=session_id,
            source=source,
            source_type=source_type,
            metadata={
                "decisions": extraction.decisions[:5],
                "action_items": extraction.action_items[:5],
                "patterns": extraction.patterns[:3],
                "preferences": extraction.preferences[:3],
            },
        )

        episode_id = episodic.get("id")

        # 3. GRAPH — update knowledge graph with extracted entities
        graph_result = self.graph.process_extraction(extraction, episode_id=episode_id)

        # 4. SEMANTIC — if decisions or preferences found, store directly as semantic
        semantic_stored = []
        for decision in extraction.decisions:
            sem = self.store.store_semantic(
                content=decision,
                category="decision",
                confidence=0.7,
                source_episodes=[episode_id] if episode_id else [],
                project=extraction.project,
                topics=extraction.topics,
            )
            semantic_stored.append(sem.get("id"))

        for pref in extraction.preferences:
            sem = self.store.store_semantic(
                content=pref,
                category="preference",
                confidence=0.6,
                source_episodes=[episode_id] if episode_id else [],
                topics=extraction.topics,
            )
            semantic_stored.append(sem.get("id"))

        # 5. PROCEDURAL — if patterns found, store as unapproved procedural
        procedural_stored = []
        for pattern in extraction.patterns:
            proc = self.store.store_procedural(
                content=pattern,
                pattern_type="rule",
                domain=extraction.project,
                confidence=0.5,
                source_episodes=[episode_id] if episode_id else [],
                approved=False,
            )
            procedural_stored.append(proc.get("id"))

        return {
            "episode_id": episode_id,
            "extraction": {
                "people": extraction.people,
                "topics": extraction.topics,
                "decisions": len(extraction.decisions),
                "action_items": len(extraction.action_items),
                "patterns": len(extraction.patterns),
                "preferences": len(extraction.preferences),
                "project": extraction.project,
                "importance": extraction.importance,
            },
            "graph": graph_result,
            "semantic_stored": len(semantic_stored),
            "procedural_stored": len(procedural_stored),
        }

    def ingest_batch(
        self,
        chunks: list[dict],
        source: str | None = None,
        source_type: str = "ingestion",
    ) -> dict:
        """Ingest multiple text chunks (from file ingestion, conversation replay, etc.).

        Each chunk dict should have: content, occurred_at (optional), session_id (optional)
        """
        total = {"episodes": 0, "semantic": 0, "procedural": 0}

        for chunk in chunks:
            result = self.ingest_conversation(
                text=chunk["content"],
                session_id=chunk.get("session_id"),
                source=source,
                source_type=source_type,
                occurred_at=chunk.get("occurred_at"),
            )
            total["episodes"] += 1
            total["semantic"] += result["semantic_stored"]
            total["procedural"] += result["procedural_stored"]

        return total

    def recall(self, query: str, project: str | None = None, top_k: int = 5) -> str:
        """Recall relevant memories for a query. Returns formatted context string."""
        return self.retriever.recall(query, project=project, top_k=top_k)

    def recall_person(self, name: str) -> dict:
        """Recall everything about a person."""
        return self.retriever.recall_about_person(name)

    def consolidate(self) -> dict:
        """Run consolidation pipeline (nightly cron)."""
        return self.consolidator.run_full_consolidation()

    def seed(self) -> dict:
        """Seed initial entities and relationships. Run once after table creation."""
        return self.graph.seed_initial_entities()

    def stats(self) -> dict:
        """Get brain statistics."""
        return self.retriever.get_brain_summary()
