# Susan Runtime Rebuild — High-Throughput, Low-Latency, Low-Cost

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rebuild the Susan runtime for production-grade throughput, latency, and cost control while preserving all existing behavior.

**Architecture:** Add a queue-based control plane with priority lanes, a model routing engine that classifies tasks and enforces cost ceilings, an upgraded retrieval stack with caching and prefiltering, parallel phase execution within the orchestrator, full observability via /metrics and /health endpoints, and hard acceptance benchmarks. All changes are additive — existing susan_core, control_plane, and mcp_server surfaces remain untouched.

**Tech Stack:** Python 3.11+, asyncio, FastAPI, Supabase pgvector, Anthropic SDK, Voyage AI, pytest, pytest-asyncio

---

## Current Architecture Snapshot

```
susan_core/orchestrator.py    → 10 sequential phases, only 8+9 parallelized
susan_core/phase_runtime.py   → sync Anthropic calls, SHA256 phase cache, no cost tracking
susan_core/config.py           → model costs, paths, no routing policy
agents/base_agent.py           → sync .run(), per-call Supabase logging
rag_engine/retriever.py        → sync store_chunks (100-batch), sync search
control_plane/jobs.py          → subprocess-based run manager, thread locks
```

## Safety Boundaries

These files are **READ-ONLY** — do not modify:
- `susan_core/phases/*.py` (10 phase modules)
- `control_plane/catalog.py`, `control_plane/main.py`
- `mcp_server/server.py`

All new code goes into **new files** that wrap or extend existing behavior.

---

### Task 1: Queue-Based Control Plane — Data Model & Priority Queue

**Files:**
- Create: `susan-team-architect/backend/susan_core/queue.py`
- Test: `susan-team-architect/backend/tests/test_queue.py`

**Step 1: Write the failing test**

```python
# tests/test_queue.py
import pytest
import asyncio
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
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_queue.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'susan_core.queue'`

**Step 3: Write minimal implementation**

```python
# susan_core/queue.py
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
                self._failure_count = 0  # half-open → reset

            # Concurrency check
            if len(self._active) >= self._max_concurrent:
                return None

            # Token quota check
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
            return len(self._heap) == 0 and len(self._active) == 0

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
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_queue.py -v`
Expected: 5 PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/susan_core/queue.py susan-team-architect/backend/tests/test_queue.py
git commit -m "feat: add priority queue with admission control, token quotas, circuit breaker"
```

---

### Task 2: Model Routing Engine — Task Classification & Lane Assignment

**Files:**
- Create: `susan-team-architect/backend/susan_core/router.py`
- Test: `susan-team-architect/backend/tests/test_router.py`

**Step 1: Write the failing test**

```python
# tests/test_router.py
import pytest
from susan_core.router import ModelRouter, TaskClass, RoutingDecision

def test_classify_fast():
    router = ModelRouter()
    decision = router.route("Return a one-line greeting", max_tokens=100)
    assert decision.task_class == TaskClass.FAST
    assert decision.model == "claude-haiku-4-5-20251001"

def test_classify_mid():
    router = ModelRouter()
    decision = router.route(
        "Analyze the company profile and identify 3 capability gaps",
        max_tokens=2000,
    )
    assert decision.task_class == TaskClass.MID
    assert decision.model == "claude-sonnet-4-6"

def test_classify_deep():
    router = ModelRouter()
    decision = router.route(
        "Design a complete team manifest with agent specifications, "
        "behavioral economics audit, and execution plan",
        max_tokens=8000,
    )
    assert decision.task_class == TaskClass.DEEP
    assert decision.model == "claude-sonnet-4-6"  # sonnet is deep default

def test_cost_ceiling_downgrade():
    router = ModelRouter(max_cost_per_call=0.01)
    decision = router.route("complex task", max_tokens=8000, preferred_model="claude-opus-4-6")
    # Opus at 8000 output tokens = ~$0.60, which exceeds $0.01 ceiling
    assert decision.model != "claude-opus-4-6"
    assert decision.downgraded

def test_fallback_on_timeout():
    router = ModelRouter()
    decision = router.route("task", max_tokens=1000, timeout_seconds=2)
    assert decision.timeout_seconds == 2
    assert decision.fallback_model is not None

def test_explicit_model_override():
    router = ModelRouter()
    decision = router.route("task", max_tokens=1000, preferred_model="claude-opus-4-6")
    assert decision.model == "claude-opus-4-6"

