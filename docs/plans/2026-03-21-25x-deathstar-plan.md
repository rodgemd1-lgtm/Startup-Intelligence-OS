# 25X DeathStar — Phased Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the Foundation layer of the 25X DeathStar — Goal Tracking + SOP Capture + Memory Lake expansion — taking Jake from 85/100 to 100/100 and laying groundwork for commercial PAI platform.

**Architecture:** Extends `jake_brain/` with a new `goals/` submodule (Supabase-backed, pgvector embeddings), a new Hermes skill for SOP capture, and document ingestion expansion. All callable via Telegram through existing Hermes plugin architecture.

**Tech Stack:** Python 3.11+, Supabase (pgvector), Voyage AI embeddings (1024-dim), Hermes plugin system, launchd crons, Telegram Bot API

**Design Doc:** `docs/plans/2026-03-21-25x-deathstar-design.md` (approved)
**Research:** `docs/plans/2026-03-21-25x-research-findings.md`

---

## Phase Map

| Phase | Name | Sessions | Dependencies |
|-------|------|----------|-------------|
| F1 | Goal Tracking Layer | 1-2 | None — builds first |
| F2 | SOP Capture Skill | 1 | F1 (SOPs can link to goals) |
| F3 | Memory Lake Expansion | 1 | F1, F2 (unified search surface) |
| F4 | Weekly Goal Check-in Cron | 0.5 | F1 |
| F5 | Hermes Plugin Integration | 1 | F1, F2, F3 |
| F6 | Validation & 100/100 Audit | 0.5 | All above |

---

## Phase F1: Goal Tracking Layer

### Task 1: Create `jake_goals` Supabase Table

**Files:**
- Create: `supabase/migrations/20260322_jake_goals.sql`

**Step 1: Write the migration SQL**

```sql
-- 20260322_jake_goals.sql
-- Phase F1: Goal Tracking Layer for 25X DeathStar Foundation

-- Goals table
CREATE TABLE IF NOT EXISTS jake_goals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    goal_type TEXT NOT NULL DEFAULT 'goal',  -- goal | milestone | kpi | okr
    parent_id UUID REFERENCES jake_goals(id) ON DELETE SET NULL,  -- milestones → goal
    project TEXT,  -- e.g. 'transformfit', 'oracle-health', 'alex-recruiting'
    status TEXT NOT NULL DEFAULT 'active',  -- active | paused | completed | abandoned
    priority TEXT DEFAULT 'P2',  -- P0 | P1 | P2 | P3
    target_value NUMERIC,  -- for KPIs: target number
    current_value NUMERIC DEFAULT 0,  -- for KPIs: current progress
    unit TEXT,  -- e.g. 'coaches', 'MRR', 'users', '%'
    deadline TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    people TEXT[] DEFAULT '{}',  -- people involved
    tags TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1024),  -- Voyage AI
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Goal check-ins (progress updates)
CREATE TABLE IF NOT EXISTS jake_goal_checkins (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    goal_id UUID NOT NULL REFERENCES jake_goals(id) ON DELETE CASCADE,
    content TEXT NOT NULL,  -- "Added 3 coaches this week"
    previous_value NUMERIC,
    new_value NUMERIC,
    delta NUMERIC,
    source TEXT DEFAULT 'manual',  -- manual | auto | telegram
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1024),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_jake_goals_status ON jake_goals(status);
CREATE INDEX idx_jake_goals_project ON jake_goals(project);
CREATE INDEX idx_jake_goals_parent ON jake_goals(parent_id);
CREATE INDEX idx_jake_goals_deadline ON jake_goals(deadline);
CREATE INDEX idx_jake_goal_checkins_goal ON jake_goal_checkins(goal_id);
CREATE INDEX idx_jake_goals_embedding ON jake_goals USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX idx_jake_goal_checkins_embedding ON jake_goal_checkins USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_jake_goals_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER jake_goals_updated_at
    BEFORE UPDATE ON jake_goals
    FOR EACH ROW
    EXECUTE FUNCTION update_jake_goals_updated_at();

-- RPC: Search goals by semantic similarity
CREATE OR REPLACE FUNCTION jake_goal_search(
    query_embedding VECTOR(1024),
    match_count INT DEFAULT 10,
    status_filter TEXT DEFAULT 'active'
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    description TEXT,
    goal_type TEXT,
    project TEXT,
    status TEXT,
    priority TEXT,
    target_value NUMERIC,
    current_value NUMERIC,
    unit TEXT,
    deadline TIMESTAMPTZ,
    progress_pct NUMERIC,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        g.id, g.title, g.description, g.goal_type, g.project,
        g.status, g.priority, g.target_value, g.current_value, g.unit,
        g.deadline,
        CASE WHEN g.target_value > 0 THEN ROUND((g.current_value / g.target_value) * 100, 1) ELSE NULL END as progress_pct,
        1 - (g.embedding <=> query_embedding) as similarity
    FROM jake_goals g
    WHERE (status_filter = 'all' OR g.status = status_filter)
    ORDER BY g.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

**Step 2: Apply the migration**

Run: `cd susan-team-architect/backend && source .venv/bin/activate && python -c "from jake_brain.store import BrainStore; s = BrainStore(); print(s.supabase.postgrest.session.headers)"` to verify Supabase connection, then apply via Supabase Dashboard SQL editor or `supabase db push`.

**Step 3: Commit**

```bash
git add supabase/migrations/20260322_jake_goals.sql
git commit -m "feat(brain): add jake_goals + jake_goal_checkins tables for goal tracking"
```

---

### Task 2: Goal Store Module

**Files:**
- Create: `susan-team-architect/backend/jake_brain/goals/__init__.py`
- Create: `susan-team-architect/backend/jake_brain/goals/store.py`

**Step 1: Create the goals package init**

```python
"""Jake Goal Tracking — embedded goal + KPI + milestone tracking."""
from jake_brain.goals.store import GoalStore

