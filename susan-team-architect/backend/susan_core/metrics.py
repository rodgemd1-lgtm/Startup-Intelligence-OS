"""Runtime metrics collector — latencies, costs, errors, token usage."""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock


class MetricsCollector:
    """Collects runtime metrics for /metrics endpoint."""

    def __init__(self, window_seconds: float = 300.0):
        self._lock = Lock()
        self._window = window_seconds
        self._latencies: dict[str, list[tuple[float, float]]] = defaultdict(list)
        self._costs: dict[str, float] = defaultdict(float)
        self._errors: dict[str, int] = defaultdict(int)
        self._tokens: dict[str, int] = defaultdict(int)
        self._request_count: int = 0

    def record_latency(self, operation: str, latency_ms: float) -> None:
        with self._lock:
            self._latencies[operation].append((time.time(), latency_ms))
            self._request_count += 1

    def record_cost(self, model: str, cost_usd: float) -> None:
        with self._lock:
            self._costs[model] += cost_usd

    def record_error(self, error_type: str) -> None:
        with self._lock:
            self._errors[error_type] += 1

    def record_tokens(self, direction: str, count: int) -> None:
        with self._lock:
            self._tokens[direction] += count

    def _prune(self, entries: list[tuple[float, float]]) -> list[tuple[float, float]]:
        cutoff = time.time() - self._window
        return [(ts, val) for ts, val in entries if ts > cutoff]

    def summary(self) -> dict:
        with self._lock:
            result: dict = {}

            for op, entries in self._latencies.items():
                pruned = self._prune(entries)
                self._latencies[op] = pruned
                if not pruned:
                    continue
                values = sorted(v for _, v in pruned)
                n = len(values)
                result[op] = {
                    "count": n,
                    "p50": values[n // 2] if n else 0,
                    "p95": values[int(n * 0.95)] if n else 0,
                    "p99": values[int(n * 0.99)] if n else 0,
                    "mean": sum(values) / n if n else 0,
                }

            result["cost_by_model"] = dict(self._costs)
            result["total_cost"] = sum(self._costs.values())
            result["errors"] = dict(self._errors)
            result["total_errors"] = sum(self._errors.values())
            result["tokens"] = dict(self._tokens)
            result["request_count"] = self._request_count

            return result


# Global singleton
metrics = MetricsCollector()
