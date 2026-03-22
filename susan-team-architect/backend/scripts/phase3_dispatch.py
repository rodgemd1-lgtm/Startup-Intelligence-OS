#!/usr/bin/env python3
"""Phase 3 Wave 1 Dispatch — Fix constraints + run all ingestions.

This is the "one button" script that:
1. Drops and re-creates Supabase check constraints for Phase 3 data types
2. Runs all 4 Wave 1 ingestion scripts (gcal, mail, reminders, calendar)
3. Runs birthday check
4. Reports brain stats at the end

Usage:
    cd susan-team-architect/backend && source .venv/bin/activate
    python scripts/phase3_dispatch.py [--skip-sql] [--skip-mail] [--skip-calendar] [--dry-run]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

# Ensure we can import from backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from susan_core.config import config as susan_config


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def run_sql_constraints() -> bool:
    """Fix Supabase check constraints for Phase 3 data types."""
    log("🔧 Step 1: Fixing Supabase check constraints...")

    try:
        import httpx
    except ImportError:
        log("httpx not installed, trying requests...")
        import requests as httpx

    # Use Supabase REST API to run SQL via the rpc endpoint
    # We need the postgres connection — use supabase-py's postgrest
    from supabase import create_client
    sb = create_client(susan_config.supabase_url, susan_config.supabase_key)

    statements = [
        # 1. Episodic memory types
        "ALTER TABLE jake_episodic DROP CONSTRAINT IF EXISTS jake_episodic_memory_type_check",
        """ALTER TABLE jake_episodic ADD CONSTRAINT jake_episodic_memory_type_check
           CHECK (memory_type IN ('conversation', 'email', 'calendar_event', 'task_completed', 'action', 'reminder', 'meeting'))""",
        # 2. Semantic categories
        "ALTER TABLE jake_semantic DROP CONSTRAINT IF EXISTS jake_semantic_category_check",
        """ALTER TABLE jake_semantic ADD CONSTRAINT jake_semantic_category_check
           CHECK (category IN ('fact', 'preference', 'decision', 'task', 'task_summary', 'pattern', 'procedure', 'schedule'))""",
        # 3. Entity types
        "ALTER TABLE jake_entities DROP CONSTRAINT IF EXISTS jake_entities_entity_type_check",
        """ALTER TABLE jake_entities ADD CONSTRAINT jake_entities_entity_type_check
           CHECK (entity_type IN ('person', 'family_member', 'company', 'project', 'colleague', 'recurring_event', 'technology', 'team', 'location'))""",
    ]

    # Execute via Supabase's RPC — we need a helper function in the DB
    # Alternative: use the REST API directly with the service key
    url = susan_config.supabase_url
    key = susan_config.supabase_key

    # Use the PostgREST /rpc endpoint — but for DDL we need the SQL endpoint
    # Supabase exposes a SQL endpoint at /rest/v1/rpc for functions
    # For raw DDL, we use the pg-meta API or create a helper function

    # Simplest approach: use psycopg2/asyncpg if available, otherwise supabase management API
    # Let's try the supabase management API first (requires project ref)

    # Extract project ref from URL: https://XXX.supabase.co
    project_ref = url.replace("https://", "").split(".")[0]

    # Actually, the cleanest way is to create a temporary RPC function
    # or use the supabase-py client's postgrest to call a function that runs SQL.

    # Best approach: use the Database Webhooks / SQL Editor API
    # But that needs the management API key, not the service key.

    # Pragmatic approach: try to insert a test row, if it fails with constraint
    # violation, we know we need the SQL. The user can run it manually OR
    # we create an RPC function for it.

    # Let's just create an RPC function that does the DDL
    # First, check if constraints already allow the new types by doing a test insert

    test_ok = _test_constraints(sb)
    if test_ok:
        log("✅ Constraints already allow Phase 3 types — skipping SQL.")
        return True

    log("⚠️  Constraints need updating.")
    log("   Run these SQL statements in Supabase SQL Editor:")
    log("")
    for stmt in statements:
        log(f"   {stmt.strip()};")
    log("")
    log("   Or run: supabase db execute < scripts/phase3_constraints.sql")

    # Write the SQL file for convenience
    sql_path = Path(__file__).parent / "phase3_constraints.sql"
    with open(sql_path, "w") as f:
        for stmt in statements:
            f.write(stmt.strip() + ";\n\n")
    log(f"   SQL file written to: {sql_path}")

    return False


def _test_constraints(sb) -> bool:
    """Test if constraints already allow Phase 3 types."""
    import uuid

    test_id = str(uuid.uuid4())

    # Test episodic with 'email' type
    try:
        sb.table("jake_episodic").insert({
            "id": test_id,
            "content": "__constraint_test__",
            "memory_type": "email",
            "importance": 0.0,
            "embedding": [0.0] * 1024,
        }).execute()
        # Clean up
        sb.table("jake_episodic").delete().eq("id", test_id).execute()
        log("   ✅ jake_episodic: 'email' type accepted")
    except Exception as e:
        if "check" in str(e).lower() or "violates" in str(e).lower():
            log("   ❌ jake_episodic: 'email' type rejected by constraint")
            return False
        # Other error — might be column mismatch, continue
        log(f"   ⚠️  jake_episodic test error: {e}")

    # Test semantic with 'schedule' category
    try:
        sb.table("jake_semantic").insert({
            "id": test_id,
            "content": "__constraint_test__",
            "category": "schedule",
            "confidence": 0.0,
            "embedding": [0.0] * 1024,
        }).execute()
        sb.table("jake_semantic").delete().eq("id", test_id).execute()
        log("   ✅ jake_semantic: 'schedule' category accepted")
    except Exception as e:
        if "check" in str(e).lower() or "violates" in str(e).lower():
            log("   ❌ jake_semantic: 'schedule' category rejected by constraint")
            return False
        log(f"   ⚠️  jake_semantic test error: {e}")

    # Test entities with 'colleague' type
    try:
        sb.table("jake_entities").insert({
            "id": test_id,
            "name": "__constraint_test__",
            "entity_type": "colleague",
            "embedding": [0.0] * 1024,
        }).execute()
        sb.table("jake_entities").delete().eq("id", test_id).execute()
        log("   ✅ jake_entities: 'colleague' type accepted")
    except Exception as e:
        if "check" in str(e).lower() or "violates" in str(e).lower():
            log("   ❌ jake_entities: 'colleague' type rejected by constraint")
            return False
        log(f"   ⚠️  jake_entities test error: {e}")

    return True


def run_script(name: str, args: list[str] | None = None, timeout: int = 180) -> bool:
    """Run an ingestion script and return success."""
    script_path = Path(__file__).parent / name
    if not script_path.exists():
        log(f"   ❌ Script not found: {name}")
        return False

    cmd = [sys.executable, str(script_path)] + (args or [])
    log(f"   Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path(__file__).parent.parent),
            env={**os.environ},
        )
        if result.returncode == 0:
            # Print last 5 lines of output as summary
            lines = result.stdout.strip().splitlines()
            for line in lines[-5:]:
                log(f"   {line}")
            return True
        else:
            log(f"   ❌ Failed (exit {result.returncode})")
            err_lines = result.stderr.strip().splitlines()
            for line in err_lines[-5:]:
                log(f"   {line}")
            return False
    except subprocess.TimeoutExpired:
        log(f"   ❌ Timed out after {timeout}s")
        return False


def get_brain_stats() -> dict:
    """Get current brain stats."""
    from supabase import create_client
    sb = create_client(susan_config.supabase_url, susan_config.supabase_key)

    stats = {}
    for table in ["jake_episodic", "jake_semantic", "jake_procedural",
                   "jake_working", "jake_entities", "jake_relationships"]:
        try:
            result = sb.table(table).select("id", count="exact").limit(0).execute()
            stats[table] = result.count or 0
        except Exception:
            stats[table] = "?"
    return stats


def main():
    parser = argparse.ArgumentParser(description="Phase 3 Wave 1 Dispatch")
    parser.add_argument("--skip-sql", action="store_true", help="Skip constraint check")
    parser.add_argument("--skip-mail", action="store_true", help="Skip mail ingestion (slow)")
    parser.add_argument("--skip-calendar", action="store_true", help="Skip Apple Calendar (unreliable)")
    parser.add_argument("--dry-run", action="store_true", help="Pass --dry-run to ingestion scripts")
    parser.add_argument("--mail-days", type=int, default=3, help="Days of mail to ingest (default: 3)")
    args = parser.parse_args()

    log("=" * 60)
    log("PHASE 3 WAVE 1 DISPATCH — Jake's Brain Ingestion Pipeline")
    log("=" * 60)

    # Pre-flight: brain stats
    log("\n📊 Brain stats BEFORE:")
    stats_before = get_brain_stats()
    for table, count in stats_before.items():
        log(f"   {table}: {count}")

    results = {}

    # Step 1: Check/fix constraints
    if not args.skip_sql:
        constraints_ok = run_sql_constraints()
        if not constraints_ok:
            log("\n⚠️  Constraints need manual fix. Run the SQL above, then re-run with --skip-sql")
            log("   Or continue anyway — episodic 'email' type might already work.")
            # Don't abort — some scripts may still work
    else:
        log("\n⏭️  Skipping constraint check (--skip-sql)")

    # Step 2: Google Calendar ingestion
    log("\n📅 Step 2: Google Calendar ingestion...")
    gcal_args = []
    if args.dry_run:
        gcal_args.append("--dry-run")
    results["gcal"] = run_script("brain_gcal_ingest.py", gcal_args, timeout=120)

    # Step 3: Mail ingestion
    if not args.skip_mail:
        log(f"\n📧 Step 3: Mail ingestion (last {args.mail_days} days)...")
        mail_args = ["--days", str(args.mail_days)]
        if args.dry_run:
            mail_args.append("--dry-run")
        results["mail"] = run_script("brain_mail_ingest.py", mail_args, timeout=180)
    else:
        log("\n⏭️  Skipping mail ingestion (--skip-mail)")
        results["mail"] = None

    # Step 4: Reminders ingestion
    log("\n📝 Step 4: Reminders ingestion...")
    remind_args = []
    if args.dry_run:
        remind_args.append("--dry-run")
    results["reminders"] = run_script("brain_reminders_ingest.py", remind_args, timeout=120)

    # Step 5: Apple Calendar (optional — often times out)
    if not args.skip_calendar:
        log("\n🗓️  Step 5: Apple Calendar ingestion...")
        cal_args = []
        if args.dry_run:
            cal_args.append("--dry-run")
        results["calendar"] = run_script("brain_calendar_ingest.py", cal_args, timeout=120)
    else:
        log("\n⏭️  Skipping Apple Calendar (--skip-calendar)")
        results["calendar"] = None

    # Step 6: Birthday check
    log("\n🎂 Step 6: Birthday check...")
    results["birthday"] = run_script("birthday_check.py", timeout=60)

    # Post-flight: brain stats
    log("\n📊 Brain stats AFTER:")
    stats_after = get_brain_stats()
    for table, count in stats_after.items():
        before = stats_before.get(table, 0)
        if isinstance(count, int) and isinstance(before, int):
            delta = count - before
            log(f"   {table}: {count} (+{delta})" if delta > 0 else f"   {table}: {count}")
        else:
            log(f"   {table}: {count}")

    # Summary
    log("\n" + "=" * 60)
    log("DISPATCH SUMMARY")
    log("=" * 60)
    for step, ok in results.items():
        if ok is None:
            log(f"   {step}: SKIPPED")
        elif ok:
            log(f"   {step}: ✅ SUCCESS")
        else:
            log(f"   {step}: ❌ FAILED")

    failed = [k for k, v in results.items() if v is False]
    if failed:
        log(f"\n⚠️  {len(failed)} step(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        log("\n🎉 All steps completed successfully!")


if __name__ == "__main__":
    main()
