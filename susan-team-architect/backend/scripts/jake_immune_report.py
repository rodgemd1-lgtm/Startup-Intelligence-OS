#!/usr/bin/env python3
"""Jake Immune System — Weekly Health Report.

Generates a comprehensive system health report and sends it to Mike via Telegram.
Run weekly (Sunday 8 AM) via launchd.

Usage:
  python3 scripts/jake_immune_report.py
  python3 scripts/jake_immune_report.py --dry-run  # print only, no Telegram
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Bootstrap: add Susan backend to path
SUSAN_BACKEND = str(Path(__file__).parent.parent)
if SUSAN_BACKEND not in sys.path:
    sys.path.insert(0, SUSAN_BACKEND)

# Load env from ~/.hermes/.env
_HERMES_ENV = Path.home() / ".hermes" / ".env"
if _HERMES_ENV.exists():
    for line in _HERMES_ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("jake.immune.report")


def send_telegram(message: str):
    """Send a message to Mike via Telegram."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.warning("Telegram not configured — printing to stdout only")
        print(message)
        return

    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("ok"):
            logger.info("Health report sent to Telegram (msg_id=%s)", data.get("result", {}).get("message_id"))
        else:
            logger.warning("Telegram returned error: %s", data)
    except Exception as exc:
        logger.error("Failed to send Telegram: %s", exc)
        print(message)  # fallback to stdout


def run_report(dry_run: bool = False):
    """Generate and send the weekly health report."""
    logger.info("Starting weekly immune system report...")

    sections = []

    # --- Health Monitor ---
    try:
        from jake_brain.immune.health_monitor import HealthMonitor
        monitor = HealthMonitor()
        sections.append(monitor.generate_report())
    except Exception as exc:
        logger.error("HealthMonitor failed: %s", exc)
        sections.append(f"⚠️ HealthMonitor error: {exc}")

    # --- Stale Detector ---
    try:
        from jake_brain.immune.stale_detector import StaleDetector
        detector = StaleDetector()
        sections.append(detector.format_stale_report(days=30))
    except Exception as exc:
        logger.error("StaleDetector failed: %s", exc)
        sections.append(f"⚠️ StaleDetector error: {exc}")

    # --- Consistency Scan (weekly) ---
    try:
        from jake_brain.immune.consistency_checker import ConsistencyChecker
        checker = ConsistencyChecker()
        contradictions = checker.scan_all(limit=50)
        if contradictions:
            lines = [f"**🔍 Consistency Issues Found: {len(contradictions)}**"]
            for c in contradictions[:3]:
                lines.append(f"  • A: {c['content_a'][:60]}...")
                lines.append(f"    B: {c['content_b'][:60]}...")
            if len(contradictions) > 3:
                lines.append(f"  _(+{len(contradictions) - 3} more — check jake_episodic for full list)_")
            sections.append("\n".join(lines))
        else:
            sections.append("**🔍 Consistency Check: No contradictions found** ✅")
    except Exception as exc:
        logger.error("ConsistencyChecker failed: %s", exc)
        sections.append(f"⚠️ ConsistencyChecker error: {exc}")

    full_report = "\n\n---\n\n".join(sections)

    if dry_run:
        print("\n" + "=" * 60)
        print(full_report)
        print("=" * 60 + "\n")
        logger.info("Dry run — report printed to stdout")
    else:
        send_telegram(full_report)
        logger.info("Weekly health report complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Jake Immune System — Weekly Health Report")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout, don't send Telegram")
    args = parser.parse_args()
    run_report(dry_run=args.dry_run)
