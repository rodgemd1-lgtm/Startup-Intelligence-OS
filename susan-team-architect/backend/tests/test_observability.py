# tests/test_observability.py
import pytest
import time
from susan_core.metrics import MetricsCollector
from susan_core.health import HealthChecker


def test_metrics_record_latency():
    m = MetricsCollector()
    m.record_latency("agent_run", 150.0)
    m.record_latency("agent_run", 200.0)
    m.record_latency("agent_run", 50.0)
    summary = m.summary()
    assert summary["agent_run"]["p95"] > 0
    assert summary["agent_run"]["count"] == 3


def test_metrics_record_cost():
    m = MetricsCollector()
    m.record_cost("sonnet", 0.005)
    m.record_cost("sonnet", 0.003)
    summary = m.summary()
    assert summary["cost_by_model"]["sonnet"] == pytest.approx(0.008)


def test_metrics_record_error():
    m = MetricsCollector()
    m.record_error("timeout")
    m.record_error("timeout")
    m.record_error("rate_limit")
    summary = m.summary()
    assert summary["errors"]["timeout"] == 2
    assert summary["errors"]["rate_limit"] == 1


def test_health_check_healthy():
    h = HealthChecker()
    h.update_component("anthropic", True)
    h.update_component("supabase", True)
    result = h.check()
    assert result["status"] == "healthy"


def test_health_check_degraded():
    h = HealthChecker()
    h.update_component("anthropic", True)
    h.update_component("supabase", False)
    result = h.check()
    assert result["status"] == "degraded"


def test_health_includes_queue_depth():
    h = HealthChecker()
    h.update_queue_depth(5)
    result = h.check()
    assert result["queue_depth"] == 5
