"""V2 runtime -- wraps existing phase_runtime with queue, router, cache, and tracing.

This is an ADDITIVE module. It does not modify phase_runtime.py.
Existing orchestrator.py and phase_runtime.py continue to work unchanged.
To use the new runtime, import RuntimeV2 instead.
"""
from __future__ import annotations

from susan_core.queue import PriorityQueue
from susan_core.router import ModelRouter
from susan_core.tracer import RunTracer
from susan_core.metrics import MetricsCollector
from susan_core.health import HealthChecker
from rag_engine.cache import QueryCache


class RuntimeV2:
    """Production runtime with queue, routing, caching, and observability."""

    def __init__(
        self,
        max_concurrent: int = 10,
        token_quota_per_minute: int = 0,
        max_cost_per_call: float = 0.0,
        cache_ttl_seconds: float = 300.0,
        run_id: str | None = None,
    ):
        self.queue = PriorityQueue(
            max_concurrent=max_concurrent,
            token_quota_per_minute=token_quota_per_minute,
        )
        self.router = ModelRouter(max_cost_per_call=max_cost_per_call)
        self.tracer = RunTracer(run_id=run_id)
        self.metrics = MetricsCollector()
        self.health = HealthChecker()
        self.cache = QueryCache(ttl_seconds=cache_ttl_seconds)

    def telemetry(self) -> dict:
        """Full runtime telemetry snapshot."""
        return {
            "queue": self.queue.telemetry(),
            "metrics": self.metrics.summary(),
            "health": self.health.check(),
            "cache": self.cache.stats(),
            "tracer": self.tracer.to_dict(),
        }
