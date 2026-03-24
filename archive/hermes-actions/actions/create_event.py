"""Create a Google Calendar event — Tier 2 (confirm before creating)."""

from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone

from jake_brain.actions import BaseAction, SafetyTier, ActionResult, register
from jake_brain.actions.audit import log_action

logger = logging.getLogger("jake-actions")

TOKEN_URL = "https://oauth2.googleapis.com/token"
GCAL_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"


def _refresh_access_token() -> str:
    """Get a fresh access token using the refresh token from env."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise RuntimeError("GOOGLE_CLIENT_ID / CLIENT_SECRET / REFRESH_TOKEN not all set")

    payload = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        return data["access_token"]


import urllib.parse  # noqa: E402 (needed above, declared here to keep imports grouped)


@register
@dataclass
class CreateEventAction(BaseAction):
    """Create a Google Calendar event on Mike's primary calendar."""

    tier: SafetyTier = SafetyTier.CONFIRM
    name: str = "create_event"
    description: str = "Create a Google Calendar event (Tier 2 — requires confirmation)"

    title: str = ""
    start: str = ""          # ISO 8601, e.g. "2026-03-22T10:00:00-05:00"
    end: str = ""            # ISO 8601
    description_text: str = ""
    location: str = ""
    attendees: list[str] = field(default_factory=list)
    calendar_id: str = "primary"

    def preview(self) -> str:
        attendee_str = ", ".join(self.attendees) if self.attendees else "none"
        return (
            f"📅 Create calendar event\n"
            f"  Title: {self.title}\n"
            f"  Start: {self.start}\n"
            f"  End:   {self.end}\n"
            f"  Location: {self.location or 'none'}\n"
            f"  Attendees: {attendee_str}\n"
            f"  Description: {self.description_text[:100] or 'none'}"
        )

    def execute(self) -> ActionResult:
        if not self.title or not self.start or not self.end:
            return ActionResult(success=False, message="title, start, and end are required", error="validation")

        try:
            access_token = _refresh_access_token()
        except Exception as exc:
            return ActionResult(success=False, message=f"OAuth refresh failed: {exc}", error=str(exc))

        event_body: dict = {
            "summary": self.title,
            "start": {"dateTime": self.start, "timeZone": "America/Chicago"},
            "end": {"dateTime": self.end, "timeZone": "America/Chicago"},
        }
        if self.description_text:
            event_body["description"] = self.description_text
        if self.location:
            event_body["location"] = self.location
        if self.attendees:
            event_body["attendees"] = [{"email": e} for e in self.attendees]

        url = GCAL_EVENTS_URL.format(calendar_id=urllib.parse.quote(self.calendar_id))
        try:
            data = json.dumps(event_body).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                event_id = result.get("id", "unknown")
                html_link = result.get("htmlLink", "")
                msg = f"Event '{self.title}' created (id: {event_id})"
                log_action(self.name, int(self.tier), self.preview(), True, msg, {"event_id": event_id, "link": html_link})
                return ActionResult(success=True, message=msg, data={"event_id": event_id, "link": html_link})

        except urllib.error.HTTPError as e:
            err = e.read().decode()
            log_action(self.name, int(self.tier), self.preview(), False, err)
            return ActionResult(success=False, message=f"Calendar API error {e.code}", error=err)
        except Exception as exc:
            log_action(self.name, int(self.tier), self.preview(), False, str(exc))
            return ActionResult(success=False, message=str(exc), error=str(exc))