__all__ = ["GoalStore"]
```

**Step 2: Write the GoalStore**

```python
"""CRUD operations for jake_goals and jake_goal_checkins tables."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from supabase import create_client, Client
from rag_engine.embedder import Embedder
from susan_core.config import config as susan_config


class GoalStore:
    """Handles storage and retrieval for goal tracking tables."""

    def __init__(self):
        self.supabase: Client = create_client(
            susan_config.supabase_url, susan_config.supabase_key
        )
        self.embedder = Embedder()

    # ------------------------------------------------------------------
    # Goals CRUD
    # ------------------------------------------------------------------

    def create_goal(
        self,
        title: str,
        description: str = "",
        goal_type: str = "goal",
        parent_id: str | None = None,
        project: str | None = None,
        priority: str = "P2",
        target_value: float | None = None,
        unit: str | None = None,
        deadline: datetime | str | None = None,
        people: list[str] | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Create a new goal, milestone, KPI, or OKR."""
        embed_text = f"{title}. {description}" if description else title
        embedding = self.embedder.embed_query(embed_text)

        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline)

        row = {
            "title": title,
            "description": description,
            "goal_type": goal_type,
            "parent_id": parent_id,
            "project": project,
            "priority": priority,
            "target_value": target_value,
            "current_value": 0,
            "unit": unit,
            "deadline": deadline.isoformat() if deadline else None,
            "people": people or [],
            "tags": tags or [],
            "metadata": metadata or {},
            "embedding": embedding,
        }
        result = self.supabase.table("jake_goals").insert(row).execute()
        return result.data[0] if result.data else {}

    def update_goal(self, goal_id: str, **updates) -> dict:
        """Update goal fields."""
        if "deadline" in updates and isinstance(updates["deadline"], datetime):
            updates["deadline"] = updates["deadline"].isoformat()
        result = self.supabase.table("jake_goals").update(updates).eq("id", goal_id).execute()
        return result.data[0] if result.data else {}

    def complete_goal(self, goal_id: str) -> dict:
        """Mark goal as completed."""
        return self.update_goal(goal_id, status="completed", completed_at=datetime.now(timezone.utc).isoformat())

    def get_goal(self, goal_id: str) -> dict | None:
        """Get a single goal by ID."""
        result = self.supabase.table("jake_goals").select("*").eq("id", goal_id).execute()
        return result.data[0] if result.data else None

    def list_goals(
        self,
        status: str = "active",
        project: str | None = None,
        goal_type: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """List goals with optional filters."""
        query = self.supabase.table("jake_goals").select("*")
        if status != "all":
            query = query.eq("status", status)
        if project:
            query = query.eq("project", project)
        if goal_type:
            query = query.eq("goal_type", goal_type)
        result = query.order("priority").order("created_at", desc=True).limit(limit).execute()
        return result.data or []

    def get_milestones(self, goal_id: str) -> list[dict]:
        """Get milestones for a goal."""
        result = (
            self.supabase.table("jake_goals")
            .select("*")
            .eq("parent_id", goal_id)
            .eq("goal_type", "milestone")
            .order("deadline")
            .execute()
        )
        return result.data or []

    def search_goals(self, query: str, status: str = "active", limit: int = 10) -> list[dict]:
        """Semantic search across goals."""
        embedding = self.embedder.embed_query(query)
        result = self.supabase.rpc("jake_goal_search", {
            "query_embedding": embedding,
            "match_count": limit,
            "status_filter": status,
        }).execute()
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
        """Log a progress check-in against a goal."""
        # Get current value
        goal = self.get_goal(goal_id)
        previous_value = goal["current_value"] if goal else None

        embedding = self.embedder.embed_query(content)
        row = {
            "goal_id": goal_id,
            "content": content,
            "previous_value": previous_value,
            "new_value": new_value,
            "delta": (new_value - previous_value) if new_value is not None and previous_value is not None else None,
            "source": source,
            "metadata": metadata or {},
            "embedding": embedding,
        }
        result = self.supabase.table("jake_goal_checkins").insert(row).execute()

        # Update goal's current_value if new_value provided
        if new_value is not None and goal:
            self.update_goal(goal_id, current_value=new_value)

        return result.data[0] if result.data else {}

    def get_checkins(self, goal_id: str, limit: int = 10) -> list[dict]:
        """Get recent check-ins for a goal."""
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
    # Dashboard / Summary
    # ------------------------------------------------------------------

    def dashboard(self, project: str | None = None) -> dict:
        """Get goal tracking dashboard summary."""
        goals = self.list_goals(status="all", project=project, limit=100)

        active = [g for g in goals if g["status"] == "active"]
        completed = [g for g in goals if g["status"] == "completed"]
        overdue = [
            g for g in active
            if g.get("deadline") and datetime.fromisoformat(g["deadline"]) < datetime.now(timezone.utc)
        ]
        behind = [
            g for g in active
            if g.get("target_value") and g.get("current_value") is not None
            and g["target_value"] > 0
            and (g["current_value"] / g["target_value"]) < 0.5
            and g.get("deadline")
            and (datetime.fromisoformat(g["deadline"]) - datetime.now(timezone.utc)).days < 14
        ]

        return {
            "total": len(goals),
            "active": len(active),
            "completed": len(completed),
            "overdue": len(overdue),
            "behind_schedule": len(behind),
            "overdue_goals": overdue,
            "behind_goals": behind,
            "active_goals": active,
        }
```

**Step 3: Commit**

```bash
git add susan-team-architect/backend/jake_brain/goals/
git commit -m "feat(brain): goal tracking store — CRUD, search, check-ins, dashboard"
```

---

### Task 3: Goal Tracking CLI

**Files:**
- Create: `susan-team-architect/backend/scripts/jake_goals_cli.py`

**Step 1: Write the CLI**

```python
#!/usr/bin/env python3
"""CLI for Jake's Goal Tracking system.

Usage:
  python jake_goals_cli.py create "Ship TransformFit MVP" --project transformfit --deadline 2026-06-21 --priority P1
  python jake_goals_cli.py list [--project X] [--status active]
  python jake_goals_cli.py checkin <goal_id> "Added 3 beta coaches" [--value 3]
  python jake_goals_cli.py dashboard [--project X]
  python jake_goals_cli.py search "fitness coaching"
  python jake_goals_cli.py milestone <goal_id> "Complete onboarding flow" --deadline 2026-04-15
  python jake_goals_cli.py complete <goal_id>
  python jake_goals_cli.py smoke  # end-to-end test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load env
env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def cmd_create(args):
    from jake_brain.goals import GoalStore
    store = GoalStore()
    goal = store.create_goal(
        title=args.title,
        description=args.description or "",
        project=args.project,
        priority=args.priority or "P2",
        target_value=args.target,
        unit=args.unit,
        deadline=args.deadline,
        people=args.people.split(",") if args.people else None,
        tags=args.tags.split(",") if args.tags else None,
    )
    print(f"✅ Goal created: {goal['id']}")
    print(f"   Title: {goal['title']}")
    print(f"   Project: {goal.get('project', '—')}")
    print(f"   Priority: {goal['priority']}")
    if goal.get("deadline"):
        print(f"   Deadline: {goal['deadline'][:10]}")


def cmd_list(args):
    from jake_brain.goals import GoalStore
    store = GoalStore()
    goals = store.list_goals(status=args.status or "active", project=args.project)
    if not goals:
        print("No goals found.")
        return
    print(f"\n{'='*60}")
    print(f"  GOALS ({args.status or 'active'}) — {len(goals)} total")
    print(f"{'='*60}")
    for g in goals:
        progress = ""
        if g.get("target_value") and g["target_value"] > 0:
            pct = (g.get("current_value", 0) / g["target_value"]) * 100
            progress = f" [{g.get('current_value', 0)}/{g['target_value']} {g.get('unit', '')} = {pct:.0f}%]"
        deadline = f" (due {g['deadline'][:10]})" if g.get("deadline") else ""
        print(f"  [{g['priority']}] {g['title']}{progress}{deadline}")
        print(f"       id: {g['id']}  project: {g.get('project', '—')}")


def cmd_checkin(args):
    from jake_brain.goals import GoalStore
    store = GoalStore()
    checkin = store.add_checkin(
        goal_id=args.goal_id,
        content=args.content,
        new_value=args.value,
        source="cli",
    )
    print(f"✅ Check-in logged: {checkin['id']}")
    if args.value is not None:
        print(f"   Value: {checkin.get('previous_value', '?')} → {args.value} (Δ {checkin.get('delta', '?')})")


def cmd_dashboard(args):
    from jake_brain.goals import GoalStore
    store = GoalStore()
    dash = store.dashboard(project=args.project)
    print(f"\n📊 GOAL DASHBOARD")
    print(f"{'='*40}")
    print(f"  Active:    {dash['active']}")
    print(f"  Completed: {dash['completed']}")
    print(f"  Overdue:   {dash['overdue']}")
    print(f"  Behind:    {dash['behind_schedule']}")
    print(f"  Total:     {dash['total']}")
    if dash["overdue_goals"]:
        print(f"\n⚠️  OVERDUE:")
        for g in dash["overdue_goals"]:
            print(f"  - {g['title']} (due {g['deadline'][:10]})")
    if dash["behind_goals"]:
        print(f"\n🔴 BEHIND SCHEDULE:")
        for g in dash["behind_goals"]:
            pct = (g.get("current_value", 0) / g["target_value"]) * 100 if g.get("target_value") else 0
            print(f"  - {g['title']} ({pct:.0f}% done, due {g['deadline'][:10]})")


def cmd_search(args):
    from jake_brain.goals import GoalStore
    store = GoalStore()
    results = store.search_goals(args.query, status=args.status or "active")
    if not results:
        print("No goals match that query.")
        return
    print(f"\n🔍 Search: '{args.query}' — {len(results)} results")
    for r in results:
        print(f"  [{r.get('similarity', 0):.3f}] {r['title']} ({r['status']})")


def cmd_milestone(args):
    from jake_brain.goals import GoalStore
    store = GoalStore()
    milestone = store.create_goal(
        title=args.title,
        goal_type="milestone",
        parent_id=args.goal_id,
        deadline=args.deadline,
        project=args.project,
    )
    print(f"✅ Milestone created: {milestone['id']} → parent {args.goal_id}")


def cmd_complete(args):
    from jake_brain.goals import GoalStore
    store = GoalStore()
    goal = store.complete_goal(args.goal_id)
    print(f"✅ Goal completed: {goal.get('title', args.goal_id)}")


def cmd_smoke(args):
    """End-to-end smoke test."""
    from jake_brain.goals import GoalStore
    store = GoalStore()
    print("🧪 SMOKE TEST — Goal Tracking")
    print("="*40)

    # Create
    goal = store.create_goal(
        title="[SMOKE TEST] Ship TransformFit MVP",
        description="Build and launch the fitness coaching AI platform",
        project="transformfit",
        priority="P1",
        target_value=10,
        unit="beta coaches",
        deadline=(datetime.now(timezone.utc) + timedelta(days=90)).isoformat(),
        tags=["smoke-test"],
    )
    print(f"  1. Create goal: {'✅' if goal.get('id') else '❌'} — {goal.get('id', 'FAILED')}")

    # Milestone
    ms = store.create_goal(
        title="[SMOKE TEST] Complete onboarding flow",
        goal_type="milestone",
        parent_id=goal["id"],
        project="transformfit",
        deadline=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    )
    print(f"  2. Add milestone: {'✅' if ms.get('id') else '❌'}")

    # Check-in
    ci = store.add_checkin(goal["id"], "Added 3 beta coaches from NASM network", new_value=3, source="cli")
    print(f"  3. Check-in: {'✅' if ci.get('id') else '❌'} — value 0→3")

    # Search
    results = store.search_goals("fitness coaching platform")
    found = any(r["id"] == goal["id"] for r in results)
    print(f"  4. Search: {'✅' if found else '❌'} — found smoke test goal in results")

    # Dashboard
    dash = store.dashboard(project="transformfit")
    print(f"  5. Dashboard: {'✅' if dash['active'] > 0 else '❌'} — {dash['active']} active goals")

    # Get milestones
    milestones = store.get_milestones(goal["id"])
    print(f"  6. Milestones: {'✅' if len(milestones) > 0 else '❌'} — {len(milestones)} milestone(s)")

    # Complete
    completed = store.complete_goal(goal["id"])
    print(f"  7. Complete: {'✅' if completed.get('status') == 'completed' else '❌'}")

    # Cleanup
    store.supabase.table("jake_goal_checkins").delete().eq("goal_id", goal["id"]).execute()
    store.supabase.table("jake_goals").delete().eq("parent_id", goal["id"]).execute()
    store.supabase.table("jake_goals").delete().eq("id", goal["id"]).execute()
    print(f"  8. Cleanup: ✅")

    print(f"\n{'='*40}")
    print("SMOKE TEST COMPLETE")


def main():
    parser = argparse.ArgumentParser(description="Jake Goal Tracking CLI")
    sub = parser.add_subparsers(dest="command")

    # create
    p = sub.add_parser("create")
    p.add_argument("title")
    p.add_argument("--description", "-d")
    p.add_argument("--project", "-p")
    p.add_argument("--priority")
    p.add_argument("--target", type=float)
    p.add_argument("--unit")
    p.add_argument("--deadline")
    p.add_argument("--people")
    p.add_argument("--tags")

    # list
    p = sub.add_parser("list")
    p.add_argument("--status", "-s", default="active")
    p.add_argument("--project", "-p")

    # checkin
    p = sub.add_parser("checkin")
    p.add_argument("goal_id")
    p.add_argument("content")
    p.add_argument("--value", "-v", type=float)

    # dashboard
    p = sub.add_parser("dashboard")
    p.add_argument("--project", "-p")

    # search
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--status", "-s", default="active")

    # milestone
    p = sub.add_parser("milestone")
    p.add_argument("goal_id")
    p.add_argument("title")
    p.add_argument("--deadline")
    p.add_argument("--project", "-p")

    # complete
    p = sub.add_parser("complete")
    p.add_argument("goal_id")

    # smoke
    sub.add_parser("smoke")

    args = parser.parse_args()
    commands = {
        "create": cmd_create, "list": cmd_list, "checkin": cmd_checkin,
        "dashboard": cmd_dashboard, "search": cmd_search, "milestone": cmd_milestone,
        "complete": cmd_complete, "smoke": cmd_smoke,
    }
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

**Step 2: Run smoke test**

Run: `cd susan-team-architect/backend && source .venv/bin/activate && python scripts/jake_goals_cli.py smoke`

Expected: 8/8 checks pass, cleanup completes.

**Step 3: Commit**

```bash
git add scripts/jake_goals_cli.py
git commit -m "feat(brain): goal tracking CLI — create, list, checkin, dashboard, search, smoke test"
```

---

## Phase F2: SOP Capture Skill

### Task 4: Create jake-sop-capture Hermes Skill

**Files:**
- Create: `~/.hermes/skills/jake-sop-capture/SKILL.md`

**Step 1: Write the SOP capture skill**

This skill guides Jake through an interview to extract implicit expertise from Mike and store it as a structured procedural memory.

```markdown
---
name: SOP Capture
description: Interview-based expertise extraction — documents processes that live in Mike's head as structured SOPs stored in Jake's brain
trigger: capture sop|document process|how do I do|write down my process|capture this workflow
---

# SOP Capture — Jake's Expertise Extraction Interview

You are Jake in SOP Capture mode. Mike has a process in his head that needs to be documented.

## Interview Flow

### Phase 1: Scope (1-2 questions)
Ask Mike:
1. "What's the process called? Give me a name I can file this under."
2. "When do you use this? What triggers it?"

### Phase 2: Steps (3-5 questions)
Walk through the process step by step:
3. "Walk me through it from the beginning. What's the first thing you do?"
4. For each step Mike describes, ask: "What could go wrong here? What do you check for?"
5. "Any tools or systems you use during this? Links, apps, specific commands?"
6. "How do you know when it's done? What does success look like?"

### Phase 3: Edge Cases (1-2 questions)
7. "What's the exception case? When does this NOT apply?"
8. "Anything you wish someone had told you the first time you did this?"

### Phase 4: Structure & Store
After the interview, format the SOP as:

```
## SOP: [Process Name]

**Trigger**: When [trigger condition]
**Owner**: Mike Rodgers
**Last updated**: [today's date]
**Estimated time**: [X minutes]

### Prerequisites
- [tools, access, context needed]

### Steps
1. [Step with detail]
   - ⚠️ Watch for: [gotcha]
2. [Step]
3. [Step]

### Success Criteria
- [How to know it worked]

### Edge Cases
- [Exception and what to do]

### Notes
- [Wisdom from Phase 3]
```

Then store it:
1. Use `brain_search` tool to check if a similar SOP already exists
2. Store via brain pipeline as `jake_procedural` with `source_type='sop'`
3. Link to relevant entities via knowledge graph
4. Confirm: "SOP captured and stored. You can find it by searching '[process name]' in the brain."

## Personality
Stay in Jake mode — keep it conversational, not formal. "Aight, let's document this before you forget it. What are we calling this process?"
```

**Step 2: Verify skill loads**

Run: `ls -la ~/.hermes/skills/jake-sop-capture/SKILL.md` — confirm file exists and is readable.

**Step 3: Commit** (commit the plan doc update noting this was created)

```bash
git add docs/plans/2026-03-21-25x-deathstar-plan.md
git commit -m "feat(hermes): SOP capture skill — interview-based expertise extraction"
```

---

### Task 5: SOP Storage Script

**Files:**
- Create: `susan-team-architect/backend/scripts/brain_sop_store.py`

**Step 1: Write the SOP storage helper**

```python
#!/usr/bin/env python3
"""Store a structured SOP in Jake's Brain as procedural memory.

Usage:
  python brain_sop_store.py --title "Coach Outreach Process" --file sop.md
  python brain_sop_store.py --title "Morning Brief Review" --content "Step 1: ..."
  echo "SOP content" | python brain_sop_store.py --title "My Process" --stdin
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def store_sop(title: str, content: str, project: str | None = None, tags: list[str] | None = None) -> dict:
    """Store SOP as procedural memory + link to knowledge graph."""
    from jake_brain.pipeline import BrainPipeline

    pipeline = BrainPipeline()

    # Store as procedural memory
    result = pipeline.store.supabase.table("jake_procedural").insert({
        "content": content,
        "embedding": pipeline.store.embedder.embed_query(content),
        "pattern_type": "sop",
        "domain": project or "general",
        "trigger_context": title,
        "success_rate": 1.0,
        "source": "sop_capture",
        "source_type": "sop",
        "metadata": {"title": title, "tags": tags or [], "captured_at": datetime.now(timezone.utc).isoformat()},
    }).execute()

    stored = result.data[0] if result.data else {}
    print(f"✅ SOP stored: {stored.get('id', 'unknown')}")
    print(f"   Title: {title}")
    print(f"   Domain: {project or 'general'}")
    print(f"   Content length: {len(content)} chars")
    return stored


def main():
    parser = argparse.ArgumentParser(description="Store SOP in Jake's Brain")
    parser.add_argument("--title", "-t", required=True)
    parser.add_argument("--content", "-c")
    parser.add_argument("--file", "-f")
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--project", "-p")
    parser.add_argument("--tags", nargs="*")
    args = parser.parse_args()

    if args.file:
        content = Path(args.file).read_text()
    elif args.stdin:
        content = sys.stdin.read()
    elif args.content:
        content = args.content
    else:
        print("Error: provide --content, --file, or --stdin")
        sys.exit(1)

    store_sop(args.title, content, project=args.project, tags=args.tags)


if __name__ == "__main__":
    main()
```

**Step 2: Test**

Run: `cd susan-team-architect/backend && source .venv/bin/activate && python scripts/brain_sop_store.py --title "[SMOKE TEST] SOP Test" --content "Step 1: Do the thing. Step 2: Check the thing." --project test`

Expected: SOP stored with UUID printed.

**Step 3: Commit**

```bash
git add scripts/brain_sop_store.py
git commit -m "feat(brain): SOP storage script — stores structured SOPs as procedural memory"
```

---

## Phase F3: Memory Lake Expansion

### Task 6: Document Ingestion Script

**Files:**
- Create: `susan-team-architect/backend/scripts/brain_doc_ingest.py`

**Step 1: Write the document ingestion script**

This script ingests any document (PDF, Markdown, plain text) into Jake's brain as semantic memory with metadata.

```python
#!/usr/bin/env python3
"""Ingest documents (PDF, Markdown, text) into Jake's Brain.

Usage:
  python brain_doc_ingest.py /path/to/doc.md --project transformfit
  python brain_doc_ingest.py /path/to/spec.pdf --project oracle-health --tags "spec,architecture"
  python brain_doc_ingest.py /path/to/folder/ --project transformfit  # all files in folder
  python brain_doc_ingest.py --dry-run /path/to/doc.md
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".json", ".yaml", ".yml", ".csv"}
CHUNK_SIZE = 2000  # chars per chunk
CHUNK_OVERLAP = 200


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def read_file(path: Path) -> str:
    """Read file content, handling PDF specially."""
    if path.suffix == ".pdf":
        try:
            import subprocess
            result = subprocess.run(
                ["pdftotext", str(path), "-"],
                capture_output=True, text=True, timeout=30,
            )
            return result.stdout
        except Exception:
            return f"[PDF extraction failed for {path.name}]"
    return path.read_text(errors="replace")


def ingest_file(
    path: Path,
    project: str | None,
    tags: list[str],
    dry_run: bool,
) -> int:
    """Ingest a single file into jake_semantic."""
    from jake_brain.pipeline import BrainPipeline

    content = read_file(path)
    if not content.strip():
        print(f"  [SKIP] {path.name} — empty")
        return 0

    chunks = chunk_text(content)
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    if dry_run:
        print(f"  [DRY] {path.name} — {len(chunks)} chunks, {len(content)} chars")
        return len(chunks)

    pipeline = BrainPipeline()
    stored = 0
    for i, chunk in enumerate(chunks):
        try:
            pipeline.store.store_semantic(
                content=chunk,
                fact_type="document",
                domain=project or "general",
                confidence=0.9,
                source=str(path),
                source_type="document",
                metadata={
                    "filename": path.name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "content_hash": content_hash,
                    "tags": tags,
                    "ingested_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            stored += 1
        except Exception as e:
            print(f"  [FAIL] {path.name} chunk {i}: {e}")

    print(f"  [OK]  {path.name} — {stored}/{len(chunks)} chunks stored")
    return stored


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into Jake's Brain")
    parser.add_argument("path", help="File or directory to ingest")
    parser.add_argument("--project", "-p")
    parser.add_argument("--tags", "-t", default="", help="Comma-separated tags")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    path = Path(args.path)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    if path.is_file():
        files = [path]
    elif path.is_dir():
        files = sorted(f for f in path.rglob("*") if f.suffix in SUPPORTED_EXTENSIONS and f.is_file())
    else:
        print(f"Error: {path} not found")
        sys.exit(1)

    print(f"{'='*60}")
    print(f"Jake Brain — Document Ingestion")
    print(f"Files: {len(files)}  Project: {args.project or 'general'}  Tags: {tags}")
    print(f"{'='*60}")

    total = 0
    for f in files:
        total += ingest_file(f, args.project, tags, args.dry_run)

    print(f"\n{'='*60}")
    action = "Would ingest" if args.dry_run else "Ingested"
    print(f"{action} {total} chunks from {len(files)} file(s)")


if __name__ == "__main__":
    main()
```

**Step 2: Dry-run test**

Run: `cd susan-team-architect/backend && source .venv/bin/activate && python scripts/brain_doc_ingest.py --dry-run ~/Startup-Intelligence-OS/docs/plans/2026-03-21-25x-deathstar-design.md --project deathstar`

Expected: Shows chunk count and char count without storing.

**Step 3: Commit**

```bash
git add scripts/brain_doc_ingest.py
git commit -m "feat(brain): document ingestion script — PDF, markdown, text → semantic memory"
```

---

## Phase F4: Weekly Goal Check-in Cron

### Task 7: Weekly Goal Report Script + Cron

**Files:**
- Create: `susan-team-architect/backend/scripts/jake_goal_weekly.py`
- Create: `~/.hermes/scripts/jake_goal_weekly.sh`
- Create: `~/Library/LaunchAgents/com.jake.goal-weekly.plist`

**Step 1: Write the weekly goal report script**

```python
#!/usr/bin/env python3
"""Weekly goal progress report — sent to Mike via Telegram every Sunday.

Usage:
  python jake_goal_weekly.py          # send report
  python jake_goal_weekly.py --dry-run  # print without sending
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

env_file = Path.home() / ".hermes" / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def format_report(dashboard: dict) -> str:
    """Format goal dashboard into Telegram-friendly message."""
    now = datetime.now(timezone.utc)
    lines = [
        f"📊 *Weekly Goal Check-in* — {now.strftime('%B %d, %Y')}",
        "",
        f"Active: {dashboard['active']}  |  Completed: {dashboard['completed']}  |  Overdue: {dashboard['overdue']}",
        "",
    ]

    if dashboard["overdue_goals"]:
        lines.append("⚠️ *OVERDUE*:")
        for g in dashboard["overdue_goals"]:
            lines.append(f"  • {g['title']} (due {g['deadline'][:10]})")
        lines.append("")

    if dashboard["behind_goals"]:
        lines.append("🔴 *BEHIND SCHEDULE*:")
        for g in dashboard["behind_goals"]:
            pct = (g.get("current_value", 0) / g["target_value"]) * 100 if g.get("target_value") else 0
            lines.append(f"  • {g['title']} ({pct:.0f}%)")
        lines.append("")

    if dashboard["active_goals"]:
        lines.append("📋 *Active Goals*:")
        for g in dashboard["active_goals"][:10]:
            progress = ""
            if g.get("target_value") and g["target_value"] > 0:
                pct = (g.get("current_value", 0) / g["target_value"]) * 100
                progress = f" — {pct:.0f}%"
            deadline = f" (due {g['deadline'][:10]})" if g.get("deadline") else ""
            lines.append(f"  • [{g['priority']}] {g['title']}{progress}{deadline}")

    if not dashboard["active_goals"]:
        lines.append("_No active goals. Set some with: goal for [project]_")

    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    """Send message via Telegram Bot API."""
    import requests
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
        timeout=10,
    )
    return resp.ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from jake_brain.goals import GoalStore
    store = GoalStore()
    dashboard = store.dashboard()
    report = format_report(dashboard)

    if args.dry_run:
        print(report)
        return

    if dashboard["active"] == 0:
        print("No active goals — skipping report.")
        return

    if send_telegram(report):
        print(f"✅ Weekly goal report sent ({dashboard['active']} active goals)")
    else:
        print("❌ Failed to send weekly goal report")


