#!/usr/bin/env python3
"""CLI wrapper for the Jake autonomous pipeline engine.

Usage:
    python scripts/jake_pipeline_runner.py --task "Research competitor X" --type research
    python scripts/jake_pipeline_runner.py --task "Draft Oracle brief" --type content
    python scripts/jake_pipeline_runner.py --task "Update stale RAG records" --type maintenance

Task types:
    research    — Query Susan RAG + synthesize findings
    content     — Draft content from RAG context
    maintenance — Check data freshness, flag stale records
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("jake.pipeline_runner")


def update_cron_status(job_name: str, status: str, actions: int = 0, error: str | None = None) -> None:
    """Update jake_cron_status table for monitoring."""
    try:
        from supabase import create_client
        from susan_core.config import config
        client = create_client(config.supabase_url, config.supabase_key)
        client.table("jake_cron_status").update({
            "status": status,
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "actions_taken": actions,
            "error_message": error,
        }).eq("job_name", job_name).execute()
    except Exception as e:
        logger.warning(f"Failed to update cron status: {e}")


def run_pipeline(task: str, task_type: str, name: str | None = None) -> dict:
    """Instantiate and run an autonomous pipeline."""
    from jake_brain.autonomous_pipeline import AutonomousPipeline

    pipeline_name = name or f"{task_type}_{int(time.time())}"
    logger.info(f"Starting pipeline: {pipeline_name}")
    logger.info(f"Task: {task}")
    logger.info(f"Type: {task_type}")

    pipeline = AutonomousPipeline(
        pipeline_name=pipeline_name,
        task_description=task,
        task_type=task_type,
    )

    start = time.time()
    result = pipeline.run()
    elapsed = round((time.time() - start) * 1000)

    result["duration_ms"] = elapsed
    return result


def print_result(result: dict) -> None:
    """Pretty-print the pipeline result."""
    status = result.get("status", "unknown")
    success = result.get("success", False)
    run_id = result.get("run_id", "?")
    duration = result.get("duration_ms", 0)

    symbol = "✓" if success else "✗"
    print(f"\n{symbol} Pipeline {result.get('pipeline_name', '')} [{status.upper()}]")
    print(f"  Run ID  : {run_id}")
    print(f"  Duration: {duration}ms")

    if result.get("reason"):
        print(f"  Reason  : {result['reason']}")

    phases = result.get("phases_completed", {})
    if phases:
        print(f"  Phases  : {', '.join(phases.keys())}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jake autonomous pipeline runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument(
        "--type",
        dest="task_type",
        choices=["research", "content", "maintenance", "custom"],
        default="research",
        help="Task type (default: research)",
    )
    parser.add_argument("--name", help="Pipeline name (auto-generated if omitted)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON result")
    args = parser.parse_args()

    cron_job = f"pipeline_{args.task_type}"
    update_cron_status(cron_job, "running")

    try:
        result = run_pipeline(args.task, args.task_type, args.name)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_result(result)

        actions = result.get("phases_completed", {})
        update_cron_status(
            cron_job,
            "success" if result.get("success") else "failed",
            actions=len(actions),
            error=result.get("reason") if not result.get("success") else None,
        )

        sys.exit(0 if result.get("success") else 1)

    except Exception as e:
        logger.error(f"Pipeline runner failed: {e}", exc_info=True)
        update_cron_status(cron_job, "failed", error=str(e))
        sys.exit(2)


if __name__ == "__main__":
    main()
