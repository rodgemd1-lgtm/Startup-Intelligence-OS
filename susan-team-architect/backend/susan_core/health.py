"""Health check aggregator for /health endpoint."""
from __future__ import annotations

import time
from threading import Lock


class HealthChecker:
    """Aggregates component health for /health endpoint."""

    def __init__(self):
        self._lock = Lock()
        self._components: dict[str, tuple[bool, float]] = {}
        self._queue_depth: int = 0

    def update_component(self, name: str, healthy: bool) -> None:
        with self._lock:
            self._components[name] = (healthy, time.time())

    def update_queue_depth(self, depth: int) -> None:
        with self._lock:
            self._queue_depth = depth

    def check(self) -> dict:
        with self._lock:
            components = {}
            all_healthy = True

            for name, (healthy, ts) in self._components.items():
                components[name] = {
                    "healthy": healthy,
                    "last_check": ts,
                }
                if not healthy:
                    all_healthy = False

            status = "healthy" if all_healthy else "degraded"
            if not self._components:
                status = "unknown"

            return {
                "status": status,
                "components": components,
                "queue_depth": self._queue_depth,
                "timestamp": time.time(),
            }


# Global singleton
health = HealthChecker()