if __name__ == "__main__":
    main()
```

**Step 2: Create shell wrapper**

```bash
#!/usr/bin/env bash
# jake_goal_weekly.sh — Weekly goal progress report
set -euo pipefail
SUSAN_BACKEND="$HOME/Startup-Intelligence-OS/susan-team-architect/backend"
VENV="$SUSAN_BACKEND/.venv/bin/python"
LOG="$HOME/.hermes/logs/goal_weekly.log"
echo "=== jake_goal_weekly.sh $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
"$VENV" "$SUSAN_BACKEND/scripts/jake_goal_weekly.py" >> "$LOG" 2>&1
echo "=== done ===" >> "$LOG"
```

**Step 3: Create launchd plist** (Sundays at 9:00 AM — after immune weekly report at 8:00 AM)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jake.goal-weekly</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/mikerodgers/.hermes/scripts/jake_goal_weekly.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/mikerodgers/.hermes/logs/goal_weekly.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/mikerodgers/.hermes/logs/goal_weekly.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HERMES_HOME</key>
        <string>/Users/mikerodgers/.hermes</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

**Step 4: Load cron and test**

Run:
```bash
chmod +x ~/.hermes/scripts/jake_goal_weekly.sh
launchctl load ~/Library/LaunchAgents/com.jake.goal-weekly.plist
cd susan-team-architect/backend && source .venv/bin/activate && python scripts/jake_goal_weekly.py --dry-run
```

**Step 5: Commit**

```bash
git add scripts/jake_goal_weekly.py
git commit -m "feat(brain): weekly goal check-in cron — Telegram report every Sunday 9 AM"
```

---

## Phase F5: Hermes Plugin Integration

### Task 8: Add Goal + SOP + Doc Tools to Hermes Plugin

**Files:**
- Modify: `~/.hermes/plugins/jake-brain-ingest/__init__.py`
- Modify: `~/.hermes/plugins/jake-brain-ingest/plugin.yaml`

**Step 1: Add 5 new tools to the Hermes plugin**

Add these tools to the existing plugin (currently v8.0.0 with 25 tools):

| Tool | Action | Purpose |
|------|--------|---------|
| `goal_create` | Create a new goal/milestone/KPI | "Set a goal for TransformFit" |
| `goal_list` | List goals by status/project | "What are my active goals?" |
| `goal_checkin` | Log progress update | "I signed up 3 coaches" |
| `goal_dashboard` | Full progress overview | "What am I behind on?" |
| `sop_capture_store` | Store structured SOP | After SOP interview completes |

**Tool schemas** (add to existing `@tool` registrations in `__init__.py`):

```python
@tool(name="goal_create", description="Create a new goal, milestone, KPI, or OKR")
def goal_create(
    title: str,
    description: str = "",
    goal_type: str = "goal",
    project: str = None,
    priority: str = "P2",
    target_value: float = None,
    unit: str = None,
    deadline: str = None,
) -> str:
    from jake_brain.goals import GoalStore
    store = GoalStore()
    goal = store.create_goal(
        title=title, description=description, goal_type=goal_type,
        project=project, priority=priority, target_value=target_value,
        unit=unit, deadline=deadline,
    )
    return json.dumps({"status": "created", "id": goal.get("id"), "title": title})


