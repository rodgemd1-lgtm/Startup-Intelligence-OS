"""TaskStore — CRUD for jake_tasks and jake_task_runs.

Every jake_goal can have many tasks. The autonomous worker picks up
'pending' tasks and executes them. This module owns all DB interactions.

Usage:
    store = TaskStore()

    # Add tasks to a goal
    task = store.create_task(goal_id="...", task_text="Build recipe system", assigned_to="claude_code")

    # Worker picks up work
    pending = store.claim_next_task(assigned_to="claude_code")

    # Record result
    store.complete_task(task["id"], output="Recipe system built.")
    store.fail_task(task["id"], error="Import error: module not found")
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from supabase import create_client, Client

from rag_engine.embedder import Embedder
from susan_core.config import config as susan_config

logger = logging.getLogger("jake-brain")


class TaskStore:
    """Handles storage and retrieval for jake_tasks and jake_task_runs."""

    def __init__(self) -> None:
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )
        self.embedder = Embedder()

    # ------------------------------------------------------------------
    # Task CRUD
    # ------------------------------------------------------------------

    def create_task(
        self,
        task_text: str,
        goal_id: str | None = None,
        description: str | None = None,
        assigned_to: str = "auto",
        executor_hint: str | None = None,
        priority: str = "P2",
        order_index: int = 0,
        due_date: str | None = None,
        max_attempts: int = 3,
    ) -> dict:
        """Create a new task, optionally linked to a goal."""
        embedding = self.embedder.embed_query(
            task_text + (f" — {description}" if description else "")
        )
        row: dict[str, Any] = {
            "task_text": task_text,
            "description": description,
            "goal_id": goal_id,
            "assigned_to": assigned_to,
            "executor_hint": executor_hint,
            "priority": priority,
            "order_index": order_index,
            "max_attempts": max_attempts,
            "status": "pending",
            "embedding": embedding,
        }
        if due_date:
            row["due_date"] = due_date
        result = self.supabase.table("jake_tasks").insert(row).execute()
        return result.data[0] if result.data else {}

    def get_task(self, task_id: str) -> dict:
        result = (
            self.supabase.table("jake_tasks")
            .select("*")
            .eq("id", task_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def list_tasks(
        self,
        goal_id: str | None = None,
        status: str | None = None,
        assigned_to: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        query = (
            self.supabase.table("jake_tasks")
            .select("*")
            .order("priority", desc=False)
            .order("order_index", desc=False)
            .order("created_at", desc=False)
            .limit(limit)
        )
        if goal_id:
            query = query.eq("goal_id", goal_id)
        if status:
            query = query.eq("status", status)
        if assigned_to:
            query = query.eq("assigned_to", assigned_to)
        return query.execute().data or []

    def claim_next_task(self, assigned_to: str | None = None) -> dict | None:
        """Pick the highest-priority pending task and mark it in_progress.

        This is the worker's main polling call. Returns None if nothing to do.
        For 'auto' assigned tasks, any executor can claim them.
        """
        query = (
            self.supabase.table("jake_tasks")
            .select("*")
            .eq("status", "pending")
            .order("priority", desc=False)
            .order("order_index", desc=False)
            .order("created_at", desc=False)
            .limit(1)
        )
        if assigned_to:
            # Claim tasks assigned to this executor OR tasks assigned to 'auto'
            # We do two queries and take whichever is higher priority
            assigned_result = (
                self.supabase.table("jake_tasks")
                .select("*")
                .eq("status", "pending")
                .eq("assigned_to", assigned_to)
                .order("priority", desc=False)
                .order("order_index", desc=False)
                .limit(1)
                .execute()
            )
            auto_result = (
                self.supabase.table("jake_tasks")
                .select("*")
                .eq("status", "pending")
                .eq("assigned_to", "auto")
                .order("priority", desc=False)
                .order("order_index", desc=False)
                .limit(1)
                .execute()
            )
            candidates = (assigned_result.data or []) + (auto_result.data or [])
            if not candidates:
                return None
            # Pick highest priority (P0 < P1 < P2 < P3)
            task = sorted(candidates, key=lambda t: (t["priority"], t["order_index"]))[0]
        else:
            result = query.execute()
            if not result.data:
                return None
            task = result.data[0]

        # Check attempt limit before claiming
        if task.get("attempt_count", 0) >= task.get("max_attempts", 3):
            self._block_task(task["id"], "Max attempts reached")
            return None

        # Atomically mark in_progress
        now = datetime.now(timezone.utc).isoformat()
        updated = (
            self.supabase.table("jake_tasks")
            .update({
                "status": "in_progress",
                "started_at": now,
                "attempt_count": task.get("attempt_count", 0) + 1,
            })
            .eq("id", task["id"])
            .eq("status", "pending")  # guard against race
            .execute()
        )
        return updated.data[0] if updated.data else None

    def complete_task(self, task_id: str, output: str = "") -> dict:
        now = datetime.now(timezone.utc).isoformat()
        result = (
            self.supabase.table("jake_tasks")
            .update({
                "status": "completed",
                "completed_at": now,
                "output": output[:8000] if output else None,  # guard large outputs
            })
            .eq("id", task_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def fail_task(self, task_id: str, error: str = "") -> dict:
        """Mark failed. If attempts exhausted → blocked. Otherwise → back to pending for retry."""
        task = self.get_task(task_id)
        attempts = task.get("attempt_count", 1)
        max_attempts = task.get("max_attempts", 3)

        if attempts >= max_attempts:
            return self._block_task(task_id, error)

        # Retry: put back to pending
        result = (
            self.supabase.table("jake_tasks")
            .update({
                "status": "pending",
                "started_at": None,
                "error_msg": error[:2000] if error else None,
            })
            .eq("id", task_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def _block_task(self, task_id: str, reason: str = "") -> dict:
        result = (
            self.supabase.table("jake_tasks")
            .update({
                "status": "blocked",
                "error_msg": reason[:2000] if reason else None,
            })
            .eq("id", task_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def skip_task(self, task_id: str, reason: str = "") -> dict:
        result = (
            self.supabase.table("jake_tasks")
            .update({"status": "skipped", "error_msg": reason[:500] if reason else None})
            .eq("id", task_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    # ------------------------------------------------------------------
    # Run log
    # ------------------------------------------------------------------

    def log_run(
        self,
        task_id: str,
        attempt: int,
        status: str,
        output: str | None = None,
        error_msg: str | None = None,
        duration_ms: int | None = None,
        executor: str | None = None,
    ) -> dict:
        row = {
            "task_id": task_id,
            "attempt": attempt,
            "status": status,
            "output": output[:8000] if output else None,
            "error_msg": error_msg[:2000] if error_msg else None,
            "duration_ms": duration_ms,
            "executor": executor,
        }
        result = self.supabase.table("jake_task_runs").insert(row).execute()
        return result.data[0] if result.data else {}

    def get_runs(self, task_id: str, limit: int = 10) -> list[dict]:
        result = (
            self.supabase.table("jake_task_runs")
            .select("*")
            .eq("task_id", task_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self, goal_id: str | None = None) -> dict:
        """Summary of task state, optionally scoped to a goal."""
        query = self.supabase.table("jake_tasks").select("*")
        if goal_id:
            query = query.eq("goal_id", goal_id)
        all_tasks = query.execute().data or []

        by_status: dict[str, list] = {}
        for t in all_tasks:
            by_status.setdefault(t["status"], []).append(t)

        return {
            "total": len(all_tasks),
            "pending": len(by_status.get("pending", [])),
            "in_progress": len(by_status.get("in_progress", [])),
            "completed": len(by_status.get("completed", [])),
            "failed": len(by_status.get("failed", [])),
            "blocked": len(by_status.get("blocked", [])),
            "skipped": len(by_status.get("skipped", [])),
            "pending_tasks": [
                {"id": t["id"], "task_text": t["task_text"], "priority": t["priority"],
                 "assigned_to": t["assigned_to"]}
                for t in by_status.get("pending", [])
            ],
            "blocked_tasks": [
                {"id": t["id"], "task_text": t["task_text"], "error_msg": t.get("error_msg")}
                for t in by_status.get("blocked", [])
            ],
        }

    # ------------------------------------------------------------------
    # Semantic search
    # ------------------------------------------------------------------

    def search_tasks(self, query: str, limit: int = 10) -> list[dict]:
        embedding = self.embedder.embed_query(query)
        result = self.supabase.rpc("jake_task_search", {
            "query_embedding": embedding,
            "match_count": limit,
        }).execute()
        return result.data or []

    # ------------------------------------------------------------------
    # Decompose a goal into tasks
    # ------------------------------------------------------------------

    def create_tasks_from_goal(
        self,
        goal_id: str,
        task_list: list[dict],
    ) -> list[dict]:
        """Bulk-create tasks for a goal from a list of task dicts.

        Each dict: {task_text, assigned_to, executor_hint, priority, order_index}
        """
        created = []
        for i, spec in enumerate(task_list):
            task = self.create_task(
                task_text=spec["task_text"],
                goal_id=goal_id,
                description=spec.get("description"),
                assigned_to=spec.get("assigned_to", "auto"),
                executor_hint=spec.get("executor_hint"),
                priority=spec.get("priority", "P2"),
                order_index=spec.get("order_index", i),
            )
            created.append(task)
        return created
