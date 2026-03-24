"""Send email via Resend API — Tier 2 (confirm before sending)."""

from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error
from dataclasses import dataclass

from jake_brain.actions import BaseAction, SafetyTier, ActionResult, register
from jake_brain.actions.audit import log_action

logger = logging.getLogger("jake-actions")

RESEND_API_URL = "https://api.resend.com/emails"
DEFAULT_FROM = "Jake <jake@rodgemd.com>"


@register
@dataclass
class SendEmailAction(BaseAction):
    """Send an email on Mike's behalf via Resend API."""

    tier: SafetyTier = SafetyTier.CONFIRM
    name: str = "send_email"
    description: str = "Send an email via Resend API (Tier 2 — requires confirmation)"

    to: str = ""
    subject: str = ""
    body: str = ""
    from_addr: str = DEFAULT_FROM
    reply_to: str | None = None

    def preview(self) -> str:
        return (
            f"📧 Send email\n"
            f"  To: {self.to}\n"
            f"  From: {self.from_addr}\n"
            f"  Subject: {self.subject}\n"
            f"  Body preview: {self.body[:200]}{'...' if len(self.body) > 200 else ''}"
        )

    def execute(self) -> ActionResult:
        api_key = os.environ.get("RESEND_API_KEY")
        if not api_key:
            return ActionResult(success=False, message="RESEND_API_KEY not set", error="missing env var")

        if not self.to or not self.subject or not self.body:
            return ActionResult(success=False, message="to, subject, and body are required", error="validation")

        payload = {
            "from": self.from_addr,
            "to": [self.to],
            "subject": self.subject,
            "text": self.body,
        }
        if self.reply_to:
            payload["reply_to"] = self.reply_to

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                RESEND_API_URL,
                data=data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read().decode())
                email_id = body.get("id", "unknown")
                msg = f"Email sent to {self.to} (id: {email_id})"
                log_action(self.name, int(self.tier), self.preview(), True, msg, {"email_id": email_id})
                return ActionResult(success=True, message=msg, data=body)

        except urllib.error.HTTPError as e:
            err = e.read().decode()
            log_action(self.name, int(self.tier), self.preview(), False, err)
            return ActionResult(success=False, message=f"Resend API error {e.code}", error=err)
        except Exception as exc:
            log_action(self.name, int(self.tier), self.preview(), False, str(exc))
            return ActionResult(success=False, message=str(exc), error=str(exc))
