"""Test the v2 runtime that wraps phase_runtime with queue, routing, cache, and tracing."""
import pytest
from susan_core.runtime_v2 import RuntimeV2
from susan_core.parallel_orchestrator import PhaseDAG


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


# --- execute_phases tests ---


def test_execute_phases_sequential():
    """Phases with linear deps execute in order; all traces are recorded."""
    dag = PhaseDAG(deps={
        "a": [],
        "b": ["a"],
        "c": ["b"],
    })
    execution_order: list[str] = []

    def make_fn(name: str):
        def fn():
            execution_order.append(name)
            return f"{name}_result"
        return fn

    rt = RuntimeV2(dag=dag)
    results = rt.execute_phases({
        "a": make_fn("a"),
        "b": make_fn("b"),
        "c": make_fn("c"),
    })

    assert results == {"a": "a_result", "b": "b_result", "c": "c_result"}
    # Because each phase depends on the previous, they must run in order
    assert execution_order == ["a", "b", "c"]
    traces = rt.tracer.get_traces()
    traced_names = {t.phase for t in traces}
    assert traced_names == {"a", "b", "c"}


def test_execute_phases_parallel():
    """Two phases with no deps can run in parallel; both complete with traces."""
    dag = PhaseDAG(deps={
        "x": [],
        "y": [],
    })
    rt = RuntimeV2(dag=dag)
    results = rt.execute_phases({
        "x": lambda: "x_done",
        "y": lambda: "y_done",
    })

    assert results == {"x": "x_done", "y": "y_done"}
    traces = rt.tracer.get_traces()
    traced_names = {t.phase for t in traces}
    assert traced_names == {"x", "y"}


def test_execute_phases_partial():
    """Only phases present in phase_fns are executed; DAG extras are skipped."""
    dag = PhaseDAG(deps={
        "p1": [],
        "p2": ["p1"],
        "p3": ["p1"],
        "p4": ["p2", "p3"],
    })
    rt = RuntimeV2(dag=dag)
    results = rt.execute_phases({
        "p1": lambda: 1,
        "p3": lambda: 3,
    })

    assert "p1" in results
    assert "p3" in results
    assert "p2" not in results
    assert "p4" not in results
    traces = rt.tracer.get_traces()
    traced_names = {t.phase for t in traces}
    assert traced_names == {"p1", "p3"}


def test_execute_phases_exception_handling():
    """A phase that raises does not block others; result contains the exception."""
    dag = PhaseDAG(deps={
        "ok1": [],
        "fail": [],
        "ok2": [],
    })
    rt = RuntimeV2(dag=dag)
    results = rt.execute_phases({
        "ok1": lambda: "fine",
        "fail": lambda: (_ for _ in ()).throw(ValueError("boom")),
        "ok2": lambda: "also_fine",
    })

    assert results["ok1"] == "fine"
    assert results["ok2"] == "also_fine"
    assert isinstance(results["fail"], ValueError)
    assert str(results["fail"]) == "boom"
    # All three should still have traces
    traces = rt.tracer.get_traces()
    traced_names = {t.phase for t in traces}
    assert traced_names == {"ok1", "fail", "ok2"}
