"""Cost-per-workflow benchmarks -- verify routing keeps costs in bounds."""
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
