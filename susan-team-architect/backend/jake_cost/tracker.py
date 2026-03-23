"""Cost Tracker — log every API call cost to jake_cost_events table."""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from supabase import create_client, Client

from .router import ModelTier, _MODEL_PRICING


@dataclass
class CostEvent:
    service: str
    operation: str
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    actor: str = "system"
    pipeline_run_id: Optional[str] = None

    def to_record(self) -> dict:
        return {
            "service": self.service,
            "operation": self.operation,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": round(self.cost_usd, 8),
            "actor": self.actor,
            "pipeline_run_id": self.pipeline_run_id,
        }


class CostTracker:
    """Record and query API call costs."""

    def __init__(self):
        self._client: Client | None = None
        self._fallback: list[dict] = []  # in-memory if DB unavailable

    def _get_client(self) -> Client | None:
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
        if url and key:
            self._client = create_client(url, key)
        return self._client

    def record(self, event: CostEvent) -> None:
        """Write a cost event. Never raises."""
        record = event.to_record()
        try:
            client = self._get_client()
            if client:
                client.table("jake_cost_events").insert(record).execute()
            else:
                self._fallback.append(record)
        except Exception:
            self._fallback.append(record)

    def record_anthropic_call(
        self,
        tier: ModelTier,
        input_tokens: int,
        output_tokens: int,
        actor: str = "system",
        pipeline_run_id: str | None = None,
    ) -> float:
        """Record an Anthropic API call and return the cost in USD."""
        pricing = _MODEL_PRICING[tier]
        cost = (
            (input_tokens / 1_000_000) * pricing["input_per_1m"] +
            (output_tokens / 1_000_000) * pricing["output_per_1m"]
        )
        self.record(CostEvent(
            service="anthropic",
            operation="completion",
            model=pricing["model_id"],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            actor=actor,
            pipeline_run_id=pipeline_run_id,
        ))
        return cost

    def record_voyage_embed(
        self,
        token_count: int,
        actor: str = "system",
    ) -> float:
        """Record a Voyage AI embedding call. ~$0.06/1M tokens."""
        cost = (token_count / 1_000_000) * 0.06
        self.record(CostEvent(
            service="voyage",
            operation="embed",
            model="voyage-3",
            input_tokens=token_count,
            cost_usd=cost,
            actor=actor,
        ))
        return cost

    def monthly_totals(self, year: int | None = None, month: int | None = None) -> dict:
        """Return cost totals for a given month (defaults to current)."""
        now = datetime.now(timezone.utc)
        year = year or now.year
        month = month or now.month
        start = f"{year:04d}-{month:02d}-01T00:00:00Z"
        if month == 12:
            end = f"{year+1:04d}-01-01T00:00:00Z"
        else:
            end = f"{year:04d}-{month+1:02d}-01T00:00:00Z"

        try:
            client = self._get_client()
            if not client:
                return self._fallback_monthly(start, end)
            result = client.table("jake_cost_events").select(
                "service,cost_usd,input_tokens,output_tokens"
            ).gte("created_at", start).lt("created_at", end).execute()
            events = result.data or []
        except Exception:
            events = self._fallback

        by_service: dict[str, dict] = {}
        total_cost = 0.0
        for e in events:
            svc = e.get("service", "unknown")
            if svc not in by_service:
                by_service[svc] = {"cost": 0.0, "calls": 0, "tokens": 0}
            by_service[svc]["cost"] += float(e.get("cost_usd", 0))
            by_service[svc]["calls"] += 1
            by_service[svc]["tokens"] += int(e.get("input_tokens", 0)) + int(e.get("output_tokens", 0))
            total_cost += float(e.get("cost_usd", 0))

        return {
            "period": f"{year:04d}-{month:02d}",
            "total_cost_usd": round(total_cost, 4),
            "total_calls": len(events),
            "by_service": {k: {
                "cost_usd": round(v["cost"], 4),
                "calls": v["calls"],
                "tokens": v["tokens"],
            } for k, v in by_service.items()},
        }

    def _fallback_monthly(self, start: str, end: str) -> dict:
        return {"period": "unknown", "total_cost_usd": 0, "total_calls": len(self._fallback), "by_service": {}}

    def daily_totals(self, days: int = 30) -> list[dict]:
        """Return daily cost totals for the last N days."""
        from datetime import timedelta
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        try:
            client = self._get_client()
            if not client:
                return []
            result = client.table("jake_cost_events").select(
                "created_at,cost_usd,service"
            ).gte("created_at", since).order("created_at").execute()
            events = result.data or []
        except Exception:
            return []

        # Aggregate by date
        by_date: dict[str, float] = {}
        for e in events:
            day = e.get("created_at", "")[:10]
            by_date[day] = by_date.get(day, 0.0) + float(e.get("cost_usd", 0))

        return [{"date": d, "cost_usd": round(c, 4)} for d, c in sorted(by_date.items())]


cost_tracker = CostTracker()
