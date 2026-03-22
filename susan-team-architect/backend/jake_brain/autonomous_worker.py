"""Autonomous Worker — Jake's 24/7 execution engine.

This module picks up pending tasks from Supabase and executes them
without Mike having to ask. It's the core of the "Jake works while
Mike sleeps" system.

Execution modes:
  - script:      Run a Python script directly (fast, deterministic)
  - claude_code: Spin up a Claude Code subprocess with -p flag (non-interactive)
  - hermes:      Call the Hermes REST API
  - cron:        Mark as handled by scheduled cron (acknowledge only)
  - auto:        Worker chooses based on task_text heuristics

Usage:
    worker = AutonomousWorker()
    worker.run_once()            # Process one task
    worker.run_loop(interval=60) # Poll every 60 seconds (daemon mode)
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("jake-autonomous-worker")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BACKEND_DIR / "scripts"
HERMES_DIR  = Path.home() / ".hermes"
HERMES_VENV = HERMES_DIR / "venv" / "bin" / "python"
VENV_PYTHON  = BACKEND_DIR / ".venv" / "bin" / "python"

# Claude Code binary (standard homebrew location)
CLAUDE_BIN = Path("/usr/local/bin/claude")
if not CLAUDE_BIN.exists():
    CLAUDE_BIN = Path("/opt/homebrew/bin/claude")
if not CLAUDE_BIN.exists():
    CLAUDE_BIN = Path(os.path.expanduser("~/.nvm/versions/node/current/bin/claude"))

# ---------------------------------------------------------------------------
# Task classifier — decides HOW to execute a task
# ---------------------------------------------------------------------------

def classify_task(task: dict) -> str:
    """Return the executor type for a task.

    Priority: explicit assignment → heuristic from task_text → default.
    """
    assigned = task.get("assigned_to", "auto")
    if assigned != "auto":
        return assigned

    text = (task.get("task_text", "") + " " + (task.get("executor_hint") or "")).lower()

    # Script tasks — run a known Python script
    script_signals = [
        "ingest", "scrape", "sync", "migrate", "backup", "export",
        "import", "build brief", "send brief", "report", "cleanup",
        "run script", ".py", "python",
    ]
    if any(s in text for s in script_signals):
        return "script"

    # Claude Code tasks — require reasoning, code generation, document creation
    claude_signals = [
        "write", "create", "build", "design", "analyze", "research",
        "plan", "generate", "draft", "update", "improve", "refactor",
        "document", "implement", "add feature", "recipe", "sop",
        "battlecard", "brief", "email", "slack",
    ]
    if any(s in text for s in claude_signals):
        return "claude_code"

    # Hermes tasks — Telegram-aware, conversation-based
    hermes_signals = ["send to telegram", "notify mike", "telegram", "message mike"]
    if any(s in text for s in hermes_signals):
        return "hermes"

    return "claude_code"  # default to claude_code for safety


# ---------------------------------------------------------------------------
# Executors
# ---------------------------------------------------------------------------

def execute_script(task: dict) -> tuple[bool, str]:
    """Run a Python script specified in executor_hint or inferred from task_text.

    Returns (success, output_text).
    """
    hint = task.get("executor_hint", "")
    script_path = None

    if hint:
        # Hint may be a relative path (scripts/foo.py) or absolute
        p = Path(hint)
        if not p.is_absolute():
            p = SCRIPTS_DIR / hint
        if p.exists():
            script_path = p

    if not script_path:
        # Try to infer from task_text
        text = task.get("task_text", "")
        for part in text.split():
            if part.endswith(".py"):
                p = SCRIPTS_DIR / part.lstrip("./")
                if p.exists():
                    script_path = p
                    break

    if not script_path:
        return False, f"No script found for task: {task.get('task_text')}"

    python = VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable)
    try:
        result = subprocess.run(
            [str(python), str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5-minute hard timeout per script
            cwd=str(BACKEND_DIR),
        )
        output = (result.stdout + result.stderr)[:4000]
        success = result.returncode == 0
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Script timed out after 5 minutes"
    except Exception as e:
        return False, f"Script execution error: {e}"


def execute_claude_code(task: dict) -> tuple[bool, str]:
    """Run a non-interactive Claude Code session via `claude -p 'prompt'`.

    The task_text becomes the Claude prompt. Any executor_hint is prepended
    as system context.
    """
    if not CLAUDE_BIN.exists():
        return False, f"Claude Code binary not found at expected paths. Install via: npm install -g @anthropic-ai/claude-code"

    task_text = task.get("task_text", "")
    hint = task.get("executor_hint", "")

    prompt = task_text
    if hint:
        prompt = f"Context: {hint}\n\nTask: {task_text}"

    # Inject Jake identity and goal context
    goal_id = task.get("goal_id")
    if goal_id:
        prompt = (
            f"You are Jake, Mike's AI co-founder. You are executing an autonomous task "
            f"as part of goal tracking system. Complete the following task independently:\n\n"
            f"{prompt}\n\n"
            f"Work in /Users/mikerodgers/Startup-Intelligence-OS. "
            f"Be thorough. Document what you did in your response."
        )

    try:
        result = subprocess.run(
            [str(CLAUDE_BIN), "-p", prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes for complex Claude tasks
            cwd=str(Path.home() / "Startup-Intelligence-OS"),
        )
        output = (result.stdout + result.stderr)[:6000]
        success = result.returncode == 0
        if not success and not output:
            output = f"Claude Code exited with code {result.returncode}"
        return success, output
    except subprocess.TimeoutExpired:
        return False, "Claude Code task timed out after 10 minutes"
    except Exception as e:
        return False, f"Claude Code execution error: {e}"


def execute_hermes(task: dict) -> tuple[bool, str]:
    """Send a task to Hermes via its REST API.

    Hermes must be running locally at http://localhost:4242.
    """
    import urllib.request
    import urllib.error

    message = task.get("executor_hint") or task.get("task_text", "")
    payload = json.dumps({"message": message, "source": "autonomous_worker"}).encode()

    try:
        req = urllib.request.Request(
            "http://localhost:4242/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return True, body[:2000]
    except urllib.error.URLError as e:
        return False, f"Hermes unreachable: {e}. Is Hermes running? (hermes start)"
    except Exception as e:
        return False, f"Hermes call error: {e}"


def execute_cron(task: dict) -> tuple[bool, str]:
    """Cron tasks are handled by scheduled jobs — just acknowledge."""
    return True, f"Acknowledged: this task is managed by cron schedule ({task.get('executor_hint', 'auto')})"


# ---------------------------------------------------------------------------
# Executor registry
# ---------------------------------------------------------------------------

EXECUTORS = {
    "script":      execute_script,
    "claude_code": execute_claude_code,
    "hermes":      execute_hermes,
    "cron":        execute_cron,
    "manual":      lambda t: (True, "Manual task — marked complete by worker"),
}


# ---------------------------------------------------------------------------
# Goal decomposer — break a free-text goal into concrete tasks
# ---------------------------------------------------------------------------

DECOMPOSITION_TEMPLATES: dict[str, list[dict]] = {
    # When Mike says "build out recipes for my job" or similar
    "recipes": [
        {"task_text": "Audit existing workflow patterns across all 3 projects and list candidate recipes",
         "assigned_to": "claude_code", "priority": "P1", "order_index": 0},
        {"task_text": "Create oracle-battlecard-update.yaml recipe in ~/.hermes/recipes/",
         "assigned_to": "claude_code", "priority": "P1", "order_index": 1},
        {"task_text": "Create morning-research.yaml recipe for daily AI research sweep",
         "assigned_to": "claude_code", "priority": "P2", "order_index": 2},
        {"task_text": "Create weekly-sop-review.yaml recipe for SOP usage tracking",
         "assigned_to": "claude_code", "priority": "P2", "order_index": 3},
        {"task_text": "Create deal-analysis.yaml recipe for Oracle win/loss analysis",
         "assigned_to": "claude_code", "priority": "P2", "order_index": 4},
        {"task_text": "Test all recipes via jake_recipe_runner.py --dry-run",
         "assigned_to": "script", "executor_hint": "scripts/jake_recipe_runner.py",
         "priority": "P1", "order_index": 5},
    ],
    # When Mike says "get tasks and projects completed" or similar
    "project_review": [
        {"task_text": "Run goal dashboard and identify all blocked/overdue items",
         "assigned_to": "script", "executor_hint": "scripts/jake_goals_cli.py dashboard",
         "priority": "P0", "order_index": 0},
        {"task_text": "For each blocked task: diagnose root cause and either fix or escalate",
         "assigned_to": "claude_code", "priority": "P0", "order_index": 1},
        {"task_text": "Send weekly progress report to Mike via Telegram",
         "assigned_to": "hermes", "priority": "P1", "order_index": 2},
    ],
    # When Mike says "build out recipes for Jake"
    "jake_recipes": [
        {"task_text": "Create jake-morning-brief.yaml recipe — full morning brief pipeline",
         "assigned_to": "claude_code", "priority": "P1", "order_index": 0},
        {"task_text": "Create jake-brain-sync.yaml recipe — sync brain from all data sources",
         "assigned_to": "claude_code", "priority": "P1", "order_index": 1},
        {"task_text": "Create jake-weekly-review.yaml recipe — Sunday week review",
         "assigned_to": "claude_code", "priority": "P2", "order_index": 2},
        {"task_text": "Create jake-sop-capture.yaml recipe — capture a new SOP from conversation",
         "assigned_to": "claude_code", "priority": "P2", "order_index": 3},
    ],
}


def decompose_goal(goal_text: str) -> list[dict]:
    """Break a goal into a task list using templates + heuristics.

    Returns a list of task specs that can be fed to TaskStore.create_tasks_from_goal().
    """
    text = goal_text.lower()

    # Match against known templates
    if any(k in text for k in ["recipe", "workflow", "template"]):
        if "jake" in text or "assistant" in text:
            return DECOMPOSITION_TEMPLATES["jake_recipes"]
        return DECOMPOSITION_TEMPLATES["recipes"]

    if any(k in text for k in ["project", "task", "complete", "done", "finish", "backlog"]):
        return DECOMPOSITION_TEMPLATES["project_review"]

    # Fallback: create a single Claude Code task for the full goal
    return [
        {
            "task_text": f"Execute goal: {goal_text}",
            "assigned_to": "claude_code",
            "priority": "P2",
            "order_index": 0,
            "description": f"Autonomous execution of goal: {goal_text}",
        }
    ]


# ---------------------------------------------------------------------------
# Main Worker
# ---------------------------------------------------------------------------

class AutonomousWorker:
    """The main autonomous worker. Polls for tasks and executes them.

    Instantiate once and call run_once() or run_loop().
    """

    def __init__(self) -> None:
        from jake_brain.goals.tasks import TaskStore
        self.tasks = TaskStore()
        self._setup_logging()

    def _setup_logging(self) -> None:
        log_dir = HERMES_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "autonomous_worker.log"
        handler = logging.FileHandler(str(log_file))
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s"
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def run_once(self, executor_filter: str | None = None) -> dict | None:
        """Claim one pending task and execute it. Returns the task dict or None."""
        task = self.tasks.claim_next_task(assigned_to=executor_filter)
        if not task:
            logger.debug("No pending tasks found.")
            return None

        task_id = task["id"]
        task_text = task.get("task_text", "unknown")
        attempt = task.get("attempt_count", 1)

        logger.info(f"[CLAIM] task={task_id[:8]} attempt={attempt} text={task_text[:60]}")
        start_ms = int(time.time() * 1000)

        # Determine executor
        executor_type = classify_task(task)
        executor_fn = EXECUTORS.get(executor_type)

        if not executor_fn:
            output = f"Unknown executor type: {executor_type}"
            self.tasks.fail_task(task_id, error=output)
            logger.error(f"[FAIL] {output}")
            return task

        # Run
        try:
            success, output = executor_fn(task)
        except Exception as e:
            success, output = False, f"Executor raised exception: {e}"

        duration_ms = int(time.time() * 1000) - start_ms

        # Log the run
        self.tasks.log_run(
            task_id=task_id,
            attempt=attempt,
            status="completed" if success else "failed",
            output=output,
            duration_ms=duration_ms,
            executor=executor_type,
        )

        # Update task status
        if success:
            self.tasks.complete_task(task_id, output=output)
            logger.info(f"[DONE] task={task_id[:8]} executor={executor_type} ms={duration_ms}")
        else:
            self.tasks.fail_task(task_id, error=output)
            logger.warning(f"[FAIL] task={task_id[:8]} executor={executor_type} error={output[:100]}")

        return task

    def run_loop(
        self,
        interval_seconds: int = 60,
        max_iterations: int | None = None,
        executor_filter: str | None = None,
    ) -> None:
        """Poll continuously for tasks. Runs until stopped or max_iterations reached.

        interval_seconds: seconds to sleep between polls when queue is empty
        max_iterations: optional limit (useful for tests)
        executor_filter: only claim tasks for this executor type
        """
        logger.info(f"[START] Autonomous worker daemon started. interval={interval_seconds}s")
        iterations = 0

        while True:
            try:
                result = self.run_once(executor_filter=executor_filter)
                if result is None:
                    # Nothing to do — sleep
                    time.sleep(interval_seconds)
                else:
                    # There might be more work — check immediately
                    time.sleep(2)
            except KeyboardInterrupt:
                logger.info("[STOP] Worker interrupted by user.")
                break
            except Exception as e:
                logger.error(f"[ERROR] Worker loop error: {e}")
                time.sleep(interval_seconds)

            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                logger.info(f"[STOP] Max iterations ({max_iterations}) reached.")
                break

    def create_goal_with_tasks(
        self,
        goal_text: str,
        priority: str = "P2",
        deadline: str | None = None,
        project: str | None = None,
    ) -> dict:
        """Create a goal + automatically decompose it into tasks.

        This is the entry point when Mike says "Jake, add a goal: X".
        Returns {goal, tasks} dict.
        """
        from jake_brain.goals.store import GoalStore

        goals = GoalStore()
        goal = goals.create_goal(
            title=goal_text,
            priority=priority,
            deadline=deadline,
            project=project,
        )

        if not goal.get("id"):
            return {"goal": goal, "tasks": [], "error": "Goal creation failed"}

        task_specs = decompose_goal(goal_text)
        tasks = self.tasks.create_tasks_from_goal(goal["id"], task_specs)

        logger.info(
            f"[GOAL] Created goal {goal['id'][:8]} with {len(tasks)} tasks: {goal_text[:60]}"
        )
        return {"goal": goal, "tasks": tasks}

    def status_report(self) -> str:
        """Generate a plain-text status report for Telegram."""
        dash = self.tasks.dashboard()
        lines = [
            "🤖 *Autonomous Worker Status*",
            "",
            f"Pending:     {dash['pending']}",
            f"In Progress: {dash['in_progress']}",
            f"Completed:   {dash['completed']}",
            f"Blocked:     {dash['blocked']}",
            f"Failed:      {dash.get('failed', 0)}",
        ]

        if dash.get("pending_tasks"):
            lines.append("\n📋 *Next Up:*")
            for t in dash["pending_tasks"][:5]:
                lines.append(f"  [{t['priority']}] {t['task_text'][:60]}")

        if dash.get("blocked_tasks"):
            lines.append("\n🚫 *Blocked:*")
            for t in dash["blocked_tasks"][:3]:
                lines.append(f"  • {t['task_text'][:50]}: {(t.get('error_msg') or 'no reason')[:40]}")

        return "\n".join(lines)
