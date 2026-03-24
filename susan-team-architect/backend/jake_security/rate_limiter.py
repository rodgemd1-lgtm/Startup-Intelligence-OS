"""Rate Limiter — prevent API abuse and runaway agent loops.

Token-bucket implementation using in-memory state + optional Supabase persistence.
Per-operation limits configurable. Supports burst capacity.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional


@dataclass
class RateWindow:
    """Sliding window rate limit state for a single key."""
    calls: list[float] = field(default_factory=list)  # timestamps
    lock: Lock = field(default_factory=Lock)

    def clean(self, window_seconds: float) -> None:
        now = time.time()
        self.calls = [t for t in self.calls if now - t < window_seconds]

    def count(self, window_seconds: float) -> int:
        self.clean(window_seconds)
        return len(self.calls)

    def record(self) -> None:
        self.calls.append(time.time())


# Default rate limits: (max_calls, window_seconds)
_DEFAULT_LIMITS: dict[str, tuple[int, float]] = {
    "anthropic_api": (60, 60.0),         # 60 calls/minute
    "voyage_embed": (100, 60.0),          # 100 embeddings/minute
    "supabase_write": (200, 60.0),        # 200 writes/minute
    "supabase_read": (500, 60.0),         # 500 reads/minute
    "osascript": (30, 60.0),             # 30 osascript calls/minute
    "telegram_send": (20, 60.0),         # 20 messages/minute
    "research_daemon": (5, 3600.0),      # 5 research runs/hour
    "employee_run": (10, 3600.0),        # 10 employee executions/hour
    "pipeline_run": (20, 3600.0),        # 20 pipeline runs/hour
    "self_improve": (3, 86400.0),        # 3 self-improvement runs/day
    "default": (100, 60.0),              # catch-all
}


class RateLimiter:
    """Sliding window rate limiter for named operations."""

    def __init__(self, limits: dict[str, tuple[int, float]] | None = None):
        self._limits = dict(_DEFAULT_LIMITS)
        if limits:
            self._limits.update(limits)
        self._windows: dict[str, RateWindow] = {}
        self._global_lock = Lock()

    def _window(self, key: str) -> RateWindow:
        with self._global_lock:
            if key not in self._windows:
                self._windows[key] = RateWindow()
            return self._windows[key]

    def _get_limit(self, operation: str) -> tuple[int, float]:
        return self._limits.get(operation, self._limits["default"])

    def check(self, operation: str, actor: str = "system") -> bool:
        """Return True if the operation is within rate limits."""
        key = f"{operation}:{actor}"
        max_calls, window_seconds = self._get_limit(operation)
        window = self._window(key)
        with window.lock:
            current = window.count(window_seconds)
            return current < max_calls

    def acquire(self, operation: str, actor: str = "system") -> bool:
        """Attempt to acquire a rate limit slot. Returns True on success."""
        key = f"{operation}:{actor}"
        max_calls, window_seconds = self._get_limit(operation)
        window = self._window(key)
        with window.lock:
            window.clean(window_seconds)
            if len(window.calls) < max_calls:
                window.record()
                return True
            return False

    def require(self, operation: str, actor: str = "system") -> None:
        """Acquire slot or raise RateLimitError."""
        if not self.acquire(operation, actor):
            max_calls, window_seconds = self._get_limit(operation)
            raise RateLimitError(
                f"Rate limit exceeded for '{operation}' (actor={actor}): "
                f"max {max_calls} calls per {window_seconds}s"
            )

    def status(self, operation: str, actor: str = "system") -> dict:
        """Return current rate limit status for an operation."""
        key = f"{operation}:{actor}"
        max_calls, window_seconds = self._get_limit(operation)
        window = self._window(key)
        with window.lock:
            current = window.count(window_seconds)
        return {
            "operation": operation,
            "actor": actor,
            "current": current,
            "max": max_calls,
            "window_seconds": window_seconds,
            "available": max_calls - current,
            "limited": current >= max_calls,
        }

    def all_status(self) -> list[dict]:
        """Return status for all tracked windows."""
        results = []
        for key, window in self._windows.items():
            parts = key.rsplit(":", 1)
            op = parts[0] if len(parts) == 2 else key
            actor = parts[1] if len(parts) == 2 else "system"
            results.append(self.status(op, actor))
        return results

    def persist(self, supabase_client) -> None:
        """Persist current rate limit state to jake_rate_limit_state table."""
        for status in self.all_status():
            max_calls, window_seconds = self._get_limit(status["operation"])
            supabase_client.table("jake_rate_limit_state").upsert({
                "operation": status["operation"],
                "actor": status["actor"],
                "call_count": status["current"],
                "window_seconds": window_seconds,
                "max_calls": max_calls,
                "updated_at": "now()",
            }, on_conflict="operation,actor").execute()


class RateLimitError(Exception):
    """Raised when a rate limit is exceeded."""
    pass


rate_limiter = RateLimiter()
