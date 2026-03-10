"""Throughput benchmarks -- queue can handle sustained load."""
import pytest
import time
from susan_core.queue import PriorityQueue, WorkItem, Priority


def test_queue_throughput_1000_items_per_second():
    """Queue must process 1000 enqueue+dequeue cycles per second."""
    q = PriorityQueue(max_concurrent=1000)
    start = time.perf_counter()
    for i in range(1000):
        item = WorkItem(id=f"item-{i}", priority=Priority.INTERACTIVE, payload={})
        q.enqueue(item)
        result = q.dequeue()
        if result:
            q.complete(result.id)
    elapsed = time.perf_counter() - start
    throughput = 1000 / elapsed
    assert throughput > 1000, f"Throughput {throughput:.0f} ops/sec below 1000"
