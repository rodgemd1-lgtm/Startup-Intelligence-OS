"""CRUD operations for jake_goals and jake_goal_checkins tables."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from supabase import create_client, Client

from rag_engine.embedder import Embedder
from susan_core.config import config as susan_config


class GoalStore:
    """Handles storage, retrieval, and dashboarding for Jake's goal tracking layer."""

    def __init__(self):
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )
        self.embedder = Embedder()

    # ------------------------------------------------------------------
    # Goals — CRUD
    # ------------------------------------------------------------------

    def create_goal(
        self,
        title: str,
        description: str | None = None,
        goal_type: str = "goal",
        parent_id: str | None = None,
        project: str | None = None,
        priority: str = "P2",
        target_value: float | None = None,
        unit: str | None = None,
        deadline: str | None = None,
        people: list[str] | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Create a new goal, milestone, KPI, or OKR."""
        embed_text = title
        if description:
            embed_text += f" — {description}"
        embedding = self.embedder.embed_query(embed_text)

        row: dict[str, Any] = {
            "title": title,
            "description": description,
            "goal_type": goal_type,
            "parent_id": parent_id,
            "project": project,
            "priority": priority,
            "target_value": target_value,
            "current_value": 0,
            "unit": unit,
            "people": people or [],
            "tags": tags or [],
            "metadata": metadata or {},
            "embedding": embedding,
        }
        if deadline:
            row["deadline"] = deadline

        result = self.supabase.table("jake_goals").insert(row).execute()
        return result.data[0] if result.data else {}

    def update_goal(self, goal_id: str, **updates: Any) -> dict:
        """Update fields on an existing goal. Re-embeds if title or description changes."""
        if "title" in updates or "description" in updates:
            # Need current values to build embed text
            current = self.get_goal(goal_id)
            if current:
                title = updates.get("title", current.get("title", ""))
                desc = updates.get("description", current.get("description"))
                embed_text = title
                if desc:
                    embed_text += f" — {desc}"
                updates["embedding"] = self.embedder.embed_query(embed_text)

        result = (
            self.supabase.table("jake_goals")
            .update(updates)
            .eq("id", goal_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def complete_goal(self, goal_id: str) -> dict:
        """Mark a goal as completed with timestamp."""
        now = datetime.now(timezone.utc).isoformat()
        result = (
            self.supabase.table("jake_goals")
            .update({"status": "completed", "completed_at": now})
            .eq("id", goal_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def get_goal(self, goal_id: str) -> dict:
        """Get a single goal by ID."""
        result = (
            self.supabase.table("jake_goals")
            .select("*")
            .eq("id", goal_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def list_goals(
        self,
        status: str | None = None,
        project: str | None = None,
        goal_type: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """List goals with optional filters."""
        query = (
            self.supabase.table("jake_goals")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
        )
        if status:
            query = query.eq("status", status)
        if project:
            query = query.eq("project", project)
        if goal_type:
            query = query.eq("goal_type", goal_type)
        return query.execute().data or []

    def get_milestones(self, goal_id: str) -> list[dict]:
        """Get child milestones for a goal."""
        result = (
            self.supabase.table("jake_goals")
            .select("*")
            .eq("parent_id", goal_id)
            .eq("goal_type", "milestone")
            .order("created_at", desc=False)
            .execute()
        )
        return result.data or []

    # ------------------------------------------------------------------
    # Semantic Search
    # ------------------------------------------------------------------

    def search_goals(
        self,
        query: str,
        status: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Semantic search across goals via jake_goal_search RPC."""
        embedding = self.embedder.embed_query(query)
        params: dict[str, Any] = {
            "query_embedding": embedding,
            "match_count": limit,
        }
        if status:
            params["status_filter"] = status
        result = self.supabase.rpc("jake_goal_search", params).execute()
        return result.data or []

    # ------------------------------------------------------------------
    # Check-ins
    # ------------------------------------------------------------------

    def add_checkin(
        self,
        goal_id: str,
        content: str,
        new_value: float | None = None,
        source: str = "manual",
        metadata: dict | None = None,
    ) -> dict:
        """Log a progress check-in. Optionally updates the goal's current_value."""
        embedding = self.embedder.embed_query(content)

        # Get current value for delta calculation
        goal = self.get_goal(goal_id)
        previous_value = goal.get("current_value") if goal else None
        delta = None
        if new_value is not None and previous_value is not None:
            delta = new_value - float(previous_value)

        row: dict[str, Any] = {
            "goal_id": goal_id,
            "content": content,
            "previous_value": previous_value,
            "new_value": new_value,
            "delta": delta,
            "source": source,
            "metadata": metadata or {},
            "embedding": embedding,
        }
        result = self.supabase.table("jake_goal_checkins").insert(row).execute()

        # Update the goal's current_value if a new value was provided
        if new_value is not None:
            self.supabase.table("jake_goals").update(
                {"current_value": new_value}
            ).eq("id", goal_id).execute()

        return result.data[0] if result.data else {}

    def get_checkins(self, goal_id: str, limit: int = 20) -> list[dict]:
        """Get check-in history for a goal, most recent first."""
        result = (
            self.supabase.table("jake_goal_checkins")
            .select("*")
            .eq("goal_id", goal_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self, project: str | None = None) -> dict:
        """Return a summary dashboard for goals, optionally filtered by project."""
        query = self.supabase.table("jake_goals").select("*")
        if project:
            query = query.eq("project", project)
        all_goals = query.execute().data or []

        now = datetime.now(timezone.utc)
        active = [g for g in all_goals if g["status"] == "active"]
        completed = [g for g in all_goals if g["status"] == "completed"]

        overdue = []
        behind_schedule = []
        for g in active:
            # Overdue: deadline passed
            if g.get("deadline"):
                dl = datetime.fromisoformat(g["deadline"].replace("Z", "+00:00"))
                if dl < now:
                    overdue.append(g)

            # Behind schedule: has target and current_value < expected progress
            if g.get("target_value") and g.get("deadline") and g.get("current_value") is not None:
                dl = datetime.fromisoformat(g["deadline"].replace("Z", "+00:00"))
                created = datetime.fromisoformat(g["created_at"].replace("Z", "+00:00"))
                total_span = (dl - created).total_seconds()
                elapsed = (now - created).total_seconds()
                if total_span > 0 and elapsed > 0:
                    expected_pct = min(elapsed / total_span, 1.0)
                    actual_pct = float(g["current_value"]) / float(g["target_value"])
                    if actual_pct < expected_pct * 0.8:  # 20% behind expected pace
                        behind_schedule.append(g)

        return {
            "total": len(all_goals),
            "active": len(active),
            "completed": len(completed),
            "overdue": len(overdue),
            "behind_schedule": len(behind_schedule),
            "overdue_goals": [{"id": g["id"], "title": g["title"], "deadline": g.get("deadline")} for g in overdue],
            "behind_goals": [{"id": g["id"], "title": g["title"], "current_value": g.get("current_value"), "target_value": g.get("target_value")} for g in behind_schedule],
            "active_goals": [{"id": g["id"], "title": g["title"], "priority": g["priority"], "project": g.get("project")} for g in active],
        }

    # ------------------------------------------------------------------
    # Cleanup (for tests)
    # ------------------------------------------------------------------

    def delete_goal(self, goal_id: str) -> None:
        """Delete a goal and its check-ins (cascade)."""
        self.supabase.table("jake_goals").delete().eq("id", goal_id).execute()
