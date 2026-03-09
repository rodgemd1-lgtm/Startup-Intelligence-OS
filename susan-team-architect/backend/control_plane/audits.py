"""Audit helpers for the intelligence cockpit."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import re

from .schemas import BacklogItem, ReconciliationIssue

FRESHNESS_WINDOWS = {
    "monthly": 31,
    "quarterly": 92,
    "semiannual": 184,
}

SEVERITY_WEIGHTS = {
    "critical": 100,
    "high": 70,
    "warning": 40,
    "info": 15,
}


def freshness_status(effective_date: date | None, cadence: str) -> str:
    if not effective_date:
        return "unknown"
    window = FRESHNESS_WINDOWS.get(cadence, 92)
    if effective_date < (date.today() - timedelta(days=window)):
        return "stale"
    return "current"


def make_issue(
    issue_id: str,
    severity: str,
    area: str,
    title: str,
    detail: str,
    recommendation: str,
    file_path: str | None = None,
) -> ReconciliationIssue:
    return ReconciliationIssue(
        id=issue_id,
        severity=severity,
        area=area,
        title=title,
        detail=detail,
        file_path=file_path,
        recommendation=recommendation,
    )


def issue_to_backlog(issue: ReconciliationIssue, tenant_id: str = "shared", owner: str | None = None) -> BacklogItem:
    return BacklogItem(
        id=f"backlog-{issue.id}",
        title=issue.title,
        reason=issue.recommendation,
        score=SEVERITY_WEIGHTS.get(issue.severity, 10),
        owner=owner,
        tenant_id=tenant_id,
    )


def extract_numeric_claim(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text)
    if not match:
        return None
    digits = re.sub(r"[^\d]", "", match.group(1))
    return int(digits) if digits else None


def file_exists_health(command_path: str | None) -> str:
    if not command_path:
        return "unknown"
    return "healthy" if Path(command_path).exists() else "missing"
