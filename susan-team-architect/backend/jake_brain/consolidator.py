"""Consolidation pipeline — promotes memories between layers.

Working → Episodic (session end or high importance)
Episodic → Semantic (3+ references to same fact)
Patterns → Procedural (detected across 3+ episodes, requires approval)
"""
from __future__ import annotations

from datetime import datetime, timezone
from collections import Counter

from jake_brain.store import BrainStore
from jake_brain.config import brain_config


class Consolidator:
    """Promotes memories between layers based on evidence thresholds."""

    def __init__(self, store: BrainStore | None = None):
        self.store = store or BrainStore()

    def consolidate_session(self, session_id: str) -> dict:
        """Consolidate a completed session — promote working → episodic.

        Call this at session end or when working memory has high-importance items.
        """
        stats = {"promoted": 0, "skipped": 0}

        working_memories = self.store.get_session_working(session_id)
        for mem in working_memories:
            if mem["importance"] >= brain_config.working_auto_promote_importance:
                # Auto-promote high-importance items
                episodic = self.store.store_episodic(
                    content=mem["content"],
                    occurred_at=mem["created_at"],
                    memory_type=mem["memory_type"],
                    session_id=session_id,
                    importance=mem["importance"],
                    source="working_promotion",
                    source_type="hermes",
                    metadata={**mem.get("metadata", {}), "promoted_from": "working"},
                )
                self.store.promote_working(mem["id"], "episodic", episodic.get("id", ""))
                stats["promoted"] += 1
            else:
                stats["skipped"] += 1

        return stats

    def promote_episodic_to_semantic(self, batch_size: int = 100) -> dict:
        """Scan episodic memories and promote recurring facts to semantic.

        A fact is promoted when it appears in 3+ different episodes.
        Uses content similarity to group related episodes.
        """
        stats = {"promoted": 0, "reinforced": 0, "scanned": 0}

        unpromoted = self.store.get_unpromoted_episodic(limit=batch_size)
        stats["scanned"] = len(unpromoted)

        if not unpromoted:
            return stats

        # Group by similarity — find clusters of related episodes
        # Simple approach: check each against existing semantic facts
        for episode in unpromoted:
            # Check if this episode's content matches an existing semantic fact
            similar_facts = self.store.find_similar_semantic(
                episode["content"],
                threshold=brain_config.contradiction_similarity_threshold,
            )

            if similar_facts:
                # Reinforce existing semantic fact with this episode
                best_match = similar_facts[0]
                self.store.reinforce_semantic(best_match["id"], episode["id"])
                stats["reinforced"] += 1
            else:
                # Check if enough episodes share this theme to warrant promotion
                # For now, track in metadata — future: cluster analysis
                pass

        return stats

    def detect_contradictions(self) -> list[dict]:
        """Scan semantic facts for contradictions.

        Two facts contradict if they're highly similar but have different content.
        Returns pairs that need Mike's review.
        """
        contradictions = []
        active_facts = self.store.get_active_semantic(limit=200)

        # Compare each pair (O(n^2) but n is small for now)
        for i, fact_a in enumerate(active_facts):
            for fact_b in active_facts[i + 1:]:
                if fact_a["category"] == fact_b["category"]:
                    # Same category — check similarity
                    # We'd need to compare embeddings, but we don't have them in the select
                    # For now, use text overlap as a proxy
                    overlap = self._text_overlap(fact_a["content"], fact_b["content"])
                    if overlap > 0.5 and fact_a["content"] != fact_b["content"]:
                        contradictions.append({
                            "fact_a": fact_a,
                            "fact_b": fact_b,
                            "overlap": overlap,
                        })

        return contradictions

    def _text_overlap(self, text_a: str, text_b: str) -> float:
        """Simple word overlap ratio between two texts."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        return len(intersection) / min(len(words_a), len(words_b))

    def run_full_consolidation(self) -> dict:
        """Run all consolidation steps. Call from nightly cron."""
        results = {
            "episodic_to_semantic": self.promote_episodic_to_semantic(),
            "contradictions": len(self.detect_contradictions()),
        }
        return results
