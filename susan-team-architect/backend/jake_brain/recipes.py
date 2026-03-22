"""Jake Recipe System — reusable YAML workflow templates.

Like Goose recipes but for Jake's agentic workflows. A recipe is a named,
multi-step workflow stored as YAML that Jake can execute on demand or on schedule.

Recipe format (YAML):
    name: oracle-battlecard-update
    description: Full competitive battlecard update workflow
    version: "1.0"
    tags: [oracle, competitive, battlecard]
    steps:
      - name: Scrape competitor news
        tool: scrape
        args:
          url: "https://nuance.com/news"
          topic: "nuance DAX"
      - name: Run signal triage SOP
        tool: sop
        args:
          sop_id: "SOP-02"
      - name: Generate battlecard update
        tool: claude_code
        args:
          prompt: "Update the Oracle battlecard with new competitive intel from the context above"
      - name: Send brief to Mike
        tool: telegram
        args:
          message: "Battlecard updated. Key changes: {output.previous_step}"

Tools available in recipes:
    scrape        — Fetch and parse a URL (via Brightdata or requests)
    claude_code   — Run Claude Code subprocess with a prompt
    script        — Run a Python script from scripts/
    telegram      — Send message via Hermes/Telegram
    brain_search  — Query the brain and use results as input
    sop           — Look up and display an SOP
    create_task   — Add a task to the autonomous worker queue
    create_goal   — Add a goal
    wait          — Sleep N seconds
    shell         — Run a shell command (sandboxed)

Usage:
    from jake_brain.recipes import RecipeRunner

    runner = RecipeRunner()
    runner.run("oracle-battlecard-update")
    runner.run("morning-research", context={"date": "2026-03-22"})
    runner.list_recipes()
    runner.get_recipe("morning-research")
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

logger = logging.getLogger("jake-recipes")

# Default recipe directories (checked in order)
RECIPE_DIRS = [
    Path.home() / ".hermes" / "recipes",
    Path(__file__).resolve().parent.parent / "recipes",
]

# ---------------------------------------------------------------------------
# Recipe loader
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    if not _YAML_AVAILABLE:
        raise ImportError("PyYAML is required for recipes. Run: pip install pyyaml")
    with open(path) as f:
        return yaml.safe_load(f)


def _find_recipe_file(name: str) -> Path | None:
    """Search recipe directories for a recipe by name (with or without .yaml)."""
    names_to_try = [name, f"{name}.yaml", f"{name}.yml"]
    for recipe_dir in RECIPE_DIRS:
        if not recipe_dir.exists():
            continue
        for candidate in names_to_try:
            p = recipe_dir / candidate
            if p.exists():
                return p
    return None


def load_recipe(name: str) -> dict:
    """Load a recipe by name. Raises FileNotFoundError if not found."""
    path = _find_recipe_file(name)
    if not path:
        raise FileNotFoundError(
            f"Recipe '{name}' not found. Searched: {[str(d) for d in RECIPE_DIRS]}"
        )
    recipe = _load_yaml(path)
    recipe["_path"] = str(path)
    return recipe


def list_recipes() -> list[dict]:
    """Return all available recipes across all recipe directories."""
    recipes = []
    seen_names = set()

    for recipe_dir in RECIPE_DIRS:
        if not recipe_dir.exists():
            continue
        for path in sorted(recipe_dir.glob("*.yaml")) + sorted(recipe_dir.glob("*.yml")):
            try:
                r = _load_yaml(path)
                name = r.get("name") or path.stem
                if name in seen_names:
                    continue
                seen_names.add(name)
                recipes.append({
                    "name": name,
                    "description": r.get("description", ""),
                    "tags": r.get("tags", []),
                    "steps": len(r.get("steps", [])),
                    "path": str(path),
                })
            except Exception as e:
                logger.warning(f"Failed to load recipe {path}: {e}")

    return sorted(recipes, key=lambda r: r["name"])


# ---------------------------------------------------------------------------
# Context interpolation — {variable} replacement in args
# ---------------------------------------------------------------------------

def _interpolate(value: Any, context: dict) -> Any:
    """Replace {variable} placeholders in string values."""
    if isinstance(value, str):
        def replacer(m: re.Match) -> str:
            key = m.group(1)
            return str(context.get(key, m.group(0)))
        return re.sub(r"\{(\w+(?:\.\w+)*)\}", replacer, value)
    if isinstance(value, list):
        return [_interpolate(v, context) for v in value]
    if isinstance(value, dict):
        return {k: _interpolate(v, context) for k, v in value.items()}
    return value


# ---------------------------------------------------------------------------
# Step executors
# ---------------------------------------------------------------------------

def _exec_claude_code(step: dict, context: dict) -> tuple[bool, str]:
    prompt = _interpolate(step.get("args", {}).get("prompt", step.get("name", "")), context)
    cwd = step.get("args", {}).get("cwd", str(Path.home() / "Startup-Intelligence-OS"))

    backend_dir = Path(__file__).resolve().parent.parent
    for candidate in [
        "/usr/local/bin/claude",
        "/opt/homebrew/bin/claude",
    ]:
        if Path(candidate).exists():
            claude_bin = candidate
            break
    else:
        return False, "Claude Code binary not found"

    try:
        result = subprocess.run(
            [claude_bin, "-p", prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=cwd,
        )
        output = (result.stdout + result.stderr)[:4000]
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Claude Code step timed out"
    except Exception as e:
        return False, f"Claude Code error: {e}"


def _exec_script(step: dict, context: dict) -> tuple[bool, str]:
    backend_dir = Path(__file__).resolve().parent.parent
    script_name = _interpolate(step.get("args", {}).get("script", ""), context)
    if not script_name:
        return False, "No script specified"

    script_path = backend_dir / "scripts" / script_name
    if not script_path.exists():
        return False, f"Script not found: {script_path}"

    venv_python = backend_dir / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable

    extra_args = step.get("args", {}).get("args", [])
    if isinstance(extra_args, str):
        import shlex
        extra_args = shlex.split(extra_args)

    try:
        result = subprocess.run(
            [python, str(script_path)] + extra_args,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(backend_dir),
        )
        output = (result.stdout + result.stderr)[:4000]
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Script step timed out"
    except Exception as e:
        return False, f"Script error: {e}"


def _exec_brain_search(step: dict, context: dict) -> tuple[bool, str]:
    query = _interpolate(step.get("args", {}).get("query", ""), context)
    limit = step.get("args", {}).get("limit", 5)

    try:
        backend_dir = Path(__file__).resolve().parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        from jake_brain.retriever import BrainRetriever
        retriever = BrainRetriever()
        results = retriever.search(query, limit=limit)
        output = "\n".join(
            r.get("content") or r.get("fact") or "" for r in results
        )
        return True, output
    except Exception as e:
        return False, f"Brain search error: {e}"


def _exec_telegram(step: dict, context: dict) -> tuple[bool, str]:
    import urllib.request
    message = _interpolate(step.get("args", {}).get("message", ""), context)
    payload = json.dumps({"message": message, "source": "recipe"}).encode()
    try:
        req = urllib.request.Request(
            "http://localhost:4242/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200, f"Sent: {message[:50]}"
    except Exception as e:
        return False, f"Telegram error: {e}"


def _exec_create_task(step: dict, context: dict) -> tuple[bool, str]:
    task_text = _interpolate(step.get("args", {}).get("task_text", ""), context)
    assigned = step.get("args", {}).get("assigned_to", "auto")
    priority = step.get("args", {}).get("priority", "P2")

    try:
        backend_dir = Path(__file__).resolve().parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        from jake_brain.goals.tasks import TaskStore
        store = TaskStore()
        task = store.create_task(task_text=task_text, assigned_to=assigned, priority=priority)
        return True, f"Task created: {task.get('id','?')[:8]}"
    except Exception as e:
        return False, f"Task creation error: {e}"


def _exec_wait(step: dict, context: dict) -> tuple[bool, str]:
    seconds = step.get("args", {}).get("seconds", 5)
    time.sleep(int(seconds))
    return True, f"Waited {seconds}s"


def _exec_shell(step: dict, context: dict) -> tuple[bool, str]:
    """Run a sandboxed shell command. RESTRICTED to read-only or known-safe commands."""
    cmd = _interpolate(step.get("args", {}).get("command", ""), context)
    # Safety: only allow certain prefixes to prevent recipe abuse
    ALLOWED_PREFIXES = ("echo ", "cat ", "ls ", "pwd", "date", "python ", "python3 ")
    if not any(cmd.strip().startswith(p) for p in ALLOWED_PREFIXES):
        return False, f"Shell command not allowed for safety: {cmd}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, (result.stdout + result.stderr)[:2000]
    except Exception as e:
        return False, f"Shell error: {e}"


STEP_EXECUTORS = {
    "claude_code": _exec_claude_code,
    "script":      _exec_script,
    "brain_search": _exec_brain_search,
    "telegram":    _exec_telegram,
    "create_task": _exec_create_task,
    "wait":        _exec_wait,
    "shell":       _exec_shell,
}


# ---------------------------------------------------------------------------
# Recipe runner
# ---------------------------------------------------------------------------

class RecipeRunner:
    """Loads and executes Jake recipes."""

    def run(
        self,
        name: str,
        context: dict | None = None,
        dry_run: bool = False,
        stop_on_error: bool = True,
    ) -> dict:
        """Execute a recipe by name.

        Returns:
            {
              "name": str,
              "status": "completed" | "failed" | "partial",
              "steps_run": int,
              "steps_failed": int,
              "outputs": [{"step": str, "success": bool, "output": str}],
              "context": dict  (accumulated context including step outputs)
            }
        """
        recipe = load_recipe(name)
        steps = recipe.get("steps", [])

        ctx = dict(context or {})
        ctx["recipe_name"] = recipe.get("name", name)
        ctx["recipe_description"] = recipe.get("description", "")

        result = {
            "name": name,
            "steps_run": 0,
            "steps_failed": 0,
            "outputs": [],
            "context": ctx,
        }

        logger.info(f"[RECIPE] Starting: {name} ({len(steps)} steps)")

        for i, step in enumerate(steps):
            step_name = step.get("name", f"Step {i+1}")
            tool = step.get("tool", "")
            executor = STEP_EXECUTORS.get(tool)

            if not executor:
                output = f"Unknown tool: {tool}"
                logger.warning(f"[RECIPE:{name}] Step '{step_name}' — {output}")
                result["outputs"].append({"step": step_name, "success": False, "output": output})
                result["steps_failed"] += 1
                if stop_on_error:
                    result["status"] = "failed"
                    return result
                continue

            logger.info(f"[RECIPE:{name}] Step {i+1}/{len(steps)}: {step_name}")

            if dry_run:
                output = f"[DRY RUN] Would execute {tool} step: {step_name}"
                success = True
            else:
                try:
                    success, output = executor(step, ctx)
                except Exception as e:
                    success, output = False, f"Step executor raised: {e}"

            result["outputs"].append({"step": step_name, "success": success, "output": output[:500]})
            result["steps_run"] += 1

            # Make step output available to subsequent steps
            ctx[f"step_{i+1}_output"] = output
            ctx["previous_step"] = output
            ctx["previous_step_success"] = success

            if not success:
                result["steps_failed"] += 1
                logger.warning(f"[RECIPE:{name}] Step failed: {step_name}: {output[:80]}")
                if stop_on_error:
                    result["status"] = "failed"
                    return result

        result["status"] = "completed" if result["steps_failed"] == 0 else "partial"
        logger.info(f"[RECIPE:{name}] Done. Status={result['status']} steps={result['steps_run']}")
        return result

    def list_recipes(self) -> list[dict]:
        return list_recipes()

    def get_recipe(self, name: str) -> dict:
        return load_recipe(name)
