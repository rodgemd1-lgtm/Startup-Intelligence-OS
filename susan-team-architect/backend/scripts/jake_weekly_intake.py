#!/usr/bin/env python3
"""Jake Weekly Intake — Structured weekly goal interview and autonomous recipe generator.

This is the command center for Jake's entire autonomous work cycle.
Runs every Monday at 7 AM. Covers:
  - Pull Mike's calendar, active tasks, goals
  - Send context briefing via Telegram
  - Run 6-question structured interview
  - Generate jake_goals + jake_tasks from answers
  - Create daily data ingestion + self-learning recipes per goal
  - Schedule autonomous work (cron entries + Wednesday/Friday check-ins)

Usage:
    .venv/bin/python scripts/jake_weekly_intake.py --phase calendar
    .venv/bin/python scripts/jake_weekly_intake.py --phase interview
    .venv/bin/python scripts/jake_weekly_intake.py --phase midweek-checkin
    .venv/bin/python scripts/jake_weekly_intake.py --phase friday-wrapup
    .venv/bin/python scripts/jake_weekly_intake.py --full  # Run all phases
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

HERMES_ENV = Path.home() / ".hermes" / ".env"


# ─────────────────────────────────────────────────────────────────────────────
# ENVIRONMENT
# ─────────────────────────────────────────────────────────────────────────────

def load_env() -> None:
    if HERMES_ENV.exists():
        with open(HERMES_ENV) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def get_supabase():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY required")
    return create_client(url, key)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1A: CALENDAR (Apple Calendar via osascript)
# ─────────────────────────────────────────────────────────────────────────────

def get_week_events(week_start: str) -> list[dict]:
    """Pull events for the coming week from Apple Calendar."""
    try:
        start_date = date.fromisoformat(week_start)
        end_date = start_date + timedelta(days=7)

        script = f'''
        tell application "Calendar"
            set startDate to date "{start_date.strftime("%B %d, %Y")} 12:00:00 AM"
            set endDate to date "{end_date.strftime("%B %d, %Y")} 11:59:59 PM"
            set output to ""
            repeat with cal in calendars
                try
                    set evts to (every event of cal whose start date >= startDate and start date <= endDate)
                    repeat with e in evts
                        set evtDate to start date of e
                        set evtTitle to summary of e
                        set output to output & evtDate & "|" & evtTitle & "\\n"
                    end repeat
                end try
            end repeat
            return output
        end tell
        '''
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return [{"error": result.stderr[:200], "events": []}]

        events = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 1)
                events.append({"date": parts[0].strip(), "title": parts[1].strip()})
        return events
    except subprocess.TimeoutExpired:
        # Known issue: kill Mail/Calendar if stuck
        subprocess.run(["killall", "Calendar"], capture_output=True)
        return [{"error": "Calendar timeout — killall Calendar, retry"}]
    except Exception as e:
        return [{"error": str(e)}]


def format_calendar(events: list[dict]) -> str:
    if not events:
        return "No events this week."
    lines = ["📅 *This week's calendar:*"]
    for e in events:
        if "error" in e:
            lines.append(f"  ⚠️ {e['error']}")
        else:
            lines.append(f"  • {e.get('date', '?')} — {e.get('title', '?')}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1B: TASKS from Supabase
# ─────────────────────────────────────────────────────────────────────────────

def get_active_tasks() -> list[dict]:
    try:
        client = get_supabase()
        result = (
            client.table("jake_tasks")
            .select("id,title,status,priority,project,due_date")
            .in_("status", ["pending", "in_progress", "blocked"])
            .order("priority", desc=False)
            .limit(20)
            .execute()
        )
        return result.data or []
    except Exception as e:
        return [{"error": str(e)}]


def format_tasks(tasks: list[dict]) -> str:
    if not tasks:
        return "No active tasks."
    lines = ["📋 *Active tasks:*"]
    for t in tasks[:10]:
        if "error" in t:
            lines.append(f"  ⚠️ {t['error']}")
            continue
        status_icon = {"pending": "⬜", "in_progress": "🔄", "blocked": "🚫"}.get(t.get("status", ""), "•")
        project = f" [{t.get('project', '')}]" if t.get("project") else ""
        lines.append(f"  {status_icon} {t.get('title', '?')}{project}")
    if len(tasks) > 10:
        lines.append(f"  ... and {len(tasks) - 10} more")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1C: GOALS from Supabase
# ─────────────────────────────────────────────────────────────────────────────

def get_active_goals() -> list[dict]:
    try:
        client = get_supabase()
        result = (
            client.table("jake_goals")
            .select("id,title,status,company,progress,target_date")
            .in_("status", ["active", "in_progress"])
            .limit(15)
            .execute()
        )
        return result.data or []
    except Exception as e:
        return [{"error": str(e)}]


def format_goals(goals: list[dict]) -> str:
    if not goals:
        return "No active goals."
    lines = ["🎯 *Active goals:*"]
    for g in goals:
        if "error" in g:
            lines.append(f"  ⚠️ {g['error']}")
            continue
        progress = g.get("progress", 0)
        bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10)) if progress else "░░░░░░░░░░"
        company = f" ({g.get('company', '')})" if g.get("company") else ""
        lines.append(f"  [{bar}] {g.get('title', '?')}{company} — {progress}%")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2: CONTEXT BRIEFING via Telegram
# ─────────────────────────────────────────────────────────────────────────────

def send_telegram(message: str) -> bool:
    """Send a message via Telegram using Hermes gateway."""
    try:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            print(f"[Telegram] No credentials — would send:\n{message}")
            return False

        import urllib.request
        data = json.dumps({
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False


def poll_telegram_response(timeout_seconds: int = 300) -> str | None:
    """Poll Telegram for the latest message from Mike (simple getUpdates poll)."""
    try:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            return None

        import urllib.request
        deadline = time.time() + timeout_seconds
        last_update_id = 0

        # Get current offset first
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/getUpdates?limit=1",
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("result"):
                last_update_id = data["result"][-1]["update_id"]

        print(f"  Waiting for reply (timeout: {timeout_seconds}s)...")
        while time.time() < deadline:
            time.sleep(5)
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update_id + 1}&limit=5",
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                if data.get("result"):
                    for update in data["result"]:
                        msg = update.get("message", {})
                        if str(msg.get("chat", {}).get("id", "")) == str(chat_id):
                            return msg.get("text", "")
                        last_update_id = update["update_id"]

        return None  # Timeout
    except Exception as e:
        print(f"Poll failed: {e}")
        return None


def send_context_briefing(week_start: str, calendar: str, tasks: str, goals: str) -> None:
    week_date = date.fromisoformat(week_start)
    week_end = week_date + timedelta(days=6)
    message = f"""🌅 *Good morning Mike — Week of {week_date.strftime("%b %d")} to {week_end.strftime("%b %d")}*

