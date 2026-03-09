"""Integration tests for the decision execution pipeline."""
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Override root for test isolation
_test_dir = tempfile.mkdtemp(prefix="decision-os-engine-test-")
os.environ["DECISION_OS_ROOT"] = _test_dir

# Create minimal structure
for d in ["decisions", "capabilities", "projects", "companies"]:
    os.makedirs(os.path.join(_test_dir, ".startup-os", d), exist_ok=True)

from decision_os.store import Store
from decision_os.decision_engine import DecisionEngine
from decision_os.models import DecisionStatus


def test_full_pipeline():
    store = Store()
    engine = DecisionEngine(store)

    result = engine.run(
        title="Test Pipeline Decision",
        context="Should we adopt a new testing framework?",
        company="test-co",
        project="test-project",
        assumptions=["Current tests are slow", "Team has capacity"],
        risks=["Migration cost", "Learning curve"],
    )

    # Decision created with ID
    assert result.id
    assert result.id.startswith("dec-")

    # Options generated (>= 3)
    assert len(result.options) >= 3
    for opt in result.options:
        assert opt.title
        assert opt.total_score > 0

    # Debate completed (5 modes)
    assert len(result.debate_log) >= 5
    modes = {e.mode for e in result.debate_log}
    assert "builder_pov" in modes
    assert "skeptic_pov" in modes
    assert "contrarian_pov" in modes
    assert "operator_pov" in modes
    assert "red_team_challenge" in modes

    # Output contract filled
    assert result.output.recommendation
    assert result.output.counter_recommendation
    assert result.output.why_now
    assert len(result.output.failure_modes) > 0
    assert result.output.next_experiment

    # Status updated
    assert result.status == DecisionStatus.proposed

    # Run trace persisted
    assert result.run_id
    run = store.runs.get(result.run_id)
    assert run is not None
    assert len(run.events) > 0

    # Decision persisted
    loaded = store.decisions.get(result.id)
    assert loaded is not None
    assert loaded.title == "Test Pipeline Decision"


def test_debate_on_existing():
    store = Store()
    engine = DecisionEngine(store)

    # Create decision first
    result = engine.run(
        title="Debate Test Decision",
        context="Should we expand the team?",
    )

    # Run debate on existing
    debated = engine.debate(result.id)
    assert debated is not None
    assert len(debated.debate_log) >= 5
    assert debated.output.recommendation


def test_scoring_produces_ranking():
    store = Store()
    engine = DecisionEngine(store)

    result = engine.run(
        title="Scoring Test",
        context="Which cloud provider to use?",
    )

    scores = [opt.total_score for opt in result.options]
    assert all(s > 0 for s in scores)
    # Options should have different scores (not all identical)
    assert len(set(scores)) > 1 or len(result.options) == 1


def cleanup():
    shutil.rmtree(_test_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        test_full_pipeline()
        test_debate_on_existing()
        test_scoring_produces_ranking()
        print("All decision engine tests passed!")
    finally:
        cleanup()
