#!/usr/bin/env python3
"""jake_daily_self_test.py — Jake's daily system health check.

Runs all subsystem checks and reports pass/fail to Telegram.
Designed to run as a cron job or on-demand.

Usage:
    python3 jake_daily_self_test.py              # stdout only
    python3 jake_daily_self_test.py --telegram   # report to Telegram
    python3 jake_daily_self_test.py --fail-only  # only report failures
    python3 jake_daily_self_test.py --quiet      # suppress stdout, only Telegram

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

SUSAN_BACKEND = os.path.expanduser(
    "~/Startup-Intelligence-OS/susan-team-architect/backend"
)
if SUSAN_BACKEND not in sys.path:
    sys.path.insert(0, SUSAN_BACKEND)

HERMES_HOME = os.path.expanduser("~/.hermes")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger("jake_daily_self_test")


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def load_env():
    hermes_env = os.path.join(HERMES_HOME, ".env")
    if os.path.exists(hermes_env):
        with open(hermes_env) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())


# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------

class CheckResult:
    def __init__(self, name: str, passed: bool, detail: str):
        self.name = name
        self.passed = passed
        self.detail = detail

    def icon(self) -> str:
        return "✅" if self.passed else "❌"

    def __repr__(self) -> str:
        return f"{self.icon()} {self.name}: {self.detail}"


def check_hermes_gateway() -> CheckResult:
    """Verify Hermes gateway process is running."""
    try:
        pid_file = os.path.join(HERMES_HOME, "gateway.pid")
        if not os.path.exists(pid_file):
            return CheckResult("Hermes Gateway", False, "gateway.pid not found")
        with open(pid_file) as f:
            raw = f.read().strip()
        # gateway.pid may contain JSON {"pid": 12345, ...} or just a plain int
        try:
            pid = int(raw)
        except ValueError:
            try:
                pid = int(json.loads(raw).get("pid", 0))
            except Exception:
                return CheckResult("Hermes Gateway", False, f"Cannot parse gateway.pid: {raw[:80]}")
        # Check if process is alive
        result = subprocess.run(
            ["kill", "-0", str(pid)], capture_output=True
        )
        if result.returncode == 0:
            return CheckResult("Hermes Gateway", True, f"running (PID {pid})")
        return CheckResult("Hermes Gateway", False, f"PID {pid} not alive — gateway is down")
    except Exception as e:
        return CheckResult("Hermes Gateway", False, str(e))


def check_telegram_api() -> CheckResult:
    """Verify Telegram bot is reachable."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("HERMES_TELEGRAM_TOKEN")
    if not bot_token:
        return CheckResult("Telegram API", False, "TELEGRAM_BOT_TOKEN not set")
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/getMe",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("ok"):
                bot_name = data.get("result", {}).get("username", "?")
                return CheckResult("Telegram API", True, f"@{bot_name} connected")
            return CheckResult("Telegram API", False, f"API error: {data}")
    except Exception as e:
        return CheckResult("Telegram API", False, str(e))


def check_brain_freshness() -> CheckResult:
    """Verify brain has recent data (< 24 hours old)."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
        if not url or not key:
            return CheckResult("Brain Freshness", False, "Supabase credentials missing")
        sb = create_client(url, key)
        r = sb.table("jake_episodic").select("created_at").order(
            "created_at", desc=True
        ).limit(1).execute()
        if not r.data:
            return CheckResult("Brain Freshness", False, "No episodic memories found")
        last_ts = r.data[0]["created_at"]
        last_dt = datetime.fromisoformat(str(last_ts).replace("Z", "+00:00"))
        age_hours = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
        if age_hours < 24:
            return CheckResult("Brain Freshness", True, f"Last ingest {age_hours:.1f}h ago")
        return CheckResult("Brain Freshness", False, f"Stale — last ingest {age_hours:.1f}h ago")
    except Exception as e:
        return CheckResult("Brain Freshness", False, str(e))


def check_supabase_connection() -> CheckResult:
    """Verify Supabase is reachable and key tables exist."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
        if not url or not key:
            return CheckResult("Supabase", False, "Credentials missing")
        sb = create_client(url, key)
        tables = ["jake_episodic", "jake_semantic", "jake_goals", "jake_tasks"]
        counts = {}
        for table in tables:
            r = sb.table(table).select("id", count="exact").execute()
            counts[table] = r.count or 0
        summary = ", ".join(f"{k.replace('jake_','')}={v}" for k, v in counts.items())
        return CheckResult("Supabase", True, summary)
    except Exception as e:
        return CheckResult("Supabase", False, str(e))


