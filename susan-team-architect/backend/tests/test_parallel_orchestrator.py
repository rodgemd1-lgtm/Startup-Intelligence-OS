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
    # phases 8 and 9 share a dependency on phase_7, so they are parallel
    parallel_group = groups[-2]
    assert "phase_8" in parallel_group and "phase_9" in parallel_group
    # phase_10 depends on both 8 and 9, so it runs last
    final_group = groups[-1]
    assert "phase_10" in final_group
    # phases 1-7 are sequential, each in its own group
    for i in range(7):
        assert f"phase_{i+1}" in groups[i]