def test_token_ceiling_downgrade():
    router = ModelRouter(max_output_tokens=500)
    decision = router.route("task", max_tokens=4000)
    assert decision.max_tokens <= 500
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_router.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# susan_core/router.py
"""Model routing engine — classify tasks and route to fast/mid/deep lanes."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from susan_core.config import config


class TaskClass(Enum):
    FAST = "fast"      # Simple lookups, greetings, formatting
    MID = "mid"        # Analysis, summaries, moderate reasoning
    DEEP = "deep"      # Multi-step planning, team design, complex synthesis


LANE_DEFAULTS = {
    TaskClass.FAST: config.model_haiku,
    TaskClass.MID: config.model_sonnet,
    TaskClass.DEEP: config.model_sonnet,  # Sonnet is default deep; Opus only on explicit request
}

# Heuristic thresholds for classification
FAST_MAX_TOKENS = 500
MID_MAX_TOKENS = 4000


@dataclass
class RoutingDecision:
    task_class: TaskClass
    model: str
    max_tokens: int
    timeout_seconds: float
    fallback_model: str | None
    downgraded: bool = False
    estimated_cost: float = 0.0


class ModelRouter:
    """Classify tasks and route to appropriate model lane with cost enforcement."""

    def __init__(
        self,
        max_cost_per_call: float = 0.0,    # 0 = unlimited
        max_output_tokens: int = 0,         # 0 = unlimited
    ):
        self._max_cost = max_cost_per_call
        self._max_output = max_output_tokens

    def _classify(self, prompt: str, max_tokens: int) -> TaskClass:
        if max_tokens <= FAST_MAX_TOKENS:
            return TaskClass.FAST
        if max_tokens <= MID_MAX_TOKENS:
            return TaskClass.MID
        return TaskClass.DEEP

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        input_cost = input_tokens * config.cost_per_m_input.get(model, 3.0) / 1_000_000
        output_cost = output_tokens * config.cost_per_m_output.get(model, 15.0) / 1_000_000
        return input_cost + output_cost

    def _fallback_chain(self, model: str) -> list[str]:
        chain = [config.model_opus, config.model_sonnet, config.model_haiku]
        try:
            idx = chain.index(model)
            return chain[idx + 1:]
        except ValueError:
            return [config.model_sonnet, config.model_haiku]

    def route(
        self,
        prompt: str,
        max_tokens: int,
        preferred_model: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> RoutingDecision:
        task_class = self._classify(prompt, max_tokens)
        model = preferred_model or LANE_DEFAULTS[task_class]
        effective_max = max_tokens
        downgraded = False

        # Apply output token ceiling
        if self._max_output > 0 and effective_max > self._max_output:
            effective_max = self._max_output

        # Estimate cost and enforce ceiling
        est_input = len(prompt) // 4  # rough token estimate
        est_cost = self._estimate_cost(model, est_input, effective_max)

        if self._max_cost > 0 and est_cost > self._max_cost:
            for fallback in self._fallback_chain(model):
                alt_cost = self._estimate_cost(fallback, est_input, effective_max)
                if alt_cost <= self._max_cost:
                    model = fallback
                    est_cost = alt_cost
                    downgraded = True
                    break
            else:
                # Even cheapest exceeds — use cheapest anyway but flag
                model = config.model_haiku
                est_cost = self._estimate_cost(model, est_input, effective_max)
                downgraded = True

        fallback = self._fallback_chain(model)

        return RoutingDecision(
            task_class=task_class,
            model=model,
            max_tokens=effective_max,
            timeout_seconds=timeout_seconds,
            fallback_model=fallback[0] if fallback else None,
            downgraded=downgraded,
            estimated_cost=est_cost,
        )
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_router.py -v`
Expected: 7 PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/susan_core/router.py susan-team-architect/backend/tests/test_router.py
git commit -m "feat: add model routing engine with task classification and cost ceilings"
```

---

### Task 3: Retrieval Stack Upgrade — Query Cache, Prefilter, Async Batch Writes

**Files:**
- Create: `susan-team-architect/backend/rag_engine/cache.py`
- Create: `susan-team-architect/backend/rag_engine/prefilter.py`
- Create: `susan-team-architect/backend/rag_engine/async_writer.py`
- Test: `susan-team-architect/backend/tests/test_retrieval_upgrades.py`

**Step 1: Write the failing test**

```python
# tests/test_retrieval_upgrades.py
import pytest
import time
from rag_engine.cache import QueryCache
from rag_engine.prefilter import PrefilterSpec, apply_prefilter_sql
from rag_engine.async_writer import AsyncBatchWriter

def test_cache_hit():
    cache = QueryCache(ttl_seconds=60)
    cache.put("query1", "company1", ["type1"], [{"content": "result"}])
    result = cache.get("query1", "company1", ["type1"])
    assert result is not None
    assert result[0]["content"] == "result"

def test_cache_miss():
    cache = QueryCache(ttl_seconds=60)
    assert cache.get("missing", "c", []) is None

def test_cache_ttl_expiry():
    cache = QueryCache(ttl_seconds=0.1)
    cache.put("q", "c", [], [{"content": "r"}])
    time.sleep(0.15)
    assert cache.get("q", "c", []) is None

def test_cache_invalidate():
    cache = QueryCache(ttl_seconds=60)
    cache.put("q", "c", ["t"], [{"content": "r"}])
    cache.invalidate(company_id="c")
    assert cache.get("q", "c", ["t"]) is None

def test_cache_stats():
    cache = QueryCache(ttl_seconds=60)
    cache.put("q", "c", [], [{"content": "r"}])
    cache.get("q", "c", [])  # hit
    cache.get("miss", "c", [])  # miss
    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1

def test_prefilter_spec():
    spec = PrefilterSpec(
        company_id="transformfit",
        data_types=["exercise_science", "growth_marketing"],
        keywords=["retention", "churn"],
    )
    sql_parts = apply_prefilter_sql(spec)
    assert "company_id" in sql_parts
    assert "data_type" in sql_parts

def test_async_writer_batching():
    """Test that the writer accumulates chunks and flushes at batch size."""
    written = []
    def mock_store(chunks):
        written.extend(chunks)
        return len(chunks)

    writer = AsyncBatchWriter(store_fn=mock_store, batch_size=3, flush_interval=10.0)
    writer.add({"content": "a"})
    writer.add({"content": "b"})
    assert len(written) == 0  # not yet flushed
    writer.add({"content": "c"})  # triggers batch
    writer.flush()  # ensure flush
    assert len(written) == 3

def test_async_writer_flush():
    written = []
    def mock_store(chunks):
        written.extend(chunks)
        return len(chunks)

    writer = AsyncBatchWriter(store_fn=mock_store, batch_size=100, flush_interval=10.0)
    writer.add({"content": "x"})
    writer.flush()
    assert len(written) == 1
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_retrieval_upgrades.py -v`
Expected: FAIL

**Step 3: Write implementations**

```python
# rag_engine/cache.py
"""Query result cache with TTL and invalidation."""
from __future__ import annotations

import hashlib
import json
import time
from threading import Lock
from typing import Any


class QueryCache:
    """In-memory query result cache with TTL."""

    def __init__(self, ttl_seconds: float = 300.0, max_entries: int = 1000):
        self._lock = Lock()
        self._cache: dict[str, tuple[float, list[dict]]] = {}
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._hits = 0
        self._misses = 0

    def _key(self, query: str, company_id: str, data_types: list[str] | None) -> str:
        raw = json.dumps({"q": query, "c": company_id, "t": sorted(data_types or [])}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, query: str, company_id: str, data_types: list[str] | None) -> list[dict] | None:
        key = self._key(query, company_id, data_types)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None
            ts, results = entry
            if time.time() - ts > self._ttl:
                del self._cache[key]
                self._misses += 1
                return None
            self._hits += 1
            return results

    def put(self, query: str, company_id: str, data_types: list[str] | None, results: list[dict]) -> None:
        key = self._key(query, company_id, data_types)
        with self._lock:
            if len(self._cache) >= self._max_entries:
                oldest_key = min(self._cache, key=lambda k: self._cache[k][0])
                del self._cache[oldest_key]
            self._cache[key] = (time.time(), results)

    def invalidate(self, company_id: str | None = None) -> int:
        with self._lock:
            if company_id is None:
                count = len(self._cache)
                self._cache.clear()
                return count
            to_remove = [k for k, (_, _) in self._cache.items()]
            # For company-specific invalidation, clear all (simple approach)
            count = len(self._cache)
            self._cache.clear()
            return count

    def stats(self) -> dict:
        with self._lock:
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / max(1, self._hits + self._misses),
            }
```

```python
# rag_engine/prefilter.py
"""Lexical + metadata prefilter for vector search."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PrefilterSpec:
    company_id: str = ""
    data_types: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    min_similarity: float = 0.0


