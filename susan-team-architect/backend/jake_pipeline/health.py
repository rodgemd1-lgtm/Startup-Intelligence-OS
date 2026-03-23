"""Customer Health Tracker — engagement scoring and churn risk for closed deals."""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from supabase import create_client, Client


@dataclass
class CustomerHealth:
    company: str
    deal_id: str
    health_score: int        # 0-100
    churn_risk: str          # low, medium, high
    last_contact: Optional[date]
    days_since_contact: int
    engagement_signals: list[str]
    flags: list[str]

    def to_dict(self) -> dict:
        return {
            "company": self.company,
            "deal_id": self.deal_id,
            "health_score": self.health_score,
            "churn_risk": self.churn_risk,
            "last_contact": str(self.last_contact) if self.last_contact else None,
            "days_since_contact": self.days_since_contact,
            "engagement_signals": self.engagement_signals,
            "flags": self.flags,
        }


class CustomerHealthTracker:
    """Track health and churn risk for closed-won customers."""

    def __init__(self):
        self._client: Client | None = None

    def _get_client(self) -> Client:
        if self._client:
            return self._client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            env_path = os.path.expanduser("~/.hermes/.env")
            if os.path.exists(env_path):
                with open(env_path) as fh:
                    for line in fh:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            k, _, v = line.partition("=")
                            if k.strip() == "SUPABASE_URL":
                                url = v.strip()
                            elif k.strip() == "SUPABASE_SERVICE_KEY":
                                key = v.strip()
        self._client = create_client(url, key)
        return self._client

    def score_customer(self, deal_id: str, company: str) -> CustomerHealth:
        """Score a customer's health based on recent pipeline events and episodic memory."""
        score = 70  # Start optimistic
        signals = []
        flags = []
        last_contact: Optional[date] = None
        days_since = 999

        # Check pipeline events for recent contact
        try:
            result = self._get_client().table("jake_pipeline_events").select("*").eq(
                "deal_id", deal_id
            ).order("created_at", desc=True).limit(10).execute()

            events = result.data or []
            if events:
                latest_event_date = datetime.fromisoformat(
                    events[0]["created_at"].replace("Z", "+00:00")
                ).date()
                last_contact = latest_event_date
                days_since = (date.today() - latest_event_date).days

                if days_since < 7:
                    score += 15
                    signals.append(f"Recent contact {days_since} days ago")
                elif days_since < 30:
                    score += 5
                    signals.append(f"Contact {days_since} days ago")
                elif days_since > 60:
                    score -= 20
                    flags.append(f"No contact in {days_since} days")
                elif days_since > 30:
                    score -= 10
                    flags.append(f"Limited contact ({days_since} days)")

                # Check for positive signals in event notes
                for event in events[:5]:
                    notes = (event.get("notes") or "").lower()
                    if any(kw in notes for kw in ["success", "happy", "expanding", "renewal", "upsell"]):
                        score += 10
                        signals.append("Positive engagement signal detected")
                        break
                    if any(kw in notes for kw in ["concern", "issue", "problem", "unhappy", "cancel"]):
                        score -= 15
                        flags.append("Negative engagement signal detected")
                        break
            else:
                score -= 20
                flags.append("No interaction history found")
        except Exception:
            pass

        # Check episodic memory for company mentions
        try:
            result = self._get_client().table("jake_episodic").select("content,importance").ilike(
                "content", f"%{company}%"
            ).order("created_at", desc=True).limit(5).execute()

            mentions = result.data or []
            if mentions:
                avg_importance = sum(float(m.get("importance", 0.5)) for m in mentions) / len(mentions)
                if avg_importance > 0.7:
                    score += 5
                    signals.append(f"High-importance company context ({len(mentions)} records)")
        except Exception:
            pass

        score = max(0, min(100, score))
        churn_risk = "low" if score >= 70 else "medium" if score >= 45 else "high"

        return CustomerHealth(
            company=company,
            deal_id=deal_id,
            health_score=score,
            churn_risk=churn_risk,
            last_contact=last_contact,
            days_since_contact=days_since,
            engagement_signals=signals,
            flags=flags,
        )

    def all_customer_health(self) -> list[CustomerHealth]:
        """Score all closed-won customers."""
        try:
            result = self._get_client().table("jake_deals").select("id,company").eq(
                "stage", "closed_won"
            ).execute()
            customers = result.data or []
        except Exception:
            return []

        return [self.score_customer(c["id"], c["company"]) for c in customers]

    def at_risk_customers(self) -> list[CustomerHealth]:
        """Return customers with high churn risk."""
        return [c for c in self.all_customer_health() if c.churn_risk == "high"]

    def health_summary(self) -> str:
        """Plain-text customer health summary."""
        customers = self.all_customer_health()
        if not customers:
            return "No closed-won customers tracked yet."

        at_risk = [c for c in customers if c.churn_risk == "high"]
        healthy = [c for c in customers if c.churn_risk == "low"]

        lines = [
            "═══ CUSTOMER HEALTH SUMMARY ═══",
            f"Total customers tracked: {len(customers)}",
            f"  Healthy (low risk):    {len(healthy)}",
            f"  At risk (high risk):   {len(at_risk)}",
            f"  Average health score:  {sum(c.health_score for c in customers) // len(customers)}/100",
        ]
        if at_risk:
            lines += ["", "AT-RISK CUSTOMERS:"]
            for c in at_risk:
                lines.append(f"  ✗ {c.company} (score={c.health_score}, {c.days_since_contact}d no contact)")
        return "\n".join(lines)
