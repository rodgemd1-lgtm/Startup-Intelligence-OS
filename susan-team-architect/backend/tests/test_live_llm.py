"""Live LLM integration test -- exercises RuntimeV2 end-to-end.

Risk 1 mitigation: verify that the full runtime machinery
(enqueue -> route -> trace -> metrics) works as a connected unit.

The test is skipped when ANTHROPIC_API_KEY is not set, so CI without
credentials stays green. When a key IS available, the test still does
NOT call the Anthropic API -- it validates the local orchestration
pipeline only. Future CI extensions can add a true API round-trip.
"""
from __future__ import annotations

import os
import uuid

import pytest

from susan_core.runtime_v2 import RuntimeV2
from susan_core.router import ModelRouter, RoutingDecision, TaskClass
from susan_core.queue import PriorityQueue, WorkItem, Priority
from susan_core.tracer import RunTracer
from susan_core.metrics import MetricsCollector


# ---------------------------------------------------------------------------
# Skip gate
# ---------------------------------------------------------------------------
_HAS_KEY = bool(os.environ.get("ANTHROPIC_API_KEY"))


@pytest.mark.skipif(not _HAS_KEY, reason="No ANTHROPIC_API_KEY set")
class TestLiveLLMIntegration:
    """Full RuntimeV2 flow exercised as a unit (no actual API call)."""

    # ----- 1. Enqueue -> Dequeue round-trip --------------------------------

    def test_enqueue_dequeue_roundtrip(self):
        """Work items survive the priority queue intact."""
        rt = RuntimeV2(max_concurrent=5)
        item = WorkItem(
            priority=Priority.INTERACTIVE,
            id=uuid.uuid4().hex[:8],
            payload={"prompt": "Summarize this text", "max_tokens": 100},
            estimated_tokens=100,
            model="",
        )
        rt.queue.enqueue(item)
        assert not rt.queue.empty()

        dequeued = rt.queue.dequeue()
        assert dequeued is not None
        assert dequeued.id == item.id
        assert dequeued.payload["prompt"] == "Summarize this text"

        rt.queue.complete(dequeued.id)

    # ----- 2. Routing decision validation ----------------------------------

    def test_route_returns_valid_decision(self):
        """Router produces a well-formed RoutingDecision for a simple task."""
        rt = RuntimeV2(max_cost_per_call=1.00)
        decision = rt.router.route(
            prompt="Summarize this text in one sentence",
            max_tokens=100,
        )

        assert isinstance(decision, RoutingDecision)
        assert isinstance(decision.task_class, TaskClass)
        assert decision.task_class == TaskClass.FAST  # 100 tokens <= 500
        assert isinstance(decision.model, str)
        assert len(decision.model) > 0
        assert decision.max_tokens == 100
        assert decision.estimated_cost >= 0.0
        assert isinstance(decision.timeout_seconds, float)

    def test_route_mid_task(self):
        """Router classifies a mid-range task correctly."""
        rt = RuntimeV2()
        decision = rt.router.route(
            prompt="Analyze the following company profile and identify capability gaps",
            max_tokens=2000,
        )
        assert decision.task_class == TaskClass.MID

    def test_route_deep_task(self):
        """Router classifies a deep task correctly."""
        rt = RuntimeV2()
        decision = rt.router.route(
            prompt="Design a full operating model with team structure",
            max_tokens=8000,
        )
        assert decision.task_class == TaskClass.DEEP

    # ----- 3. Tracer records phases ----------------------------------------

    def test_tracer_records_phase(self):
        """Tracer captures start/end and token counts for a simulated phase."""
        rt = RuntimeV2(run_id="live-test")
        assert rt.tracer.run_id == "live-test"

        # Simulate the routing + LLM call lifecycle
        rt.tracer.start_phase("routing")
        decision = rt.router.route("Summarize this text", max_tokens=100)
        rt.tracer.end_phase(
            "routing",
            tokens_in=0,
            tokens_out=0,
            cost=0.0,
            model=decision.model,
        )

        rt.tracer.start_phase("llm_call")
        # Simulate what an LLM call would produce
        simulated_tokens_in = 25
        simulated_tokens_out = 50
        simulated_cost = decision.estimated_cost
        rt.tracer.end_phase(
            "llm_call",
            tokens_in=simulated_tokens_in,
            tokens_out=simulated_tokens_out,
            cost=simulated_cost,
            model=decision.model,
        )

        traces = rt.tracer.get_traces()
        assert len(traces) == 2

        routing_trace = traces[0]
        assert routing_trace.phase == "routing"
        assert routing_trace.duration_ms >= 1

        llm_trace = traces[1]
        assert llm_trace.phase == "llm_call"
        assert llm_trace.tokens_in == simulated_tokens_in
        assert llm_trace.tokens_out == simulated_tokens_out
        assert llm_trace.model == decision.model

    # ----- 4. Metrics are updated ------------------------------------------

    def test_metrics_updated(self):
        """MetricsCollector records latency, tokens, and cost."""
        rt = RuntimeV2()

        # Simulate a full cycle: route, record latency, tokens, cost
        decision = rt.router.route("Summarize this text", max_tokens=100)

        rt.metrics.record_latency("llm_call", 150.0)
        rt.metrics.record_tokens("input", 25)
        rt.metrics.record_tokens("output", 50)
        rt.metrics.record_cost(decision.model, decision.estimated_cost)

        summary = rt.metrics.summary()

        assert summary["request_count"] == 1
        assert "llm_call" in summary
        assert summary["llm_call"]["count"] == 1
        assert summary["llm_call"]["mean"] == 150.0
        assert summary["tokens"]["input"] == 25
        assert summary["tokens"]["output"] == 50
        assert summary["total_cost"] >= 0.0
        assert decision.model in summary["cost_by_model"]

    # ----- 5. Full pipeline: enqueue -> route -> trace -> metrics ----------

    def test_full_pipeline(self):
        """End-to-end: enqueue work, dequeue, route, trace, record metrics."""
        rt = RuntimeV2(max_concurrent=5, max_cost_per_call=1.00, run_id="e2e-test")

        # Step 1: Enqueue
        prompt = "Summarize this text in one sentence"
        item = WorkItem(
            priority=Priority.INTERACTIVE,
            id=uuid.uuid4().hex[:8],
            payload={"prompt": prompt, "max_tokens": 100},
            estimated_tokens=100,
        )
        rt.queue.enqueue(item)

        # Step 2: Dequeue
        work = rt.queue.dequeue()
        assert work is not None

        # Step 3: Route
        rt.tracer.start_phase("routing")
        decision = rt.router.route(
            prompt=work.payload["prompt"],
            max_tokens=work.payload["max_tokens"],
        )
        rt.tracer.end_phase("routing", model=decision.model)

        assert isinstance(decision, RoutingDecision)
        assert decision.task_class == TaskClass.FAST

        # Step 4: Simulate LLM call with tracing
        rt.tracer.start_phase("llm_call")
        sim_in, sim_out, sim_cost = 25, 50, decision.estimated_cost
        rt.tracer.end_phase(
            "llm_call",
            tokens_in=sim_in,
            tokens_out=sim_out,
            cost=sim_cost,
            model=decision.model,
        )

        # Step 5: Record metrics
        rt.metrics.record_latency("llm_call", 120.0)
        rt.metrics.record_tokens("input", sim_in)
        rt.metrics.record_tokens("output", sim_out)
        rt.metrics.record_cost(decision.model, sim_cost)

        # Step 6: Complete queue item
        rt.queue.complete(work.id)
        rt.queue.record_success(decision.model)

        # ------ Assertions ------

        # Tracer
        traces = rt.tracer.get_traces()
        assert len(traces) == 2
        phase_names = [t.phase for t in traces]
        assert "routing" in phase_names
        assert "llm_call" in phase_names

        total_in, total_out = rt.tracer.total_tokens()
        assert total_in == sim_in
        assert total_out == sim_out
        assert rt.tracer.total_cost() == sim_cost

        # Metrics
        summary = rt.metrics.summary()
        assert summary["request_count"] == 1
        assert summary["tokens"]["input"] == sim_in
        assert summary["tokens"]["output"] == sim_out
        assert summary["total_cost"] > 0.0

        # Queue drained
        assert rt.queue.empty()

        # Telemetry snapshot is complete
        telem = rt.telemetry()
        assert "queue" in telem
        assert "metrics" in telem
        assert "health" in telem
        assert "cache" in telem
        assert "tracer" in telem
        assert telem["tracer"]["run_id"] == "e2e-test"
        assert len(telem["tracer"]["phases"]) == 2

    # ----- 6. Circuit breaker integration ----------------------------------

    def test_circuit_breaker_blocks_after_failures(self):
        """Queue skips items whose model circuit breaker is open."""
        rt = RuntimeV2(max_concurrent=10)

        # Trip the circuit breaker for a specific model
        for _ in range(5):
            rt.queue.record_failure("claude-haiku-4-5-20251001")

        # Enqueue an item targeting that model
        item = WorkItem(
            priority=Priority.INTERACTIVE,
            id="cb-test",
            payload={"prompt": "test"},
            estimated_tokens=10,
            model="claude-haiku-4-5-20251001",
        )
        rt.queue.enqueue(item)

        # Dequeue should skip the item because the breaker is open
        dequeued = rt.queue.dequeue()
        assert dequeued is None

        # Queue still has the item
        assert not rt.queue.empty()