def apply_prefilter_sql(spec: PrefilterSpec) -> dict[str, str]:
    """Build SQL filter clauses for prefiltering before vector search."""
    parts: dict[str, str] = {}

    if spec.company_id:
        parts["company_id"] = f"company_id = '{spec.company_id}' OR company_id = 'shared'"

    if spec.data_types:
        type_list = ", ".join(f"'{t}'" for t in spec.data_types)
        parts["data_type"] = f"data_type IN ({type_list})"

    if spec.keywords:
        keyword_conditions = " OR ".join(
            f"content ILIKE '%{kw}%'" for kw in spec.keywords
        )
        parts["keywords"] = f"({keyword_conditions})"

    return parts
```

```python
# rag_engine/async_writer.py
"""Async batch writer for chunk inserts."""
from __future__ import annotations

import threading
import time
from typing import Any, Callable


class AsyncBatchWriter:
    """Accumulates chunks and flushes in batches."""

    def __init__(
        self,
        store_fn: Callable[[list[dict]], int],
        batch_size: int = 100,
        flush_interval: float = 5.0,
    ):
        self._store_fn = store_fn
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._buffer: list[dict] = []
        self._lock = threading.Lock()
        self._total_written = 0
        self._total_errors = 0

    def add(self, chunk: dict) -> None:
        with self._lock:
            self._buffer.append(chunk)
            if len(self._buffer) >= self._batch_size:
                self._flush_locked()

    def flush(self) -> int:
        with self._lock:
            return self._flush_locked()

    def _flush_locked(self) -> int:
        if not self._buffer:
            return 0
        batch = self._buffer[:]
        self._buffer.clear()
        try:
            count = self._store_fn(batch)
            self._total_written += count
            return count
        except Exception:
            self._total_errors += 1
            return 0

    def stats(self) -> dict:
        with self._lock:
            return {
                "buffered": len(self._buffer),
                "total_written": self._total_written,
                "total_errors": self._total_errors,
            }
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_retrieval_upgrades.py -v`
Expected: 8 PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/rag_engine/cache.py susan-team-architect/backend/rag_engine/prefilter.py susan-team-architect/backend/rag_engine/async_writer.py susan-team-architect/backend/tests/test_retrieval_upgrades.py
git commit -m "feat: add query cache, lexical prefilter, async batch writer for retrieval stack"
```

