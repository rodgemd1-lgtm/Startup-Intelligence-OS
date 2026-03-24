"""Email Alert Scanner — detect urgent Oracle/work emails via osascript.

Urgency scoring:
  Base score from sender VIP list + keyword matching + subject patterns
  P0 (≥0.75): Send Telegram alert immediately
  P1 (≥0.50): Include in next batched notification
  P2/P3: Skip real-time alert (daily brief handles these)

State:
  Uses EventBus.seen_events to avoid re-alerting on same message ID
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

from .event_bus import EventBus, NervousEvent, EventType

logger = logging.getLogger(__name__)

# ── Urgency config ─────────────────────────────────────────────────────────

# VIP senders → urgency boost (name fragment → boost)
VIP_SENDERS: dict[str, float] = {
    "matt cohlmia": 0.4,
    "cohlmia": 0.4,
    "seema verma": 0.4,
    "bharat sutariya": 0.35,
    "elizabeth krulish": 0.3,
    "krulish": 0.3,
    "oracle": 0.2,
    "director": 0.2,
    "vp ": 0.25,
    "vice president": 0.25,
    "cto": 0.3,
    "ceo": 0.3,
    "ellen": 0.25,
}

# Subject/body keywords → urgency boost
URGENT_KEYWORDS: dict[str, float] = {
    "urgent": 0.4,
    "asap": 0.35,
    "action required": 0.4,
    "action needed": 0.35,
    "critical": 0.4,
    "immediately": 0.3,
    "deadline": 0.25,
    "by eod": 0.3,
    "by end of day": 0.3,
    "overdue": 0.35,
    "approval needed": 0.35,
    "please respond": 0.2,
    "response needed": 0.25,
    "security alert": 0.45,
    "incident": 0.35,
    "outage": 0.4,
    "escalation": 0.35,
    "p0": 0.5,
    "p1": 0.4,
}

# Minimum urgency to emit a real-time alert
ALERT_THRESHOLD = 0.50


def _fetch_recent_emails_graph(max_emails: int = 20) -> list[dict[str, Any]]:
    """Fetch recent Oracle emails via Microsoft Graph API (preferred — no Mail.app dependency)."""
    try:
        # Import the Graph auth helper from the scripts dir
        # This may raise ImportError if msal is not installed — that's OK,
        # the caller falls back to osascript.
        scripts_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        scripts_dir = os.path.join(scripts_dir, "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)

        from ms_graph_auth import get_access_token
        import urllib.request as _req
        import urllib.parse as _parse

        token = get_access_token()
        if not token:
            return []

        from datetime import timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = _parse.urlencode({
            "$filter": f"receivedDateTime ge {cutoff}",
            "$select": "id,subject,from,receivedDateTime,isRead,importance",
            "$top": max_emails,
            "$orderby": "receivedDateTime desc",
        })
        url = f"https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?{params}"
        request = _req.Request(url, headers={"Authorization": f"Bearer {token}"})
        with _req.urlopen(request, timeout=15) as resp:
            data = json.loads(resp.read())

        results = []
        for msg in data.get("value", []):
            sender_info = msg.get("from", {}).get("emailAddress", {})
            sender = f"{sender_info.get('name', '')} <{sender_info.get('address', '')}>".strip(" <>")
            results.append({
                "id": msg.get("id", ""),
                "subject": msg.get("subject", "(no subject)"),
                "sender": sender,
                "date": msg.get("receivedDateTime", ""),
                "read": msg.get("isRead", True),
                "importance": msg.get("importance", "normal"),
            })
        return results

    except Exception as exc:
        logger.debug("Graph API email fetch failed: %s", exc)
        return []


def _fetch_recent_emails_osascript(max_emails: int = 20) -> list[dict[str, Any]]:
    """Fallback: Fetch recent Oracle emails via osascript (may timeout if Mail.app is slow)."""
    script = f"""
ObjC.import('Foundation');