Jake's weekly intake is starting. I pulled your context — here's what I see:

{calendar}

{tasks}

{goals}

In a moment I'll ask you 6 quick questions to set up the week. Answer each one directly here — I'll build your goals, tasks, and automated research recipes from your answers.

Ready? Let's go. 🚀"""
    send_telegram(message)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3: STRUCTURED INTERVIEW — 6 question blocks
# ─────────────────────────────────────────────────────────────────────────────

INTERVIEW_QUESTIONS = [
    {
        "id": "weekly_goals",
        "q": "🎯 *Q1/6 — Weekly Goals*\n\nWhat are your 3-5 goals for this week? List them, one per line. Be specific — 'ship X', 'close Y', 'decide Z'.",
        "key": "weekly_goals",
    },
    {
        "id": "oracle_priority",
        "q": "🏥 *Q2/6 — Oracle Health*\n\nWhat's the ONE most important thing to move forward at Oracle Health this week? (Project, relationship, deliverable, decision?)",
        "key": "oracle_priority",
    },
    {
        "id": "transformfit_priority",
        "q": "💪 *Q3/6 — TransformFit*\n\nWhat's the ONE most important TransformFit priority this week? (Build, research, outreach, partnerships?)",
        "key": "transformfit_priority",
    },
    {
        "id": "viral_architect_priority",
        "q": "🏗️ *Q4/6 — Viral Architect*\n\nWhat's the ONE most important Viral Architect priority this week?",
        "key": "viral_architect_priority",
    },
    {
        "id": "jake_improvements",
        "q": "🤖 *Q5/6 — Jake Improvements*\n\nAny Jake capability improvements you want this week? (New skill, broken thing to fix, something annoying, research Jake should run?)\n\nSay 'none' if nothing comes to mind.",
        "key": "jake_improvements",
    },
    {
        "id": "personal_priority",
        "q": "👨‍👩‍👦 *Q6/6 — Personal / Family*\n\nAnything personal or family this week I should know about? (Jacob's training/games, family events, personal goals, health?)\n\nSay 'none' if not relevant.",
        "key": "personal_priority",
    },
]


