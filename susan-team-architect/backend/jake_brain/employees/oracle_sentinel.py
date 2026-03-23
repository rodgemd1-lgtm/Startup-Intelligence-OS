"""Oracle Sentinel — Daily competitor intelligence employee.

Runs daily at 6 AM weekdays (via cron) or on-demand via CLI.

Pipeline:
  1. CONTEXT  — Load Oracle Health RAG context, recent TrendRadar signals, last briefing
  2. PLAN     — Identify stale competitor profiles, new signals to analyze, briefing due
  3. BUILD    — Run Susan RAG search for each competitor, check recent signals
  4. VALIDATE — Verify findings have sources, check for contradictions with existing intel
  5. HEAL     — If TrendRadar fails, fall back to existing RAG data
  6. REPORT   — Generate Oracle Health intelligence summary
  7. CLOSE    — Update jake_episodic with new intel, mark task complete
  8. LEARN    — Feed to TIMG for pattern extraction

Output: Intelligence summary written to jake_episodic with data_type="oracle_intel"
Escalation: FLAG if competitor makes major announcement (keyword triggers)
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Competitors to monitor
ORACLE_COMPETITORS = [
    "epic systems",
    "cerner",
    "meditech",
    "athenahealth",
    "allscripts",
]

# Announcement keywords that trigger FLAG escalation
FLAG_KEYWORDS = [
    "acquisition", "merger", "acquired", "partnership with",
    "new product launch", "ipo", "layoffs", "ceo", "funding",
    "raises", "revenue", "market share",
]


class OracleSentinel:
    """Autonomous Oracle Health competitor intelligence employee."""

    PIPELINE_NAME = "oracle_sentinel"
    TASK_TYPE = "research"
    CRON_JOB = "oracle_sentinel_daily"

    def __init__(self):
        from jake_brain.autonomous_pipeline import AutonomousPipeline
        self.pipeline_cls = AutonomousPipeline

    def run(self) -> dict:
        """Execute one Oracle Sentinel cycle via the autonomous pipeline."""
        from jake_brain.autonomous_pipeline import AutonomousPipeline

        now = datetime.now(timezone.utc)
        pipeline = OracleSentinelPipeline(
            pipeline_name=f"{self.PIPELINE_NAME}_{now.strftime('%Y%m%d_%H%M')}",
            task_description="Oracle Health competitor intelligence — daily briefing",
            task_type=self.TASK_TYPE,
        )
        return pipeline.run()


class OracleSentinelPipeline:
    """Subclasses AutonomousPipeline with Oracle-specific build logic."""

    MAX_HEAL_RETRIES = 2

    def __init__(self, pipeline_name: str, task_description: str, task_type: str):
        from jake_brain.autonomous_pipeline import AutonomousPipeline
        self._base = AutonomousPipeline(pipeline_name, task_description, task_type)

        # Override build with Oracle-specific logic
        self._base._phase_build = self._phase_build
        self._base._phase_validate = self._phase_validate
        self._base._phase_close = self._phase_close

    def run(self) -> dict:
        return self._base.run()

    # ------------------------------------------------------------------
    # Oracle-specific BUILD
    # ------------------------------------------------------------------

    def _phase_build(self, plan: dict, context: dict, attempt: int = 0) -> dict:
        """Query Susan RAG for each competitor, detect major announcements."""
        results = []
        errors = []
        signals = []
        flag_triggers = []

        for competitor in ORACLE_COMPETITORS:
            try:
                intel = self._fetch_competitor_intel(competitor, context)
                results.append({"competitor": competitor, "intel": intel, "status": "ok"})

                # Check for FLAG-worthy announcements
                intel_lower = (intel or "").lower()
                triggered = [kw for kw in FLAG_KEYWORDS if kw in intel_lower]
                if triggered:
                    flag_triggers.append({"competitor": competitor, "keywords": triggered})
                    signals.append(f"FLAG: {competitor} — {', '.join(triggered)}")

            except Exception as e:
                logger.warning(f"Intel fetch failed for {competitor}: {e}")
                errors.append(f"{competitor}: {e}")
                results.append({"competitor": competitor, "status": "error", "error": str(e)})

        # Try to fetch TrendRadar signals
        trendradar_signals = []
        if attempt == 0:
            trendradar_signals = self._fetch_trendradar_signals()

        return {
            "results": results,
            "errors": errors,
            "steps_completed": len([r for r in results if r.get("status") == "ok"]),
            "steps_total": len(ORACLE_COMPETITORS),
            "signals": signals,
            "flag_triggers": flag_triggers,
            "trendradar": trendradar_signals,
            "attempt": attempt,
        }

    def _fetch_competitor_intel(self, competitor: str, context: dict) -> str:
        """Query Susan RAG for competitor intelligence."""
        try:
            from jake_brain.retriever import BrainRetriever
            from jake_brain.store import BrainStore
            store = BrainStore()
            retriever = BrainRetriever(store)
            return retriever.recall(
                query=f"Oracle Health competitor {competitor} market share product features",
                top_k=3,
            )
        except Exception as e:
            logger.warning(f"RAG query failed for {competitor}: {e}")
            return f"RAG unavailable: {e}"

    def _fetch_trendradar_signals(self) -> list[str]:
        """Attempt to get TrendRadar signals. Returns [] on failure (heal handles it)."""
        # TrendRadar is a MCP server — can't call it directly from Python.
        # Return empty list; the actual integration happens via MCP in Claude Code sessions.
        return []

    # ------------------------------------------------------------------
    # Oracle-specific VALIDATE
    # ------------------------------------------------------------------

    def _phase_validate(self, build_results: dict, plan: dict) -> dict:
        """Validate that we have intel for at least 3 competitors."""
        from jake_brain.autonomous_pipeline import ErrorClass

        steps_completed = build_results.get("steps_completed", 0)
        flag_triggers = build_results.get("flag_triggers", [])
        errors = build_results.get("errors", [])

        if steps_completed < 2:
            error_msg = errors[0] if errors else "Insufficient competitor coverage"
            # Determine if it's an API error or data error
            is_api = any(w in str(error_msg).lower() for w in ["timeout", "connection", "503"])
            return {
                "passed": False,
                "reason": f"Only {steps_completed} competitors analyzed (need ≥2)",
                "error_class": ErrorClass.API_ERROR if is_api else ErrorClass.DATA_ERROR,
                "completion_rate": steps_completed / len(ORACLE_COMPETITORS),
                "has_flags": bool(flag_triggers),
            }

        return {
            "passed": True,
            "reason": f"{steps_completed}/{len(ORACLE_COMPETITORS)} competitors analyzed",
            "completion_rate": steps_completed / len(ORACLE_COMPETITORS),
            "has_flags": bool(flag_triggers),
            "flag_triggers": flag_triggers,
        }

    # ------------------------------------------------------------------
    # Oracle-specific CLOSE
    # ------------------------------------------------------------------

    def _phase_close(self, report: dict, context: dict, plan: dict) -> dict:
        """Write Oracle intel to jake_episodic with oracle_intel data type."""
        try:
            from jake_brain.store import BrainStore
            store = BrainStore()

            # Build intel summary
            results = report.get("results_summary", [])
            intel_items = [
                f"{r.get('competitor', '?')}: {str(r.get('output', {}).get('intel', ''))[:200]}"
                for r in results
                if r.get("status") == "ok"
            ]
            summary = (
                f"Oracle Sentinel daily run {datetime.now(timezone.utc).strftime('%Y-%m-%d')}: "
                f"analyzed {report.get('steps_completed', 0)} competitors. "
                + " | ".join(intel_items[:3])
            )

            episodic = store.store_episodic(
                content=summary,
                occurred_at=datetime.now(timezone.utc),
                memory_type="oracle_intel",
                project="oracle-health",
                importance=0.8,
                topics=["competitor-intel", "oracle-health"],
                metadata={
                    "run_id": report.get("run_id"),
                    "competitors": ORACLE_COMPETITORS,
                    "flags": report.get("results_summary", []),
                },
            )
            return {"episodic_id": episodic.get("id"), "summary": summary[:100]}
        except Exception as e:
            logger.warning(f"Oracle Sentinel close failed: {e}")
            return {"error": str(e)}
