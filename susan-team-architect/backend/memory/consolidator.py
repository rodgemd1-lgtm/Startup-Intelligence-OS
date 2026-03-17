"""Mem0-style Memory Consolidation.

Runs periodic maintenance over the tip store to keep memory quality high:
  - **Merge** similar tips (deduplication via Jaccard similarity)
  - **Decay** old, unused tips (reduce confidence over time)
  - **Promote** frequently-accessed tips (boost confidence)
  - **Prune** tips that fall below a minimum confidence threshold

The consolidator produces a human-readable summary after each cycle, and
returns structured stats on all changes made.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .graph_builder import KnowledgeGraphBuilder
from .tip_store import TipStore


def _parse_iso(ts: str) -> datetime | None:
    """Try to parse an ISO timestamp string."""
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _days_since(ts: str) -> float:
    """Return fractional days between now and a timestamp string."""
    dt = _parse_iso(ts)
    if dt is None:
        return 0.0
    now = datetime.now(timezone.utc)
    delta = now - dt
    return max(delta.total_seconds() / 86400.0, 0.0)


class MemoryConsolidator:
    """Runs full consolidation cycles over the memory system."""

    def __init__(
        self,
        tip_store: TipStore,
        graph_builder: KnowledgeGraphBuilder,
    ) -> None:
        self.tip_store = tip_store
        self.graph_builder = graph_builder

    # ------------------------------------------------------------------
    # Full consolidation
    # ------------------------------------------------------------------

    def consolidate(self) -> dict:
        """Run a complete consolidation cycle and return change stats.

        Steps:
          1. Merge similar tips (deduplication)
          2. Decay old, unused tips
          3. Promote frequently-accessed tips
          4. Prune below threshold
          5. Return stats on changes made
        """
        stats: dict[str, int | float | str] = {}

        # 1. Merge
        all_tips = self.tip_store.list_tips()
        before_count = len(all_tips)
        merged = self.tip_store.merge_similar_tips(all_tips, similarity_threshold=0.85)
        stats["tips_before_merge"] = before_count
        stats["tips_after_merge"] = len(merged)
        stats["tips_merged"] = before_count - len(merged)

        # 2. Decay old, unused
        decayed = self.decay_unused(days_threshold=30, decay_rate=0.1)
        stats["tips_decayed"] = decayed

        # 3. Promote popular
        promoted = self.promote_popular(access_threshold=5, boost=0.1)
        stats["tips_promoted"] = promoted

        # 4. Prune low confidence
        pruned = self.tip_store.prune_low_confidence(threshold=0.2)
        stats["tips_pruned"] = pruned

        # Final count
        final = self.tip_store.get_stats()
        stats["tips_remaining"] = final.total_tips
        stats["avg_confidence"] = final.avg_confidence

        return stats

    # ------------------------------------------------------------------
    # Decay
    # ------------------------------------------------------------------

    def decay_unused(
        self,
        days_threshold: int = 30,
        decay_rate: float = 0.1,
    ) -> int:
        """Reduce confidence of tips that have not been accessed recently.

        A tip is considered stale if:
          - It has a last_accessed timestamp older than days_threshold, OR
          - It has never been accessed and its created_at is older than
            days_threshold.

        The confidence is reduced by decay_rate, clamped to [0, 1].

        Returns the number of tips that were decayed.
        """
        count = 0
        for tip in self.tip_store.list_tips():
            ref_ts = tip.last_accessed or tip.created_at
            age_days = _days_since(ref_ts)

            if age_days < days_threshold:
                continue

            # Apply decay
            new_conf = max(tip.confidence - decay_rate, 0.0)
            if new_conf != tip.confidence:
                tip.confidence = round(new_conf, 4)
                self.tip_store.save_tip(tip)
                count += 1

        return count

    # ------------------------------------------------------------------
    # Promote
    # ------------------------------------------------------------------

    def promote_popular(
        self,
        access_threshold: int = 5,
        boost: float = 0.1,
    ) -> int:
        """Boost confidence of tips that are frequently accessed.

        A tip qualifies if its access_count >= access_threshold.  Confidence
        is increased by boost, clamped to [0, 1].

        Returns the number of tips promoted.
        """
        count = 0
        for tip in self.tip_store.list_tips():
            if tip.access_count < access_threshold:
                continue

            new_conf = min(tip.confidence + boost, 1.0)
            if new_conf != tip.confidence:
                tip.confidence = round(new_conf, 4)
                self.tip_store.save_tip(tip)
                count += 1

        return count

    # ------------------------------------------------------------------
    # Summary report
    # ------------------------------------------------------------------

    def generate_summary(self) -> str:
        """Produce a human-readable consolidation report."""
        stats = self.tip_store.get_stats()

        lines: list[str] = [
            "# Memory Consolidation Report",
            "",
            f"**Total tips:** {stats.total_tips}",
            f"**Average confidence:** {stats.avg_confidence:.2f}",
            "",
            "## Tips by Type",
        ]
        for t, c in sorted(stats.tips_by_type.items()):
            lines.append(f"- {t}: {c}")

        lines.append("")
        lines.append("## Tips by Domain")
        for d, c in sorted(stats.tips_by_domain.items()):
            lines.append(f"- {d}: {c}")

        # Graph stats
        lines.append("")
        lines.append("## Knowledge Graph")
        lines.append(f"- Nodes: {len(self.graph_builder.nodes)}")
        lines.append(f"- Edges: {len(self.graph_builder.edges)}")

        return "\n".join(lines)
