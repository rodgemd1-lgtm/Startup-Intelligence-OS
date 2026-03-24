"""Error Recovery — auto-retry with exponential backoff + per-source error budgets.

Error budget rules:
  - Each source (google-calendar, apple-mail, apple-reminders, voyage-ai, supabase, telegram)
    gets 5 failures/day before Jake disables it and alerts Mike.
  - Budget resets at midnight UTC.
  - Retry policy: 3 attempts, exponential backoff (2s, 4s, 8s).
  - On source disable: Telegram alert sent to Mike.
"""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger("jake.immune.error_recovery")

# Budget file — simple JSON, no DB dependency for bootstrap resilience
_BUDGET_FILE = Path.home() / ".hermes" / "immune_error_budget.json"
_MAX_FAILURES_PER_DAY = 5
_MAX_RETRY_ATTEMPTS = 3
_BACKOFF_BASE = 2.0  # seconds


class ErrorBudget:
    """Per-source failure tracker backed by a JSON file.

    Structure: { "source_name": { "date": "YYYY-MM-DD", "failures": int, "disabled": bool } }
    """

    def __init__(self, budget_file: Path = _BUDGET_FILE):
        self.budget_file = budget_file
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.budget_file.exists():
            try:
                self._data = json.loads(self.budget_file.read_text())
            except Exception:
                self._data = {}

    def _save(self):
        try:
            self.budget_file.parent.mkdir(parents=True, exist_ok=True)
            self.budget_file.write_text(json.dumps(self._data, indent=2))
        except Exception as exc:
            logger.warning("Could not save error budget: %s", exc)

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _entry(self, source: str) -> dict:
        today = self._today()
        entry = self._data.get(source, {})
        # Reset if new day
        if entry.get("date") != today:
            entry = {"date": today, "failures": 0, "disabled": False}
            self._data[source] = entry
        return entry

    def record_failure(self, source: str) -> int:
        """Record a failure for source. Returns current failure count."""
        entry = self._entry(source)
        entry["failures"] += 1
        self._save()
        return entry["failures"]

    def record_success(self, source: str):
        """A success does NOT reset the budget — budget is day-scoped."""
        # Just refresh the entry to ensure it's today
        self._entry(source)

    def is_disabled(self, source: str) -> bool:
        return self._entry(source).get("disabled", False)

    def disable(self, source: str):
        entry = self._entry(source)
        entry["disabled"] = True
        self._save()
        logger.warning("Source DISABLED (budget exhausted): %s", source)

    def get_stats(self) -> dict[str, dict]:
        today = self._today()
        return {
            src: {**entry}
            for src, entry in self._data.items()
            if entry.get("date") == today
        }

    def reset_source(self, source: str):
        """Manually re-enable a disabled source (called by Mike or admin)."""
        entry = self._entry(source)
        entry["disabled"] = False
        entry["failures"] = 0
        self._save()
        logger.info("Source re-enabled: %s", source)


def _send_telegram_alert(message: str):
    """Fire-and-forget Telegram alert to Mike."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.warning("Telegram alert skipped — no token/chat_id configured")
        return
    try:
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
        urllib.request.urlopen(req, timeout=5)
    except Exception as exc:
        logger.warning("Telegram alert failed: %s", exc)


class ErrorRecovery:
    """Main interface for the immune system's error recovery component."""

    def __init__(self):
        self.budget = ErrorBudget()

    def run_with_retry(
        self,
        fn: Callable,
        source: str,
        *,
        max_attempts: int = _MAX_RETRY_ATTEMPTS,
        backoff_base: float = _BACKOFF_BASE,
        **kwargs,
    ) -> Any:
        """Run fn with exponential backoff. Track failures against source budget.

        Raises the last exception if all attempts fail.
        Disables source and alerts Mike if budget is exhausted.
        """
        if self.budget.is_disabled(source):
            raise RuntimeError(
                f"Source '{source}' is currently disabled — error budget exhausted today. "
                "Mike has been notified. Budget resets at midnight UTC."
            )

        last_exc = None
        for attempt in range(1, max_attempts + 1):
            try:
                result = fn(**kwargs) if kwargs else fn()
                self.budget.record_success(source)
                return result
            except Exception as exc:
                last_exc = exc
                failures = self.budget.record_failure(source)
                logger.warning(
                    "Source '%s' failure %d/%d (attempt %d/%d): %s",
                    source, failures, _MAX_FAILURES_PER_DAY, attempt, max_attempts, exc,
                )

                if failures >= _MAX_FAILURES_PER_DAY:
                    self.budget.disable(source)
                    _send_telegram_alert(
                        f"🚨 *Jake Immune System Alert*\n\n"
                        f"Source `{source}` has been *disabled* — "
                        f"{failures} failures today (limit: {_MAX_FAILURES_PER_DAY}).\n\n"
                        f"Last error: `{exc}`\n\n"
                        f"Budget resets at midnight UTC. "
                        f"Or call `immune_health` to manually re-enable."
                    )
                    raise RuntimeError(
                        f"Source '{source}' disabled after {failures} failures. Mike notified."
                    ) from exc

                if attempt < max_attempts:
                    sleep_secs = backoff_base ** attempt
                    logger.info("Retrying '%s' in %.1fs...", source, sleep_secs)
                    time.sleep(sleep_secs)

        raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Decorator for easy use
# ---------------------------------------------------------------------------

def with_retry(source: str, max_attempts: int = 3, backoff_base: float = 2.0):
    """Decorator that wraps a function with error recovery + retry."""
    recovery = ErrorRecovery()

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return recovery.run_with_retry(
                lambda: fn(*args, **kwargs),
                source=source,
                max_attempts=max_attempts,
                backoff_base=backoff_base,
            )
        return wrapper
    return decorator