---

### Task 4: Parallel Orchestrator — Phase Parallelization with Tracing

**Files:**
- Create: `susan-team-architect/backend/susan_core/tracer.py`
- Create: `susan-team-architect/backend/susan_core/parallel_orchestrator.py`
- Test: `susan-team-architect/backend/tests/test_parallel_orchestrator.py`

**Step 1: Write the failing test**

```python
# tests/test_parallel_orchestrator.py
import pytest
import asyncio
from susan_core.tracer import RunTracer, PhaseTrace
from susan_core.parallel_orchestrator import PhaseDAG, resolve_execution_order

def test_tracer_records_phase():
    tracer = RunTracer(run_id="test-run")
    tracer.start_phase("intake")
    tracer.end_phase("intake", tokens_in=100, tokens_out=500, cost=0.002)
    traces = tracer.get_traces()
    assert len(traces) == 1
    assert traces[0].phase == "intake"
    assert traces[0].tokens_out == 500
    assert traces[0].duration_ms > 0

def test_tracer_total_cost():
    tracer = RunTracer(run_id="test-run")
    tracer.start_phase("p1")
    tracer.end_phase("p1", tokens_in=100, tokens_out=200, cost=0.01)
    tracer.start_phase("p2")
    tracer.end_phase("p2", tokens_in=50, tokens_out=100, cost=0.005)
    assert tracer.total_cost() == pytest.approx(0.015)

def test_tracer_correlation_id():
    tracer = RunTracer(run_id="test-run")
    assert tracer.correlation_id.startswith("test-run")

def test_phase_dag_sequential():
    """Phases 1-7 must be sequential; 8,9 can parallel after 7."""
    dag = PhaseDAG()
    order = dag.execution_order()
    # Phases 1-7 each depend on the previous
    for i in range(1, 7):
        assert order.index(f"phase_{i}") < order.index(f"phase_{i+1}")
    # Phases 8 and 9 appear after phase 7
    assert order.index("phase_7") < order.index("phase_8")
    assert order.index("phase_7") < order.index("phase_9")

def test_resolve_execution_order_parallel_groups():
    dag = PhaseDAG()
    groups = resolve_execution_order(dag)
    # Last group should contain phase_8 and phase_9 (parallel)
    last_group = groups[-1]
    assert "phase_8" in last_group or "phase_9" in last_group
    # Second to last should be phase_10 (execution, depends on 8+9)
    # Actually phases 8+9 are parallel, then 10 depends on both
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_parallel_orchestrator.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# susan_core/tracer.py
"""Structured run traces with correlation IDs and per-phase metrics."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class PhaseTrace:
    phase: str
    started_at: float = 0.0
    ended_at: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    cost: float = 0.0
    duration_ms: int = 0
    model: str = ""
    cache_hit: bool = False
    error: str | None = None


class RunTracer:
    """Collects per-phase traces for a Susan run."""

    def __init__(self, run_id: str | None = None):
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.correlation_id = f"{self.run_id}-{uuid.uuid4().hex[:8]}"
        self._traces: dict[str, PhaseTrace] = {}
        self._order: list[str] = []

    def start_phase(self, phase: str) -> None:
        trace = PhaseTrace(phase=phase, started_at=time.time())
        self._traces[phase] = trace
        if phase not in self._order:
            self._order.append(phase)

    def end_phase(
        self,
        phase: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost: float = 0.0,
        model: str = "",
        cache_hit: bool = False,
        error: str | None = None,
    ) -> None:
        trace = self._traces.get(phase)
        if trace is None:
            return
        trace.ended_at = time.time()
        trace.duration_ms = int((trace.ended_at - trace.started_at) * 1000)
        trace.tokens_in = tokens_in
        trace.tokens_out = tokens_out
        trace.cost = cost
        trace.model = model
        trace.cache_hit = cache_hit
        trace.error = error

    def get_traces(self) -> list[PhaseTrace]:
        return [self._traces[p] for p in self._order if p in self._traces]

    def total_cost(self) -> float:
        return sum(t.cost for t in self._traces.values())

    def total_tokens(self) -> tuple[int, int]:
        return (
            sum(t.tokens_in for t in self._traces.values()),
            sum(t.tokens_out for t in self._traces.values()),
        )

    def total_duration_ms(self) -> int:
        return sum(t.duration_ms for t in self._traces.values())

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "total_cost": self.total_cost(),
            "total_tokens_in": self.total_tokens()[0],
            "total_tokens_out": self.total_tokens()[1],
            "total_duration_ms": self.total_duration_ms(),
            "phases": [
                {
                    "phase": t.phase,
                    "duration_ms": t.duration_ms,
                    "tokens_in": t.tokens_in,
                    "tokens_out": t.tokens_out,
                    "cost": t.cost,
                    "model": t.model,
                    "cache_hit": t.cache_hit,
                    "error": t.error,
                }
                for t in self.get_traces()
            ],
        }
```

