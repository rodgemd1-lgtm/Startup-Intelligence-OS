"""Consolidation pipeline — promotes memories between layers.

Working → Episodic (session end or high importance)
Episodic → Semantic (3+ references to same fact within 14 days)
Patterns → Procedural (detected across 3+ episodes, requires approval)
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from collections import Counter

from jake_brain.store import BrainStore
from jake_brain.config import brain_config

AUTO_PROMOTE_WINDOW_DAYS = 14  # Look for clusters within this window


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

        A fact is promoted when 3+ episodes with similar content exist within 14 days.
        Uses content similarity to group related episodes.
        """
        stats = {"promoted": 0, "reinforced": 0, "scanned": 0}

        unpromoted = self.store.get_unpromoted_episodic(limit=batch_size)
        stats["scanned"] = len(unpromoted)

        if not unpromoted:
            return stats

        # Group by similarity — find clusters of related episodes
        # Check each against existing semantic facts
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
                # Check if enough recent episodes share this theme to warrant promotion
                promoted = self._auto_promote_if_threshold_met(episode, unpromoted)
                if promoted:
                    stats["promoted"] += 1

        return stats

    def _auto_promote_if_threshold_met(
        self, anchor: dict, candidates: list[dict]
    ) -> bool:
        """Promote anchor episodic to semantic if 3+ similar episodes exist within 14 days.

        Returns True if promotion occurred.
        """
        threshold = brain_config.promotion_episode_threshold  # default 3
        window_cutoff = datetime.now(timezone.utc) - timedelta(days=AUTO_PROMOTE_WINDOW_DAYS)

        # Find candidates within the time window
        anchor_text = anchor["content"].lower()
        anchor_words = set(anchor_text.split())
        cluster_ids = [anchor["id"]]

        for candidate in candidates:
            if candidate["id"] == anchor["id"]:
                continue
            # Check time window
            occurred = candidate.get("occurred_at", "")
            if occurred:
                try:
                    occurred_dt = datetime.fromisoformat(occurred.replace("Z", "+00:00"))
                    if occurred_dt < window_cutoff:
                        continue
                except (ValueError, AttributeError):
                    continue

            # Check text overlap (simple proxy for semantic similarity without embedding call)
            cand_words = set(candidate["content"].lower().split())
            overlap = len(anchor_words & cand_words) / max(len(anchor_words), len(cand_words), 1)
            if overlap >= 0.3:  # 30% word overlap = related theme
                cluster_ids.append(candidate["id"])

        if len(cluster_ids) < threshold:
            return False

        # Synthesize a semantic fact from the cluster
        # Use the anchor content as the base (first representative episode)
        category = self._infer_category(anchor["content"])
        people = anchor.get("people") or []

        semantic = self.store.store_semantic(
            content=anchor["content"],
            category=category,
            confidence=0.6,  # start at 60%, grows with reinforcement
            source_episodes=cluster_ids[:threshold],
            project=anchor.get("project"),
            topics=anchor.get("topics") or [],
            metadata={
                "auto_promoted": True,
                "promoted_at": datetime.now(timezone.utc).isoformat(),
                "cluster_size": len(cluster_ids),
                "window_days": AUTO_PROMOTE_WINDOW_DAYS,
            },
        )

        if semantic.get("id"):
            # Mark the anchor episode as promoted
            self.store.supabase.table("jake_episodic").update({
                "promoted_to_semantic": True,
                "metadata": {
                    **(anchor.get("metadata") or {}),
                    "promoted_to_semantic_id": semantic["id"],
                },
            }).eq("id", anchor["id"]).execute()
            print(f"  → Auto-promoted episodic to semantic: {anchor['content'][:60]}... (cluster={len(cluster_ids)})")
            return True

        return False

    def _infer_category(self, content: str) -> str:
        """Infer semantic category from content keywords."""
        content_lower = content.lower()
        if any(w in content_lower for w in ["jacob", "alex", "james", "jen", "family", "kids"]):
            return "relationship"
        if any(w in content_lower for w in ["oracle", "health", "cohlmia", "myhelp"]):
            return "work"
        if any(w in content_lower for w in ["project", "build", "deploy", "code", "feature"]):
            return "project"
        if any(w in content_lower for w in ["prefer", "like", "hate", "want", "always", "never"]):
            return "preference"
        return "fact"

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
