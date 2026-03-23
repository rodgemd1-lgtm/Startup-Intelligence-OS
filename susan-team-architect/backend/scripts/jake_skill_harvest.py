#!/usr/bin/env python3
"""Jake Skill Harvester — auto-generate Hermes skills from successful pipeline patterns.

Scans Supabase for:
  - High-importance episodic memories (grouped by data_type)
  - Successful pipeline runs (jake_pipeline_runs table, if it exists)

Generates Hermes skill files via SkillGenerator and updates jake_cron_status.

Cron: daily at 4 AM
  Add to ~/.hermes/jobs.json:
  {
    "name": "skill_harvest",
    "schedule": "0 4 * * *",
    "command": "/Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/.venv/bin/python /Users/mikerodgers/Startup-Intelligence-OS/susan-team-architect/backend/scripts/jake_skill_harvest.py"
  }
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))


# ---------------------------------------------------------------------------
# Env loader
# ---------------------------------------------------------------------------

def load_env() -> None:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


# ---------------------------------------------------------------------------
# Cron status updater
# ---------------------------------------------------------------------------

def update_cron_status(job_name: str, status: str, error: str = "", duration_ms: int = 0) -> None:
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            return
        client = create_client(url, key)
        client.table("jake_cron_status").upsert({
            "job_name": job_name,
            "last_run": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "error_message": error[:500] if error else "",
            "duration_ms": duration_ms,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="job_name").execute()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def get_supabase_client():
    """Return a Supabase client or None if env not configured."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        if not url or not key:
            print("  [WARN] SUPABASE_URL or SUPABASE_SERVICE_KEY not set — skipping DB queries")
            return None
        return create_client(url, key)
    except ImportError:
        print("  [WARN] supabase-py not installed — skipping DB queries")
        return None


def fetch_episodic_memories(client) -> list[dict]:
    """Fetch high-importance episodic memories.

    The actual table uses source_type as the category column.
    We remap it to data_type so SkillGenerator.generate_from_episodic() can group it.
    """
    try:
        result = (
            client.table("jake_episodic")
            .select("id, source_type, content, importance, created_at")
            .gt("importance", 0.75)
            .order("created_at", desc=True)
            .limit(500)
            .execute()
        )
        rows = result.data or []
        # Remap source_type → data_type for SkillGenerator compatibility
        for row in rows:
            if "data_type" not in row:
                row["data_type"] = row.get("source_type") or "general"
        return rows
    except Exception as exc:
        print(f"  [WARN] Could not query jake_episodic: {exc}")
        return []


def fetch_pipeline_runs(client) -> list[dict]:
    """Fetch completed pipeline runs. Returns empty list if table doesn't exist."""
    try:
        result = (
            client.table("jake_pipeline_runs")
            .select("id, pipeline_name, task_description, task_type, phases_completed, created_at")
            .eq("status", "completed")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )
        return result.data or []
    except Exception as exc:
        err_str = str(exc).lower()
        if "does not exist" in err_str or "relation" in err_str or "42p01" in err_str:
            print("  [INFO] jake_pipeline_runs table does not exist yet — skipping pipeline harvest")
        else:
            print(f"  [WARN] Could not query jake_pipeline_runs: {exc}")
        return []


# ---------------------------------------------------------------------------
# Harvest logic
# ---------------------------------------------------------------------------

def harvest_from_episodic(client, generator) -> list[Path]:
    """Generate skills from clustered episodic memories."""
    print("\n[1/2] Scanning episodic memories...")
    memories = fetch_episodic_memories(client) if client else []

    if not memories:
        print("  No high-importance episodic memories found.")
        return []

    # Group by data_type for reporting
    by_type: dict[str, int] = {}
    for m in memories:
        dt = m.get("data_type", "general")
        by_type[dt] = by_type.get(dt, 0) + 1

    print(f"  Found {len(memories)} high-importance memories across {len(by_type)} data types:")
    for dt, count in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    • {dt}: {count} entries")

    generated = generator.generate_from_episodic(memories)
    print(f"  Generated {len(generated)} skills from episodic patterns:")
    for p in generated:
        print(f"    + {p.name}")

    return generated


def harvest_from_pipelines(client, generator) -> list[Path]:
    """Generate skills from successful pipeline runs."""
    print("\n[2/2] Scanning pipeline runs...")
    runs = fetch_pipeline_runs(client) if client else []

    if not runs:
        print("  No qualifying pipeline runs found.")
        return []

    print(f"  Found {len(runs)} completed pipeline runs")

    generated = []
    for run in runs:
        pipeline_name = run.get("pipeline_name", "unknown")
        task_description = run.get("task_description", "")
        task_type = run.get("task_type", "general")
        phases = run.get("phases_completed") or {}
        quality_score = float(run.get("quality_score", 1.0))  # default 1.0 (all runs qualify)
        run_id = str(run.get("id", ""))

        path = generator.generate_from_pipeline(
            pipeline_name=pipeline_name,
            task_description=task_description,
            task_type=task_type,
            phases_completed=phases,
            quality_score=quality_score,
            run_id=run_id,
        )
        if path:
            generated.append(path)
            print(f"    + {path.name} (from run {run_id[:8]}..., score={quality_score:.2f})")

    print(f"  Generated {len(generated)} skills from pipeline runs")
    return generated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    start_ms = int(time.time() * 1000)
    load_env()

    print("=" * 60)
    print("Jake Skill Harvester")
    print(f"Run at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    try:
        from self_improvement.skill_generator import SkillGenerator
    except ImportError as exc:
        msg = f"Could not import SkillGenerator: {exc}"
        print(f"[ERROR] {msg}")
        update_cron_status("skill_harvest", "error", error=msg)
        sys.exit(1)

    generator = SkillGenerator()
    client = get_supabase_client()

    episodic_skills = harvest_from_episodic(client, generator)
    pipeline_skills = harvest_from_pipelines(client, generator)

    total = len(episodic_skills) + len(pipeline_skills)

    print("\n" + "=" * 60)
    print("Harvest Report")
    print("=" * 60)
    print(f"  Skills from episodic patterns : {len(episodic_skills)}")
    print(f"  Skills from pipeline runs     : {len(pipeline_skills)}")
    print(f"  Total new skills generated    : {total}")
    print(f"  Skills dir                    : {generator.skills_dir}")

    if total == 0:
        print("\n  No new skills generated this run.")
        print("  (Skills already exist or not enough pattern data yet)")
    else:
        print("\n  New skills:")
        for p in episodic_skills + pipeline_skills:
            print(f"    • {p.stem}")

    print("\nFull inventory:")
    print(generator.report())

    duration_ms = int(time.time() * 1000) - start_ms
    update_cron_status("skill_harvest", "success", duration_ms=duration_ms)
    print(f"\nDone in {duration_ms}ms")


if __name__ == "__main__":
    main()
