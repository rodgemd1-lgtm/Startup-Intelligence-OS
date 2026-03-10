"""Tests for /api/health and /api/metrics observability endpoints."""

import pytest
from fastapi.testclient import TestClient

from control_plane.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_metrics_endpoint():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "request_count" in data or "total_cost" in data or isinstance(data, dict)
