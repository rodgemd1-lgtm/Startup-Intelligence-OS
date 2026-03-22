#!/usr/bin/env python3
"""Jake Immune System — Daily Smoke Test.

Runs at 5:30 AM daily via launchd.
Tests all critical Jake Brain systems and reports health status.
"""

import sys
import os
import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path
BACKEND = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND))

results = {}
overall_healthy = True

def test(name, fn):
    global overall_healthy
    try:
        result = fn()
        results[name] = {"status": "ok", "detail": result}
        print(f"  ✅ {name}: {result}")
    except Exception as e:
        results[name] = {"status": "fail", "error": str(e)}
        overall_healthy = False
        print(f"  ❌ {name}: {e}")

print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Jake Immune Daily Smoke Test")
print("=" * 60)

# Test 1: Supabase connection
def check_supabase():
    from supabase import create_client
    import os
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        # Try loading from .env
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("SUPABASE_URL="):
                    url = line.split("=", 1)[1].strip().strip('"').strip("'")
                elif line.startswith("SUPABASE_SERVICE_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not url or not key:
        raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_KEY not set")
    client = create_client(url, key)
    res = client.table("jake_episodic").select("id", count="exact").limit(1).execute()
    count = res.count or 0
    return f"{count}+ episodic memories"

test("supabase_connection", check_supabase)

# Test 2: jake_brain import
def check_brain_import():
    from jake_brain.retriever import BrainRetriever
    return "BrainRetriever importable"

test("brain_import", check_brain_import)

# Test 3: Voyage AI embedder
def check_embedder():
    # Load from .env if not in environment
    voyage_key = os.environ.get("VOYAGE_API_KEY", "")
    if not voyage_key:
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("VOYAGE_API_KEY="):
                    voyage_key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not voyage_key:
        # Also check Susan backend .env
        susan_env = BACKEND / ".env"
        if susan_env.exists():
            for line in susan_env.read_text().splitlines():
                if line.startswith("VOYAGE_API_KEY="):
                    voyage_key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not voyage_key:
        raise ValueError("VOYAGE_API_KEY not found in env or .env files")
    return "Voyage AI key present"

test("voyage_api_key", check_embedder)

# Test 4: Brain memory counts
def check_memory_counts():
    from jake_brain.retriever import BrainRetriever
    r = BrainRetriever()
    # Just verify it instantiates without error
    return "BrainRetriever initialized"

test("brain_retriever_init", check_memory_counts)

# Test 5: Log directory writable
def check_logs():
    log_dir = Path.home() / ".hermes" / "logs"
    log_dir.mkdir(exist_ok=True)
    test_file = log_dir / ".immune_write_test"
    test_file.write_text("ok")
    test_file.unlink()
    return "logs dir writable"

test("log_directory", check_logs)

# Test 6: Scripts dir has key ingest scripts
def check_scripts():
    scripts = Path(__file__).parent
    required = ["brain_morning_brief.py", "brain_calendar_ingest.py"]
    missing = [s for s in required if not (scripts / s).exists()]
    if missing:
        raise FileNotFoundError(f"Missing: {missing}")
    return f"{len(required)} key scripts present"

test("required_scripts", check_scripts)

# Summary
print("=" * 60)
status = "HEALTHY" if overall_healthy else "DEGRADED"
print(f"Status: {status}")
passed = sum(1 for v in results.values() if v["status"] == "ok")
print(f"Tests: {passed}/{len(results)} passed")

# Write health report
report_path = Path.home() / ".hermes" / "logs" / f"immune_health_{datetime.now().strftime('%Y%m%d')}.json"
report = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "status": status,
    "passed": passed,
    "total": len(results),
    "tests": results
}
report_path.write_text(json.dumps(report, indent=2))
print(f"Report: {report_path}")

sys.exit(0 if overall_healthy else 1)
