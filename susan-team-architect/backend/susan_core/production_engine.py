"""Production engine — manages the lifecycle of film and image productions."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProductionStatus(str, Enum):
    DESIGN = "design"
    STORYBOARD = "storyboard"
    GENERATION = "generation"
    REFINEMENT = "refinement"
    DELIVERED = "delivered"


_PHASE_ORDER = [
    ProductionStatus.DESIGN,
    ProductionStatus.STORYBOARD,
    ProductionStatus.GENERATION,
    ProductionStatus.REFINEMENT,
    ProductionStatus.DELIVERED,
]


@dataclass
class Production:
    production_id: str
    brief: str
    company_id: str
    format: str
    status: ProductionStatus = ProductionStatus.DESIGN
    agents_assigned: list[str] = field(default_factory=list)
    outputs: list[dict[str, Any]] = field(default_factory=list)


class ProductionEngine:
    """In-memory production lifecycle manager."""

    def __init__(self) -> None:
        self._productions: dict[str, Production] = {}

    def start(
        self,
        brief: str,
        company_id: str,
        format: str,
        title: str | None = None,
    ) -> Production:
        prod_id = f"prod-{uuid.uuid4().hex[:12]}"
        prod = Production(
            production_id=prod_id,
            brief=brief,
            company_id=company_id,
            format=format,
        )
        self._productions[prod_id] = prod
        return prod

    def list_productions(self, company_id: str) -> list[Production]:
        return [p for p in self._productions.values() if p.company_id == company_id]

    def get_status(self, production_id: str) -> dict[str, Any]:
        prod = self._productions[production_id]
        return {
            "production_id": prod.production_id,
            "brief": prod.brief,
            "company_id": prod.company_id,
            "format": prod.format,
            "phase": prod.status.value,
            "agents_assigned": prod.agents_assigned,
            "outputs": prod.outputs,
        }

    def advance_phase(self, production_id: str) -> ProductionStatus:
        prod = self._productions[production_id]
        idx = _PHASE_ORDER.index(prod.status)
        if idx < len(_PHASE_ORDER) - 1:
            prod.status = _PHASE_ORDER[idx + 1]
        return prod.status

    def assign_agents(self, production_id: str, agent_ids: list[str]) -> None:
        self._productions[production_id].agents_assigned.extend(agent_ids)

    def add_output(self, production_id: str, output: dict[str, Any]) -> None:
        self._productions[production_id].outputs.append(output)
