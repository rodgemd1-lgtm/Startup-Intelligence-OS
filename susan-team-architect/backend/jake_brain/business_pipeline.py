"""Jake Business Pipeline — Track deals, pipeline stages, and business outcomes.

Monitors:
  - Oracle Health deals and opportunities
  - Pipeline stage progression
  - Revenue impact of work done
  - Customer health indicators
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any

from supabase import create_client, Client
from susan_core.config import config as susan_config


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STAGES = ["DISCOVERY", "DEMO", "PROPOSAL", "NEGOTIATION", "CLOSED_WON", "CLOSED_LOST"]

# Stage probability defaults (used when deal has no explicit probability)
STAGE_PROBABILITIES: dict[str, float] = {
    "DISCOVERY": 0.1,
    "DEMO": 0.3,
    "PROPOSAL": 0.5,
    "NEGOTIATION": 0.7,
    "CLOSED_WON": 1.0,
    "CLOSED_LOST": 0.0,
}

# Estimated hours for a deal of each stage maturity (for revenue impact calc)
STAGE_HOURS_EST: dict[str, float] = {
    "DISCOVERY": 5.0,
    "DEMO": 15.0,
    "PROPOSAL": 30.0,
    "NEGOTIATION": 50.0,
    "CLOSED_WON": 100.0,
    "CLOSED_LOST": 50.0,
}


# ---------------------------------------------------------------------------
# Deal dataclass
# ---------------------------------------------------------------------------

@dataclass
class Deal:
    id: str
    name: str
    company: str
    stage: str          # DISCOVERY | DEMO | PROPOSAL | NEGOTIATION | CLOSED_WON | CLOSED_LOST
    value_usd: float
    probability: float  # 0.0–1.0
    owner: str
    created_at: datetime
    updated_at: datetime
    next_action: str
    notes: str
    source: str         # "oracle_health" | "alex_recruiting" | "susan_commercial"

    @property
    def weighted_value(self) -> float:
        return round(self.value_usd * self.probability, 2)

    @classmethod
    def from_row(cls, row: dict) -> "Deal":
        """Build a Deal from a Supabase row dict."""
        def _parse_dt(val: str | None) -> datetime:
            if val is None:
                return datetime.now(timezone.utc)
            if val.endswith("Z"):
                val = val[:-1] + "+00:00"
            return datetime.fromisoformat(val)

        return cls(
            id=row.get("id", ""),
            name=row.get("name", ""),
            company=row.get("company", ""),
            stage=row.get("stage", "DISCOVERY"),
            value_usd=float(row.get("value_usd", 0) or 0),
            probability=float(row.get("probability", 0.1) or 0.1),
            owner=row.get("owner", "mike"),
            created_at=_parse_dt(row.get("created_at")),
            updated_at=_parse_dt(row.get("updated_at")),
            next_action=row.get("next_action") or "",
            notes=row.get("notes") or "",
            source=row.get("source", "oracle_health"),
        )


# ---------------------------------------------------------------------------
# Pipeline Manager
# ---------------------------------------------------------------------------

class PipelineManager:
    """CRUD and analytics for the deals pipeline."""

    DEALS_TABLE = "jake_deals"
    EVENTS_TABLE = "jake_deal_events"

    def __init__(self):
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )

    # ------------------------------------------------------------------
    # Create / Update
    # ------------------------------------------------------------------

    def create_deal(
        self,
        name: str,
        company: str,
        stage: str = "DISCOVERY",
        value_usd: float = 0.0,
        probability: float | None = None,
        source: str = "oracle_health",
        owner: str = "mike",
        next_action: str = "",
        notes: str = "",
        metadata: dict | None = None,
    ) -> Deal:
        """Create a new deal record."""
        if stage not in STAGES:
            raise ValueError(f"Invalid stage '{stage}'. Must be one of: {STAGES}")

        prob = probability if probability is not None else STAGE_PROBABILITIES.get(stage, 0.1)
        now = datetime.now(timezone.utc).isoformat()

        row = {
            "name": name,
            "company": company,
            "stage": stage,
            "value_usd": value_usd,
            "probability": prob,
            "owner": owner,
            "source": source,
            "next_action": next_action,
            "notes": notes,
            "metadata": metadata or {},
        }

        result = self.supabase.table(self.DEALS_TABLE).insert(row).execute()
        deal_row = result.data[0] if result.data else {**row, "id": str(uuid.uuid4()),
                                                        "created_at": now, "updated_at": now}
        deal = Deal.from_row(deal_row)

        # Log creation event
        self._log_event(
            deal_id=deal.id,
            event_type="created",
            description=f"Deal created at stage {stage}",
            to_stage=stage,
        )
        return deal

    def update_stage(self, deal_id: str, new_stage: str, notes: str = "") -> Deal | None:
        """Move a deal to a new pipeline stage."""
        if new_stage not in STAGES:
            raise ValueError(f"Invalid stage '{new_stage}'. Must be one of: {STAGES}")

        # Get current deal
        result = self.supabase.table(self.DEALS_TABLE).select("*").eq("id", deal_id).execute()
        if not result.data:
            return None

        current = result.data[0]
        old_stage = current.get("stage", "DISCOVERY")
        new_prob = STAGE_PROBABILITIES.get(new_stage, current.get("probability", 0.1))

        updated = (
            self.supabase.table(self.DEALS_TABLE)
            .update({
                "stage": new_stage,
                "probability": new_prob,
                "notes": (current.get("notes") or "") + (f"\n{notes}" if notes else ""),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            .eq("id", deal_id)
            .execute()
        )

        # Log stage transition event
        self._log_event(
            deal_id=deal_id,
            event_type="stage_change",
            from_stage=old_stage,
            to_stage=new_stage,
            description=notes or f"Stage moved from {old_stage} to {new_stage}",
        )

        row = updated.data[0] if updated.data else {**current, "stage": new_stage}
        return Deal.from_row(row)

    def add_note(self, deal_id: str, note: str) -> None:
        """Append a note to a deal and log the event."""
        result = self.supabase.table(self.DEALS_TABLE).select("notes, updated_at").eq("id", deal_id).execute()
        if not result.data:
            return
        existing_notes = result.data[0].get("notes") or ""
        self.supabase.table(self.DEALS_TABLE).update({
            "notes": existing_notes + f"\n{note}",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", deal_id).execute()

        self._log_event(deal_id=deal_id, event_type="note_added", description=note)

    # ------------------------------------------------------------------
    # Queries / Analytics
    # ------------------------------------------------------------------

    def get_all_deals(self, source: str | None = None) -> list[Deal]:
        """Return all deals, optionally filtered by source."""
        query = self.supabase.table(self.DEALS_TABLE).select("*").neq("stage", "CLOSED_LOST")
        if source:
            query = query.eq("source", source)
        result = query.order("updated_at", desc=True).execute()
        return [Deal.from_row(r) for r in (result.data or [])]

    def get_pipeline_summary(self, source: str | None = None) -> dict[str, Any]:
        """Return {stage: [deals], total_value: N, weighted_value: N}."""
        deals = self.get_all_deals(source=source)

        by_stage: dict[str, list[dict]] = {s: [] for s in STAGES}
        total_value = 0.0
        weighted_value = 0.0

        for deal in deals:
            by_stage[deal.stage].append({
                "id": deal.id,
                "name": deal.name,
                "company": deal.company,
                "value_usd": deal.value_usd,
                "probability": deal.probability,
                "weighted_value": deal.weighted_value,
                "owner": deal.owner,
                "next_action": deal.next_action,
                "updated_at": deal.updated_at.isoformat(),
            })
            if deal.stage not in ("CLOSED_LOST",):
                total_value += deal.value_usd
                weighted_value += deal.weighted_value

        return {
            "stages": by_stage,
            "total_value": round(total_value, 2),
            "weighted_value": round(weighted_value, 2),
            "deal_count": len(deals),
            "source_filter": source,
        }

    def get_deals_needing_action(self, days_stale: int = 7) -> list[Deal]:
        """Return deals with no update in the last N days (excluding closed)."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days_stale)).isoformat()
        result = (
            self.supabase.table(self.DEALS_TABLE)
            .select("*")
            .lt("updated_at", cutoff)
            .neq("stage", "CLOSED_WON")
            .neq("stage", "CLOSED_LOST")
            .order("updated_at", desc=False)
            .execute()
        )
        return [Deal.from_row(r) for r in (result.data or [])]

    def calculate_revenue_impact(self, deal_id: str) -> dict[str, Any]:
        """Estimate the revenue impact of work done on a deal."""
        result = self.supabase.table(self.DEALS_TABLE).select("*").eq("id", deal_id).execute()
        if not result.data:
            return {"error": f"Deal {deal_id} not found"}

        deal = Deal.from_row(result.data[0])
        est_hours = STAGE_HOURS_EST.get(deal.stage, 50.0)
        hourly_value = (deal.value_usd * deal.probability / est_hours) if est_hours > 0 else 0

        return {
            "deal_id": deal_id,
            "deal_name": deal.name,
            "company": deal.company,
            "stage": deal.stage,
            "value_usd": deal.value_usd,
            "probability": deal.probability,
            "weighted_value": deal.weighted_value,
            "estimated_hours_to_close": est_hours,
            "estimated_hourly_value_usd": round(hourly_value, 2),
        }

    def get_customer_health_score(self, company: str) -> dict[str, Any]:
        """Estimate customer health based on deal activity and episodic memory."""
        # Get deals for this company
        result = (
            self.supabase.table(self.DEALS_TABLE)
            .select("*")
            .eq("company", company)
            .execute()
        )
        deals = [Deal.from_row(r) for r in (result.data or [])]

        # Get event count for these deals
        deal_ids = [d.id for d in deals]
        event_count = 0
        if deal_ids:
            try:
                ev_result = (
                    self.supabase.table(self.EVENTS_TABLE)
                    .select("id", count="exact")
                    .in_("deal_id", deal_ids)
                    .execute()
                )
                event_count = ev_result.count or 0
            except Exception:
                pass

        # Score: 0-100 based on deal progression + activity
        won_count = sum(1 for d in deals if d.stage == "CLOSED_WON")
        active_count = sum(1 for d in deals if d.stage not in ("CLOSED_WON", "CLOSED_LOST"))
        pipeline_value = sum(d.weighted_value for d in deals if d.stage not in ("CLOSED_LOST",))

        score = min(100, (
            won_count * 20 +
            active_count * 10 +
            min(event_count, 10) * 2 +
            min(pipeline_value / 10_000, 20)  # up to 20 pts for pipeline value
        ))

        return {
            "company": company,
            "health_score": round(score),
            "total_deals": len(deals),
            "won_deals": won_count,
            "active_deals": active_count,
            "total_interactions": event_count,
            "pipeline_weighted_value": round(pipeline_value, 2),
            "assessment": (
                "Healthy" if score >= 60 else
                "Needs attention" if score >= 30 else
                "At risk"
            ),
        }

    # ------------------------------------------------------------------
    # Seed data
    # ------------------------------------------------------------------

    def seed_sample_data(self) -> list[Deal]:
        """Create 3 sample Oracle Health deals for demo/testing purposes."""
        samples = [
            {
                "name": "Oracle Health EHR Intelligence Module",
                "company": "Oracle Health",
                "stage": "PROPOSAL",
                "value_usd": 250_000.0,
                "probability": 0.4,
                "source": "oracle_health",
                "next_action": "Send revised proposal deck by EOW",
                "notes": "Matt Cohlmia is the exec sponsor. Key concern: integration timeline.",
            },
            {
                "name": "Clinical AI Advisory Services",
                "company": "Oracle Health",
                "stage": "DEMO",
                "value_usd": 85_000.0,
                "probability": 0.6,
                "source": "oracle_health",
                "next_action": "Schedule technical deep-dive with engineering team",
                "notes": "Strong interest post-demo. Procurement review pending.",
            },
            {
                "name": "Susan Commercial License (Pilot)",
                "company": "Pilot Customer",
                "stage": "DISCOVERY",
                "value_usd": 50_000.0,
                "probability": 0.2,
                "source": "susan_commercial",
                "next_action": "Define success criteria for pilot program",
                "notes": "Early stage. Needs product-market fit validation.",
            },
        ]

        created_deals = []
        for s in samples:
            try:
                deal = self.create_deal(**s)
                created_deals.append(deal)
            except Exception as exc:
                # Non-fatal — may already exist
                print(f"  Warning: could not seed deal '{s['name']}': {exc}")

        return created_deals

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _log_event(
        self,
        deal_id: str,
        event_type: str,
        description: str = "",
        from_stage: str | None = None,
        to_stage: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Insert a deal event record."""
        try:
            self.supabase.table(self.EVENTS_TABLE).insert({
                "deal_id": deal_id,
                "event_type": event_type,
                "from_stage": from_stage,
                "to_stage": to_stage,
                "description": description,
                "metadata": metadata or {},
            }).execute()
        except Exception:
            pass  # Non-fatal


# ---------------------------------------------------------------------------
# Revenue Impact Tracker
# ---------------------------------------------------------------------------

class RevenueImpactTracker:
    """Log work activities and estimate their revenue impact."""

    ACTIVITIES_TABLE = "jake_deal_events"  # reuse events table with event_type="activity"

    def __init__(self):
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )
        self.pipeline = PipelineManager()

    def track_activity(
        self,
        activity_type: str,
        company: str,
        deal_id: str | None = None,
        hours_spent: float = 0.0,
        description: str = "",
    ) -> None:
        """Log a work activity and link to a deal if provided."""
        metadata = {
            "company": company,
            "hours_spent": hours_spent,
            "activity_type": activity_type,
        }

        if deal_id:
            try:
                self.supabase.table(self.ACTIVITIES_TABLE).insert({
                    "deal_id": deal_id,
                    "event_type": "activity",
                    "description": description or f"{activity_type} — {company}",
                    "metadata": metadata,
                }).execute()
            except Exception:
                pass
        # If no deal_id, activity is unlinked — still useful for time tracking

    def calculate_hourly_value(self, deal_id: str) -> float:
        """Return estimated USD per hour for a given deal."""
        result = (
            self.pipeline.supabase.table(PipelineManager.DEALS_TABLE)
            .select("value_usd, probability, stage")
            .eq("id", deal_id)
            .execute()
        )
        if not result.data:
            return 0.0

        row = result.data[0]
        value = float(row.get("value_usd", 0) or 0)
        prob = float(row.get("probability", 0.1) or 0.1)
        stage = row.get("stage", "DISCOVERY")
        est_hours = STAGE_HOURS_EST.get(stage, 50.0)

        return round((value * prob) / est_hours, 2) if est_hours > 0 else 0.0

    def weekly_impact_summary(self) -> dict[str, Any]:
        """Return activity summary for the last 7 days."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        try:
            result = (
                self.supabase.table(self.ACTIVITIES_TABLE)
                .select("deal_id, metadata, occurred_at")
                .eq("event_type", "activity")
                .gte("occurred_at", cutoff)
                .execute()
            )
            rows = result.data or []
        except Exception:
            return {"error": "Failed to fetch activity data"}

        companies: set[str] = set()
        total_hours = 0.0
        deal_ids: set[str] = set()

        for r in rows:
            meta = r.get("metadata") or {}
            companies.add(meta.get("company", "unknown"))
            total_hours += float(meta.get("hours_spent", 0) or 0)
            if r.get("deal_id"):
                deal_ids.add(r["deal_id"])

        # Estimate revenue impact
        estimated_impact = 0.0
        for deal_id in deal_ids:
            hourly = self.calculate_hourly_value(deal_id)
            estimated_impact += hourly * total_hours

        return {
            "period": "last_7_days",
            "activity_count": len(rows),
            "companies_touched": sorted(companies),
            "total_hours_logged": round(total_hours, 1),
            "deal_ids_touched": list(deal_ids),
            "estimated_revenue_impact_usd": round(estimated_impact, 2),
        }


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_pipeline: PipelineManager | None = None
_impact: RevenueImpactTracker | None = None


def get_pipeline() -> PipelineManager:
    global _pipeline
    if _pipeline is None:
        _pipeline = PipelineManager()
    return _pipeline


def get_impact_tracker() -> RevenueImpactTracker:
    global _impact
    if _impact is None:
        _impact = RevenueImpactTracker()
    return _impact
