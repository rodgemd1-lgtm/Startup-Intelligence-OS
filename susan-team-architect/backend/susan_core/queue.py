"""Priority queue with admission control, token quotas, and circuit breaker."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import IntEnum
from heapq import heappush, heappop
from threading import Lock
from typing import Any


class Priority(IntEnum):
    REALTIME = 0
    INTERACTIVE = 1
    BATCH_RESEARCH = 2
    OFFLINE_LEARNING = 3


class CircuitBreaker:
    """Per-model circuit breaker with closed/open/half-open states."""

    def __init__(self, threshold: int = 5, reset_seconds: float = 60.0):
        self._threshold = threshold
        self._reset_seconds = reset_seconds
        self._failure_count: int = 0
        self._last_failure: float = 0.0

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure = time.time()

    def record_success(self) -> None:
        self._failure_count = max(0, self._failure_count - 1)

    def is_open(self) -> bool:
        if self._failure_count >= self._threshold:
            if time.time() - self._last_failure < self._reset_seconds:
                return True
        return False

    def try_reset(self) -> None:
        """Reset failure count when transitioning from half-open to closed."""
        if self._failure_count >= self._threshold:
            if time.time() - self._last_failure >= self._reset_seconds:
                self._failure_count = 0

    def state(self) -> str:
        if self._failure_count >= self._threshold:
            if time.time() - self._last_failure < self._reset_seconds:
                return "open"
            return "half-open"
        return "closed"


class CircuitBreakerRegistry:
    """Maintains per-model circuit breakers, creating them on demand."""

    def __init__(self, threshold: int = 5, reset_seconds: float = 60.0):
        self._threshold = threshold
        self._reset_seconds = reset_seconds
        self._breakers: dict[str, CircuitBreaker] = {}

    def get(self, model: str = "") -> CircuitBreaker:
        if model not in self._breakers:
            self._breakers[model] = CircuitBreaker(
                threshold=self._threshold,
                reset_seconds=self._reset_seconds,
            )
        return self._breakers[model]

    def all_states(self) -> dict[str, str]:
        return {model: cb.state() for model, cb in self._breakers.items()}


@dataclass(order=True)
class WorkItem:
    priority: Priority = field(compare=True)
    id: str = field(compare=False)
    payload: dict[str, Any] = field(compare=False, default_factory=dict)
    estimated_tokens: int = field(compare=False, default=0)
    enqueued_at: float = field(compare=False, default_factory=time.time)
    model: str = field(compare=False, default="")


class PriorityQueue:
    """Thread-safe priority queue with admission control."""

    def __init__(
        self,
        max_concurrent: int = 10,
        token_quota_per_minute: int = 0,  # 0 = unlimited
        circuit_breaker_threshold: int = 5,
        circuit_breaker_reset_seconds: float = 60.0,
    ):
        self._lock = Lock()
        self._heap: list[WorkItem] = []
        self._max_concurrent = max_concurrent
        self._active: set[str] = set()

        # Token quota
        self._token_quota = token_quota_per_minute
        self._tokens_this_window: int = 0
        self._window_start: float = time.time()

        # Per-model circuit breaker registry
        self._cb_registry = CircuitBreakerRegistry(
            threshold=circuit_breaker_threshold,
            reset_seconds=circuit_breaker_reset_seconds,
        )

    def enqueue(self, item: WorkItem) -> None:
        with self._lock:
            heappush(self._heap, item)

    def dequeue(self) -> WorkItem | None:
        with self._lock:
            # Concurrency check
            if len(self._active) >= self._max_concurrent:
                return None

            # Token quota window reset
            if self._token_quota > 0:
                now = time.time()
                if now - self._window_start > 60:
                    self._tokens_this_window = 0
                    self._window_start = now

            if not self._heap:
                return None

            # Try to find a dequeue-able item, skipping those whose
            # model circuit breaker is open.
            skipped: list[WorkItem] = []
            result: WorkItem | None = None

            while self._heap:
                candidate = self._heap[0]

                # Token quota check (only against the top-priority item)
                if self._token_quota > 0:
                    if self._tokens_this_window + candidate.estimated_tokens > self._token_quota:
                        # Put skipped items back before returning
                        for s in skipped:
                            heappush(self._heap, s)
                        return None

                # Check circuit breaker for this item's model
                model_key = candidate.model  # "" for unset
                cb = self._cb_registry.get(model_key)

                if cb.is_open():
                    # This model's breaker is open -- skip this item
                    heappop(self._heap)
                    skipped.append(candidate)
                    continue

                # Half-open reset: if breaker was tripped but reset window
                # has elapsed, clear the failure count.
                cb.try_reset()

                # This item can be dispatched
                result = heappop(self._heap)
                break

            # Restore any skipped items back onto the heap
            for s in skipped:
                heappush(self._heap, s)

            if result is not None:
                self._active.add(result.id)

            return result

    def complete(self, item_id: str) -> None:
        with self._lock:
            self._active.discard(item_id)

    def record_tokens(self, count: int) -> None:
        with self._lock:
            now = time.time()
            if now - self._window_start > 60:
                self._tokens_this_window = 0
                self._window_start = now
            self._tokens_this_window += count

    def record_failure(self, model: str = "") -> None:
        with self._lock:
            self._cb_registry.get(model).record_failure()

    def record_success(self, model: str = "") -> None:
        with self._lock:
            self._cb_registry.get(model).record_success()

    def empty(self) -> bool:
        with self._lock:
            return len(self._heap) == 0

    def telemetry(self) -> dict:
        with self._lock:
            depth_by_priority: dict[str, int] = {}
            for item in self._heap:
                name = Priority(item.priority).name.lower()
                depth_by_priority[name] = depth_by_priority.get(name, 0) + 1

            # Per-model circuit states
            circuit_states = self._cb_registry.all_states()

            # Legacy global circuit_state field for backward compatibility.
            # Uses the global ("") breaker's state.
            global_cb = self._cb_registry.get("")
            circuit_state = global_cb.state()

            return {
                "depth": len(self._heap),
                "active": len(self._active),
                "depth_by_priority": depth_by_priority,
                "tokens_this_window": self._tokens_this_window,
                "circuit_state": circuit_state,
                "failure_count": global_cb._failure_count,
                "circuit_states": circuit_states,
            }