def check_daily_scripts() -> CheckResult:
    """Verify all three daily cadence scripts exist."""
    scripts_dir = os.path.join(SUSAN_BACKEND, "scripts")
    required = [
        "jake_morning_brief.py",
        "jake_midday_pulse.py",
        "jake_eod_report.py",
    ]
    missing = [s for s in required if not os.path.exists(os.path.join(scripts_dir, s))]
    if missing:
        return CheckResult("Daily Scripts", False, f"Missing: {', '.join(missing)}")
    return CheckResult("Daily Scripts", True, "7AM + 12PM + 6PM scripts present")


def check_cron_freshness() -> CheckResult:
    """Verify key cron jobs have run recently via log file mtimes.

    'no log' is a warning (first run pending), not a failure.
    Stale logs (older than threshold) are failures.
    """
    log_dir = os.path.join(HERMES_HOME, "logs")
    scripts_dir = os.path.join(SUSAN_BACKEND, "scripts")
    important_logs = [
        (os.path.join(log_dir, "jake_morning_brief.log"), 26, "morning-brief",
         os.path.join(scripts_dir, "jake_morning_brief.py")),
        (os.path.join(log_dir, "pulse.log"), 1, "pulse-monitor", None),
        (os.path.join(log_dir, "brain_morning_brief.log"), 26, "brain-morning-brief",
         os.path.join(scripts_dir, "brain_morning_brief.py")),
    ]
    ok_results = []
    warn_results = []
    failed = []
    for log_file, max_hours, label, script_path in important_logs:
        if not os.path.exists(log_file):
            # If the script exists, treat as "never run yet" (acceptable on first day)
            if script_path and os.path.exists(script_path):
                warn_results.append(f"{label} (script present, not yet run)")
            else:
                failed.append(f"{label} (no log, no script)")
            continue
        mtime = os.path.getmtime(log_file)
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        if age_hours > max_hours:
            failed.append(f"{label} ({age_hours:.0f}h stale)")
        else:
            ok_results.append(f"{label} OK")

    if failed:
        detail = f"Stale: {', '.join(failed)}"
        if warn_results:
            detail += f" | Pending first run: {', '.join(warn_results)}"
        return CheckResult("Cron Jobs", False, detail)
    detail = f"{len(ok_results)} healthy"
    if warn_results:
        detail += f", {len(warn_results)} pending first run"
    return CheckResult("Cron Jobs", True, detail)


