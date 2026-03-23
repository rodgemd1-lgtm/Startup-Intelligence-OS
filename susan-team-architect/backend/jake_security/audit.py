"""Audit Trail — log all Jake operations to Supabase jake_audit_log table.

Every agent action, pipeline execution, and security event is recorded
with actor, action, resource, outcome, and sanitized context.
"""
from __future__ import annotations

import json
import os
import traceback
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from supabase import create_client, Client


class AuditEvent(str, Enum):
    # Brain operations
    BRAIN_READ = "brain.read"
    BRAIN_WRITE = "brain.write"
    BRAIN_PROMOTE = "brain.promote"
    BRAIN_CONTRADICT = "brain.contradict"

    # Pipeline operations
    PIPELINE_START = "pipeline.start"
    PIPELINE_PHASE = "pipeline.phase"
    PIPELINE_COMPLETE = "pipeline.complete"
    PIPELINE_FAIL = "pipeline.fail"
    PIPELINE_HEAL = "pipeline.heal"

    # Employee operations
    EMPLOYEE_RUN = "employee.run"
    EMPLOYEE_COMPLETE = "employee.complete"
    EMPLOYEE_FAIL = "employee.fail"

    # Security events
    SECURITY_VAULT_ACCESS = "security.vault_access"
    SECURITY_AUTH_FAIL = "security.auth_fail"
    SECURITY_RATE_LIMIT = "security.rate_limit"
    SECURITY_PII_DETECTED = "security.pii_detected"
    SECURITY_PERMISSION_DENY = "security.permission_deny"

    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_CRON = "system.cron"
    SYSTEM_EVOLVE = "system.evolve"

    # Cost events
    COST_API_CALL = "cost.api_call"
    COST_EMBED = "cost.embed"
    COST_MONTHLY_REPORT = "cost.monthly_report"


class AuditTrail:
    """Write-only audit log. Records all operations to jake_audit_log."""

    def __init__(self):
        self._client: Client | None = None
        self._fallback_log: list[dict] = []  # in-memory fallback if Supabase unavailable

    def _get_client(self) -> Client | None:
        if self._client:
            return self._client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            # Try loading from ~/.hermes/.env
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

    def log(
        self,
        event: AuditEvent | str,
        actor: str,
        resource: str = "",
        outcome: str = "success",
        context: dict | None = None,
        error: str = "",
    ) -> None:
        """Write an audit event. Never raises — failures are silently swallowed."""
        record = {
            "event": str(event),
            "actor": actor,
            "resource": resource,
            "outcome": outcome,
            "context": _sanitize(context or {}),
            "error": error[:2000] if error else "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            client = self._get_client()
            if client:
                client.table("jake_audit_log").insert(record).execute()
            else:
                self._fallback_log.append(record)
        except Exception:
            self._fallback_log.append(record)

    def log_error(self, event: AuditEvent | str, actor: str, exc: Exception, resource: str = "") -> None:
        """Convenience method: log a failure with exception details."""
        self.log(
            event=event,
            actor=actor,
            resource=resource,
            outcome="failure",
            error=traceback.format_exc()[:2000],
        )

    def get_recent(self, limit: int = 50, actor: str | None = None) -> list[dict]:
        """Fetch recent audit events from Supabase."""
        try:
            client = self._get_client()
            if not client:
                return self._fallback_log[-limit:]
            query = client.table("jake_audit_log").select("*").order(
                "created_at", desc=True
            ).limit(limit)
            if actor:
                query = query.eq("actor", actor)
            result = query.execute()
            return result.data or []
        except Exception:
            return self._fallback_log[-limit:]

    def get_security_events(self, hours: int = 24) -> list[dict]:
        """Fetch security events from the last N hours."""
        try:
            client = self._get_client()
            if not client:
                return [e for e in self._fallback_log if "security." in e.get("event", "")]
            from datetime import timedelta
            since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            result = client.table("jake_audit_log").select("*").gte(
                "created_at", since
            ).like("event", "security.%").order("created_at", desc=True).execute()
            return result.data or []
        except Exception:
            return []


def _sanitize(data: dict) -> dict:
    """Remove any credential-like values from context before logging."""
    _REDACT_KEYS = {"key", "token", "secret", "password", "api_key", "auth", "credential"}
    sanitized = {}
    for k, v in data.items():
        if any(rk in k.lower() for rk in _REDACT_KEYS):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = _sanitize(v)
        else:
            sanitized[k] = v
    return sanitized


audit = AuditTrail()