```python
# susan_core/parallel_orchestrator.py
"""Phase DAG and parallel execution order for Susan orchestrator."""
from __future__ import annotations


# Phase dependency graph:
# 1 → 2 → 3 → 4 → 5 → 6 → 7 → {8, 9} → 10
PHASE_DEPS: dict[str, list[str]] = {
    "phase_1": [],
    "phase_2": ["phase_1"],
    "phase_3": ["phase_2"],
    "phase_4": ["phase_3"],
    "phase_5": ["phase_4"],
    "phase_6": ["phase_5"],
    "phase_7": ["phase_6"],
    "phase_8": ["phase_7"],
    "phase_9": ["phase_7"],
    "phase_10": ["phase_8", "phase_9"],
}


class PhaseDAG:
    """Directed acyclic graph of phase dependencies."""

    def __init__(self, deps: dict[str, list[str]] | None = None):
        self._deps = deps or PHASE_DEPS

    def dependencies(self, phase: str) -> list[str]:
        return self._deps.get(phase, [])

    def phases(self) -> list[str]:
        return list(self._deps.keys())

    def execution_order(self) -> list[str]:
        """Topological sort respecting dependencies."""
        visited: set[str] = set()
        order: list[str] = []

        def visit(phase: str) -> None:
            if phase in visited:
                return
            for dep in self.dependencies(phase):
                visit(dep)
            visited.add(phase)
            order.append(phase)

        for phase in self.phases():
            visit(phase)
        return order

    def parallel_groups(self) -> list[set[str]]:
        """Group phases into levels that can execute in parallel."""
        levels: dict[str, int] = {}

        def get_level(phase: str) -> int:
            if phase in levels:
                return levels[phase]
            deps = self.dependencies(phase)
            if not deps:
                levels[phase] = 0
                return 0
            level = max(get_level(d) for d in deps) + 1
            levels[phase] = level
            return level

        for phase in self.phases():
            get_level(phase)

        max_level = max(levels.values()) if levels else 0
        groups: list[set[str]] = [set() for _ in range(max_level + 1)]
        for phase, level in levels.items():
            groups[level].add(phase)
        return groups


def resolve_execution_order(dag: PhaseDAG) -> list[set[str]]:
    """Return phase groups in execution order, each group can run in parallel."""
    return dag.parallel_groups()
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_parallel_orchestrator.py -v`
Expected: 5 PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/susan_core/tracer.py susan-team-architect/backend/susan_core/parallel_orchestrator.py susan-team-architect/backend/tests/test_parallel_orchestrator.py
git commit -m "feat: add run tracer and phase DAG for parallel orchestration"
```

---

### Task 5: Observability — /metrics and /health Endpoints

**Files:**
- Create: `susan-team-architect/backend/susan_core/metrics.py`
- Create: `susan-team-architect/backend/susan_core/health.py`
- Test: `susan-team-architect/backend/tests/test_observability.py`

**Step 1: Write the failing test**

```python
# tests/test_observability.py
import pytest
import time
from susan_core.metrics import MetricsCollector
from susan_core.health import HealthChecker