def check_launchd_exits() -> CheckResult:
    """Check if any Jake launchd jobs have non-zero exit codes."""
    try:
        result = subprocess.run(
            ["launchctl", "list"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split("\n")
        failing = []
        for line in lines:
            parts = line.split("\t")
            if len(parts) >= 3 and "jake" in parts[2]:
                exit_code = parts[1].strip()
                label = parts[2].strip()
                # Skip expected non-running jobs (exit 0 or "-")
                if exit_code not in ("0", "-") and exit_code != "":
                    failing.append(f"{label.replace('com.jake.','')} (exit {exit_code})")
        if failing:
            return CheckResult("LaunchD Jobs", False, f"Failing: {', '.join(failing[:3])}")
        return CheckResult("LaunchD Jobs", True, "No failing launchd jobs")
    except Exception as e:
        return CheckResult("LaunchD Jobs", False, str(e))


def check_mail_app() -> CheckResult:
    """Quick check if Mail.app is responsive."""
    try:
        script = 'tell application "Mail" to return name of accounts'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            accounts = result.stdout.strip()[:80]
            return CheckResult("Mail.app", True, f"responsive ({accounts})")
        return CheckResult("Mail.app", False, f"Not responding (exit {result.returncode})")
    except subprocess.TimeoutExpired:
        return CheckResult("Mail.app", False, "Timed out after 10s")
    except Exception as e:
        return CheckResult("Mail.app", False, str(e))


def check_correction_handler() -> CheckResult:
    """Check learner plugin state for correction tracking."""
    state_file = os.path.join(HERMES_HOME, "logs", "learner_state.json")
    if not os.path.exists(state_file):
        return CheckResult("Correction Handler", False, "learner_state.json not found")
    try:
        with open(state_file) as f:
            state = json.load(f)
        corrections = state.get("corrections_count", 0)
        last_correction = state.get("last_correction") or "never"
        return CheckResult(
            "Correction Handler",
            True,  # Existence of state file is sufficient — 0 corrections is valid
            f"{corrections} corrections logged, last: {str(last_correction)[:20]}"
        )
    except Exception as e:
        return CheckResult("Correction Handler", False, str(e))


def check_autonomous_worker() -> CheckResult:
    """Check if autonomous worker plist is enabled.

    DISABLED is a known state — the worker was intentionally disabled
    until the underlying script (jake_autonomous_worker.sh) is built.
    This returns True with a warning note rather than failing the test.
    """
    plist = os.path.expanduser(
        "~/Library/LaunchAgents/com.jake.autonomous-worker.plist"
    )
    plist_disabled = plist + ".disabled"
    scripts_dir = os.path.join(SUSAN_BACKEND, "scripts")
    worker_script = os.path.join(scripts_dir, "jake_autonomous_worker.sh")
    script_exists = os.path.exists(worker_script)

    if os.path.exists(plist):
        result = subprocess.run(
            ["launchctl", "list", "com.jake.autonomous-worker"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return CheckResult("Autonomous Worker", True, "loaded in launchd")
        return CheckResult("Autonomous Worker", False, "plist exists but NOT loaded")
    elif os.path.exists(plist_disabled):
        # Intentionally disabled — not a failure if script also doesn't exist
        if not script_exists:
            return CheckResult(
                "Autonomous Worker", True,
                "disabled (intentional — script not yet built)"
            )
        return CheckResult(
            "Autonomous Worker", False,
            "script exists but plist disabled — enable with: "
            "mv ~/Library/LaunchAgents/com.jake.autonomous-worker.plist.disabled "
            "~/Library/LaunchAgents/com.jake.autonomous-worker.plist && launchctl load ..."
        )
    return CheckResult("Autonomous Worker", True, "not configured (optional component)")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_checks() -> list[CheckResult]:
    checks = [
        check_hermes_gateway,
        check_telegram_api,
        check_supabase_connection,
        check_brain_freshness,
        check_daily_scripts,
        check_cron_freshness,
        check_launchd_exits,
        check_mail_app,
        check_correction_handler,
        check_autonomous_worker,
    ]
    results = []
    for check_fn in checks:
        try:
            r = check_fn()
        except Exception as e:
            r = CheckResult(check_fn.__name__, False, f"Exception: {e}")
        results.append(r)
        logger.info("%s", r)
    return results


def format_report(results: list[CheckResult], now: datetime) -> str:
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    total = len(results)

    time_str = now.strftime("%-I:%M %p")
    date_str = now.strftime("%a %b %-d")

    score = len(passed)
    pct = int((score / total) * 100) if total else 0

    if pct >= 90:
        grade = "🟢 HEALTHY"
    elif pct >= 70:
        grade = "🟡 DEGRADED"
    else:
        grade = "🔴 CRITICAL"

    lines = [
        f"🔬 *JAKE DAILY SELF-TEST — {date_str} {time_str}*",
        f"{grade} — {score}/{total} checks passing ({pct}%)\n",
    ]

    if failed:
        lines.append("❌ *FAILURES*")
        for r in failed:
            lines.append(f"  {r.icon()} {r.name}: {r.detail}")
        lines.append("")

    lines.append("✅ *PASSING*")
    for r in passed:
        lines.append(f"  {r.icon()} {r.name}: {r.detail}")

    if failed:
        lines.append("\n⚠️ *ACTION NEEDED:* Fix the failures above.")
    else:
        lines.append("\n🤙 All systems go. Jake is operational.")

    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("HERMES_TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    try:
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            if data.get("ok"):
                logger.info("Telegram: delivered")
                return True
            logger.error("Telegram API error: %s", data)
            return False
    except Exception as e:
        logger.error("Telegram send failed: %s", e)
        return False


def main():
    parser = argparse.ArgumentParser(description="Jake Daily Self-Test")
    parser.add_argument("--telegram", action="store_true", help="Send report to Telegram")
    parser.add_argument("--fail-only", action="store_true", help="Only report if there are failures")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout output")
    args = parser.parse_args()

    load_env()
    now = datetime.now(timezone.utc).astimezone()

    logger.info("Running Jake daily self-test...")
    results = run_all_checks()

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total = len(results)

    report = format_report(results, now)

    if not args.quiet:
        print("\n" + "=" * 60)
        print(report)
        print("=" * 60 + "\n")

    if args.telegram:
        # --fail-only: skip Telegram if everything is passing
        if args.fail_only and failed == 0:
            logger.info("All checks passed, skipping Telegram (--fail-only)")
        else:
            logger.info("Sending report to Telegram...")
            send_telegram(report)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
