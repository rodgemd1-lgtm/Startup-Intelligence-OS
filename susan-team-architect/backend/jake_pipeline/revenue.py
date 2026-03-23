"""Revenue Analyzer — forecast revenue impact, ARR modeling, deal scoring."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from .deals import DealTracker, DealStage


@dataclass
class RevenueProjection:
    period_label: str
    expected_revenue: float
    best_case: float
    worst_case: float
    deal_count: int

    def to_dict(self) -> dict:
        return {
            "period": self.period_label,
            "expected": round(self.expected_revenue, 2),
            "best_case": round(self.best_case, 2),
            "worst_case": round(self.worst_case, 2),
            "deal_count": self.deal_count,
        }


class RevenueAnalyzer:
    """Revenue impact modeling and forecasting."""

    def __init__(self, tracker: DealTracker | None = None):
        self.tracker = tracker or DealTracker()

    def quarterly_forecast(self) -> list[RevenueProjection]:
        """Project revenue for next 3 months based on expected close dates."""
        deals = self.tracker.list_active()
        today = date.today()
        quarters = []
        for q in range(3):
            start = today + timedelta(days=30 * q)
            end = today + timedelta(days=30 * (q + 1))
            period_deals = [
                d for d in deals
                if d.expected_close and start <= d.expected_close < end
            ]
            expected = sum(d.weighted_value for d in period_deals)
            best = sum(d.value_usd for d in period_deals if d.stage != DealStage.PROSPECT)
            worst = sum(d.value_usd for d in period_deals if d.stage == DealStage.CLOSED_WON)

            label = f"Month {q+1} ({start.strftime('%b %Y')})"
            quarters.append(RevenueProjection(
                period_label=label,
                expected_revenue=expected,
                best_case=best,
                worst_case=worst,
                deal_count=len(period_deals),
            ))
        return quarters

    def arr_estimate(self) -> dict:
        """Estimate Annual Recurring Revenue from closed + weighted pipeline."""
        try:
            client = self.tracker._get_client()
            won_result = client.table("jake_deals").select("value_usd").eq(
                "stage", "closed_won"
            ).execute()
            closed_arr = sum(float(d.get("value_usd", 0)) for d in (won_result.data or []))
        except Exception:
            closed_arr = 0.0

        deals = self.tracker.list_active()
        weighted_pipeline = sum(d.weighted_value for d in deals)
        projected_arr = closed_arr + weighted_pipeline

        return {
            "closed_arr": round(closed_arr, 2),
            "weighted_pipeline": round(weighted_pipeline, 2),
            "projected_arr": round(projected_arr, 2),
            "conservative_arr": round(closed_arr + weighted_pipeline * 0.5, 2),
        }

    def deal_score(self, deal_id: str) -> dict:
        """Score a specific deal 0-100 based on multiple factors."""
        deal = self.tracker.get(deal_id)
        if not deal:
            return {"score": 0, "error": "Deal not found"}

        score = 0
        factors = []

        # Stage progression (0-40)
        stage_scores = {
            DealStage.PROSPECT: 5,
            DealStage.QUALIFIED: 15,
            DealStage.PROPOSAL: 25,
            DealStage.NEGOTIATION: 35,
            DealStage.CLOSED_WON: 40,
            DealStage.CLOSED_LOST: 0,
        }
        stage_score = stage_scores.get(deal.stage, 0)
        score += stage_score
        factors.append(f"Stage ({deal.stage.value}): +{stage_score}")

        # Has contact info (0-10)
        if deal.contact_name and deal.contact_email:
            score += 10
            factors.append("Contact info complete: +10")
        elif deal.contact_name:
            score += 5
            factors.append("Contact name only: +5")

        # Value defined (0-15)
        if deal.value_usd > 0:
            score += 15
            factors.append(f"Value defined (${deal.value_usd:,.0f}): +15")

        # Has next action (0-15)
        if deal.next_action and deal.next_action_due:
            if deal.next_action_due >= date.today():
                score += 15
                factors.append(f"Next action scheduled: +15")
            else:
                score += 5
                factors.append("Next action overdue: +5")
        elif deal.next_action:
            score += 10
            factors.append("Next action defined (no date): +10")

        # Has expected close (0-10)
        if deal.expected_close and deal.expected_close >= date.today():
            score += 10
            factors.append(f"Close date set: +10")

        # Has notes (0-10)
        if len(deal.notes) > 50:
            score += 10
            factors.append("Rich notes: +10")

        return {
            "deal_id": deal_id,
            "company": deal.company,
            "score": min(100, score),
            "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
            "factors": factors,
        }

    def revenue_impact_report(self) -> str:
        """Plain-text revenue impact report."""
        arr = self.arr_estimate()
        forecast = self.quarterly_forecast()

        lines = [
            "═══ REVENUE IMPACT REPORT ═══",
            "",
            "ARR ESTIMATE:",
            f"  Closed ARR:        ${arr['closed_arr']:>12,.0f}",
            f"  Weighted Pipeline: ${arr['weighted_pipeline']:>12,.0f}",
            f"  Projected ARR:     ${arr['projected_arr']:>12,.0f}",
            f"  Conservative ARR:  ${arr['conservative_arr']:>12,.0f}",
            "",
            "QUARTERLY FORECAST:",
        ]
        for proj in forecast:
            lines += [
                f"  {proj.period_label}:",
                f"    Expected: ${proj.expected_revenue:,.0f}  |  Best: ${proj.best_case:,.0f}  |  Worst: ${proj.worst_case:,.0f}",
                f"    Deals closing: {proj.deal_count}",
            ]
        return "\n".join(lines)