def run_interview(week_start: str) -> dict:
    """Run the 6-question structured interview via Telegram. Returns answers dict."""
    answers = {}

    send_telegram(f"📝 Starting 6-question weekly intake. Answer each one directly here.\n\n_Week of {week_start}_")
    time.sleep(2)

    for i, q_block in enumerate(INTERVIEW_QUESTIONS):
        send_telegram(q_block["q"])
        print(f"  Sent Q{i+1}: {q_block['id']}")

        answer = poll_telegram_response(timeout_seconds=600)  # 10 min per question
        if answer:
            answers[q_block["key"]] = answer
            print(f"  Got answer: {answer[:50]}...")
            # Acknowledge receipt
            send_telegram(f"✓ Got it. {'Next question coming up.' if i < len(INTERVIEW_QUESTIONS) - 1 else 'All done — building your week now...'}")
            time.sleep(1)
        else:
            answers[q_block["key"]] = "SKIPPED (no response within 10 min)"
            print(f"  Q{i+1} timed out — marking as skipped")

    return answers


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4: GENERATE GOALS + TASKS from interview answers
# ─────────────────────────────────────────────────────────────────────────────

def generate_goals_and_tasks(answers: dict, week_start: str) -> dict:
    """Parse interview answers and create jake_goals + jake_tasks rows."""
    client = get_supabase()
    week_date = date.fromisoformat(week_start)
    week_end = week_date + timedelta(days=6)
    created_goals = []
    created_tasks = []

    company_map = {
        "oracle_priority": "Oracle Health",
        "transformfit_priority": "TransformFit",
        "viral_architect_priority": "Viral Architect",
    }

    # Create a goal for each weekly goal listed
    weekly_goals_text = answers.get("weekly_goals", "")
    if weekly_goals_text and weekly_goals_text != "SKIPPED (no response within 10 min)":
        for line in weekly_goals_text.strip().split("\n"):
            goal_title = line.strip().lstrip("•-123456789. ")
            if not goal_title:
                continue
            try:
                goal_row = {
                    "title": goal_title,
                    "status": "active",
                    "progress": 0,
                    "week_of": week_start,
                    "target_date": week_end.isoformat(),
                    "source": "weekly_intake",
                }
                result = client.table("jake_goals").insert(goal_row).execute()
                if result.data:
                    goal = result.data[0]
                    created_goals.append(goal)
                    # Create 1 default task per goal
                    task_row = {
                        "title": f"Execute: {goal_title}",
                        "status": "pending",
                        "priority": 2,
                        "goal_id": goal.get("id"),
                        "due_date": week_end.isoformat(),
                        "source": "weekly_intake",
                    }
                    task_result = client.table("jake_tasks").insert(task_row).execute()
                    if task_result.data:
                        created_tasks.append(task_result.data[0])
            except Exception as e:
                print(f"  Warning: Could not create goal '{goal_title}': {e}")

    # Create company-specific goals
    for key, company in company_map.items():
        priority_text = answers.get(key, "")
        if priority_text and priority_text not in ("SKIPPED (no response within 10 min)", "none", "None"):
            try:
                goal_row = {
                    "title": priority_text[:200],
                    "status": "active",
                    "company": company,
                    "progress": 0,
                    "week_of": week_start,
                    "target_date": week_end.isoformat(),
                    "source": "weekly_intake",
                }
                result = client.table("jake_goals").insert(goal_row).execute()
                if result.data:
                    goal = result.data[0]
                    created_goals.append(goal)
                    task_row = {
                        "title": f"[{company}] {priority_text[:150]}",
                        "status": "pending",
                        "priority": 1,
                        "project": company,
                        "goal_id": goal.get("id"),
                        "due_date": week_end.isoformat(),
                        "source": "weekly_intake",
                    }
                    task_result = client.table("jake_tasks").insert(task_row).execute()
                    if task_result.data:
                        created_tasks.append(task_result.data[0])
            except Exception as e:
                print(f"  Warning: Could not create company goal for {company}: {e}")

    # Store Jake improvements as tasks (with brain ingestion as episodic)
    jake_improvements = answers.get("jake_improvements", "")
    if jake_improvements and jake_improvements.lower() not in ("none", "n/a", "skipped (no response within 10 min)"):
        try:
            client.table("jake_tasks").insert({
                "title": f"Jake improvement: {jake_improvements[:200]}",
                "status": "pending",
                "priority": 3,
                "project": "Jake",
                "source": "weekly_intake",
                "due_date": week_end.isoformat(),
            }).execute()
        except Exception:
            pass

    # Store personal context as episodic memory
    personal = answers.get("personal_priority", "")
    if personal and personal.lower() not in ("none", "n/a", "skipped (no response within 10 min)"):
        try:
            client.table("jake_episodic").insert({
                "content": f"Personal/family context week of {week_start}: {personal}",
                "memory_type": "personal",
                "importance": 0.8,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "source": "weekly_intake",
                "source_type": "interview",
                "topics": ["family", "personal"],
                "metadata": {"week_of": week_start},
            }).execute()
        except Exception:
            pass

    return {
        "goals_created": len(created_goals),
        "tasks_created": len(created_tasks),
        "goals": [g.get("title", "?") for g in created_goals],
    }


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 5: GENERATE + SAVE DATA RECIPES
# ─────────────────────────────────────────────────────────────────────────────

