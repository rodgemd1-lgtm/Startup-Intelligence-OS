"""Replayability tests -- decision traces can be reproduced."""
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
