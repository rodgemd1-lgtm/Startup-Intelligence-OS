"""Oracle Sentinel — daily competitive intelligence employee.

Runs Monday-Friday at 6 AM. Monitors Oracle Health competitors,
checks for stale intel, and generates a structured intelligence summary.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from jake_brain.autonomous_pipeline import AutonomousPipeline, PipelineTask

logger = logging.getLogger(__name__)

# Known Oracle Health competitors to track
ORACLE_COMPETITORS = [
    "Epic Systems",
    "Microsoft Health",
    "AWS HealthLake",
    "Google Health",
    "Meditech",
    "Veeva Systems",
]

# Intel staleness threshold — if last entry is older than this, flag for refresh
STALE_THRESHOLD_DAYS = 7


class OracleSentinel:
    """Daily Oracle Health competitive intelligence employee.

    Loads recent oracle_intel episodic memories, checks for gaps/stale records,
    and produces a structured intelligence summary.
    """

    EMPLOYEE_NAME = "oracle_sentinel"
    TASK_TYPE = "oracle_intelligence"
    CONTEXT_HINTS = ["oracle", "competitor", "healthcare_AI", "intelligence"]
    SUCCESS_CRITERIA = [
        "intel_summary produced",
        "competitors_analyzed list non-empty",
        "stale_records identified",
    ]

    def __init__(self, store=None):
        """
        Args:
            store: BrainStore instance. If None, pipeline runs without memory persistence.
        """
        self._store = store
        self._pipeline = AutonomousPipeline(store=store)

    def run(self, task_description: str | None = None) -> dict[str, Any]:
        """Run the Oracle Sentinel employee.

        Args:
            task_description: Optional override for the task description.

        Returns:
            dict with intel_summary, competitors_analyzed, new_signals, stale_records.
        """
        description = task_description or (
            "Analyze Oracle Health competitive landscape: load recent intel, "
            "identify new signals, flag stale records, produce daily summary."
        )

        task = PipelineTask(
            task_type=self.TASK_TYPE,
            description=description,
            success_criteria=self.SUCCESS_CRITERIA,
            context_hints=self.CONTEXT_HINTS,
            employee_name=self.EMPLOYEE_NAME,
        )

        result = self._pipeline.run(task, build_fn=self._build)
        return result.outputs

    def _build(self, task: PipelineTask, context_data: dict) -> dict[str, Any]:
        """BUILD phase: analyze oracle intel and generate summary."""
        now = datetime.now(timezone.utc)
        stale_cutoff = now - timedelta(days=STALE_THRESHOLD_DAYS)

        # ── Load recent oracle intel from episodic memory ──────────────────
        recent_intel: list[dict] = []
        stale_records: list[str] = []

        if self._store is not None:
            try:
                result = (
                    self._store.supabase.table("jake_episodic")
                    .select("id, content, occurred_at, topics, metadata")
                    .eq("memory_type", "oracle_intel")
                    .order("occurred_at", desc=True)
                    .limit(20)
                    .execute()
                )
                recent_intel = result.data or []
            except Exception as exc:
                logger.warning("OracleSentinel: failed to load recent intel: %s", exc)

        # ── Check staleness by competitor ─────────────────────────────────
        competitors_with_intel: set[str] = set()
        for entry in recent_intel:
            meta = entry.get("metadata") or {}
            competitor = meta.get("competitor", "")
            if competitor:
                competitors_with_intel.add(competitor)

            # Check if this record is stale
            try:
                entry_date = datetime.fromisoformat(entry["occurred_at"].replace("Z", "+00:00"))
                if entry_date < stale_cutoff:
                    stale_records.append(entry.get("id", "unknown"))
            except Exception:
                pass

        # ── Identify missing competitor coverage ──────────────────────────
        missing_coverage = [c for c in ORACLE_COMPETITORS if c not in competitors_with_intel]
        new_signals: list[str] = []

        # ── Pull recent oracle episodic for new signal detection ──────────
        if self._store is not None:
            try:
                # Look for any recent oracle-tagged episodic (last 24h)
                yesterday = (now - timedelta(days=1)).isoformat()
                recent_result = (
                    self._store.supabase.table("jake_episodic")
                    .select("id, content, occurred_at, topics")
                    .contains("topics", ["oracle"])
                    .gte("occurred_at", yesterday)
                    .order("occurred_at", desc=True)
                    .limit(10)
                    .execute()
                )
                for entry in (recent_result.data or []):
                    # Extract a brief signal from content
                    content = entry.get("content", "")
                    if content and len(content) > 20:
                        signal = content[:120].replace("\n", " ").strip()
                        new_signals.append(signal)
            except Exception as exc:
                logger.warning("OracleSentinel: failed to load new signals: %s", exc)

        # ── Build intelligence summary ─────────────────────────────────────
        intel_lines = [
            f"Oracle Health Intelligence Summary — {now.strftime('%Y-%m-%d')}",
            f"Total intel entries loaded: {len(recent_intel)}",
            f"Competitors with coverage: {', '.join(sorted(competitors_with_intel)) or 'none yet'}",
            f"Missing coverage: {', '.join(missing_coverage) or 'none'}",
            f"Stale records (>{STALE_THRESHOLD_DAYS}d): {len(stale_records)}",
            f"New signals (last 24h): {len(new_signals)}",
        ]

        if missing_coverage:
            intel_lines.append(
                f"\nACTION NEEDED: No intel found for {', '.join(missing_coverage)}. "
                "Run a competitive research sweep."
            )

        if new_signals:
            intel_lines.append("\nNew Signals:")
            for sig in new_signals[:5]:
                intel_lines.append(f"  - {sig}")

        intel_summary = "\n".join(intel_lines)

        # ── Store intel summary to episodic ───────────────────────────────
        if self._store is not None:
            try:
                self._store.store_episodic(
                    content=intel_summary,
                    occurred_at=now,
                    memory_type="oracle_intel",
                    project="oracle-health",
                    importance=0.7,
                    topics=["oracle", "intelligence", "competitive"],
                    source=self.EMPLOYEE_NAME,
                    source_type="autonomous_employee",
                    metadata={
                        "competitors_analyzed": list(competitors_with_intel),
                        "new_signals_count": len(new_signals),
                        "stale_records_count": len(stale_records),
                    },
                )
            except Exception as exc:
                logger.warning("OracleSentinel: failed to store intel: %s", exc)

        return {
            "intel_summary": intel_summary,
            "competitors_analyzed": sorted(competitors_with_intel),
            "missing_coverage": missing_coverage,
            "new_signals": new_signals[:10],
            "stale_records": stale_records,
            "total_entries_reviewed": len(recent_intel),
            "generated_at": now.isoformat(),
        }