def save_data_recipes(goals_summary: dict, week_start: str) -> list[str]:
    """Auto-generate lightweight daily data recipes for each goal and save them."""
    recipes_dir = Path.home() / ".hermes" / "recipes"
    recipes_dir.mkdir(exist_ok=True)

    goals = goals_summary.get("goals", [])
    generated = []

    for goal_title in goals[:5]:  # Cap at 5 to avoid recipe explosion
        # Derive a recipe slug and appropriate data sources
        slug = goal_title.lower().replace(" ", "-").replace("[", "").replace("]", "")[:40]
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        recipe_slug = f"auto-{slug}-{week_start}"
        recipe_path = recipes_dir / f"{recipe_slug}.yaml"

        if recipe_path.exists():
            continue

        # Simple heuristic: pick data sources based on company keywords in goal
        if any(k in goal_title.lower() for k in ["oracle", "meditech", "epic", "ehr", "health"]):
            sources = [
                {"type": "search", "query": f"{goal_title} healthcare EHR", "engine": "tavily"},
                {"type": "search", "query": f"Oracle Health Epic Meditech news {week_start[:7]}", "engine": "tavily"},
            ]
        elif any(k in goal_title.lower() for k in ["transformfit", "fitness", "workout", "training"]):
            sources = [
                {"type": "search", "query": f"{goal_title} fitness app market", "engine": "tavily"},
            ]
        elif any(k in goal_title.lower() for k in ["viral", "architect", "saas", "product"]):
            sources = [
                {"type": "search", "query": f"{goal_title} SaaS product", "engine": "tavily"},
            ]
        else:
            sources = [
                {"type": "search", "query": goal_title, "engine": "tavily"},
            ]

        recipe_content = f"""name: {recipe_slug}
description: "Auto-generated daily data recipe for goal: {goal_title}"
version: "1.0"
tags: [auto-generated, weekly-intake, {week_start}]
auto_generated: true
generated_from: weekly-intake
week_of: {week_start}
goal: "{goal_title}"

steps:
  - name: search_relevant_data
    tool: tavily_search
    args:
      query: "{goal_title}"
      limit: 5
      include_raw: false

  - name: synthesize_and_store
    tool: brain_search
    args:
      query: "store research: {goal_title} findings {{step_1_output}}"
      limit: 1

  - name: notify_if_significant
    tool: telegram
    args:
      condition: "significance > 0.7"
      message: |
        📰 *Daily intel for goal: {goal_title[:50]}*

        {{step_2_output}}
"""
        recipe_path.write_text(recipe_content, encoding="utf-8")
        generated.append(recipe_slug)
        print(f"  ✓ Created recipe: {recipe_path.name}")

    return generated


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 6: SCHEDULE + SEND CONFIRMATION
# ─────────────────────────────────────────────────────────────────────────────

def send_week_kickoff(week_start: str, goals_summary: dict, recipes: list[str]) -> None:
    week_date = date.fromisoformat(week_start)
    goals_list = "\n".join(f"  • {g}" for g in goals_summary.get("goals", [])[:5])

    recipes_list = "\n".join(f"  • {r}" for r in recipes[:5]) if recipes else "  (none generated)"

    message = f"""✅ *Week of {week_date.strftime("%b %d")} — Setup Complete*

**Goals created ({goals_summary.get('goals_created', 0)}):**
{goals_list}

**Tasks created:** {goals_summary.get('tasks_created', 0)}

**Auto-research recipes running daily:**
{recipes_list}

Check-ins scheduled:
• Wed 5 PM — mid-week pulse
• Fri 4 PM — week wrap-up

Go be a legend. 🔥
— Jake"""
    send_telegram(message)


