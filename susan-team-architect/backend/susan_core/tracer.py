"""Structured run traces with correlation IDs and per-phase metrics."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class PhaseTrace:
    phase: str
    started_at: float = 0.0
    ended_at: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    cost: float = 0.0
    duration_ms: int = 0
    model: str = ""
    cache_hit: bool = False
    error: str | None = None


class RunTracer:
    """Collects per-phase traces for a Susan run."""

    def __init__(self, run_id: str | None = None):
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.correlation_id = f"{self.run_id}-{uuid.uuid4().hex[:8]}"
        self._traces: dict[str, PhaseTrace] = {}
        self._order: list[str] = []

    def start_phase(self, phase: str) -> None:
        trace = PhaseTrace(phase=phase, started_at=time.time())
        self._traces[phase] = trace
        if phase not in self._order:
            self._order.append(phase)

    def end_phase(
        self,
        phase: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost: float = 0.0,
        model: str = "",
        cache_hit: bool = False,
        error: str | None = None,
    ) -> None:
        trace = self._traces.get(phase)
        if trace is None:
            return
        trace.ended_at = time.time()
        trace.duration_ms = max(1, int((trace.ended_at - trace.started_at) * 1000))
        trace.tokens_in = tokens_in
        trace.tokens_out = tokens_out
        trace.cost = cost
        trace.model = model
        trace.cache_hit = cache_hit
        trace.error = error

    def get_traces(self) -> list[PhaseTrace]:
        return [self._traces[p] for p in self._order if p in self._traces]

    def total_cost(self) -> float:
        return sum(t.cost for t in self._traces.values())

    def total_tokens(self) -> tuple[int, int]:
        return (
            sum(t.tokens_in for t in self._traces.values()),
            sum(t.tokens_out for t in self._traces.values()),
        )

    def total_duration_ms(self) -> int:
        return sum(t.duration_ms for t in self._traces.values())

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "total_cost": self.total_cost(),
            "total_tokens_in": self.total_tokens()[0],
            "total_tokens_out": self.total_tokens()[1],
            "total_duration_ms": self.total_duration_ms(),
            "phases": [
                {
                    "phase": t.phase,
                    "duration_ms": t.duration_ms,
                    "tokens_in": t.tokens_in,
                    "tokens_out": t.tokens_out,
                    "cost": t.cost,
                    "model": t.model,
                    "cache_hit": t.cache_hit,
                    "error": t.error,
                }
                for t in self.get_traces()
            ],
        }
