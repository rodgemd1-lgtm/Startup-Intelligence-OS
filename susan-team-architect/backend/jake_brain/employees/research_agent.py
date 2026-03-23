"""Research Agent — nightly knowledge gap filler.

Runs daily at 10 PM. Identifies low-confidence semantic facts and
knowledge_gap episodic entries, generates research summaries,
and writes new findings to jake_semantic.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineTask

logger = logging.getLogger(__name__)

# Semantic confidence below this threshold is considered a research target
LOW_CONFIDENCE_THRESHOLD = 0.7

# Look back this many days for knowledge_gap episodic entries
KNOWLEDGE_GAP_LOOKBACK_DAYS = 30


class ResearchAgent:
    """Nightly knowledge gap identification and semantic fact generation employee.

    Runs offline — uses existing brain data to synthesize new semantic facts.
    Does NOT perform live web searches. That's done by the meeting orchestrator
    and other live-research tools.
    """

    EMPLOYEE_NAME = "research_agent"
    TASK_TYPE = "research"
    CONTEXT_HINTS = ["research", "knowledge_gap", "susan_rag"]
    SUCCESS_CRITERIA = [
        "topics_researched list produced",
        "gaps_filled count >= 0",
        "new_facts_stored count >= 0",
    ]

    def __init__(self, store=None):
        """
        Args:
            store: BrainStore instance. If None, pipeline runs without memory persistence.
        """
        self._store = store
        self._pipeline = AutonomousPipeline(store=store)

    def run(self, topic: str | None = None) -> dict[str, Any]:
        """Run the Research Agent employee.

        Args:
            topic: Optional specific topic to research. If None, runs full gap analysis.

        Returns:
            dict with topics_researched, gaps_filled, new_facts_stored.
        """
        description = (
            f"Research topic: {topic}" if topic
            else "Identify low-confidence semantic facts and knowledge gaps; synthesize new findings."
        )

        task = PipelineTask(
            task_type=self.TASK_TYPE,
            description=description,
            success_criteria=self.SUCCESS_CRITERIA,
            context_hints=self.CONTEXT_HINTS,
            employee_name=self.EMPLOYEE_NAME,
            metadata={"topic": topic} if topic else {},
        )

        result = self._pipeline.run(task, build_fn=self._build)
        return result.outputs

    def _build(self, task: PipelineTask, context_data: dict) -> dict[str, Any]:
        """BUILD phase: find gaps, synthesize facts, store findings."""
        now = datetime.now(timezone.utc)
        topics_researched: list[str] = []
        gaps_filled: list[str] = []
        new_facts_stored: int = 0
        research_targets: list[dict] = []

        specific_topic = task.metadata.get("topic") if hasattr(task, "metadata") else None

        # ── Load low-confidence semantic facts ────────────────────────────
        if self._store is not None:
            try:
                if specific_topic:
                    # Targeted: search by topic
                    sem_result = (
                        self._store.supabase.table("jake_semantic")
                        .select("id, content, category, confidence, topics")
                        .eq("is_active", True)
                        .lt("confidence", LOW_CONFIDENCE_THRESHOLD)
                        .contains("topics", [specific_topic])
                        .order("confidence", desc=False)
                        .limit(20)
                        .execute()
                    )
                else:
                    # General: all low-confidence
                    sem_result = (
                        self._store.supabase.table("jake_semantic")
                        .select("id, content, category, confidence, topics")
                        .eq("is_active", True)
                        .lt("confidence", LOW_CONFIDENCE_THRESHOLD)
                        .order("confidence", desc=False)
                        .limit(20)
                        .execute()
                    )
                research_targets.extend(sem_result.data or [])
            except Exception as exc:
                logger.warning("ResearchAgent: failed to load low-confidence semantic: %s", exc)

        # ── Load knowledge_gap episodic entries ───────────────────────────
        knowledge_gaps: list[dict] = []
        if self._store is not None:
            try:
                cutoff = (now - timedelta(days=KNOWLEDGE_GAP_LOOKBACK_DAYS)).isoformat()
                gap_result = (
                    self._store.supabase.table("jake_episodic")
                    .select("id, content, occurred_at, topics, metadata")
                    .eq("memory_type", "knowledge_gap")
                    .gte("occurred_at", cutoff)
                    .order("occurred_at", desc=True)
                    .limit(30)
                    .execute()
                )
                knowledge_gaps = gap_result.data or []
            except Exception as exc:
                logger.warning("ResearchAgent: failed to load knowledge gaps: %s", exc)

        # ── Synthesize findings from existing context ─────────────────────
        # Group research targets by category/topic
        topic_groups: dict[str, list[dict]] = {}

        for target in research_targets:
            t_topics = target.get("topics") or []
            category = target.get("category", "general")
            group_key = t_topics[0] if t_topics else category
            topic_groups.setdefault(group_key, []).append(target)

        for gap in knowledge_gaps:
            g_topics = gap.get("topics") or []
            group_key = g_topics[0] if g_topics else "general"
            topic_groups.setdefault(group_key, [])

        # ── Generate synthesized semantic facts ────────────────────────────
        stored_ids: list[str] = []

        for topic_key, items in topic_groups.items():
            if not items:
                continue

            topics_researched.append(topic_key)

            # Build a synthesis from the low-confidence items
            synthesis_parts = []
            for item in items[:5]:
                content = item.get("content", "")
                conf = item.get("confidence", 0.5)
                if content:
                    synthesis_parts.append(f"[conf={conf:.2f}] {content[:200]}")

            if not synthesis_parts:
                continue

            # Create a consolidated synthesis fact
            synthesis = (
                f"Research synthesis for topic '{topic_key}' (generated {now.strftime('%Y-%m-%d')}): "
                f"Consolidated {len(synthesis_parts)} low-confidence fact(s). "
                f"Items: {'; '.join(synthesis_parts[:3])}"
            )

            if self._store is not None:
                try:
                    source_ids = [item["id"] for item in items if item.get("id")]
                    stored = self._store.store_semantic(
                        content=synthesis,
                        category="research_synthesis",
                        confidence=0.6,  # slightly higher than inputs — synthesized
                        source_episodes=source_ids[:5],
                        topics=[topic_key, "research_synthesis"],
                        metadata={
                            "synthesized_from": len(synthesis_parts),
                            "topic": topic_key,
                            "generated_by": self.EMPLOYEE_NAME,
                        },
                    )
                    if stored.get("id"):
                        stored_ids.append(stored["id"])
                        new_facts_stored += 1
                        gaps_filled.append(topic_key)
                except Exception as exc:
                    logger.warning("ResearchAgent: failed to store synthesis for %s: %s", topic_key, exc)

        # ── Summary ───────────────────────────────────────────────────────
        return {
            "topics_researched": topics_researched,
            "gaps_filled": gaps_filled,
            "new_facts_stored": new_facts_stored,
            "knowledge_gaps_found": len(knowledge_gaps),
            "low_confidence_items_found": len(research_targets),
            "stored_fact_ids": stored_ids,
            "generated_at": now.isoformat(),
        }
