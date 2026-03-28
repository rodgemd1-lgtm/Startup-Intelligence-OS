"""Tests for jake_cost model router and OpenRouter client.

Validates the V1.5 cost optimization routing: task types map to correct
tiers, complexity bumps work, legacy mapping works, pricing is sane,
and FORCE_ANTHROPIC rollback functions.
"""
import os
import pytest
from unittest.mock import patch, MagicMock

# Must be importable from the backend directory
from jake_cost.router import (
    ModelRouter, ModelTier, Provider, RoutingDecision,
    _MODEL_PRICING, _TASK_ROUTING, _LEGACY_TIER_MAP,
    router, anthropic_router,
)


# ── Tier routing ──────────────────────────────────────────────────────

class TestTierRouting:
    """Task types route to correct tiers."""

    @pytest.mark.parametrize("task_type,expected_tier", [
        ("classify", ModelTier.FREE_BULK),
        ("tag", ModelTier.FREE_BULK),
        ("extract_fields", ModelTier.FREE_BULK),
        ("embed_prep", ModelTier.LOCAL),
        ("triage", ModelTier.VOLUME_OPS),
        ("email_triage", ModelTier.VOLUME_OPS),
        ("rag_query", ModelTier.VOLUME_OPS),
        ("susan_agent_ops", ModelTier.VOLUME_OPS),
        ("content_generation", ModelTier.VOLUME_OPS),
        ("research", ModelTier.SMART_OPS),
        ("brief", ModelTier.SMART_OPS),
        ("competitive_analysis", ModelTier.SMART_OPS),
        ("strategy", ModelTier.SMART_OPS),
        ("jake_fallback", ModelTier.FALLBACK),
        ("architecture", ModelTier.OPUS),
        ("security_audit", ModelTier.OPUS),
    ])
    def test_task_routes_to_correct_tier(self, task_type, expected_tier):
        decision = router.route(task_type)
        assert decision.tier == expected_tier

    def test_unknown_task_gets_default_tier(self):
        decision = router.route("some_random_task_that_doesnt_exist")
        assert decision.tier == ModelTier.VOLUME_OPS

    def test_custom_default_tier(self):
        custom = ModelRouter(default_tier=ModelTier.FREE_BULK)
        decision = custom.route("unknown_task")
        assert decision.tier == ModelTier.FREE_BULK


# ── Provider routing ──────────────────────────────────────────────────

class TestProviderRouting:
    """OpenRouter tiers route to OpenRouter, Anthropic tiers to Anthropic."""

    def test_free_bulk_routes_to_openrouter(self):
        decision = router.route("classify")
        assert decision.provider == Provider.OPENROUTER

    def test_volume_ops_routes_to_openrouter(self):
        decision = router.route("triage")
        assert decision.provider == Provider.OPENROUTER

    def test_smart_ops_routes_to_openrouter(self):
        decision = router.route("research")
        assert decision.provider == Provider.OPENROUTER

    def test_fallback_routes_to_openrouter(self):
        decision = router.route("jake_fallback")
        assert decision.provider == Provider.OPENROUTER

    def test_opus_routes_to_anthropic(self):
        decision = router.route("architecture")
        assert decision.provider == Provider.ANTHROPIC


# ── Complexity bumps ──────────────────────────────────────────────────

class TestComplexityBumps:
    """High complexity bumps tier up by one level."""

    def test_free_bulk_bumps_to_volume_ops(self):
        decision = router.route("classify", complexity="high")
        assert decision.tier == ModelTier.VOLUME_OPS

    def test_volume_ops_bumps_to_smart_ops(self):
        decision = router.route("triage", complexity="high")
        assert decision.tier == ModelTier.SMART_OPS

    def test_smart_ops_bumps_to_fallback(self):
        decision = router.route("research", complexity="high")
        assert decision.tier == ModelTier.FALLBACK

    def test_medium_complexity_no_bump(self):
        decision = router.route("classify", complexity="medium")
        assert decision.tier == ModelTier.FREE_BULK

    def test_bump_rationale_includes_reason(self):
        decision = router.route("classify", complexity="high")
        assert "high complexity" in decision.rationale.lower()


# ── Force tier override ───────────────────────────────────────────────

class TestForceTier:
    """force_tier overrides all routing logic."""

    def test_force_tier_overrides_routing(self):
        decision = router.route("classify", force_tier=ModelTier.OPUS)
        assert decision.tier == ModelTier.OPUS
        assert decision.provider == Provider.ANTHROPIC

    def test_force_tier_rationale(self):
        decision = router.route("classify", force_tier=ModelTier.SMART_OPS)
        assert "forced" in decision.rationale.lower()


# ── Force Anthropic mode ──────────────────────────────────────────────

class TestForceAnthropic:
    """anthropic_router forces all OpenRouter tiers back to Anthropic."""

    def test_anthropic_router_forces_sonnet(self):
        decision = anthropic_router.route("classify")
        assert decision.provider == Provider.ANTHROPIC
        assert decision.tier == ModelTier.SONNET

    def test_anthropic_router_forces_volume_ops_to_sonnet(self):
        decision = anthropic_router.route("triage")
        assert decision.tier == ModelTier.SONNET

    def test_anthropic_router_keeps_opus_as_opus(self):
        decision = anthropic_router.route("architecture")
        assert decision.tier == ModelTier.OPUS


