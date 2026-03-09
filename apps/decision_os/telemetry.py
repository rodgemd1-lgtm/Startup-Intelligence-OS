"""Telemetry and audit trail for Decision OS runs.

Every decision run logs step-level events with timestamps, evidence IDs,
confidence/uncertainty, and outputs. Runs are fully replayable from the
event trace.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Run, RunEvent, RunStatus, OutputContract, _now
from .store import Store


class RunTracer:
    """Wraps a Run object and provides step-level logging with persistence."""

    def __init__(self, run: Run, store: Store):
        self._run = run
        self._store = store

    @property
    def run(self) -> Run:
        return self._run

    def log(self, step: str, data: dict[str, Any] | None = None,
            evidence_ids: list[str] | None = None,
            confidence: float = 0.5) -> RunEvent:
        evt = self._run.add_event(
            step=step,
            data=data,
            evidence_ids=evidence_ids,
            confidence=confidence,
        )
        self._store.runs.save(self._run)
        return evt

    def complete(self, output: OutputContract | None = None) -> Run:
        self._run.complete(output)
        self._store.runs.save(self._run)
        return self._run

    def fail(self, reason: str) -> Run:
        self._run.status = RunStatus.failed
        self._run.completed_at = _now()
        self._run.add_event("failure", data={"reason": reason}, confidence=1.0)
        self._store.runs.save(self._run)
        return self._run

    def replay(self) -> list[dict]:
        """Return the full event trace for audit replay."""
        return [evt.model_dump(mode="json") for evt in self._run.events]


def start_run(store: Store, trigger: str, decision: str = "",
              company: str = "", project: str = "",
              mode: str = "decision") -> RunTracer:
    """Create and persist a new run, returning a tracer for step logging."""
    run = Run(
        trigger=trigger,
        decision=decision,
        company=company,
        project=project,
        mode=mode,
    )
    store.runs.save(run)
    return RunTracer(run, store)
