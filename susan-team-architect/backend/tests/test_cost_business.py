"""Tests for Jake Cost Optimizer and Business Pipeline modules.

Run from backend/:
  .venv/bin/python -m pytest tests/test_cost_business.py -v
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch, call
import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def router():
    """ModelRouter instance (no Supabase needed)."""
    from jake_brain.cost_optimizer import ModelRouter
    return ModelRouter()


@pytest.fixture
def mock_supabase():
    """Generic mock Supabase client."""
    client = MagicMock()
    # Make table(...).select(...).execute() return empty list by default
    mock_execute = MagicMock()
    mock_execute.execute.return_value = MagicMock(data=[], count=0)
    client.table.return_value.select.return_value = mock_execute
    client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])
    client.table.return_value.update.return_value.execute.return_value = MagicMock(data=[])
    return client


@pytest.fixture
def cost_tracker(mock_supabase):
    """CostTracker with mocked Supabase."""
    from jake_brain.cost_optimizer import CostTracker
    with patch("jake_brain.cost_optimizer.create_client", return_value=mock_supabase):
        tracker = CostTracker()
    return tracker


@pytest.fixture
def pipeline_manager(mock_supabase):
    """PipelineManager with mocked Supabase."""
    from jake_brain.business_pipeline import PipelineManager
    with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
        mgr = PipelineManager()
    return mgr


# ---------------------------------------------------------------------------
# ModelRouter tests
# ---------------------------------------------------------------------------

class TestModelRouter:
    def test_route_lookup_returns_haiku(self, router):
        model, reason = router.route_task("lookup the user's email address")
        assert "haiku" in model.lower(), f"Expected haiku, got {model}"
        assert reason

    def test_route_format_returns_haiku(self, router):
        model, reason = router.route_task("format this JSON response")
        assert "haiku" in model.lower()

    def test_route_summarize_returns_haiku(self, router):
        model, reason = router.route_task("summarize these meeting notes")
        assert "haiku" in model.lower()

    def test_route_analyze_returns_sonnet(self, router):
        model, reason = router.route_task("analyze the quarterly data trends")
        assert "sonnet" in model.lower(), f"Expected sonnet, got {model}"

    def test_route_research_returns_sonnet(self, router):
        model, reason = router.route_task("research competitor pricing")
        assert "sonnet" in model.lower()

    def test_route_review_returns_sonnet(self, router):
        model, reason = router.route_task("review this pull request")
        assert "sonnet" in model.lower()

    def test_route_plan_returns_sonnet(self, router):
        model, reason = router.route_task("plan the next sprint")
        assert "sonnet" in model.lower()

    def test_route_decide_returns_opus(self, router):
        model, reason = router.route_task("decide whether to migrate the database")
        assert "opus" in model.lower(), f"Expected opus, got {model}"

    def test_route_architecture_returns_opus(self, router):
        model, reason = router.route_task("architecture review for the new service")
        assert "opus" in model.lower()

    def test_route_security_returns_opus(self, router):
        model, reason = router.route_task("security audit of authentication flow")
        assert "opus" in model.lower()

    def test_route_irreversible_returns_opus(self, router):
        model, reason = router.route_task("irreversible production deployment")
        assert "opus" in model.lower()

    def test_route_default_returns_sonnet(self, router):
        """Unknown task with no keywords → default sonnet."""
        model, reason = router.route_task("do the thing")
        assert "sonnet" in model.lower()
        assert "default" in reason

    def test_task_type_override_maintenance(self, router):
        """task_type='maintenance' forces haiku regardless of description."""
        model, reason = router.route_task("decide architecture", task_type="maintenance")
        assert "haiku" in model.lower()
        assert "maintenance" in reason

    def test_task_type_override_decision(self, router):
        """task_type='decision' forces opus."""
        model, reason = router.route_task("list items", task_type="decision")
        assert "opus" in model.lower()

    def test_task_type_override_research(self, router):
        model, reason = router.route_task("count records", task_type="research")
        assert "sonnet" in model.lower()

    def test_opus_beats_haiku_on_mixed_keywords(self, router):
        """When description has both haiku and opus keywords, opus wins."""
        model, reason = router.route_task("decide and list all options")
        assert "opus" in model.lower()

    def test_route_returns_tuple_of_two_strings(self, router):
        result = router.route_task("anything")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(x, str) for x in result)


class TestEstimateCost:
    def test_haiku_cost_lower_than_sonnet(self, router):
        haiku = router.estimate_cost("claude-haiku-4-5-20251001", 1000, 1000)
        sonnet = router.estimate_cost("claude-sonnet-4-6", 1000, 1000)
        assert haiku < sonnet

    def test_sonnet_cost_lower_than_opus(self, router):
        sonnet = router.estimate_cost("claude-sonnet-4-6", 1000, 1000)
        opus = router.estimate_cost("claude-opus-4-6", 1000, 1000)
        assert sonnet < opus

    def test_zero_tokens_zero_cost(self, router):
        cost = router.estimate_cost("claude-sonnet-4-6", 0, 0)
        assert cost == 0.0

    def test_cost_calculation_is_correct(self, router):
        """1M input + 1M output at sonnet rates: $3 + $15 = $18."""
        cost = router.estimate_cost("claude-sonnet-4-6", 1_000_000, 1_000_000)
        assert abs(cost - 18.0) < 0.001

    def test_haiku_cost_calculation(self, router):
        """1M input + 1M output at haiku: $0.80 + $4.00 = $4.80."""
        cost = router.estimate_cost("claude-haiku-4-5-20251001", 1_000_000, 1_000_000)
        assert abs(cost - 4.80) < 0.001

    def test_unknown_model_falls_back_to_sonnet_rate(self, router):
        cost = router.estimate_cost("unknown-model", 1_000_000, 1_000_000)
        assert cost > 0  # Falls back gracefully

    def test_cost_is_rounded_to_6_decimal_places(self, router):
        cost = router.estimate_cost("claude-sonnet-4-6", 123, 456)
        assert isinstance(cost, float)
        assert len(str(cost).split(".")[-1]) <= 6


class TestTokenBudget:
    def test_maintenance_budget(self, router):
        budget = router.get_token_budget("maintenance")
        assert budget["input_limit"] == 4_000
        assert budget["output_limit"] == 1_000

    def test_research_budget(self, router):
        budget = router.get_token_budget("research")
        assert budget["input_limit"] == 8_000
        assert budget["output_limit"] == 4_000

    def test_decision_budget(self, router):
        budget = router.get_token_budget("decision")
        assert budget["input_limit"] == 16_000
        assert budget["output_limit"] == 8_000

    def test_default_budget(self, router):
        budget = router.get_token_budget("unknown_type")
        assert budget["input_limit"] == 8_000
        assert budget["output_limit"] == 4_000

    def test_budget_returns_dict(self, router):
        budget = router.get_token_budget("research")
        assert isinstance(budget, dict)
        assert "input_limit" in budget
        assert "output_limit" in budget


# ---------------------------------------------------------------------------
# PipelineManager tests
# ---------------------------------------------------------------------------

class TestPipelineManager:
    def _make_deal_row(self, **kwargs) -> dict:
        """Build a minimal deal row for mock returns."""
        base = {
            "id": str(uuid.uuid4()),
            "name": "Test Deal",
            "company": "Test Co",
            "stage": "DISCOVERY",
            "value_usd": 10_000.0,
            "probability": 0.1,
            "owner": "mike",
            "source": "oracle_health",
            "next_action": "",
            "notes": "",
            "metadata": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        base.update(kwargs)
        return base

    def test_create_deal_returns_deal_object(self, mock_supabase):
        from jake_brain.business_pipeline import PipelineManager, Deal
        row = self._make_deal_row(name="Oracle EHR", stage="PROPOSAL",
                                   value_usd=250_000.0, probability=0.4)
        mock_supabase.table.return_value.insert.return_value.execute.return_value = \
            MagicMock(data=[row])
        with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
            mgr = PipelineManager()
        deal = mgr.create_deal("Oracle EHR", "Oracle Health", stage="PROPOSAL",
                               value_usd=250_000.0, probability=0.4)
        assert isinstance(deal, Deal)
        assert deal.name == "Oracle EHR"
        assert deal.stage == "PROPOSAL"
        assert deal.value_usd == 250_000.0

    def test_create_deal_invalid_stage_raises(self, mock_supabase):
        from jake_brain.business_pipeline import PipelineManager
        with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
            mgr = PipelineManager()
        with pytest.raises(ValueError, match="Invalid stage"):
            mgr.create_deal("Bad Deal", "Co", stage="INVALID")

    def test_update_stage_moves_deal(self, mock_supabase):
        from jake_brain.business_pipeline import PipelineManager, Deal
        original_row = self._make_deal_row(stage="DISCOVERY")
        updated_row = {**original_row, "stage": "DEMO", "probability": 0.3}

        select_mock = MagicMock()
        select_mock.execute.return_value = MagicMock(data=[original_row])
        mock_supabase.table.return_value.select.return_value.eq.return_value = select_mock

        update_mock = MagicMock()
        update_mock.execute.return_value = MagicMock(data=[updated_row])
        mock_supabase.table.return_value.update.return_value.eq.return_value = update_mock

        with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
            mgr = PipelineManager()
        deal = mgr.update_stage(original_row["id"], "DEMO", notes="Scheduled demo")
        assert deal is not None
        assert deal.stage == "DEMO"

    def test_update_stage_invalid_raises(self, mock_supabase):
        from jake_brain.business_pipeline import PipelineManager
        with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
            mgr = PipelineManager()
        with pytest.raises(ValueError, match="Invalid stage"):
            mgr.update_stage("some-id", "BOGUS")

    def test_get_pipeline_summary_returns_correct_structure(self, mock_supabase):
        from jake_brain.business_pipeline import PipelineManager, STAGES
        rows = [
            self._make_deal_row(stage="PROPOSAL", value_usd=100_000.0, probability=0.5),
            self._make_deal_row(stage="DEMO", value_usd=50_000.0, probability=0.3),
            self._make_deal_row(stage="DISCOVERY", value_usd=25_000.0, probability=0.1),
        ]
        q = mock_supabase.table.return_value.select.return_value
        q.neq.return_value.order.return_value.execute.return_value = MagicMock(data=rows)

        with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
            mgr = PipelineManager()
        summary = mgr.get_pipeline_summary()

        assert "stages" in summary
        assert "total_value" in summary
        assert "weighted_value" in summary
        assert "deal_count" in summary
        # All STAGES should be present as keys
        for stage in STAGES:
            assert stage in summary["stages"]
        assert summary["deal_count"] == 3
        # Total value: 100K + 50K + 25K = 175K
        assert summary["total_value"] == 175_000.0
        # Weighted: 50K + 15K + 2.5K = 67.5K
        assert abs(summary["weighted_value"] - 67_500.0) < 1.0

    def test_weighted_value_excludes_closed_lost(self, mock_supabase):
        from jake_brain.business_pipeline import PipelineManager
        rows = [
            self._make_deal_row(stage="CLOSED_LOST", value_usd=500_000.0, probability=0.0),
            self._make_deal_row(stage="PROPOSAL", value_usd=100_000.0, probability=0.5),
        ]
        # Note: get_all_deals filters out CLOSED_LOST via neq
        q = mock_supabase.table.return_value.select.return_value
        # Simulate Supabase filtering — only return PROPOSAL deal
        q.neq.return_value.order.return_value.execute.return_value = MagicMock(data=[rows[1]])

        with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
            mgr = PipelineManager()
        summary = mgr.get_pipeline_summary()
        assert summary["total_value"] == 100_000.0
        assert summary["weighted_value"] == 50_000.0

    def test_deal_weighted_value_property(self):
        from jake_brain.business_pipeline import Deal
        deal = Deal(
            id="test", name="Test", company="Co", stage="PROPOSAL",
            value_usd=100_000.0, probability=0.4, owner="mike",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            next_action="", notes="", source="oracle_health",
        )
        assert deal.weighted_value == 40_000.0

    def test_seed_sample_data_creates_three_deals(self, mock_supabase):
        from jake_brain.business_pipeline import PipelineManager, Deal

        call_count = 0
        def make_insert_mock(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            row = {
                "id": str(uuid.uuid4()),
                "name": f"Deal {call_count}",
                "company": "Test",
                "stage": "DISCOVERY",
                "value_usd": 10_000.0,
                "probability": 0.1,
                "owner": "mike",
                "source": "oracle_health",
                "next_action": "",
                "notes": "",
                "metadata": {},
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_exec = MagicMock()
            mock_exec.execute.return_value = MagicMock(data=[row])
            return mock_exec

        mock_supabase.table.return_value.insert = make_insert_mock

        with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
            mgr = PipelineManager()
        deals = mgr.seed_sample_data()
        assert len(deals) == 3
        assert all(isinstance(d, Deal) for d in deals)

    def test_get_deals_needing_action_returns_stale_deals(self, mock_supabase):
        from jake_brain.business_pipeline import PipelineManager
        stale_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        stale_row = {
            "id": str(uuid.uuid4()),
            "name": "Stale Deal",
            "company": "Co",
            "stage": "DEMO",
            "value_usd": 50_000.0,
            "probability": 0.3,
            "owner": "mike",
            "source": "oracle_health",
            "next_action": "Follow up",
            "notes": "",
            "metadata": {},
            "created_at": stale_date,
            "updated_at": stale_date,
        }
        # get_deals_needing_action chains: table.select.lt.neq.neq.order.execute
        q = (mock_supabase.table.return_value
             .select.return_value
             .lt.return_value
             .neq.return_value
             .neq.return_value
             .order.return_value)
        q.execute.return_value = MagicMock(data=[stale_row])

        with patch("jake_brain.business_pipeline.create_client", return_value=mock_supabase):
            mgr = PipelineManager()
        stale = mgr.get_deals_needing_action(days_stale=7)
        assert len(stale) == 1
        assert stale[0].name == "Stale Deal"


# ---------------------------------------------------------------------------
# Integration smoke test (no network)
# ---------------------------------------------------------------------------

class TestModuleImports:
    def test_cost_optimizer_importable(self):
        from jake_brain import cost_optimizer
        assert hasattr(cost_optimizer, "ModelRouter")
        assert hasattr(cost_optimizer, "CostTracker")
        assert hasattr(cost_optimizer, "get_router")
        assert hasattr(cost_optimizer, "get_tracker")

    def test_business_pipeline_importable(self):
        from jake_brain import business_pipeline
        assert hasattr(business_pipeline, "Deal")
        assert hasattr(business_pipeline, "PipelineManager")
        assert hasattr(business_pipeline, "RevenueImpactTracker")
        assert hasattr(business_pipeline, "STAGES")

    def test_stages_constant_has_all_six(self):
        from jake_brain.business_pipeline import STAGES
        expected = {"DISCOVERY", "DEMO", "PROPOSAL", "NEGOTIATION", "CLOSED_WON", "CLOSED_LOST"}
        assert set(STAGES) == expected
