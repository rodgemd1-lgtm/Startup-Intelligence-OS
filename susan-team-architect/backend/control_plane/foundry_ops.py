"""Operational storage helpers for foundry decisions, experiments, metrics, and stage reviews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from supabase import create_client

from susan_core.config import config


def _supabase():
    return create_client(config.supabase_url, config.supabase_key)


def _local_writeback_rows(company_id: str, record_key: str) -> list[dict[str, Any]]:
    path = config.companies_dir / company_id / "susan-outputs" / "foundry-writeback.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    records = payload.get("records", {})
    rows = records.get(record_key, [])
    return rows if isinstance(rows, list) else []


def _list_rows(table_name: str, company_id: str, limit: int, order_column: str) -> list[dict[str, Any]]:
    try:
        rows = (
            _supabase()
            .table(table_name)
            .select("*")
            .eq("company_id", company_id)
            .order(order_column, desc=True)
            .limit(limit)
            .execute()
        )
        return rows.data or []
    except Exception:
        return []


def _upsert_row(table_name: str, payload: dict[str, Any], conflict_column: str) -> dict[str, Any]:
    try:
        result = (
            _supabase()
            .table(table_name)
            .upsert(payload, on_conflict=conflict_column)
            .execute()
        )
        return (result.data or [payload])[0]
    except Exception as exc:
        fallback = dict(payload)
        metadata = dict(fallback.get("metadata") or {})
        metadata["_persistence_error"] = str(exc)
        fallback["metadata"] = metadata
        return fallback


def _insert_row(table_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        result = _supabase().table(table_name).insert(payload).execute()
        return (result.data or [payload])[0]
    except Exception as exc:
        fallback = dict(payload)
        metadata = dict(fallback.get("metadata") or {})
        metadata["_persistence_error"] = str(exc)
        fallback["metadata"] = metadata
        return fallback


def list_foundry_decisions(company_id: str, limit: int = 50) -> list[dict[str, Any]]:
    rows = _list_rows("foundry_decisions", company_id, limit, "decided_at")
    return rows or _local_writeback_rows(company_id, "decisions")[:limit]


def save_foundry_decision(payload: dict[str, Any]) -> dict[str, Any]:
    return _upsert_row("foundry_decisions", payload, "decision_id")


def list_foundry_experiments(company_id: str, limit: int = 50) -> list[dict[str, Any]]:
    rows = _list_rows("foundry_experiments", company_id, limit, "created_at")
    return rows or _local_writeback_rows(company_id, "experiments")[:limit]


def save_foundry_experiment(payload: dict[str, Any]) -> dict[str, Any]:
    return _upsert_row("foundry_experiments", payload, "experiment_id")


def list_foundry_metrics(company_id: str, limit: int = 50) -> list[dict[str, Any]]:
    rows = _list_rows("foundry_metrics", company_id, limit, "created_at")
    return rows or _local_writeback_rows(company_id, "metrics")[:limit]


def save_foundry_metric(payload: dict[str, Any]) -> dict[str, Any]:
    return _upsert_row("foundry_metrics", payload, "metric_id")


def list_foundry_stage_reviews(company_id: str, limit: int = 50) -> list[dict[str, Any]]:
    rows = _list_rows("foundry_stage_reviews", company_id, limit, "reviewed_at")
    return rows or _local_writeback_rows(company_id, "stage_reviews")[:limit]


def save_foundry_stage_review(payload: dict[str, Any]) -> dict[str, Any]:
    return _insert_row("foundry_stage_reviews", payload)
