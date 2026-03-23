"""Deal Tracker — CRM-style deal management backed by Supabase jake_deals table."""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from supabase import create_client, Client


class DealStage(str, Enum):
    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

    @property
    def weight(self) -> float:
        """Probability weight for weighted pipeline value."""
        return {
            "prospect": 0.10,
            "qualified": 0.25,
            "proposal": 0.50,
            "negotiation": 0.75,
            "closed_won": 1.00,
            "closed_lost": 0.00,
        }[self.value]


@dataclass
class Deal:
    company: str
    deal_type: str = "sales"
    contact_name: str = ""
    contact_email: str = ""
    stage: DealStage = DealStage.PROSPECT
    value_usd: float = 0.0
    probability: int = 0
    expected_close: Optional[date] = None
    notes: str = ""
    next_action: str = ""
    next_action_due: Optional[date] = None
    id: Optional[str] = None
    created_at: Optional[str] = None

    @property
    def weighted_value(self) -> float:
        return self.value_usd * (self.probability / 100.0)

    def to_record(self) -> dict:
        return {
            "company": self.company,
            "deal_type": self.deal_type,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "stage": self.stage.value,
            "value_usd": self.value_usd,
            "probability": self.probability,
            "expected_close": str(self.expected_close) if self.expected_close else None,
            "notes": self.notes,
            "next_action": self.next_action,
            "next_action_due": str(self.next_action_due) if self.next_action_due else None,
        }

    @classmethod
    def from_record(cls, r: dict) -> "Deal":
        return cls(
            id=r.get("id"),
            company=r.get("company", ""),
            deal_type=r.get("deal_type", "sales"),
            contact_name=r.get("contact_name", ""),
            contact_email=r.get("contact_email", ""),
            stage=DealStage(r.get("stage", "prospect")),
            value_usd=float(r.get("value_usd", 0)),
            probability=int(r.get("probability", 0)),
            expected_close=date.fromisoformat(r["expected_close"]) if r.get("expected_close") else None,
            notes=r.get("notes", ""),
            next_action=r.get("next_action", ""),
            next_action_due=date.fromisoformat(r["next_action_due"]) if r.get("next_action_due") else None,
            created_at=r.get("created_at"),
        )


class DealTracker:
    """CRUD operations for the jake_deals table."""

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

    def create(self, deal: Deal) -> Deal:
        """Insert a new deal. Returns deal with assigned ID."""
        record = deal.to_record()
        result = self._get_client().table("jake_deals").insert(record).execute()
        deal.id = result.data[0]["id"]
        deal.created_at = result.data[0]["created_at"]
        self._log_event(deal.id, "deal_created", "", deal.stage.value, f"Deal created: {deal.company}")
        return deal

    def update(self, deal_id: str, **kwargs) -> dict:
        """Update deal fields by ID."""
        # Convert enums to values
        if "stage" in kwargs and isinstance(kwargs["stage"], DealStage):
            kwargs["stage"] = kwargs["stage"].value
        if "expected_close" in kwargs and isinstance(kwargs.get("expected_close"), date):
            kwargs["expected_close"] = str(kwargs["expected_close"])
        kwargs["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = self._get_client().table("jake_deals").update(kwargs).eq("id", deal_id).execute()
        return result.data[0] if result.data else {}

    def advance_stage(self, deal_id: str, to_stage: DealStage, notes: str = "") -> None:
        """Move a deal to the next stage."""
        current = self.get(deal_id)
        if not current:
            raise ValueError(f"Deal {deal_id} not found")
        self.update(deal_id, stage=to_stage, probability=int(to_stage.weight * 100))
        self._log_event(deal_id, "stage_change", current.stage.value, to_stage.value, notes)

    def get(self, deal_id: str) -> Optional[Deal]:
        result = self._get_client().table("jake_deals").select("*").eq("id", deal_id).execute()
        if result.data:
            return Deal.from_record(result.data[0])
        return None

    def list_active(self) -> list[Deal]:
        """All deals not in closed_won or closed_lost."""
        result = self._get_client().table("jake_deals").select("*").not_.in_(
            "stage", ["closed_won", "closed_lost"]
        ).order("updated_at", desc=True).execute()
        return [Deal.from_record(r) for r in (result.data or [])]

    def list_by_stage(self, stage: DealStage) -> list[Deal]:
        result = self._get_client().table("jake_deals").select("*").eq(
            "stage", stage.value
        ).order("value_usd", desc=True).execute()
        return [Deal.from_record(r) for r in (result.data or [])]

    def pipeline_summary(self) -> dict:
        """Return pipeline totals by stage."""
        deals = self.list_active()
        by_stage: dict[str, list[Deal]] = {}
        for d in deals:
            by_stage.setdefault(d.stage.value, []).append(d)

        summary = {
            "total_deals": len(deals),
            "total_value": sum(d.value_usd for d in deals),
            "weighted_value": sum(d.weighted_value for d in deals),
            "by_stage": {
                stage: {
                    "count": len(stage_deals),
                    "total_value": sum(d.value_usd for d in stage_deals),
                    "weighted_value": sum(d.weighted_value for d in stage_deals),
                }
                for stage, stage_deals in by_stage.items()
            },
        }
        return summary

    def overdue_actions(self) -> list[Deal]:
        """Deals with overdue next actions."""
        today = str(date.today())
        result = self._get_client().table("jake_deals").select("*").lte(
            "next_action_due", today
        ).not_.in_("stage", ["closed_won", "closed_lost"]).execute()
        return [Deal.from_record(r) for r in (result.data or [])]

    def _log_event(self, deal_id: str, event_type: str, from_stage: str, to_stage: str, notes: str) -> None:
        try:
            self._get_client().table("jake_pipeline_events").insert({
                "deal_id": deal_id,
                "event_type": event_type,
                "from_stage": from_stage,
                "to_stage": to_stage,
                "notes": notes,
                "actor": "jake",
            }).execute()
        except Exception:
            pass