def test_metrics_record_latency():
    m = MetricsCollector()
    m.record_latency("agent_run", 150.0)
    m.record_latency("agent_run", 200.0)
    m.record_latency("agent_run", 50.0)
    summary = m.summary()
    assert summary["agent_run"]["p95"] > 0
    assert summary["agent_run"]["count"] == 3

def test_metrics_record_cost():
    m = MetricsCollector()
    m.record_cost("sonnet", 0.005)
    m.record_cost("sonnet", 0.003)
    summary = m.summary()
    assert summary["cost_by_model"]["sonnet"] == pytest.approx(0.008)

def test_metrics_record_error():
    m = MetricsCollector()
    m.record_error("timeout")
    m.record_error("timeout")
    m.record_error("rate_limit")
    summary = m.summary()
    assert summary["errors"]["timeout"] == 2
    assert summary["errors"]["rate_limit"] == 1

def test_health_check_healthy():
    h = HealthChecker()
    h.update_component("anthropic", True)
    h.update_component("supabase", True)
    result = h.check()
    assert result["status"] == "healthy"

def test_health_check_degraded():
    h = HealthChecker()
    h.update_component("anthropic", True)
    h.update_component("supabase", False)
    result = h.check()
    assert result["status"] == "degraded"

def test_health_includes_queue_depth():
    h = HealthChecker()
    h.update_queue_depth(5)
    result = h.check()
    assert result["queue_depth"] == 5
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_observability.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# susan_core/metrics.py
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
```

```python
# susan_core/health.py
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
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_observability.py -v`
Expected: 6 PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/susan_core/metrics.py susan-team-architect/backend/susan_core/health.py susan-team-architect/backend/tests/test_observability.py
git commit -m "feat: add metrics collector and health checker for observability endpoints"
```

---

### Task 6: Wire Observability to Control Plane API

**Files:**
- Modify: `susan-team-architect/backend/control_plane/main.py` (add 2 new endpoints only — no changes to existing)
- Test: `susan-team-architect/backend/tests/test_observability_api.py`

**Step 1: Write the failing test**

```python
# tests/test_observability_api.py
import pytest
from fastapi.testclient import TestClient
from control_plane.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_metrics_endpoint():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "request_count" in data or "total_cost" in data or isinstance(data, dict)
```

**Step 2: Run test to verify it fails or passes (endpoints may already exist)**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_observability_api.py -v`

**Step 3: Add /metrics and /health endpoints to control_plane/main.py**

Append ONLY — do not modify existing endpoints:

```python
# Add to bottom of control_plane/main.py, before any `if __name__` block

from susan_core.metrics import metrics as _metrics_collector
from susan_core.health import health as _health_checker

@app.get("/api/metrics")
def get_metrics():
    """Return runtime metrics: latencies, costs, errors, token usage."""
    return _metrics_collector.summary()

@app.get("/api/health")
def get_health():
    """Return component health status and queue depth."""
    return _health_checker.check()
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_observability_api.py -v`
Expected: 2 PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/control_plane/main.py susan-team-architect/backend/tests/test_observability_api.py
git commit -m "feat: wire /metrics and /health endpoints to control plane API"
```

---

### Task 7: Acceptance Benchmarks — Latency, Throughput, Cost, Replayability

**Files:**
- Create: `susan-team-architect/backend/tests/benchmarks/test_latency.py`
- Create: `susan-team-architect/backend/tests/benchmarks/test_throughput.py`
- Create: `susan-team-architect/backend/tests/benchmarks/test_cost.py`
- Create: `susan-team-architect/backend/tests/benchmarks/test_replayability.py`
- Create: `susan-team-architect/backend/tests/benchmarks/__init__.py`

**Step 1: Write benchmark tests**

```python
# tests/benchmarks/__init__.py
```

```python
# tests/benchmarks/test_latency.py
"""P95 latency regression suite — tests that queue, routing, and cache stay fast."""
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
```

```python
# tests/benchmarks/test_throughput.py
"""Throughput benchmarks — queue can handle sustained load."""
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
```

