"""AI Employee registry — autonomous agent loops that run on schedule."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class EmployeeSpec:
    name: str
    description: str
    cron: str        # cron expression
    actor: str       # access control actor name
    module: str      # dotted module path
    enabled: bool = True


EMPLOYEE_REGISTRY: dict[str, EmployeeSpec] = {
    "oracle_sentinel": EmployeeSpec(
        name="oracle_sentinel",
        description="Daily Oracle Health competitive intelligence and briefing",
        cron="0 6 * * 1-5",  # 6 AM weekdays
        actor="oracle_sentinel",
        module="jake_brain.employees.oracle_sentinel",
    ),
    "inbox_zero": EmployeeSpec(
        name="inbox_zero",
        description="Email triage and action extraction (3x daily weekdays)",
        cron="0 8,12,17 * * 1-5",
        actor="inbox_zero",
        module="jake_brain.employees.inbox_zero",
    ),
    "meeting_prep": EmployeeSpec(
        name="meeting_prep",
        description="Pre-meeting research and briefing generation",
        cron="0 7 * * 1-5",  # 7 AM weekdays — prep for the day's meetings
        actor="meeting_prep",
        module="jake_brain.employees.meeting_prep",
    ),
    "research_agent": EmployeeSpec(
        name="research_agent",
        description="Autonomous background research on queued topics",
        cron="0 3 * * *",  # 3 AM daily
        actor="research_agent",
        module="jake_brain.employees.research_agent",
    ),
}


def get_employee(name: str) -> EmployeeSpec | None:
    return EMPLOYEE_REGISTRY.get(name)


def list_employees() -> list[EmployeeSpec]:
    return list(EMPLOYEE_REGISTRY.values())
