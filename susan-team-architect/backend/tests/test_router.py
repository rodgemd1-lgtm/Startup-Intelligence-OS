"""Tests for the model routing engine."""
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
