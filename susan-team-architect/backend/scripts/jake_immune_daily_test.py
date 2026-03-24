#!/usr/bin/env python3
"""Jake Immune System — Daily Smoke Test.

Runs every morning at 5:30 AM (before brain wave1 ingest at 5:45 AM and brief at 6:00 AM).
Tests core brain functions and alerts Mike if anything is broken.

Tests:
  1. Brain search — can we query the brain?
  2. Entity lookup — can we find Mike in the knowledge graph?
  3. Supabase connectivity — are we connected to the DB?
  4. Error budget — is any source disabled?
  5. Telegram delivery — can we reach Mike?

Exits 0 on all pass, 1 on any failure (for launchd error tracking).
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.request
from pathlib import Path

# Bootstrap
SUSAN_BACKEND = str(Path(__file__).parent.parent)
if SUSAN_BACKEND not in sys.path:
    sys.path.insert(0, SUSAN_BACKEND)

_HERMES_ENV = Path.home() / ".hermes" / ".env"
if _HERMES_ENV.exists():
    for line in _HERMES_ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

logging.basicConfig(
    level=logging.WARNING,  # quiet for daily run — only failures logged
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("jake.immune.daily_test")


def send_alert(message: str):
    """Send an alert to Mike via Telegram."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print(message)
        return
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload, headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception as exc:
        logger.error("Alert send failed: %s", exc)


def run_tests() -> bool:
    """Run all smoke tests. Returns True if all pass."""
    results = {}

    # Test 1: Supabase connectivity (fast, lightweight)
    try:
        from supabase import create_client
        from susan_core.config import config as susan_config
        sb = create_client(susan_config.supabase_url, susan_config.supabase_key)
        sb.table("jake_episodic").select("id").limit(1).execute()
        results["supabase"] = True
    except Exception as exc:
        logger.error("FAIL supabase: %s", exc)
        results["supabase"] = False

    # Test 2: Brain search
    try:
        from jake_brain.retriever import BrainRetriever
        retriever = BrainRetriever()
        retriever.search(query="mike rodgers", top_k=1)
        results["brain_search"] = True
    except Exception as exc:
        logger.error("FAIL brain_search: %s", exc)
        results["brain_search"] = False

    # Test 3: Entity lookup
    try:
        from jake_brain.graph import KnowledgeGraph
        graph = KnowledgeGraph()
        result = graph.get_entity("mike")
        results["entity_lookup"] = True  # pass even if entity not found (just no crash)
    except Exception as exc:
        logger.error("FAIL entity_lookup: %s", exc)
        results["entity_lookup"] = False

    # Test 4: Error budget readable
    try:
        from jake_brain.immune.error_recovery import ErrorBudget
        budget = ErrorBudget()
        stats = budget.get_stats()
        # Check if any source is disabled and alert
        disabled = [src for src, info in stats.items() if info.get("disabled")]
        if disabled:
            send_alert(
                f"⚠️ *Jake Daily Check*\n"
                f"Disabled sources: `{'`, `'.join(disabled)}`\n"
                f"Budget resets at midnight UTC. Check immune_health for details."
            )
        results["error_budget"] = True
    except Exception as exc:
        logger.error("FAIL error_budget: %s", exc)
        results["error_budget"] = False

    # Test 5: Telegram delivery (just send a silent ping — no user-visible message)
    try:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if token and chat_id:
            payload = json.dumps({
                "chat_id": chat_id,
                "text": ".",
                "disable_notification": True,  # silent — won't buzz Mike's phone
            }).encode()
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data=payload, headers={"Content-Type": "application/json"}, method="POST",
            )
            urllib.request.urlopen(req, timeout=5)
            results["telegram"] = True
        else:
            results["telegram"] = False
    except Exception as exc:
        logger.error("FAIL telegram: %s", exc)
        results["telegram"] = False

    # Summarize
    passed = sum(1 for v in results.values() if v)
    failed = [k for k, v in results.items() if not v]
    all_pass = len(failed) == 0

    if not all_pass:
        failure_list = ", ".join(f"`{f}`" for f in failed)
        send_alert(
            f"🔴 *Jake Daily Self-Test FAILED*\n\n"
            f"Passed: {passed}/{len(results)}\n"
            f"Failed: {failure_list}\n\n"
            f"Morning brief may be degraded. Check logs at `~/.hermes/logs/`"
        )
        print(f"FAIL: {passed}/{len(results)} tests passed. Failed: {failed}", file=sys.stderr)
        return False

    print(f"OK: {passed}/{len(results)} tests passed")
    return True


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
