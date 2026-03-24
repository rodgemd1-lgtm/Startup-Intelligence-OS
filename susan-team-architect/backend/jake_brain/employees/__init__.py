<<<<<<< HEAD
"""AI Employee Registry."""
from .oracle_sentinel import OracleSentinel
from .research_agent import ResearchAgent
from .content_creator import ContentCreator
from .family_coordinator import FamilyCoordinator

EMPLOYEE_REGISTRY = {
    "oracle_sentinel": OracleSentinel,
    "research_agent": ResearchAgent,
    "content_creator": ContentCreator,
    "family_coordinator": FamilyCoordinator,
}

EMPLOYEE_SCHEDULES = {
    "oracle_sentinel": "0 6 * * 1-5",     # Daily 6 AM weekdays
    "research_agent": "0 22 * * *",        # Daily 10 PM
    "content_creator": "0 9 * * 1",        # Monday 9 AM
    "family_coordinator": "0 7 * * 0",     # Sunday 7 AM (weekly family summary)
}
=======
"""AI Employee registry — all autonomous employee loops.

Each employee is a specialized AutonomousPipeline that runs on a cron schedule
and performs a specific recurring task autonomously.

Registry maps employee_name → (class, cron_schedules)
"""
from __future__ import annotations

EMPLOYEE_REGISTRY = {
    "oracle_sentinel": {
        "module": "jake_brain.employees.oracle_sentinel",
        "class": "OracleSentinel",
        "description": "Oracle Health competitor intelligence — daily 6 AM weekdays",
        "cron_jobs": ["oracle_sentinel_daily"],
        "cron_schedules": ["0 6 * * 1-5"],  # Mon-Fri 6 AM
        "trigger": "daily",
    },
    "inbox_zero": {
        "module": "jake_brain.employees.inbox_zero",
        "class": "InboxZero",
        "description": "Apple Mail inbox triage — 3x daily weekdays",
        "cron_jobs": ["inbox_zero_morning", "inbox_zero_midday", "inbox_zero_evening"],
        "cron_schedules": [
            "0 8 * * 1-5",   # Mon-Fri 8 AM
            "0 12 * * 1-5",  # Mon-Fri 12 PM
            "0 17 * * 1-5",  # Mon-Fri 5 PM
        ],
        "trigger": "3x_daily",
    },
}


def get_employee(name: str):
    """Instantiate an employee by name. Returns None if not found."""
    if name not in EMPLOYEE_REGISTRY:
        return None

    entry = EMPLOYEE_REGISTRY[name]
    import importlib
    mod = importlib.import_module(entry["module"])
    cls = getattr(mod, entry["class"])
    return cls()


def list_employees() -> list[dict]:
    """Return all registered employees with their metadata."""
    return [
        {"name": name, **{k: v for k, v in meta.items() if k != "module"}}
        for name, meta in EMPLOYEE_REGISTRY.items()
    ]
>>>>>>> claude/nifty-ptolemy
