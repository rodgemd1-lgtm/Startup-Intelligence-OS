"""Jake Cost Optimizer — Smart model routing and token budget management.

Routes tasks to the right model based on complexity:
  - Haiku:  Simple lookups, single-fact questions, formatting tasks
  - Sonnet: Standard analysis, summaries, code review, research synthesis
  - Opus:   Architecture decisions, complex reasoning, irreversible actions

Token budget tracking per task type.
Cost tracking in Supabase.
Monthly spend reports.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Any

from supabase import create_client, Client
from susan_core.config import config as susan_config


# ---------------------------------------------------------------------------
# Model Router
# ---------------------------------------------------------------------------

class ModelRouter:
    """Route tasks to the right Claude model based on complexity signals."""

    # Cost per 1M tokens (approximate, Mar 2026)
    MODEL_COSTS = {
        "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
        "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
        "claude-opus-4-6": {"input": 15.00, "output": 75.00},
    }

    # Friendly short names → full model IDs
    MODEL_ALIASES = {
        "haiku": "claude-haiku-4-5-20251001",
        "sonnet": "claude-sonnet-4-6",
        "opus": "claude-opus-4-6",
    }

    # Complexity signals → (model_alias, reason)
    COMPLEXITY_RULES: dict[str, tuple[str, str]] = {
        # Haiku — simple tasks
        "lookup": ("haiku", "simple fact retrieval"),
        "format": ("haiku", "formatting only"),
        "summarize": ("haiku", "summarization"),
        "count": ("haiku", "counting/stats"),
        "list": ("haiku", "listing items"),
        "translate": ("haiku", "translation task"),
        "parse": ("haiku", "parsing/extraction"),
        # Sonnet — analysis tasks
        "analyze": ("sonnet", "analysis required"),
        "research": ("sonnet", "research synthesis"),
        "review": ("sonnet", "code/content review"),
        "plan": ("sonnet", "planning task"),
        "draft": ("sonnet", "content creation"),
        "explain": ("sonnet", "explanation required"),
        "debug": ("sonnet", "debugging task"),
        "compare": ("sonnet", "comparison analysis"),
        # Opus — decision/architecture tasks
        "decide": ("opus", "decision required"),
        "architecture": ("opus", "architectural decision"),
        "security": ("opus", "security analysis"),
        "irreversible": ("opus", "irreversible action"),
        "design": ("opus", "system design"),
        "audit": ("opus", "full audit required"),
        "strategy": ("opus", "strategic decision"),
    }

    # Task type → model alias override
    TASK_TYPE_ROUTING: dict[str, str] = {
        "maintenance": "haiku",
        "formatting": "haiku",
        "lookup": "haiku",
        "research": "sonnet",
        "analysis": "sonnet",
        "code_review": "sonnet",
        "content": "sonnet",
        "decision": "opus",
        "architecture": "opus",
        "security": "opus",
    }

    # Token budgets per task type
    TOKEN_BUDGETS: dict[str, dict[str, int]] = {
        "maintenance": {"input_limit": 4_000, "output_limit": 1_000},
        "research": {"input_limit": 8_000, "output_limit": 4_000},
        "decision": {"input_limit": 16_000, "output_limit": 8_000},
        "default": {"input_limit": 8_000, "output_limit": 4_000},
    }

    def route_task(
        self,
        task_description: str,
        task_type: str | None = None,
    ) -> tuple[str, str]:
        """Return (model_id, reason) for a given task.

        Priority order:
          1. task_type override (if provided and known)
          2. Keyword scan of task_description
          3. Default → sonnet
        """
        # 1. task_type override
        if task_type and task_type in self.TASK_TYPE_ROUTING:
            alias = self.TASK_TYPE_ROUTING[task_type]
            model_id = self.MODEL_ALIASES[alias]
            return model_id, f"task_type={task_type} → {alias}"

        # 2. Keyword scan (case-insensitive, word-boundary aware)
        desc_lower = task_description.lower()
        # Scan in priority order: opus rules first, then sonnet, then haiku
        for priority_tier in [("opus", "decide", "architecture", "security", "irreversible", "design", "audit", "strategy"),
                               ("sonnet", "analyze", "research", "review", "plan", "draft", "explain", "debug", "compare"),
                               ("haiku", "lookup", "format", "summarize", "count", "list", "translate", "parse")]:
            tier_alias = priority_tier[0]
            keywords = priority_tier[1:]
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                    rule = self.COMPLEXITY_RULES.get(kw, (tier_alias, f"keyword match: {kw}"))
                    model_id = self.MODEL_ALIASES[rule[0]]
                    return model_id, rule[1]

        # 3. Default → sonnet
        return self.MODEL_ALIASES["sonnet"], "default routing"

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for a given model and token counts."""
        costs = self.MODEL_COSTS.get(model)
        if not costs:
            # Try resolving alias
            alias_model = self.MODEL_ALIASES.get(model)
            costs = self.MODEL_COSTS.get(alias_model, {"input": 3.00, "output": 15.00})
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        return round(input_cost + output_cost, 6)

    def get_token_budget(self, task_type: str) -> dict[str, int]:
        """Return token budget dict for a given task type."""
        return self.TOKEN_BUDGETS.get(task_type, self.TOKEN_BUDGETS["default"]).copy()

    def model_info(self) -> dict[str, Any]:
        """Return all model cost/alias info for display."""
        return {
            "models": self.MODEL_COSTS,
            "aliases": self.MODEL_ALIASES,
            "routing_rules": {k: v[0] for k, v in self.COMPLEXITY_RULES.items()},
        }


# ---------------------------------------------------------------------------
# Cost Tracker
# ---------------------------------------------------------------------------