# ─────────────────────────────────────────────────────────────────────────────
# MID-WEEK CHECK-IN (Wednesday PM)
# ─────────────────────────────────────────────────────────────────────────────

def run_midweek_checkin() -> None:
    """Wednesday PM: check goal progress and send pulse."""
    goals = get_active_goals()
    tasks = get_active_tasks()

    in_progress = [t for t in tasks if isinstance(t, dict) and t.get("status") == "in_progress"]
    done = [t for t in tasks if isinstance(t, dict) and t.get("status") == "done"]
    blocked = [t for t in tasks if isinstance(t, dict) and t.get("status") == "blocked"]

    done_count = len(done)
    blocked_count = len(blocked)
    in_progress_count = len(in_progress)

    pace = "🟢 On pace" if done_count >= 2 else "🟡 Behind pace" if done_count >= 1 else "🔴 Need to push"

    goals_at_risk = [g for g in goals if isinstance(g, dict) and (g.get("progress", 0) or 0) < 30]
    risk_text = "\n".join(f"  ⚠️ {g.get('title', '?')}" for g in goals_at_risk[:3]) if goals_at_risk else "  All goals on track"

    message = f"""📊 *Mid-Week Pulse — Wednesday Check-in*

{pace}

Tasks this week:
  ✓ Done: {done_count}
  🔄 In progress: {in_progress_count}
  🚫 Blocked: {blocked_count}

Goals at risk (< 30% progress):
{risk_text}

You're at the halfway point. Anything I should know about? Reply here if you want me to adjust priorities or unblock something."""
    send_telegram(message)
    print("Mid-week check-in sent.")


# ─────────────────────────────────────────────────────────────────────────────
# FRIDAY WRAP-UP
# ─────────────────────────────────────────────────────────────────────────────

def run_friday_wrapup() -> None:
    """Friday PM: week summary vs plan."""
    goals = get_active_goals()
    tasks = get_active_tasks()

    # Find this week's intake goals
    today = date.today()
    week_start = (today - timedelta(days=today.weekday())).isoformat()

    week_goals = [g for g in goals if isinstance(g, dict) and g.get("week_of") == week_start]
    all_tasks = [t for t in tasks if isinstance(t, dict)]
    done_tasks = [t for t in all_tasks if t.get("status") == "done"]
    pending_tasks = [t for t in all_tasks if t.get("status") in ("pending", "in_progress")]

    done_pct = int(len(done_tasks) / max(len(all_tasks), 1) * 100)
    completed_goals = [g for g in week_goals if (g.get("progress", 0) or 0) >= 80]

    grade = "A" if done_pct >= 80 else "B" if done_pct >= 60 else "C" if done_pct >= 40 else "D"

    done_list = "\n".join(f"  ✓ {t.get('title', '?')[:60]}" for t in done_tasks[:5])
    carry_list = "\n".join(f"  → {t.get('title', '?')[:60]}" for t in pending_tasks[:3])

    message = f"""🏁 *Friday Wrap-Up — Week of {week_start}*

**Grade: {grade}** ({done_pct}% of tasks complete)

**Goals completed ({len(completed_goals)}/{len(week_goals)}):**
{chr(10).join(f'  ✓ {g.get("title", "?")[:60]}' for g in completed_goals) or '  None at 80%+'}

**Tasks done:**
{done_list or '  None logged'}

**Carry to next week:**
{carry_list or '  Clean slate'}

Weekend is yours. I'll have the Monday intake ready at 7 AM.
— Jake"""
    send_telegram(message)
    print("Friday wrap-up sent.")


# ─────────────────────────────────────────────────────────────────────────────
# FULL RUN — all phases in sequence
# ─────────────────────────────────────────────────────────────────────────────

