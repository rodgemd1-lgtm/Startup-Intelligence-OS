"""TIMG Phase 3 -- Runtime Tip Retrieval.

Given a MemoryQuery, finds the most relevant MemoryTips from the TipStore
using keyword-overlap scoring (with future embedding support), boosted by
confidence and access-count signals.

The retriever also provides a markdown formatter for injecting retrieved tips
directly into agent system prompts.
"""
from __future__ import annotations

import math
import re

from .schemas import MemoryQuery, MemoryTip
from .tip_store import TipStore


def _tokenize(text: str) -> set[str]:
    """Simple tokenizer producing lowercase alphanumeric tokens."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class TipRetriever:
    """Retrieves and ranks MemoryTips relevant to a runtime query."""

    def __init__(self, store: TipStore) -> None:
        self.store = store

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def score_relevance(self, tip: MemoryTip, query: MemoryQuery) -> float:
        """Compute a composite relevance score for a tip against a query.

        Scoring components:
          1. **Text similarity** (Jaccard overlap on keyword tokens) -- base signal.
          2. **Confidence boost** -- higher-confidence tips rank higher.
          3. **Popularity boost** -- tips that have been accessed more get a log boost.
          4. **Domain match bonus** -- exact domain match adds a flat bonus.

        All components are combined into a 0-1 score.
        """
        # -- Text similarity (0..1) --
        query_tokens = _tokenize(query.query_text)
        tip_tokens = _tokenize(tip.content) | _tokenize(" ".join(tip.tags))
        if not query_tokens or not tip_tokens:
            text_sim = 0.0
        else:
            intersection = query_tokens & tip_tokens
            union = query_tokens | tip_tokens
            text_sim = len(intersection) / len(union)

        # -- Confidence component (0..1) --
        conf = tip.confidence

        # -- Popularity boost: logarithmic (0..~0.15) --
        pop_boost = min(math.log1p(tip.access_count) * 0.05, 0.15)

        # -- Domain match bonus --
        domain_bonus = 0.0
        if query.task_domain and query.task_domain.lower() == tip.task_domain.lower():
            domain_bonus = 0.15

        # Weighted combination
        score = (
            0.50 * text_sim
            + 0.25 * conf
            + pop_boost
            + domain_bonus
        )

        return min(score, 1.0)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(self, query: MemoryQuery) -> list[MemoryTip]:
        """Find the top-N most relevant tips for a query.

        Steps:
          1. Filter by domain and tip_type if specified in the query.
          2. Score remaining tips.
          3. Filter by min_confidence.
          4. Return top max_results sorted by relevance descending.
        """
        # Pre-filter
        candidates = self.store.list_tips()

        if query.task_domain:
            domain_lower = query.task_domain.lower()
            candidates = [
                t for t in candidates
                if t.task_domain.lower() == domain_lower
            ]

        if query.tip_types:
            allowed = {tt.lower() for tt in query.tip_types}
            candidates = [
                t for t in candidates
                if t.tip_type.lower() in allowed
            ]

        # Filter by min confidence
        candidates = [t for t in candidates if t.confidence >= query.min_confidence]

        # Score and rank
        scored: list[tuple[float, MemoryTip]] = []
        for tip in candidates:
            s = self.score_relevance(tip, query)
            scored.append((s, tip))

        scored.sort(key=lambda pair: pair[0], reverse=True)

        top_tips = [tip for _, tip in scored[: query.max_results]]

        # Track access for returned tips
        for tip in top_tips:
            self.store.increment_access(tip.id)

        return top_tips

    # ------------------------------------------------------------------
    # Prompt injection formatting
    # ------------------------------------------------------------------

    def format_for_injection(self, tips: list[MemoryTip]) -> str:
        """Format retrieved tips as markdown suitable for prompt injection.

        Output structure:
            ## Relevant Experience (from prior runs)
            ### Strategy: <content>
            Source: <agent> on <date>, Confidence: <score>
        """
        if not tips:
            return ""

        lines: list[str] = ["## Relevant Experience (from prior runs)", ""]
        for tip in tips:
            type_label = tip.tip_type.capitalize()
            lines.append(f"### {type_label}: {tip.content}")
            lines.append(
                f"Source: {tip.source_agent} on {tip.created_at}, "
                f"Confidence: {tip.confidence:.2f}"
            )
            if tip.tags:
                lines.append(f"Tags: {', '.join(tip.tags)}")
            lines.append("")

        return "\n".join(lines)
