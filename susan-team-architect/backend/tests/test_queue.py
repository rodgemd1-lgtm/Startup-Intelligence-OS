"""Tests for PriorityQueue with admission control, token quotas, and circuit breaker."""
import pytest
from susan_core.queue import (
    PriorityQueue,
    WorkItem,
    Priority,
    CircuitBreaker,
    CircuitBreakerRegistry,
)


def test_priority_ordering():
    q = PriorityQueue()
    q.enqueue(WorkItem(id="low", priority=Priority.BATCH_RESEARCH, payload={}))
    q.enqueue(WorkItem(id="high", priority=Priority.REALTIME, payload={}))
    q.enqueue(WorkItem(id="mid", priority=Priority.INTERACTIVE, payload={}))
    items = []
    while not q.empty():
        items.append(q.dequeue())
    assert [i.id for i in items] == ["high", "mid", "low"]


def test_concurrency_limit():
    q = PriorityQueue(max_concurrent=2)
    q.enqueue(WorkItem(id="a", priority=Priority.REALTIME, payload={}))
    q.enqueue(WorkItem(id="b", priority=Priority.REALTIME, payload={}))
    q.enqueue(WorkItem(id="c", priority=Priority.REALTIME, payload={}))
    a = q.dequeue()
    b = q.dequeue()
    assert q.dequeue() is None  # blocked by concurrency limit
    q.complete(a.id)
    c = q.dequeue()
    assert c.id == "c"


def test_token_quota_rejection():
    q = PriorityQueue(token_quota_per_minute=1000)
    q.record_tokens(900)
    item = WorkItem(id="x", priority=Priority.REALTIME, payload={}, estimated_tokens=200)
    q.enqueue(item)
    assert q.dequeue() is None  # over quota


def test_circuit_breaker():
    q = PriorityQueue()
    for i in range(5):
        q.record_failure()
    item = WorkItem(id="x", priority=Priority.REALTIME, payload={})
    q.enqueue(item)
    assert q.dequeue() is None  # circuit open after 5 failures


def test_queue_telemetry():
    q = PriorityQueue()
    q.enqueue(WorkItem(id="a", priority=Priority.REALTIME, payload={}))
    q.enqueue(WorkItem(id="b", priority=Priority.BATCH_RESEARCH, payload={}))
    stats = q.telemetry()
    assert stats["depth"] == 2
    assert stats["depth_by_priority"]["realtime"] == 1
    assert stats["circuit_state"] == "closed"


# ---- CircuitBreaker unit tests ----


def test_circuit_breaker_starts_closed():
    cb = CircuitBreaker(threshold=3, reset_seconds=60.0)
    assert cb.state() == "closed"
    assert not cb.is_open()


def test_circuit_breaker_opens_after_threshold():
    cb = CircuitBreaker(threshold=3, reset_seconds=60.0)
    for _ in range(3):
        cb.record_failure()
    assert cb.is_open()
    assert cb.state() == "open"


def test_circuit_breaker_success_decrements():
    cb = CircuitBreaker(threshold=3, reset_seconds=60.0)
    cb.record_failure()
    cb.record_failure()
    assert cb.state() == "closed"
    cb.record_success()
    assert cb._failure_count == 1


def test_circuit_breaker_half_open_after_reset(monkeypatch):
    cb = CircuitBreaker(threshold=2, reset_seconds=1.0)
    cb.record_failure()
    cb.record_failure()
    assert cb.state() == "open"
    # Simulate time passing beyond reset window
    cb._last_failure -= 2.0
    assert cb.state() == "half-open"


# ---- CircuitBreakerRegistry tests ----


def test_registry_creates_breakers_on_demand():
    reg = CircuitBreakerRegistry(threshold=3, reset_seconds=30.0)
    cb = reg.get("opus")
    assert isinstance(cb, CircuitBreaker)
    assert reg.get("opus") is cb  # same object


def test_registry_isolates_models():
    reg = CircuitBreakerRegistry(threshold=2, reset_seconds=60.0)
    reg.get("opus").record_failure()
    reg.get("opus").record_failure()
    assert reg.get("opus").is_open()
    assert not reg.get("sonnet").is_open()


