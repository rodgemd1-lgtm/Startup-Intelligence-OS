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


@dataclass(order=True)
class WorkItem:
    priority: Priority = field(compare=True)
    id: str = field(compare=False)
    payload: dict[str, Any] = field(compare=False, default_factory=dict)
    estimated_tokens: int = field(compare=False, default=0)
    enqueued_at: float = field(compare=False, default_factory=time.time)


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

        # Circuit breaker
        self._cb_threshold = circuit_breaker_threshold
        self._cb_reset_seconds = circuit_breaker_reset_seconds
        self._failure_count: int = 0
        self._last_failure: float = 0.0

    def enqueue(self, item: WorkItem) -> None:
        with self._lock:
            heappush(self._heap, item)

    def dequeue(self) -> WorkItem | None:
        with self._lock:
            # Circuit breaker check
            if self._failure_count >= self._cb_threshold:
                if time.time() - self._last_failure < self._cb_reset_seconds:
                    return None
                self._failure_count = 0  # half-open -> reset

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

            # Peek at next item for token check
            if self._token_quota > 0:
                candidate = self._heap[0]
                if self._tokens_this_window + candidate.estimated_tokens > self._token_quota:
                    return None

            item = heappop(self._heap)
            self._active.add(item.id)
            return item

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

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure = time.time()

    def record_success(self) -> None:
        with self._lock:
            self._failure_count = max(0, self._failure_count - 1)

    def empty(self) -> bool:
        with self._lock:
            return len(self._heap) == 0

    def telemetry(self) -> dict:
        with self._lock:
            depth_by_priority: dict[str, int] = {}
            for item in self._heap:
                name = Priority(item.priority).name.lower()
                depth_by_priority[name] = depth_by_priority.get(name, 0) + 1

            circuit_state = "closed"
            if self._failure_count >= self._cb_threshold:
                if time.time() - self._last_failure < self._cb_reset_seconds:
                    circuit_state = "open"
                else:
                    circuit_state = "half-open"

            return {
                "depth": len(self._heap),
                "active": len(self._active),
                "depth_by_priority": depth_by_priority,
                "tokens_this_window": self._tokens_this_window,
                "circuit_state": circuit_state,
                "failure_count": self._failure_count,
            }
