"""P95 latency regression suite -- tests that queue, routing, and cache stay fast."""
import pytest
import time
from susan_core.queue import PriorityQueue, WorkItem, Priority
from susan_core.router import ModelRouter
from rag_engine.cache import QueryCache


def test_queue_enqueue_dequeue_p95_under_1ms():
    """Queue operations must complete in under 1ms p95."""
    q = PriorityQueue()
    latencies = []
    for i in range(1000):
        item = WorkItem(id=f"item-{i}", priority=Priority.INTERACTIVE, payload={})
        start = time.perf_counter()
        q.enqueue(item)
        q.dequeue()
        q.complete(item.id)
        latencies.append((time.perf_counter() - start) * 1000)
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    assert p95 < 1.0, f"Queue p95 latency {p95:.3f}ms exceeds 1ms"


def test_router_classify_p95_under_1ms():
    """Model routing must classify in under 1ms p95."""
    router = ModelRouter()
    latencies = []
    for _ in range(1000):
        start = time.perf_counter()
        router.route("Analyze capability gaps", max_tokens=2000)
        latencies.append((time.perf_counter() - start) * 1000)
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    assert p95 < 1.0, f"Router p95 latency {p95:.3f}ms exceeds 1ms"


def test_cache_lookup_p95_under_1ms():
    """Cache hit must resolve in under 1ms p95."""
    cache = QueryCache(ttl_seconds=60)
    # Populate
    for i in range(100):
        cache.put(f"query-{i}", "company", ["type"], [{"content": f"result-{i}"}])
    latencies = []
    for i in range(1000):
        start = time.perf_counter()
        cache.get(f"query-{i % 100}", "company", ["type"])
        latencies.append((time.perf_counter() - start) * 1000)
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    assert p95 < 1.0, f"Cache p95 latency {p95:.3f}ms exceeds 1ms"