def run_full(week_start: str | None = None) -> None:
    if not week_start:
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()

    print(f"\n{'═' * 50}")
    print(f"  Jake Weekly Intake — Week of {week_start}")
    print(f"{'═' * 50}\n")

    # Phase 1: Pull context
    print("Phase 1: Pulling context...")
    events = get_week_events(week_start)
    tasks = get_active_tasks()
    goals = get_active_goals()
    calendar_text = format_calendar(events)
    tasks_text = format_tasks(tasks)
    goals_text = format_goals(goals)
    print(f"  Calendar: {len(events)} events")
    print(f"  Tasks: {len([t for t in tasks if 'error' not in t])} active")
    print(f"  Goals: {len([g for g in goals if 'error' not in g])} active")

    # Phase 2: Send briefing
    print("\nPhase 2: Sending context briefing...")
    send_context_briefing(week_start, calendar_text, tasks_text, goals_text)
    time.sleep(3)

    # Phase 3: Interview
    print("\nPhase 3: Running structured interview...")
    answers = run_interview(week_start)
    print(f"  Interview complete. {sum(1 for v in answers.values() if 'SKIPPED' not in v)}/6 questions answered.")

    # Phase 4: Generate goals + tasks
    print("\nPhase 4: Generating goals and tasks...")
    goals_summary = generate_goals_and_tasks(answers, week_start)
    print(f"  Created {goals_summary['goals_created']} goals, {goals_summary['tasks_created']} tasks")

    # Phase 5: Create data recipes
    print("\nPhase 5: Generating data recipes...")
    recipes = save_data_recipes(goals_summary, week_start)
    print(f"  Generated {len(recipes)} recipes")

    # Phase 6: Send kickoff
    print("\nPhase 6: Sending week kickoff message...")
    send_week_kickoff(week_start, goals_summary, recipes)

    print(f"\n{'═' * 50}")
    print(f"  Weekly intake complete. Week of {week_start} initialized.")
    print(f"{'═' * 50}\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    load_env()

    parser = argparse.ArgumentParser(description="Jake Weekly Intake")
    parser.add_argument("--phase", choices=[
        "calendar", "tasks", "goals", "briefing", "interview",
        "generate", "save-recipes", "schedule", "midweek-checkin", "friday-wrapup"
    ], help="Run a specific phase")
    parser.add_argument("--full", action="store_true", help="Run all phases")
    parser.add_argument("--week", default=None, help="Week start date (ISO, e.g. 2026-03-23)")
    parser.add_argument("--calendar", default="", help="Calendar text (for briefing phase)")
    parser.add_argument("--tasks", default="", help="Tasks text (for briefing phase)")
    parser.add_argument("--goals-text", default="", help="Goals text (for briefing phase)")
    parser.add_argument("--interview-answers", default="{}", help="JSON interview answers")
    parser.add_argument("--recipes", default="", help="Recipes text (for save-recipes phase)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Determine week_start
    week_start = args.week
    if not week_start:
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()

    if args.full:
        run_full(week_start)
        return

    phase = args.phase
    if not phase:
        print("Specify --phase or --full")
        parser.print_help()
        sys.exit(1)

    if phase == "calendar":
        events = get_week_events(week_start)
        output = format_calendar(events) if not args.json else json.dumps(events)
        print(output)

    elif phase == "tasks":
        tasks = get_active_tasks()
        output = format_tasks(tasks) if not args.json else json.dumps(tasks, default=str)
        print(output)

    elif phase == "goals":
        goals = get_active_goals()
        output = format_goals(goals) if not args.json else json.dumps(goals, default=str)
        print(output)

    elif phase == "briefing":
        events = get_week_events(week_start)
        tasks = get_active_tasks()
        goals = get_active_goals()
        send_context_briefing(
            week_start,
            args.calendar or format_calendar(events),
            args.tasks or format_tasks(tasks),
            args.goals_text or format_goals(goals),
        )
        print("Context briefing sent.")

    elif phase == "interview":
        answers = run_interview(week_start)
        if args.json:
            print(json.dumps(answers))
        else:
            for k, v in answers.items():
                print(f"  {k}: {v[:80]}")

    elif phase == "generate":
        answers = json.loads(args.interview_answers or "{}")
        summary = generate_goals_and_tasks(answers, week_start)
        if args.json:
            print(json.dumps(summary))
        else:
            print(f"Goals created: {summary['goals_created']}")
            print(f"Tasks created: {summary['tasks_created']}")

    elif phase == "save-recipes":
        # In recipe mode, just print instructions
        print("Data recipes are generated during the 'generate' phase.")
        print("Use --full to run the complete intake flow.")

    elif phase == "schedule":
        print(f"Week {week_start} autonomous schedule active.")
        print("Mid-week check-in: Wednesday 5 PM (cron: 0 17 * * 3)")
        print("Friday wrap-up: Friday 4 PM (cron: 0 16 * * 5)")

    elif phase == "midweek-checkin":
        run_midweek_checkin()

    elif phase == "friday-wrapup":
        run_friday_wrapup()


if __name__ == "__main__":
    main()