@tool(name="goal_list", description="List goals filtered by status and project")
def goal_list(status: str = "active", project: str = None) -> str:
    from jake_brain.goals import GoalStore
    store = GoalStore()
    goals = store.list_goals(status=status, project=project)
    return json.dumps([{"id": g["id"], "title": g["title"], "priority": g["priority"],
                        "progress": f"{(g.get('current_value',0)/g['target_value']*100):.0f}%" if g.get("target_value") else "—",
                        "deadline": g.get("deadline","")[:10] if g.get("deadline") else "—"} for g in goals])


@tool(name="goal_checkin", description="Log a progress check-in against a goal")
def goal_checkin(goal_id: str, content: str, new_value: float = None) -> str:
    from jake_brain.goals import GoalStore
    store = GoalStore()
    ci = store.add_checkin(goal_id, content, new_value=new_value, source="hermes")
    return json.dumps({"status": "logged", "checkin_id": ci.get("id"), "delta": ci.get("delta")})


@tool(name="goal_dashboard", description="Get goal tracking dashboard — active, overdue, behind schedule")
def goal_dashboard(project: str = None) -> str:
    from jake_brain.goals import GoalStore
    store = GoalStore()
    dash = store.dashboard(project=project)
    return json.dumps({
        "active": dash["active"], "completed": dash["completed"],
        "overdue": dash["overdue"], "behind_schedule": dash["behind_schedule"],
        "overdue_goals": [{"title": g["title"], "deadline": g.get("deadline","")[:10]} for g in dash["overdue_goals"]],
        "behind_goals": [{"title": g["title"]} for g in dash["behind_goals"]],
    })


