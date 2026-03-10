"""Supabase persistence layer for the Film & Image Studio production engine."""
from __future__ import annotations

import json
import logging
from typing import Any

from susan_core.production_engine import (
    Production,
    ProductionStatus,
    QualityGateResult,
)

logger = logging.getLogger(__name__)


class ProductionStore:
    """Thin Supabase wrapper for persisting productions across sessions.

    Usage::

        from supabase import create_client
        client = create_client(url, key)
        store = ProductionStore(client)
        engine = ProductionEngine(store=store)
    """

    TABLE = "productions"

    def __init__(self, supabase_client: Any) -> None:
        self.client = supabase_client

    # ── Write operations ──────────────────────────────────────

    def save(self, production: Production) -> None:
        """Upsert a full production record."""
        row = self._to_row(production)
        self.client.table(self.TABLE).upsert(row, on_conflict="production_id").execute()

    def update_status(self, production_id: str, status: str) -> None:
        """Update only the status field."""
        self.client.table(self.TABLE).update(
            {"status": status}
        ).eq("production_id", production_id).execute()

    def update_agents(self, production_id: str, agents: list[str]) -> None:
        """Replace the agents_assigned array."""
        self.client.table(self.TABLE).update(
            {"agents_assigned": agents}
        ).eq("production_id", production_id).execute()

    def add_output(self, production_id: str, output: dict) -> None:
        """Append an output to the outputs JSONB array."""
        # Read current, append, write back (Supabase doesn't support array_append on jsonb)
        result = (
            self.client.table(self.TABLE)
            .select("outputs")
            .eq("production_id", production_id)
            .single()
            .execute()
        )
        current = result.data.get("outputs", []) if result.data else []
        current.append(output)
        self.client.table(self.TABLE).update(
            {"outputs": current}
        ).eq("production_id", production_id).execute()

    def add_quality_result(self, production_id: str, result_dict: dict) -> None:
        """Append or replace a quality gate result."""
        result = (
            self.client.table(self.TABLE)
            .select("quality_results")
            .eq("production_id", production_id)
            .single()
            .execute()
        )
        current = result.data.get("quality_results", []) if result.data else []
        # Replace existing result for same gate
        current = [r for r in current if r.get("gate_name") != result_dict.get("gate_name")]
        current.append(result_dict)
        self.client.table(self.TABLE).update(
            {"quality_results": current}
        ).eq("production_id", production_id).execute()

    # ── Read operations ───────────────────────────────────────

    def load(self, production_id: str) -> Production | None:
        """Load a single production by ID."""
        result = (
            self.client.table(self.TABLE)
            .select("*")
            .eq("production_id", production_id)
            .single()
            .execute()
        )
        if not result.data:
            return None
        return self._from_row(result.data)

    def list_by_company(self, company_id: str) -> list[Production]:
        """List all productions for a company."""
        result = (
            self.client.table(self.TABLE)
            .select("*")
            .eq("company_id", company_id)
            .order("created_at", desc=True)
            .execute()
        )
        return [self._from_row(row) for row in (result.data or [])]

    def list_active(self) -> list[Production]:
        """List all non-delivered productions (for engine init)."""
        result = (
            self.client.table(self.TABLE)
            .select("*")
            .neq("status", "delivered")
            .order("created_at", desc=True)
            .execute()
        )
        return [self._from_row(row) for row in (result.data or [])]

    # ── Serialization ─────────────────────────────────────────

    @staticmethod
    def _to_row(prod: Production) -> dict[str, Any]:
        return {
            "production_id": prod.production_id,
            "company_id": prod.company_id,
            "brief": prod.brief,
            "format": prod.format,
            "status": prod.status.value,
            "agents_assigned": prod.agents_assigned,
            "outputs": prod.outputs,
            "quality_results": [
                {
                    "gate_name": r.gate_name,
                    "passed": r.passed,
                    "score": r.score,
                    "details": r.details,
                }
                for r in prod.quality_results
            ],
        }

    @staticmethod
    def _from_row(row: dict[str, Any]) -> Production:
        quality_results = []
        for r in row.get("quality_results", []):
            quality_results.append(
                QualityGateResult(
                    gate_name=r["gate_name"],
                    passed=r["passed"],
                    score=r["score"],
                    details=r.get("details", ""),
                )
            )
        return Production(
            production_id=row["production_id"],
            brief=row["brief"],
            company_id=row["company_id"],
            format=row["format"],
            status=ProductionStatus(row["status"]),
            agents_assigned=row.get("agents_assigned", []),
            outputs=row.get("outputs", []),
            quality_results=quality_results,
        )
