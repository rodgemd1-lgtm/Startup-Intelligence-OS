"""Set an Apple Reminder via osascript — Tier 1 (auto-execute)."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass

from jake_brain.actions import BaseAction, SafetyTier, ActionResult, register
from jake_brain.actions.audit import log_action

logger = logging.getLogger("jake-actions")

DEFAULT_LIST = "Mike"  # Mike's primary Reminders list on this Mac


@register
@dataclass
class SetReminderAction(BaseAction):
    """Create an Apple Reminders entry via osascript. Tier 1 — no confirmation needed."""

    tier: SafetyTier = SafetyTier.AUTO
    name: str = "set_reminder"
    description: str = "Create an Apple Reminder via osascript (Tier 1 — auto-execute)"

    title: str = ""
    due_date: str | None = None    # e.g. "March 25, 2026 at 9:00 AM"
    notes: str = ""
    list_name: str = DEFAULT_LIST

    def preview(self) -> str:
        due = f"\n  Due: {self.due_date}" if self.due_date else ""
        notes = f"\n  Notes: {self.notes[:100]}" if self.notes else ""
        return f"⏰ Set reminder\n  Title: {self.title}{due}{notes}\n  List: {self.list_name}"

    def execute(self) -> ActionResult:
        if not self.title:
            return ActionResult(success=False, message="title is required", error="validation")

        # Build JXA script
        props = f'name: "{self.title}"'
        if self.notes:
            escaped_notes = self.notes.replace('"', '\\"')
            props += f', body: "{escaped_notes}"'

        if self.due_date:
            escaped_due = self.due_date.replace('"', '\\"')
            script = f"""
tell application "Reminders"
    set targetList to list "{self.list_name}"
    set newReminder to make new reminder at end of reminders of targetList with properties {{{props}}}
    set due date of newReminder to date "{escaped_due}"
end tell
return "ok"
"""
        else:
            script = f"""
tell application "Reminders"
    set targetList to list "{self.list_name}"
    make new reminder at end of reminders of targetList with properties {{{props}}}
end tell
return "ok"
"""

        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                err = result.stderr.strip()
                log_action(self.name, int(self.tier), self.preview(), False, err)
                return ActionResult(success=False, message=f"osascript error: {err}", error=err)

            msg = f"Reminder '{self.title}' set in '{self.list_name}'"
            log_action(self.name, int(self.tier), self.preview(), True, msg)
            return ActionResult(success=True, message=msg, data={"list": self.list_name})

        except subprocess.TimeoutExpired:
            err = "osascript timed out (15s)"
            log_action(self.name, int(self.tier), self.preview(), False, err)
            return ActionResult(success=False, message=err, error=err)
        except Exception as exc:
            log_action(self.name, int(self.tier), self.preview(), False, str(exc))
            return ActionResult(success=False, message=str(exc), error=str(exc))
