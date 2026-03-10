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