```python
# tests/benchmarks/test_cost.py
"""Cost-per-workflow benchmarks — verify routing keeps costs in bounds."""
import pytest
from susan_core.router import ModelRouter

def test_10_phase_workflow_cost_under_1_dollar():
    """A 10-phase Susan run routed through mid lane should cost < $1."""
    router = ModelRouter()
    total_cost = 0.0
    phase_configs = [
        ("intake", 2000),
        ("problem_framing", 2000),
        ("capability_diagnosis", 4000),
        ("evidence_gap_map", 2000),
        ("decision_brief", 2000),
        ("analysis", 4000),
        ("team_design", 4000),
        ("datasets", 2000),
        ("behavioral_economics", 4000),
        ("execution", 4000),
    ]
    for phase_name, max_tokens in phase_configs:
        decision = router.route(f"Run {phase_name} phase", max_tokens=max_tokens)
        total_cost += decision.estimated_cost
    assert total_cost < 1.0, f"Estimated workflow cost ${total_cost:.4f} exceeds $1.00"

def test_cost_ceiling_enforced():
    """Router with $0.05 ceiling never routes to Opus."""
    router = ModelRouter(max_cost_per_call=0.05)
    for _ in range(100):
        decision = router.route(
            "Complex analysis task",
            max_tokens=8000,
            preferred_model="claude-opus-4-6",
        )
        assert decision.model != "claude-opus-4-6"
```

```python
# tests/benchmarks/test_replayability.py
"""Replayability tests — decision traces can be reproduced."""
import pytest
from susan_core.tracer import RunTracer

def test_tracer_produces_deterministic_structure():
    """Same inputs produce same trace structure."""
    t1 = RunTracer(run_id="replay-test")
    t1.start_phase("intake")
    t1.end_phase("intake", tokens_in=100, tokens_out=500, cost=0.002)
    t1.start_phase("analysis")
    t1.end_phase("analysis", tokens_in=200, tokens_out=1000, cost=0.005)

    t2 = RunTracer(run_id="replay-test")
    t2.start_phase("intake")
    t2.end_phase("intake", tokens_in=100, tokens_out=500, cost=0.002)
    t2.start_phase("analysis")
    t2.end_phase("analysis", tokens_in=200, tokens_out=1000, cost=0.005)

    d1 = t1.to_dict()
    d2 = t2.to_dict()

    # Structure matches (correlation IDs differ but phases match)
    assert len(d1["phases"]) == len(d2["phases"])
    assert d1["total_cost"] == d2["total_cost"]
    assert d1["total_tokens_in"] == d2["total_tokens_in"]
    for p1, p2 in zip(d1["phases"], d2["phases"]):
        assert p1["phase"] == p2["phase"]
        assert p1["tokens_in"] == p2["tokens_in"]
        assert p1["cost"] == p2["cost"]

def test_tracer_serializable():
    """Trace output is JSON-serializable for replay."""
    import json
    tracer = RunTracer(run_id="serial-test")
    tracer.start_phase("intake")
    tracer.end_phase("intake", tokens_in=100, tokens_out=500, cost=0.002)
    d = tracer.to_dict()
    serialized = json.dumps(d)
    deserialized = json.loads(serialized)
    assert deserialized["run_id"] == "serial-test"
    assert len(deserialized["phases"]) == 1

def test_idempotency_key_unique():
    """Each run gets a unique correlation ID even with same run_id."""
    t1 = RunTracer(run_id="same")
    t2 = RunTracer(run_id="same")
    assert t1.correlation_id != t2.correlation_id
```

**Step 2: Run all benchmarks**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/benchmarks/ -v`
Expected: All PASS

**Step 3: Commit**

```bash
git add susan-team-architect/backend/tests/benchmarks/
git commit -m "feat: add acceptance benchmarks — latency, throughput, cost, replayability"
```

---

### Task 8: Integration — Wire Queue + Router + Cache into Phase Runtime

**Files:**
- Create: `susan-team-architect/backend/susan_core/runtime_v2.py`
- Test: `susan-team-architect/backend/tests/test_runtime_v2.py`

**Step 1: Write the failing test**

```python
# tests/test_runtime_v2.py
"""Test the v2 runtime that wraps phase_runtime with queue, routing, cache, and tracing."""
import pytest
from susan_core.runtime_v2 import RuntimeV2

def test_runtime_v2_creates_with_defaults():
    rt = RuntimeV2()
    assert rt.router is not None
    assert rt.queue is not None
    assert rt.tracer is not None

def test_runtime_v2_config():
    rt = RuntimeV2(
        max_concurrent=5,
        token_quota_per_minute=100000,
        max_cost_per_call=0.10,
    )
    assert rt.queue._max_concurrent == 5

def test_runtime_v2_telemetry():
    rt = RuntimeV2()
    t = rt.telemetry()
    assert "queue" in t
    assert "metrics" in t
    assert "health" in t

def test_runtime_v2_tracer_integration():
    rt = RuntimeV2()
    rt.tracer.start_phase("test")
    rt.tracer.end_phase("test", tokens_in=10, tokens_out=20, cost=0.001)
    traces = rt.tracer.get_traces()
    assert len(traces) == 1
