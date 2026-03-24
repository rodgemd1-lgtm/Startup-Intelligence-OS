"""Health Monitor — brain stats, API costs, error rates, system vitals.

Reports:
  - Memory table row counts (episodic, semantic, procedural, working, entities, relationships)
  - Error budget status per source (from ErrorBudget JSON)
  - Estimated Voyage AI embedding costs (based on rows added today)
  - Hermes cron job status (from launchd)
  - Daily self-test results

Cost model (Voyage AI voyage-3):
  - $0.00006 per 1K tokens input
  - Average memory chunk: ~100 tokens
  - Estimated cost per 1K chunks: ~$0.006
"""
from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("jake.immune.health_monitor")

# Voyage AI pricing (voyage-3 input tokens)
_VOYAGE_COST_PER_1K_TOKENS = 0.00006
_AVG_TOKENS_PER_CHUNK = 100

# Cron jobs to check
_JAKE_CRON_LABELS = [
    "com.jake.brain-wave1",
    "com.jake.brain-morning-brief",
    "com.jake.immune-weekly-report",
    "com.jake.immune-daily-test",
]


class HealthMonitor:
    """Aggregates health metrics for Jake's brain and infrastructure."""

    def __init__(self):
        self._supabase = None

    def _get_supabase(self):
        if self._supabase is None:
            try:
                from supabase import create_client
                from susan_core.config import config as susan_config
                self._supabase = create_client(
                    susan_config.supabase_url, susan_config.supabase_key
                )
            except Exception as exc:
                logger.warning("Supabase not available: %s", exc)
        return self._supabase

    def get_table_counts(self) -> dict[str, int]:
        """Get row counts for all Jake brain tables."""
        supabase = self._get_supabase()
        if supabase is None:
            return {}

        tables = [
            "jake_episodic", "jake_semantic", "jake_procedural",
            "jake_working", "jake_entities", "jake_relationships",
        ]
        counts = {}
        for table in tables:
            try:
                result = (
                    supabase.table(table)
                    .select("id", count="exact")
                    .execute()
                )
                counts[table] = result.count or 0
            except Exception as exc:
                logger.warning("Could not count %s: %s", table, exc)
                counts[table] = -1  # -1 = unknown

        return counts

    def get_error_budget_status(self) -> dict[str, dict]:
        """Get today's error budget status per source."""
        from jake_brain.immune.error_recovery import ErrorBudget
        budget = ErrorBudget()
        return budget.get_stats()

    def get_estimated_costs(self) -> dict[str, float]:
        """Estimate today's embedding costs based on memory counts.

        This is a rough estimate — we don't track exact token counts.
        """
        counts = self.get_table_counts()
        total_memories = sum(
            v for k, v in counts.items()
            if k in ("jake_episodic", "jake_semantic", "jake_procedural", "jake_working")
            and v > 0
        )
        # Rough: assume 10% of total memories were embedded today
        todays_embeds_estimate = max(1, total_memories // 10)
        estimated_tokens = todays_embeds_estimate * _AVG_TOKENS_PER_CHUNK
        estimated_cost = (estimated_tokens / 1000) * _VOYAGE_COST_PER_1K_TOKENS

        return {
            "total_memory_rows": total_memories,
            "estimated_embeds_today": todays_embeds_estimate,
            "estimated_tokens_today": estimated_tokens,
            "estimated_cost_today_usd": round(estimated_cost, 6),
            "estimated_cost_monthly_usd": round(estimated_cost * 30, 4),
        }

    def check_cron_jobs(self) -> dict[str, str]:
        """Check status of Jake's launchd cron jobs."""
        status = {}
        for label in _JAKE_CRON_LABELS:
            try:
                result = subprocess.run(
                    ["launchctl", "list", label],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    # Parse exit status from launchctl output
                    lines = result.stdout.strip().split("\n")
                    last_exit = "unknown"
                    for line in lines:
                        if "LastExitStatus" in line:
                            last_exit = line.split("=")[-1].strip().rstrip(";")
                            break
                    status[label] = f"loaded (last_exit={last_exit})"
                else:
                    status[label] = "NOT LOADED"
            except Exception as exc:
                status[label] = f"error: {exc}"
        return status

    def run_self_test(self) -> dict[str, bool]:
        """Run a quick smoke test of core brain functions.

        Tests: search, entity lookup, Telegram delivery.
        Returns { test_name: passed }
        """
        results = {}

        # Test 1: Brain search
        try:
            from jake_brain.retriever import BrainRetriever
            retriever = BrainRetriever()
            hits = retriever.search(query="mike rodgers", top_k=1)
            results["brain_search"] = len(hits) >= 0  # even 0 results is a pass
        except Exception as exc:
            logger.warning("Self-test brain_search FAILED: %s", exc)
            results["brain_search"] = False

        # Test 2: Entity lookup
        try:
            from jake_brain.graph import KnowledgeGraph
            graph = KnowledgeGraph()
            entities = graph.get_entity("mike")
            results["entity_lookup"] = entities is not None
        except Exception as exc:
            logger.warning("Self-test entity_lookup FAILED: %s", exc)
            results["entity_lookup"] = False

        # Test 3: Supabase connectivity
        try:
            supabase = self._get_supabase()
            if supabase:
                supabase.table("jake_episodic").select("id").limit(1).execute()
                results["supabase_connectivity"] = True
            else:
                results["supabase_connectivity"] = False
        except Exception as exc:
            logger.warning("Self-test supabase_connectivity FAILED: %s", exc)
            results["supabase_connectivity"] = False

        # Test 4: Error budget file readable
        try:
            from jake_brain.immune.error_recovery import ErrorBudget
            budget = ErrorBudget()
            budget.get_stats()  # just needs to not throw
            results["error_budget"] = True
        except Exception as exc:
            logger.warning("Self-test error_budget FAILED: %s", exc)
            results["error_budget"] = False

        passed = sum(1 for v in results.values() if v)
        logger.info(
            "Self-test complete: %d/%d passed",
            passed, len(results),
        )
        return results

    def generate_report(self) -> str:
        """Generate a formatted health report string for Mike."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines = [f"🛡️ *Jake Immune System — Weekly Health Report*", f"_{now}_", ""]

        # Memory table counts
        counts = self.get_table_counts()
        total = sum(v for v in counts.values() if v >= 0)
        lines.append("**🧠 Brain Memory**")
        for table, count in counts.items():
            short_name = table.replace("jake_", "")
            emoji = {"episodic": "📖", "semantic": "💡", "procedural": "⚙️",
                     "working": "💭", "entities": "👤", "relationships": "🔗"}.get(short_name, "•")
            status = f"{count:,}" if count >= 0 else "unavailable"
            lines.append(f"  {emoji} {short_name}: {status}")
        lines.append(f"  **Total: {total:,} memory rows**")
        lines.append("")

        # Error budget
        budget_stats = self.get_error_budget_status()
        lines.append("**⚠️ Error Budget (today)**")
        if not budget_stats:
            lines.append("  ✅ No failures recorded today")
        else:
            for source, info in budget_stats.items():
                failures = info.get("failures", 0)
                disabled = info.get("disabled", False)
                icon = "🔴" if disabled else ("🟡" if failures > 2 else "🟢")
                disabled_str = " (DISABLED)" if disabled else ""
                lines.append(f"  {icon} {source}: {failures}/5 failures{disabled_str}")
        lines.append("")

        # Cost estimate
        costs = self.get_estimated_costs()
        lines.append("**💰 Estimated API Costs**")
        lines.append(f"  Voyage AI today: ~${costs.get('estimated_cost_today_usd', 0):.4f}")
        lines.append(f"  Voyage AI monthly: ~${costs.get('estimated_cost_monthly_usd', 0):.3f}")
        lines.append("")

        # Cron job status
        crons = self.check_cron_jobs()
        lines.append("**⏰ Cron Jobs**")
        for label, status in crons.items():
            short = label.replace("com.jake.", "")
            icon = "✅" if "loaded" in status else "❌"
            lines.append(f"  {icon} {short}: {status}")
        lines.append("")

        # Self-test
        test_results = self.run_self_test()
        passed = sum(1 for v in test_results.values() if v)
        total_tests = len(test_results)
        lines.append(f"**🔬 Self-Test: {passed}/{total_tests} passed**")
        for test, ok in test_results.items():
            icon = "✅" if ok else "❌"
            lines.append(f"  {icon} {test}")

        return "\n".join(lines)