@tool(name="sop_capture_store", description="Store a captured SOP as procedural memory in Jake's brain")
def sop_capture_store(title: str, content: str, project: str = None, tags: list = None) -> str:
    sys.path.insert(0, str(Path.home() / "Startup-Intelligence-OS/susan-team-architect/backend"))
    from scripts.brain_sop_store import store_sop
    result = store_sop(title, content, project=project, tags=tags)
    return json.dumps({"status": "stored", "id": result.get("id"), "title": title})
```

**Step 2: Bump plugin version**

Update `plugin.yaml` version to `v9.0.0` and tool count to 30.

**Step 3: Verify plugin loads**

Restart Hermes or trigger a reload. Verify the new tools appear.

**Step 4: Commit**

```bash
git commit -m "feat(hermes): v9.0.0 — goal tracking + SOP capture tools (30 total)"
```

---

## Phase F6: Validation & 100/100 Audit

### Task 9: End-to-End Validation

**Step 1: Run goal smoke test**

Run: `python scripts/jake_goals_cli.py smoke`
Expected: 8/8 pass

**Step 2: Create Mike's first real goals**

Via CLI, create the initial goal set from the DeathStar design doc:

```bash
python scripts/jake_goals_cli.py create "Ship TransformFit MVP" \
  --project transformfit --priority P1 --target 10 --unit "beta coaches" \
  --deadline 2026-06-21 -d "Build and launch fitness coaching AI with 10 beta coaches"