COST_LOG_PATH = Path("~/.hermes/logs/cost_tracking.jsonl").expanduser()


class CostTracker:
    """Track token usage and costs in Supabase (with local JSONL backup)."""

    TABLE = "jake_cost_tracking"

    def __init__(self):
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )
        self.router = ModelRouter()
        # Ensure log directory exists
        COST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def record_usage(
        self,
        task_type: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        employee: str | None = None,
        task_id: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Insert a cost record to Supabase and local backup log."""
        cost = self.router.estimate_cost(model, input_tokens, output_tokens)
        now = datetime.now(timezone.utc)

        row = {
            "task_type": task_type,
            "employee_name": employee,
            "task_id": task_id,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": cost,
            "metadata": metadata or {},
        }

        # Write to Supabase
        try:
            result = self.supabase.table(self.TABLE).insert(row).execute()
            db_row = result.data[0] if result.data else row
        except Exception as exc:
            db_row = {**row, "supabase_error": str(exc)}

        # Write local backup
        log_entry = {
            "recorded_at": now.isoformat(),
            **row,
            "estimated_cost_usd": float(cost),
        }
        try:
            with COST_LOG_PATH.open("a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except OSError:
            pass  # Non-fatal — Supabase is primary

        return db_row

    def get_daily_spend(self) -> float:
        """Return today's total estimated cost in USD."""
        today = date.today().isoformat()
        try:
            result = (
                self.supabase.table(self.TABLE)
                .select("estimated_cost_usd")
                .gte("recorded_at", f"{today}T00:00:00Z")
                .lte("recorded_at", f"{today}T23:59:59Z")
                .execute()
            )
            return round(sum(float(r["estimated_cost_usd"]) for r in (result.data or [])), 4)
        except Exception:
            return 0.0

    def get_monthly_spend(self) -> dict[str, Any]:
        """Return {model: cost, total: cost} for current month."""
        now = datetime.now(timezone.utc)
        month_start = f"{now.year}-{now.month:02d}-01T00:00:00Z"
        try:
            result = (
                self.supabase.table(self.TABLE)
                .select("model, estimated_cost_usd")
                .gte("recorded_at", month_start)
                .execute()
            )
            rows = result.data or []
        except Exception:
            return {"total": 0.0}

        by_model: dict[str, float] = {}
        for r in rows:
            model = r["model"]
            cost = float(r["estimated_cost_usd"])
            by_model[model] = by_model.get(model, 0.0) + cost

        return {
            **{k: round(v, 4) for k, v in by_model.items()},
            "total": round(sum(by_model.values()), 4),
        }

    def get_cost_by_employee(self, days: int = 30) -> dict[str, float]:
        """Return cost breakdown by employee_name over last N days."""
        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        try:
            result = (
                self.supabase.table(self.TABLE)
                .select("employee_name, estimated_cost_usd")
                .gte("recorded_at", cutoff)
                .execute()
            )
            rows = result.data or []
        except Exception:
            return {}

        by_employee: dict[str, float] = {}
        for r in rows:
            emp = r.get("employee_name") or "unknown"
            cost = float(r["estimated_cost_usd"])
            by_employee[emp] = by_employee.get(emp, 0.0) + cost

        return {k: round(v, 4) for k, v in sorted(by_employee.items(), key=lambda x: -x[1])}

    def generate_monthly_report(self) -> str:
        """Generate a formatted text report for the current month."""
        now = datetime.now(timezone.utc)
        month_label = now.strftime("%B %Y")
        month_start = f"{now.year}-{now.month:02d}-01T00:00:00Z"

        try:
            result = (
                self.supabase.table(self.TABLE)
                .select("model, input_tokens, output_tokens, estimated_cost_usd, employee_name")
                .gte("recorded_at", month_start)
                .execute()
            )
            rows = result.data or []
        except Exception as exc:
            return f"Error fetching data: {exc}"

        # Aggregate by model
        model_stats: dict[str, dict] = {}
        for r in rows:
            model = r["model"]
            if model not in model_stats:
                model_stats[model] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0.0}
            model_stats[model]["calls"] += 1
            model_stats[model]["input_tokens"] += r.get("input_tokens", 0) or 0
            model_stats[model]["output_tokens"] += r.get("output_tokens", 0) or 0
            model_stats[model]["cost"] += float(r.get("estimated_cost_usd", 0) or 0)

        total_cost = sum(s["cost"] for s in model_stats.values())
        total_calls = sum(s["calls"] for s in model_stats.values())

        lines = [
            f"=== Jake Cost Report — {month_label} ===",
            f"Total calls: {total_calls}  |  Total cost: ${total_cost:.4f}",
            "",
            f"{'Model':<40} {'Calls':>6} {'Input Tok':>12} {'Output Tok':>12} {'Cost USD':>10}",
            "-" * 84,
        ]
        for model, stats in sorted(model_stats.items(), key=lambda x: -x[1]["cost"]):
            lines.append(
                f"{model:<40} {stats['calls']:>6} {stats['input_tokens']:>12,} "
                f"{stats['output_tokens']:>12,} ${stats['cost']:>9.4f}"
            )
        lines += ["", f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}"]

        report = "\n".join(lines)

        # Save to log file
        log_path = Path(f"~/.hermes/logs/cost_report_{now.year}-{now.month:02d}.txt").expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            log_path.write_text(report)
        except OSError:
            pass

        return report


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_router = ModelRouter()
_tracker: CostTracker | None = None


def get_router() -> ModelRouter:
    return _router


def get_tracker() -> CostTracker:
    global _tracker
    if _tracker is None:
        _tracker = CostTracker()
    return _tracker
