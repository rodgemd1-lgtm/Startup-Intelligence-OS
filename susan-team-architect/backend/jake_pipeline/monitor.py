"""Pipeline Monitor — alerts, velocity tracking, and pipeline health scoring."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Optional

from .deals import DealTracker, Deal, DealStage


class PipelineMonitor:
    """Tracks pipeline health, velocity, and generates alerts."""

    def __init__(self, tracker: DealTracker | None = None):
        self.tracker = tracker or DealTracker()

    def health_score(self) -> dict:
        """0-100 pipeline health score based on deal distribution and velocity."""
        summary = self.tracker.pipeline_summary()
        deals = self.tracker.list_active()
        overdue = self.tracker.overdue_actions()

        # Scoring factors
        score = 100
        issues = []

        # No deals in pipeline
        if summary["total_deals"] == 0:
            return {"score": 0, "grade": "N/A", "issues": ["No active deals in pipeline"], "summary": summary, "overdue_count": 0}

        # Overdue actions
        overdue_pct = len(overdue) / max(summary["total_deals"], 1) * 100
        if overdue_pct > 50:
            score -= 30
            issues.append(f"{len(overdue)} deals have overdue actions ({overdue_pct:.0f}%)")
        elif overdue_pct > 25:
            score -= 15
            issues.append(f"{len(overdue)} deals have overdue actions")

        # Deals stuck in prospect too long
        by_stage = summary.get("by_stage", {})
        prospect_count = by_stage.get("prospect", {}).get("count", 0)
        if prospect_count > summary["total_deals"] * 0.6:
            score -= 20
            issues.append(f"Too many deals stuck in prospect stage ({prospect_count})")

        # Pipeline concentration risk
        if summary["total_deals"] <= 2:
            score -= 15
            issues.append("Low deal count — pipeline concentration risk")

        # No deals in proposal/negotiation
        has_late_stage = any(
            by_stage.get(s, {}).get("count", 0) > 0
            for s in ["proposal", "negotiation"]
        )
        if not has_late_stage:
            score -= 10
            issues.append("No deals in proposal or negotiation stage")

        return {
            "score": max(0, score),
            "grade": "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D",
            "issues": issues,
            "summary": summary,
            "overdue_count": len(overdue),
        }

    def velocity_report(self) -> dict:
        """Estimate deals closed per month and average deal size."""
        # For now, query closed deals from DB
        try:
            client = self.tracker._get_client()
            result = client.table("jake_deals").select("*").eq(
                "stage", "closed_won"
            ).gte(
                "updated_at",
                (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
            ).execute()
            closed = result.data or []
        except Exception:
            closed = []

        count = len(closed)
        total_value = sum(float(d.get("value_usd", 0)) for d in closed)
        avg_value = total_value / count if count else 0

        return {
            "closed_last_90d": count,
            "revenue_last_90d": total_value,
            "avg_deal_size": avg_value,
            "monthly_velocity": round(count / 3, 1),
            "monthly_revenue_run_rate": round(total_value / 3, 2),
        }

    def alerts(self) -> list[dict]:
        """Return actionable pipeline alerts."""
        alerts = []
        overdue = self.tracker.overdue_actions()
        for deal in overdue:
            alerts.append({
                "type": "overdue_action",
                "severity": "high",
                "message": f"Deal '{deal.company}' — action overdue: {deal.next_action}",
                "deal_id": deal.id,
                "due_date": str(deal.next_action_due),
            })

        # Check for stale deals (no update in 30+ days)
        try:
            stale_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            client = self.tracker._get_client()
            result = client.table("jake_deals").select("*").not_.in_(
                "stage", ["closed_won", "closed_lost"]
            ).lte("updated_at", stale_date).execute()
            for d in (result.data or []):
                alerts.append({
                    "type": "stale_deal",
                    "severity": "medium",
                    "message": f"Deal '{d.get('company')}' hasn't been updated in 30+ days",
                    "deal_id": d.get("id"),
                })
        except Exception:
            pass

        return alerts

    def weekly_report(self) -> str:
        """Generate a plain-text weekly pipeline report."""
        health = self.health_score()
        velocity = self.velocity_report()
        alerts = self.alerts()
        summary = health["summary"]

        lines = [
            "═══ PIPELINE WEEKLY REPORT ═══",
            f"Health Score: {health['score']}/100 (Grade: {health['grade']})",
            f"Total Active Deals: {summary['total_deals']}",
            f"Total Pipeline Value: ${summary['total_value']:,.0f}",
            f"Weighted Pipeline: ${summary['weighted_value']:,.0f}",
            "",
            "BY STAGE:",
        ]
        for stage, data in summary.get("by_stage", {}).items():
            lines.append(f"  {stage.upper()}: {data['count']} deals, ${data['total_value']:,.0f}")

        lines += [
            "",
            f"VELOCITY (last 90 days):",
            f"  Deals closed: {velocity['closed_last_90d']}",
            f"  Revenue: ${velocity['revenue_last_90d']:,.0f}",
            f"  Avg deal size: ${velocity['avg_deal_size']:,.0f}",
            f"  Monthly run rate: ${velocity['monthly_revenue_run_rate']:,.0f}/mo",
        ]

        if alerts:
            lines += ["", f"ALERTS ({len(alerts)}):"]
            for a in alerts[:5]:
                lines.append(f"  [{a['severity'].upper()}] {a['message']}")
        else:
            lines.append("\n✓ No pipeline alerts")

        if health["issues"]:
            lines += ["", "ISSUES TO ADDRESS:"]
            for issue in health["issues"]:
                lines.append(f"  • {issue}")

        return "\n".join(lines)
