"""Tests for PriorityQueue with admission control, token quotas, and circuit breaker."""
import pytest
from susan_core.queue import PriorityQueue, WorkItem, Priority


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