# ── Pricing table sanity ─────────────────────────────────────────────

class TestPricingSanity:
    """Pricing table has required fields and sane values."""

    @pytest.mark.parametrize("tier", list(ModelTier))
    def test_every_tier_has_pricing(self, tier):
        assert tier in _MODEL_PRICING

    @pytest.mark.parametrize("tier", list(ModelTier))
    def test_pricing_has_required_fields(self, tier):
        info = _MODEL_PRICING[tier]
        assert "model_id" in info
        assert "provider" in info
        assert "input_per_1m" in info
        assert "output_per_1m" in info
        assert "max_tokens" in info
        assert "context_window" in info

    def test_free_bulk_is_actually_free(self):
        info = _MODEL_PRICING[ModelTier.FREE_BULK]
        assert info["input_per_1m"] == 0.0
        assert info["output_per_1m"] == 0.0

    def test_openrouter_tiers_cheaper_than_anthropic(self):
        volume = _MODEL_PRICING[ModelTier.VOLUME_OPS]
        sonnet = _MODEL_PRICING[ModelTier.SONNET]
        assert volume["input_per_1m"] < sonnet["input_per_1m"]
        assert volume["output_per_1m"] < sonnet["output_per_1m"]


# ── Cost estimation ──────────────────────────────────────────────────

class TestCostEstimation:
    """Cost estimates are mathematically correct."""

    def test_free_bulk_costs_zero(self):
        cost = router.cost_estimate(ModelTier.FREE_BULK, 100_000, 50_000)
        assert cost == 0.0

    def test_volume_ops_cost_calculation(self):
        info = _MODEL_PRICING[ModelTier.VOLUME_OPS]
        cost = router.cost_estimate(ModelTier.VOLUME_OPS, 1_000_000, 1_000_000)
        expected = info["input_per_1m"] + info["output_per_1m"]
        assert abs(cost - expected) < 0.0001

    def test_zero_tokens_costs_zero(self):
        cost = router.cost_estimate(ModelTier.OPUS, 0, 0)
        assert cost == 0.0


# ── Savings report ───────────────────────────────────────────────────

class TestSavingsReport:
    """Savings report correctly compares actual vs Sonnet baseline."""

    def test_savings_report_structure(self):
        calls = [
            {"tier": "free_bulk", "input_tokens": 10000, "output_tokens": 5000},
            {"tier": "volume_ops", "input_tokens": 20000, "output_tokens": 10000},
        ]
        report = router.savings_report(calls)
        assert "actual_cost" in report
        assert "sonnet_baseline_cost" in report
        assert "savings_usd" in report
        assert "savings_pct" in report
        assert "call_count" in report
        assert report["call_count"] == 2

    def test_savings_are_positive_when_using_cheap_tiers(self):
        calls = [
            {"tier": "free_bulk", "input_tokens": 100000, "output_tokens": 50000},
        ]
        report = router.savings_report(calls)
        assert report["savings_usd"] > 0
        assert report["savings_pct"] > 0

    def test_empty_calls_returns_zero(self):
        report = router.savings_report([])
        assert report["actual_cost"] == 0
        assert report["call_count"] == 0


# ── RoutingDecision serialization ────────────────────────────────────

class TestRoutingDecision:
    """RoutingDecision.to_dict() serializes correctly."""

    def test_to_dict_has_all_fields(self):
        decision = router.route("classify")
        d = decision.to_dict()
        assert set(d.keys()) == {
            "task_type", "tier", "model_id", "provider",
            "rationale", "estimated_cost_per_1k_tokens",
        }

    def test_to_dict_values_are_strings_and_floats(self):
        d = router.route("research").to_dict()
        assert isinstance(d["task_type"], str)
        assert isinstance(d["tier"], str)
        assert isinstance(d["model_id"], str)
        assert isinstance(d["provider"], str)
        assert isinstance(d["rationale"], str)
        assert isinstance(d["estimated_cost_per_1k_tokens"], float)


# ── Pricing table display ────────────────────────────────────────────

class TestPricingTable:
    """pricing_table() returns a readable string."""

    def test_pricing_table_not_empty(self):
        table = ModelRouter.pricing_table()
        assert len(table) > 100

    def test_pricing_table_includes_all_tiers(self):
        table = ModelRouter.pricing_table()
        for tier in ModelTier:
            assert tier.value.upper() in table


# ── Legacy tier mapping ──────────────────────────────────────────────

class TestLegacyMapping:
    """Legacy Anthropic tiers map to new OpenRouter tiers."""

    def test_haiku_maps_to_free_bulk(self):
        assert _LEGACY_TIER_MAP[ModelTier.HAIKU] == ModelTier.FREE_BULK

    def test_sonnet_maps_to_smart_ops(self):
        assert _LEGACY_TIER_MAP[ModelTier.SONNET] == ModelTier.SMART_OPS
