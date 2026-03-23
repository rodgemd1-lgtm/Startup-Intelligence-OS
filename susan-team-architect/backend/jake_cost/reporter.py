"""Spend Reporter — monthly cost reports with trend analysis and recommendations."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .tracker import CostTracker
from .router import ModelRouter, ModelTier
from .budget import MONTHLY_BUDGET_USD


class SpendReporter:
    """Generate cost reports and optimization recommendations."""

    def __init__(self, tracker: CostTracker | None = None, router: ModelRouter | None = None):
        self.tracker = tracker or CostTracker()
        self.router = router or ModelRouter()

    def monthly_report(self, year: int | None = None, month: int | None = None) -> str:
        now = datetime.now(timezone.utc)
        year = year or now.year
        month = month or now.month
        totals = self.tracker.monthly_totals(year, month)
        daily = self.tracker.daily_totals(days=30)

        spend = totals["total_cost_usd"]
        budget_pct = (spend / MONTHLY_BUDGET_USD) * 100

        lines = [
            "═══ MONTHLY COST REPORT ═══",
            f"Period: {totals['period']}",
            f"",
            f"SPEND SUMMARY:",
            f"  Total: ${spend:.4f} / ${MONTHLY_BUDGET_USD:.0f} budget ({budget_pct:.1f}%)",
            f"  Calls: {totals['total_calls']:,}",
        ]

        if budget_pct >= 100:
            lines.append(f"  ⚠ BUDGET EXCEEDED — ${spend - MONTHLY_BUDGET_USD:.2f} over limit")
        elif budget_pct >= 80:
            lines.append(f"  ⚠ WARNING — approaching budget limit")
        else:
            lines.append(f"  ✓ Within budget")

        lines.append("")
        lines.append("BY SERVICE:")
        by_service = totals.get("by_service", {})
        for svc, data in sorted(by_service.items(), key=lambda x: -x[1]["cost_usd"]):
            lines.append(
                f"  {svc}: ${data['cost_usd']:.4f} "
                f"({data['calls']:,} calls, {data['tokens']:,} tokens)"
            )

        if daily:
            lines.append("")
            lines.append("DAILY TREND (last 7 days):")
            for entry in daily[-7:]:
                bar = "█" * min(20, int(entry["cost_usd"] / 0.50))
                lines.append(f"  {entry['date']}: ${entry['cost_usd']:.4f} {bar}")

        # Optimization recommendations
        recs = self._recommendations(totals)
        if recs:
            lines.append("")
            lines.append("OPTIMIZATION RECOMMENDATIONS:")
            for rec in recs:
                lines.append(f"  • {rec}")

        return "\n".join(lines)

    def _recommendations(self, totals: dict) -> list[str]:
        recs = []
        by_service = totals.get("by_service", {})

        anthropic = by_service.get("anthropic", {})
        if anthropic.get("calls", 0) > 0:
            avg_per_call = anthropic.get("cost_usd", 0) / anthropic["calls"]
            if avg_per_call > 0.10:
                recs.append(
                    f"High avg cost/call (${avg_per_call:.3f}). "
                    "Consider routing more tasks to Haiku for classification ops."
                )
            if anthropic.get("cost_usd", 0) > MONTHLY_BUDGET_USD * 0.60:
                recs.append(
                    "Anthropic API is >60% of spend. "
                    "Review task routing — use Haiku for triage/classify."
                )

        voyage = by_service.get("voyage", {})
        if voyage.get("tokens", 0) > 5_000_000:
            recs.append(
                "High embedding volume. Consider caching frequently-embedded content."
            )

        if not recs:
            recs.append("Cost profile looks healthy. Smart routing is working.")

        return recs

    def savings_estimate(self) -> str:
        """Estimate savings from smart routing vs using Opus everywhere."""
        totals = self.tracker.monthly_totals()
        by_service = totals.get("by_service", {})
        anthropic = by_service.get("anthropic", {})
        actual_cost = anthropic.get("cost_usd", 0)
        total_tokens = anthropic.get("tokens", 0)

        if total_tokens == 0:
            return "No Anthropic API calls recorded this month."

        # Estimate what Opus would cost for same token volume
        avg_input = int(total_tokens * 0.6)
        avg_output = int(total_tokens * 0.4)
        opus_cost = self.router.cost_estimate(ModelTier.OPUS, avg_input, avg_output)
        savings = max(0, opus_cost - actual_cost)
        pct = (savings / opus_cost * 100) if opus_cost > 0 else 0

        return (
            f"Smart routing saved ~${savings:.2f} ({pct:.0f}%) vs Opus-for-everything.\n"
            f"  Actual Anthropic spend: ${actual_cost:.4f}\n"
            f"  Opus baseline estimate: ${opus_cost:.4f}\n"
            f"  Tokens this month: {total_tokens:,}"
        )


spend_reporter = SpendReporter()
