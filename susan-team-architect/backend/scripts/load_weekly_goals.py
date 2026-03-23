#!/usr/bin/env python3
"""Load Mike's weekly goals (March 23-28, 2026) into jake_goals and jake_tasks."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from supabase import create_client
from susan_core.config import config as susan_config
from rag_engine.embedder import Embedder

client = create_client(susan_config.supabase_url, susan_config.supabase_key)
embedder = Embedder()


def embed(text: str) -> list[float]:
    return embedder.embed_query(text)


def create_goal(title, description, priority, deadline, project, tags=None):
    row = {
        "title": title,
        "description": description,
        "goal_type": "goal",
        "project": project,
        "priority": priority,
        "status": "active",
        "current_value": 0,
        "people": ["mike"],
        "tags": tags or [],
        "metadata": {"week": "2026-03-23"},
        "deadline": deadline,
        "embedding": embed(f"{title} — {description}"),
    }
    result = client.table("jake_goals").insert(row).execute()
    goal = result.data[0]
    print(f"  ✓ Goal: {goal['id']} — {title}")
    return goal["id"]


def create_task(goal_id, task_text, order_index, priority, due_date, assigned_to="auto"):
    row = {
        "goal_id": goal_id,
        "task_text": task_text,
        "status": "pending",
        "assigned_to": assigned_to,
        "priority": priority,
        "order_index": order_index,
        "attempt_count": 0,
        "max_attempts": 3,
        "due_date": due_date,
        "embedding": embed(task_text),
    }
    result = client.table("jake_tasks").insert(row).execute()
    task = result.data[0]
    print(f"    · Task {order_index}: {task_text[:60]}")
    return task["id"]


def main():
    print("\n=== Loading Weekly Goals — Week of March 23-28, 2026 ===\n")

    # ------------------------------------------------------------------ #
    # GOAL 1: Jake 24/7 Operational — P0, deadline EOW
    # ------------------------------------------------------------------ #
    print("GOAL 1: Jake 24/7 Operational")
    g1 = create_goal(
        title="Jake 24/7 Operational — Telegram + Dispatch",
        description="Wire Telegram to Claude Code dispatch pipeline, set daily cadence crons, and achieve zero-error baseline for Jake's continuous operation.",
        priority="P0",
        deadline="2026-03-28T23:59:00Z",
        project="startup-intelligence-os",
        tags=["jake", "telegram", "dispatch", "crons", "ops"],
    )
    for i, (text, executor) in enumerate([
        ("Wire Telegram → Claude Code Dispatch pipeline", "claude_code"),
        ("Test 50% context handoff protocol", "claude_code"),
        ("Set up 7AM/12PM/6PM daily cadence crons", "cron"),
        ("Test meeting prep on real calendar events", "hermes"),
        ("Zero errors target — monitor and fix", "auto"),
    ], 1):
        create_task(g1, text, i, "P0", "2026-03-28T23:59:00Z", executor)

    # ------------------------------------------------------------------ #
    # GOAL 2: TransformFit Alpha Live — P0, deadline Wednesday
    # ------------------------------------------------------------------ #
    print("\nGOAL 2: TransformFit Alpha Live by Wednesday")
    g2 = create_goal(
        title="TransformFit Alpha Live by Wednesday",
        description="Build and deploy 6-coach TransformFit app, website, and onboarding. Run alpha outreach to local targets.",
        priority="P0",
        deadline="2026-03-26T23:59:00Z",
        project="transformfit",
        tags=["transformfit", "alpha", "build", "deploy", "outreach"],
    )
    tasks_g2 = [
        ("Design sessions with Michael today — coach UX in Stitch/Figma", "2026-03-23T23:59:00Z", "manual"),
        ("Tonight: build + test + deploy coach screens (Pulse, Iron + 4 others)", "2026-03-23T23:59:00Z", "claude_code"),
        ("Tomorrow AM: deploy for Michael's review", "2026-03-24T12:00:00Z", "claude_code"),
        ("Wednesday: full app live with all 6 coaches, website, onboarding", "2026-03-26T23:59:00Z", "claude_code"),
        ("Scrape local alpha targets for DM outreach", "2026-03-26T23:59:00Z", "script"),
        ("Create full alpha outreach recipe (DM scripts, content, sign-on flow)", "2026-03-26T23:59:00Z", "manual"),
    ]
    for i, (text, due, executor) in enumerate(tasks_g2, 1):
        create_task(g2, text, i, "P0", due, executor)

    # ------------------------------------------------------------------ #
    # GOAL 3: Viral Architect Production Studio — P1, deadline EOW
    # ------------------------------------------------------------------ #
    print("\nGOAL 3: Viral Architect Production Studio")
    g3 = create_goal(
        title="Viral Architect Production Studio",
        description="Review Sema Studio 2.5, build production studio indoor app in Coworker, integrate film workflow.",
        priority="P1",
        deadline="2026-03-28T23:59:00Z",
        project="viral-architect",
        tags=["viral-architect", "studio", "film", "production"],
    )
    for i, text in enumerate([
        "Review Sema Studio 2.5 file",
        "Build production studio indoor app in Coworker",
        "Integrate film workflow",
    ], 1):
        create_task(g3, text, i, "P1", "2026-03-28T23:59:00Z", "manual")

    # ------------------------------------------------------------------ #
    # GOAL 4: Alex Recruiting App Done by Tomorrow — P1, deadline Monday
    # ------------------------------------------------------------------ #
    print("\nGOAL 4: Alex Recruiting App Done by Tomorrow")
    g4 = create_goal(
        title="Alex Recruiting App Done by Tomorrow",
        description="Ship PWA build, text Jacob + Jennifer with link, scrape D3 coaches, execute DM wave 1, add more coach waves.",
        priority="P1",
        deadline="2026-03-24T23:59:00Z",
        project="alex-recruiting",
        tags=["alex-recruiting", "pwa", "outreach", "coaches"],
    )
    tasks_g4 = [
        ("PWA build + test + deploy", "2026-03-24T12:00:00Z", "claude_code"),
        ("Text Jacob + Jennifer Rogers with link", "2026-03-24T14:00:00Z", "manual"),
        ("Scrape 3 additional states D3 coaches", "2026-03-24T23:59:00Z", "script"),
        ("Execute DM wave 1 on X", "2026-03-24T23:59:00Z", "manual"),
        ("Add 3 more coach waves to pipeline", "2026-03-24T23:59:00Z", "script"),
    ]
    for i, (text, due, executor) in enumerate(tasks_g4, 1):
        create_task(g4, text, i, "P1", due, executor)

    # ------------------------------------------------------------------ #
    # GOAL 5: Oracle Health Domain Recipes — P3, deadline EOW
    # ------------------------------------------------------------------ #
    print("\nGOAL 5: Oracle Health Domain Recipes")
    g5 = create_goal(
        title="Oracle Health Domain Recipes",
        description="Create UPDATE_DOMAIN_{name} recipe template and set up 6 domain recipes with recurring triggers.",
        priority="P3",
        deadline="2026-03-28T23:59:00Z",
        project="oracle-health",
        tags=["oracle-health", "recipes", "automation", "domains"],
    )
    for i, text in enumerate([
        "Create UPDATE_DOMAIN_{name} recipe template",
        "Set up 6 domain recipes (Payer, Life Sciences, Health Systems, Interop, RCM, ERP)",
        "Set recurring 2-week trigger for domain recipe runs",
    ], 1):
        create_task(g5, text, i, "P3", "2026-03-28T23:59:00Z", "auto")

    print(f"\n=== Done. 5 goals + 22 tasks loaded. ===\n")


if __name__ == "__main__":
    main()