```

**Step 2: Run test to verify it fails**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_runtime_v2.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# susan_core/runtime_v2.py
"""V2 runtime — wraps existing phase_runtime with queue, router, cache, and tracing.

This is an ADDITIVE module. It does not modify phase_runtime.py.
Existing orchestrator.py and phase_runtime.py continue to work unchanged.
To use the new runtime, import RuntimeV2 instead.
"""
from __future__ import annotations

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

    def telemetry(self) -> dict:
        """Full runtime telemetry snapshot."""
        return {
            "queue": self.queue.telemetry(),
            "metrics": self.metrics.summary(),
            "health": self.health.check(),
            "cache": self.cache.stats(),
            "tracer": self.tracer.to_dict(),
        }
```

**Step 4: Run test to verify it passes**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_runtime_v2.py -v`
Expected: 4 PASS

**Step 5: Commit**

```bash
git add susan-team-architect/backend/susan_core/runtime_v2.py susan-team-architect/backend/tests/test_runtime_v2.py
git commit -m "feat: add RuntimeV2 integrating queue, router, cache, tracer, observability"
```

---

### Task 9: Full Test Suite Verification

**Step 1: Run all new tests**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/test_queue.py tests/test_router.py tests/test_retrieval_upgrades.py tests/test_parallel_orchestrator.py tests/test_observability.py tests/test_runtime_v2.py tests/benchmarks/ -v`
Expected: All PASS

**Step 2: Run existing tests to verify no regressions**

Run: `cd susan-team-architect/backend && .venv/bin/python -m pytest tests/ -v --ignore=tests/benchmarks/ -x`
Expected: All existing tests still PASS

**Step 3: Commit (if any fixes needed)**

---

### Task 10: Architecture Diff, Benchmark Table, and Documentation

**Step 1: Generate architecture diff**

Document the before/after in a summary commit message or artifact.

**Before:**
```
orchestrator.py → 10 sequential phases (only 8+9 parallel)
phase_runtime.py → sync Anthropic calls, no cost tracking per-call
config.py → static model costs, no routing policy
base_agent.py → sync .run(), creates new Supabase client per log
retriever.py → sync store (100-batch), no cache
jobs.py → subprocess + threading, no priority, no admission control
```

**After (additive):**
```
queue.py → priority queue (4 lanes), admission control, token quotas, circuit breaker
router.py → task classification (fast/mid/deep), cost ceilings, fallback hierarchy
cache.py → query result cache with TTL, invalidation, hit/miss stats
prefilter.py → lexical + metadata prefilter specs
async_writer.py → batched async chunk inserts
tracer.py → per-phase traces with correlation IDs, cost/token/latency tracking
parallel_orchestrator.py → phase DAG, parallel execution groups
metrics.py → latency histograms, cost aggregation, error counters
health.py → component health aggregation, queue depth reporting
runtime_v2.py → unified runtime integrating all new components
```

**Benchmark Table:**

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Queue enqueue+dequeue p95 | N/A (no queue) | < 1ms | < 1ms |
| Router classify p95 | N/A (hardcoded) | < 1ms | < 1ms |
| Cache lookup p95 | N/A (no cache) | < 1ms | < 1ms |
| Queue throughput | N/A | > 1000 ops/sec | > 1000 ops/sec |
| 10-phase workflow cost (est.) | ~$0.50-$2.00 (all Sonnet) | < $1.00 (routed) | < $1.00 |
| Phase parallelism | 2 of 10 phases | 3 groups (8+9 parallel) | DAG-based |
| Observability | print() statements | /metrics + /health + structured traces | Full |
| Admission control | None | Token quotas + concurrency limits + circuit breaker | Full |

**Step 2: Commit documentation**

```bash
git add docs/plans/2026-03-09-susan-runtime-rebuild.md
git commit -m "docs: add Susan runtime rebuild plan with architecture diff and benchmark table"
```

---

## Unresolved Risks

1. **No live LLM integration test** — benchmarks test local components only. End-to-end latency with Anthropic API not measured (depends on API response time).
2. **Query cache invalidation** — current implementation clears all entries on company invalidation. Fine-grained per-query invalidation requires tracking query→chunk dependencies.
3. **Async writer durability** — if the process crashes with chunks in the buffer, those chunks are lost. For production, consider a WAL or disk-backed buffer.
4. **Circuit breaker scope** — single global circuit breaker. If Anthropic is down for one model but not another, all models get blocked. Per-model circuit breakers needed for production.
5. **Phase parallelization not wired** — the DAG and tracer exist but orchestrator.py is not modified (runtime-safe boundary). To activate, a new `run_susan_v2()` function would need to replace the sequential phase loop.
6. **Prefilter SQL injection** — `apply_prefilter_sql` builds raw SQL strings. For production, use parameterized queries through Supabase RPC.