def test_registry_all_states():
    reg = CircuitBreakerRegistry(threshold=2, reset_seconds=60.0)
    reg.get("opus").record_failure()
    reg.get("opus").record_failure()
    reg.get("sonnet")  # just touch it
    states = reg.all_states()
    assert states["opus"] == "open"
    assert states["sonnet"] == "closed"


# ---- Per-model circuit breaker in PriorityQueue ----


def test_per_model_circuit_breaker():
    """When a specific model's breaker opens, items for that model are blocked
    but items without a model (global) and items for other models still flow."""
    q = PriorityQueue(circuit_breaker_threshold=2)

    # Trip the opus breaker
    q.record_failure(model="opus")
    q.record_failure(model="opus")

    # Enqueue items for opus, sonnet, and no-model
    q.enqueue(WorkItem(id="opus-job", priority=Priority.REALTIME, model="opus"))
    q.enqueue(WorkItem(id="sonnet-job", priority=Priority.REALTIME, model="sonnet"))
    q.enqueue(WorkItem(id="global-job", priority=Priority.REALTIME))

    # sonnet and global should dequeue; opus should be skipped
    results = []
    for _ in range(3):
        item = q.dequeue()
        if item:
            results.append(item.id)
            q.complete(item.id)
    assert "sonnet-job" in results
    assert "global-job" in results
    assert "opus-job" not in results


def test_per_model_breaker_isolation():
    """Failures for model A do not affect model B."""
    q = PriorityQueue(circuit_breaker_threshold=3)

    # Record 3 failures for opus
    for _ in range(3):
        q.record_failure(model="opus")

    # Record 1 failure for sonnet (below threshold)
    q.record_failure(model="sonnet")

    q.enqueue(WorkItem(id="s1", priority=Priority.REALTIME, model="sonnet"))
    q.enqueue(WorkItem(id="o1", priority=Priority.REALTIME, model="opus"))

    s = q.dequeue()
    assert s is not None
    assert s.id == "s1"
    q.complete(s.id)

    # opus is still blocked
    o = q.dequeue()
    assert o is None  # opus breaker is open, only opus item remains


def test_per_model_telemetry():
    """Telemetry reports per-model circuit states."""
    q = PriorityQueue(circuit_breaker_threshold=2)
    q.record_failure(model="opus")
    q.record_failure(model="opus")
    q.record_failure(model="sonnet")

    stats = q.telemetry()
    assert "circuit_states" in stats
    assert stats["circuit_states"]["opus"] == "open"
    assert stats["circuit_states"]["sonnet"] == "closed"
    # Legacy global field should still be present
    assert "circuit_state" in stats


def test_record_success_resets_model_breaker():
    """record_success for a model decrements that model's failure count."""
    q = PriorityQueue(circuit_breaker_threshold=3)
    q.record_failure(model="opus")
    q.record_failure(model="opus")
    q.record_failure(model="opus")

    # Breaker is open
    q.enqueue(WorkItem(id="o1", priority=Priority.REALTIME, model="opus"))
    assert q.dequeue() is None

    # Record successes to close the breaker
    q.record_success(model="opus")
    q.record_success(model="opus")
    q.record_success(model="opus")

    item = q.dequeue()
    assert item is not None
    assert item.id == "o1"


def test_backward_compat_global_breaker():
    """Calling record_failure() with no model argument still works via the
    global '' breaker, preserving backward compatibility."""
    q = PriorityQueue(circuit_breaker_threshold=2)
    q.record_failure()  # no model -> global
    q.record_failure()

    # Item with no model should be blocked by global breaker
    q.enqueue(WorkItem(id="g1", priority=Priority.REALTIME))
    assert q.dequeue() is None

    # Item with a specific model should NOT be blocked by global breaker
    q.enqueue(WorkItem(id="m1", priority=Priority.REALTIME, model="sonnet"))
    item = q.dequeue()
    assert item is not None
    assert item.id == "m1"
