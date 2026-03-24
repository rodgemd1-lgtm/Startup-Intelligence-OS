"""Send a Telegram message — Tier 1 (auto-execute)."""

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

TELEGRAM_BASE = "https://api.telegram.org/bot{token}/sendMessage"


@register
@dataclass
class SendTelegramAction(BaseAction):
    """Send a Telegram message to Mike's chat. Tier 1 — auto-execute."""

    tier: SafetyTier = SafetyTier.AUTO
    name: str = "send_telegram"
    description: str = "Send a Telegram message (Tier 1 — auto-execute)"

    text: str = ""
    chat_id: str | None = None     # defaults to TELEGRAM_CHAT_ID env var
    parse_mode: str = "Markdown"   # or "HTML"

    def preview(self) -> str:
        target = self.chat_id or os.environ.get("TELEGRAM_CHAT_ID", "Mike's chat")
        return f"💬 Send Telegram message\n  To: {target}\n  Text: {self.text[:200]}{'...' if len(self.text) > 200 else ''}"

    def execute(self) -> ActionResult:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            return ActionResult(success=False, message="TELEGRAM_BOT_TOKEN not set", error="missing env var")

        chat_id = self.chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        if not chat_id:
            return ActionResult(success=False, message="TELEGRAM_CHAT_ID not set", error="missing env var")

        if not self.text:
            return ActionResult(success=False, message="text is required", error="validation")

        url = TELEGRAM_BASE.format(token=token)
        payload = {
            "chat_id": chat_id,
            "text": self.text,
            "parse_mode": self.parse_mode,
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                msg_id = result.get("result", {}).get("message_id", "unknown")
                msg = f"Telegram message sent (id: {msg_id})"
                log_action(self.name, int(self.tier), self.preview(), True, msg, {"message_id": msg_id})
                return ActionResult(success=True, message=msg, data={"message_id": msg_id})

        except urllib.error.HTTPError as e:
            err = e.read().decode()
            log_action(self.name, int(self.tier), self.preview(), False, err)
            return ActionResult(success=False, message=f"Telegram API error {e.code}", error=err)
        except Exception as exc:
            log_action(self.name, int(self.tier), self.preview(), False, str(exc))
            return ActionResult(success=False, message=str(exc), error=str(exc))