function run() {{
    var app = Application('Mail');
    var results = [];
    var accounts = app.accounts();

    for (var i = 0; i < accounts.length; i++) {{
        var account = accounts[i];
        var name = account.name();
        if (!name.toLowerCase().includes('exchange') && !name.toLowerCase().includes('oracle')) {{
            continue;
        }}

        var mailboxes = account.mailboxes();
        for (var j = 0; j < mailboxes.length; j++) {{
            var mb = mailboxes[j];
            if (mb.name().toLowerCase() !== 'inbox') continue;

            var messages = mb.messages();
            var count = Math.min({max_emails}, messages.length);

            for (var k = 0; k < count; k++) {{
                try {{
                    var msg = messages[k];
                    results.push({{
                        id: msg.messageId(),
                        subject: msg.subject(),
                        sender: msg.sender(),
                        date: msg.dateSent().toString(),
                        read: msg.readStatus()
                    }});
                }} catch(e) {{}}
            }}
            break;
        }}
        break;
    }}

    return JSON.stringify(results);
}}
"""
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout.strip())
    except Exception as exc:
        logger.debug("osascript email fallback failed: %s", exc)
    return []


def _fetch_recent_emails(max_emails: int = 20) -> list[dict[str, Any]]:
    """Fetch recent Oracle emails. Tries Graph API first, falls back to osascript."""
    # Prefer Graph API (fast, reliable, no Mail.app dependency)
    emails = _fetch_recent_emails_graph(max_emails)
    if emails:
        return emails
    # Fallback: osascript (unreliable if Mail.app has been running long)
    logger.debug("Graph API returned nothing — trying osascript fallback")
    return _fetch_recent_emails_osascript(max_emails)


def _score_urgency(subject: str, sender: str, is_unread: bool) -> float:
    """Score email urgency 0.0 – 1.0."""
    score = 0.0
    subject_lower = subject.lower()
    sender_lower = sender.lower()

    # VIP sender boost
    for fragment, boost in VIP_SENDERS.items():
        if fragment in sender_lower:
            score += boost
            break  # one sender boost max

    # Keyword boost (subject)
    for keyword, boost in URGENT_KEYWORDS.items():
        if keyword in subject_lower:
            score += boost
            break  # one keyword boost max

    # Unread boost
    if is_unread:
        score += 0.1

    return min(score, 1.0)


class EmailAlertScanner:
    """Scan recent emails for urgency and emit events to the bus."""

    def __init__(self, bus: EventBus):
        self.bus = bus

    def scan(self) -> list[NervousEvent]:
        """Scan emails, emit new urgent events. Returns list of new events emitted."""
        emails = _fetch_recent_emails(max_emails=20)
        new_events: list[NervousEvent] = []

        for email in emails:
            msg_id = email.get("id", "")
            subject = email.get("subject", "(no subject)")
            sender = email.get("sender", "")
            is_unread = not email.get("read", True)

            urgency = _score_urgency(subject, sender, is_unread)
            if urgency < ALERT_THRESHOLD:
                continue

            event_id = f"email:{msg_id}"
            if not msg_id:
                # Fallback ID from subject + sender
                import hashlib
                event_id = "email:" + hashlib.md5(f"{subject}{sender}".encode()).hexdigest()[:12]

            body = f"From: {sender}\nSubject: {subject}"
            if urgency >= 0.75:
                tier = "P0 — Act now"
            else:
                tier = "P1 — Check soon"

            event = NervousEvent(
                event_id=event_id,
                event_type=EventType.URGENT_EMAIL,
                title=f"Urgent email: {subject[:60]}",
                body=f"{body}\nUrgency: {tier} ({urgency:.0%})",
                urgency=urgency,
                source="oracle_mail",
                metadata={"sender": sender, "subject": subject, "unread": is_unread},
            )

            if self.bus.emit(event):
                new_events.append(event)
                logger.info("Urgent email event: %s (urgency=%.2f)", subject, urgency)

        self.bus.update_email_check()
        return new_events