python scripts/jake_goals_cli.py create "Jake 100/100 Score" \
  --project startup-intelligence-os --priority P1 --target 100 --unit "score" \
  --deadline 2026-04-21 -d "Complete all 25X Foundation capabilities"

python scripts/jake_goals_cli.py create "OpenClaw PAI Plugin MVP" \
  --project startup-intelligence-os --priority P2 --target 1 --unit "external user" \
  --deadline 2026-05-21 -d "First external user on Jake PAI platform"

python scripts/jake_goals_cli.py create "Weekly Goal Check-ins Active" \
  --project startup-intelligence-os --priority P1 --target 4 --unit "weeks" \
  --deadline 2026-04-21 -d "4 consecutive weeks of Telegram goal reports"
```

**Step 3: Run weekly report dry-run**

Run: `python scripts/jake_goal_weekly.py --dry-run`
Expected: Formatted report showing all 4 goals

**Step 4: Test SOP capture**

Run: `python scripts/brain_sop_store.py --title "Morning Brief Review" --content "Step 1: Open Telegram. Step 2: Read Jake's morning brief. Step 3: Reply with priorities. Step 4: Jake adjusts the day's plan." --project startup-intelligence-os`

**Step 5: Test document ingestion**

Run: `python scripts/brain_doc_ingest.py docs/plans/2026-03-21-25x-deathstar-design.md --project deathstar --tags "design,approved" --dry-run`

**Step 6: Verify brain search finds goals**

Run: `python scripts/jake_goals_cli.py search "fitness coaching"`
Expected: TransformFit goal appears in results

**Step 7: Update 9-phase doc**

Add Foundation phase status to the architecture doc.

**Step 8: Commit everything**

```bash
git add -A
git commit -m "feat(25x): Foundation Phase F1-F6 complete — goal tracking, SOP capture, memory lake"
```

---

## Success Criteria (Foundation complete when all pass)

| # | Criterion | Validation Command |
|---|-----------|-------------------|
| 1 | Jake tracks 5+ active goals with weekly Telegram check-ins | `python scripts/jake_goals_cli.py list` → 5+ goals |
| 2 | SOP capture works: describe process → stored in <5 min | `python scripts/brain_sop_store.py --title "Test" --content "..."` |
| 3 | Memory lake: any doc ingested and searchable in <60 seconds | `python scripts/brain_doc_ingest.py <file> && python scripts/jake_brain_cli.py search "keyword"` |
| 4 | Jake answers "what am I behind on?" correctly | `python scripts/jake_goals_cli.py dashboard` → behind_schedule list |
| 5 | Weekly goal report sends to Telegram | `python scripts/jake_goal_weekly.py` → Telegram message |
| 6 | Goal smoke test passes end-to-end | `python scripts/jake_goals_cli.py smoke` → 8/8 pass |

---

## What Comes After Foundation

Per the DeathStar design doc timeline:

| Next Phase | When | What |
|-----------|------|------|
| **Walls Phase 1** (60-90 days) | After Foundation validated | AI Dev Studio skill + AI Social Media Studio skill |
| **Roof Seeding** (60-90 days) | Parallel with Walls | TransformFit v0.1 with 3 beta coaches |
| **OpenClaw PAI** (30-60 days) | After Foundation | Plugin config for multi-user support |

The Foundation is the base everything else builds on. Get goals tracking, SOPs capturing, and docs ingesting — then the studios and verticals have infrastructure to stand on.
