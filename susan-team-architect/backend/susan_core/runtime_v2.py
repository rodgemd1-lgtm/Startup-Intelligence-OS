"""V2 runtime -- wraps existing phase_runtime with queue, router, cache, and tracing.

This is an ADDITIVE module. It does not modify phase_runtime.py.
Existing orchestrator.py and phase_runtime.py continue to work unchanged.
To use the new runtime, import RuntimeV2 instead.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

from susan_core.parallel_orchestrator import PhaseDAG
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
        dag: PhaseDAG | None = None,
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
        self.dag = dag or PhaseDAG()

    def execute_phases(self, phase_fns: dict[str, Callable[[], Any]]) -> dict[str, Any]:
        """Execute phase functions respecting DAG parallelism with tracing.

        Args:
            phase_fns: Mapping of phase name to a callable that returns a result.

        Returns:
            Mapping of phase name to its return value (or the raised exception).
        """
        results: dict[str, Any] = {}
        groups = self.dag.parallel_groups()

        for group in groups:
            # Only execute phases that the caller actually provided
            runnable = group & set(phase_fns)
            if not runnable:
                continue

            with ThreadPoolExecutor(max_workers=len(runnable)) as pool:
                futures = {}
                for name in runnable:
                    futures[pool.submit(self._run_phase, name, phase_fns[name])] = name

                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        results[name] = future.result()
                    except Exception as exc:  # noqa: BLE001
                        results[name] = exc

        return results

    def _run_phase(self, name: str, fn: Callable[[], Any]) -> Any:
        """Run a single phase function with tracer bookends."""
        self.tracer.start_phase(name)
        try:
            result = fn()
        except Exception:
            self.tracer.end_phase(name)
            raise
        self.tracer.end_phase(name)
        return result

    def telemetry(self) -> dict:
        """Full runtime telemetry snapshot."""
        return {
            "queue": self.queue.telemetry(),
            "metrics": self.metrics.summary(),
            "health": self.health.check(),
            "cache": self.cache.stats(),
            "tracer": self.tracer.to_dict(),
        }
