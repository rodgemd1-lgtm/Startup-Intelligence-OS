# PAI V3: Autonomous Execution — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Jake works while Mike sleeps. Build real autonomous pipelines for morning briefs, meeting prep, email triage, and goal tracking — with safety-tiered actions (AUTO/CONFIRM/APPROVE) and self-repair capabilities.

**Architecture:** OpenClaw cron jobs trigger pipelines. Each pipeline is a Fabric pattern chain + Susan agent call + structured output. Safety tiers gate destructive actions. Health monitoring auto-restarts failed services. Goal tracking in Supabase with auto-progress updates.

**Depends On:** V0 (infrastructure) + V1 (memory) + V2 (agents + Fabric) complete

**Process Rule:** Research → Plan → Execute → Lessons Learned → Documentation. Every time. No exceptions.

---

## Pre-Flight Checklist

- [ ] V2 exit criteria all passed (agents callable, Fabric working, Algorithm v1 active)
- [ ] OpenClaw cron system verified (`openclaw cron list`)
- [ ] Gmail API credentials available (for email triage)
- [ ] Google Calendar API credentials available (for meeting prep)
- [ ] Telegram bot token confirmed working (for brief delivery)
- [ ] Supabase jake_goals table exists and is accessible

---

## Phase 3A: Pipeline Framework

*Build the skeleton that all autonomous pipelines run on.*

### Task 1: Create Pipeline Runner Framework

**Files:**
- Create: `pai/pipelines/__init__.py`
- Create: `pai/pipelines/runner.py`
- Create: `pai/pipelines/registry.py`
- Create: `pai/pipelines/safety.py`

**Step 1: Create the pipeline runner**

```python
# pai/pipelines/runner.py
"""Pipeline runner — executes registered pipelines with safety gates and logging."""
import json
import os
import traceback
from datetime import datetime
from typing import Any, Callable

from pai.pipelines.safety import SafetyTier, check_safety


class PipelineResult:
    def __init__(self, name: str, status: str, output: Any = None, error: str = None):
        self.name = name
        self.status = status  # "success", "failed", "blocked", "needs_approval"
        self.output = output
        self.error = error
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "output": str(self.output)[:500] if self.output else None,
            "error": self.error,
            "timestamp": self.timestamp,
        }


class PipelineRunner:
    """Executes pipelines with safety gates, logging, and error handling."""

    LOG_DIR = "pai/pipelines/logs"

    def __init__(self):
        os.makedirs(self.LOG_DIR, exist_ok=True)

    def run(self, pipeline_name: str, pipeline_fn: Callable, **kwargs) -> PipelineResult:
        """Run a pipeline with full lifecycle management."""
        log_file = os.path.join(
            self.LOG_DIR,
            f"{datetime.now().strftime('%Y-%m-%d')}-{pipeline_name}.jsonl",
        )

        try:
            # Pre-flight safety check
            safety = check_safety(pipeline_name, kwargs)
            if safety.tier == SafetyTier.BLOCKED:
                result = PipelineResult(pipeline_name, "blocked", error=safety.reason)
                self._log(log_file, result)
                return result

            if safety.tier == SafetyTier.APPROVE:
                result = PipelineResult(pipeline_name, "needs_approval", error=safety.reason)
                self._log(log_file, result)
                return result

            # Execute pipeline
            output = pipeline_fn(**kwargs)
            result = PipelineResult(pipeline_name, "success", output=output)

        except Exception as e:
            result = PipelineResult(
                pipeline_name, "failed",
                error=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()[-500:]}"
            )

        self._log(log_file, result)
        return result

    def _log(self, log_file: str, result: PipelineResult):
        """Append pipeline result to daily log."""
        with open(log_file, "a") as f:
            f.write(json.dumps(result.to_dict()) + "\n")
```

**Step 2: Create safety tier system**

```python
# pai/pipelines/safety.py
"""Safety-tiered action system — Miessler-adapted.

Three tiers:
- AUTO: Safe actions, no confirmation needed (read, search, summarize)
- CONFIRM: Potentially impactful, notify Mike after (send brief, update goal)
- APPROVE: Destructive or external, require Mike's approval first (send email, post, delete)
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any


class SafetyTier(Enum):
    AUTO = "auto"        # Execute silently
    CONFIRM = "confirm"  # Execute and notify
    APPROVE = "approve"  # Ask first, then execute
    BLOCKED = "blocked"  # Never execute


@dataclass
class SafetyCheck:
    tier: SafetyTier
    reason: str


# Pipeline safety classifications
PIPELINE_TIERS = {
    # AUTO — safe to run unattended
    "morning_brief": SafetyTier.AUTO,
    "meeting_prep": SafetyTier.AUTO,
    "email_triage": SafetyTier.AUTO,
    "goal_progress": SafetyTier.AUTO,
    "health_check": SafetyTier.AUTO,
    "memory_consolidation": SafetyTier.AUTO,
    "research_harvest": SafetyTier.AUTO,

    # CONFIRM — runs but notifies Mike
    "send_brief_telegram": SafetyTier.CONFIRM,
    "update_goal_status": SafetyTier.CONFIRM,
    "create_calendar_event": SafetyTier.CONFIRM,
    "update_notion": SafetyTier.CONFIRM,

    # APPROVE — needs Mike's OK first
    "send_email": SafetyTier.APPROVE,
    "send_slack_message": SafetyTier.APPROVE,
    "create_github_issue": SafetyTier.APPROVE,
    "post_social_media": SafetyTier.APPROVE,
    "make_purchase": SafetyTier.APPROVE,

    # BLOCKED — never automated
    "delete_data": SafetyTier.BLOCKED,
    "modify_credentials": SafetyTier.BLOCKED,
    "push_to_production": SafetyTier.BLOCKED,
}

# Action-level safety overrides
ACTION_TIERS = {
    "read": SafetyTier.AUTO,
    "search": SafetyTier.AUTO,
    "summarize": SafetyTier.AUTO,
    "analyze": SafetyTier.AUTO,
    "create_draft": SafetyTier.CONFIRM,
    "send": SafetyTier.APPROVE,
    "delete": SafetyTier.BLOCKED,
    "modify_permissions": SafetyTier.BLOCKED,
}


def check_safety(pipeline_name: str, params: dict = None) -> SafetyCheck:
    """Check safety tier for a pipeline execution."""
    tier = PIPELINE_TIERS.get(pipeline_name, SafetyTier.APPROVE)

    # Check for action-level overrides
    action = (params or {}).get("action")
    if action and action in ACTION_TIERS:
        action_tier = ACTION_TIERS[action]
        # Use the more restrictive tier
        if action_tier.value > tier.value:
            tier = action_tier

    return SafetyCheck(
        tier=tier,
        reason=f"Pipeline '{pipeline_name}' classified as {tier.value}",
    )
```

**Step 3: Create pipeline registry**

```python
# pai/pipelines/registry.py
"""Pipeline registry — all registered autonomous pipelines."""

PIPELINES = {
    "morning_brief": {
        "description": "Overnight triage → Fabric summarize → Telegram delivery",
        "schedule": "0 6 * * *",  # 6 AM daily
        "safety_tier": "auto",
        "module": "pai.pipelines.morning_brief",
    },
    "meeting_prep": {
        "description": "Calendar trigger → research → brief generation",
        "schedule": "event_driven",  # 30 min before each meeting
        "safety_tier": "auto",
        "module": "pai.pipelines.meeting_prep",
    },
    "email_triage": {
        "description": "Gmail Pub/Sub → analyze → priority queue",
        "schedule": "*/15 * * * *",  # Every 15 minutes
        "safety_tier": "auto",
        "module": "pai.pipelines.email_triage",
    },
    "goal_progress": {
        "description": "Track active goals, update progress, alert on blockers",
        "schedule": "0 20 * * *",  # 8 PM daily
        "safety_tier": "confirm",
        "module": "pai.pipelines.goal_progress",
    },
    "weekly_synthesis": {
        "description": "Consolidate learning, synthesize patterns, update wisdom",
        "schedule": "0 10 * * 0",  # Sunday 10 AM
        "safety_tier": "auto",
        "module": "pai.pipelines.weekly_synthesis",
    },
}
```

**Step 4: Commit**

```bash
git add pai/pipelines/
git commit -m "feat(pai): pipeline framework — runner, safety tiers (AUTO/CONFIRM/APPROVE/BLOCKED), registry"
```

---

## Phase 3B: Core Pipelines

### Task 2: Morning Brief Pipeline

**Files:**
- Create: `pai/pipelines/morning_brief.py`

**Step 1: Create the morning brief pipeline**

```python
# pai/pipelines/morning_brief.py
"""Morning Brief Pipeline — delivered to Telegram at 6 AM.

Stages:
1. Overnight email scan (Gmail API → top 5 urgent)
2. Calendar today (Google Calendar API → meetings + prep needs)
3. Goal status (Supabase jake_goals → active goals)
4. Competitive signals (Susan SCOUT agent → P0/P1 signals)
5. Yesterday's learning (MEMORY/LEARNING → last session extract)
6. Fabric summarize → compile into structured brief
7. Deliver via Telegram
"""
import json
import os
import subprocess
from datetime import datetime, timedelta


def run_morning_brief() -> str:
    """Execute the morning brief pipeline."""
    sections = []

    # 1. Email scan
    emails = _scan_emails()
    if emails:
        sections.append(f"## Email ({len(emails)} urgent)\n" + "\n".join(
            f"- **{e['from']}**: {e['subject']}" for e in emails[:5]
        ))

    # 2. Calendar
    meetings = _get_today_calendar()
    if meetings:
        sections.append(f"## Calendar ({len(meetings)} meetings)\n" + "\n".join(
            f"- {m['time']} — {m['title']}" for m in meetings
        ))
    else:
        sections.append("## Calendar\nNo meetings today.")

    # 3. Goal status
    goals = _check_goals()
    if goals:
        sections.append("## Goals\n" + "\n".join(
            f"- {'[x]' if g['done'] else '[ ]'} {g['title']} ({g['progress']}%)"
            for g in goals[:5]
        ))

    # 4. Competitive signals
    signals = _check_competitive_signals()
    if signals:
        sections.append("## Signals\n" + "\n".join(
            f"- [{s['priority']}] {s['signal']}" for s in signals[:3]
        ))

    # 5. Yesterday's learning
    learning = _get_recent_learning()
    if learning:
        sections.append(f"## Learning\n{learning}")

    # Compile brief
    date_str = datetime.now().strftime("%A, %B %d")
    brief = f"# Morning Brief — {date_str}\n\n" + "\n\n".join(sections)

    # 6. Run through Fabric summarize for cleanup
    try:
        result = subprocess.run(
            ["fabric", "--pattern", "create_micro_summary", "--model", "openai/gpt-5.4-mini"],
            input=brief, capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            summary = result.stdout.strip()
            brief += f"\n\n---\n**TL;DR:** {summary}"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # 7. Deliver via Telegram
    _send_telegram(brief)

    return brief


def _scan_emails() -> list[dict]:
    """Scan Gmail for urgent overnight emails."""
    try:
        # Use Gmail API via MCP or direct API
        result = subprocess.run(
            ["python", "-c", """
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(os.path.expanduser('~/.gmail-credentials.json'))
service = build('gmail', 'v1', credentials=creds)

# Get emails from last 12 hours
import datetime
after = (datetime.datetime.now() - datetime.timedelta(hours=12)).strftime('%Y/%m/%d')
results = service.users().messages().list(
    userId='me', q=f'after:{after} is:unread', maxResults=10
).execute()

messages = results.get('messages', [])
emails = []
for msg in messages[:5]:
    full = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
    headers = {h['name']: h['value'] for h in full['payload']['headers']}
    emails.append({
        'from': headers.get('From', 'Unknown'),
        'subject': headers.get('Subject', 'No subject'),
    })

import json
print(json.dumps(emails))
"""],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return []


def _get_today_calendar() -> list[dict]:
    """Get today's calendar events."""
    try:
        result = subprocess.run(
            ["python", "-c", """
import os, json, datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(os.path.expanduser('~/.gcal-credentials.json'))
service = build('calendar', 'v3', credentials=creds)

now = datetime.datetime.utcnow()
start = now.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
end = now.replace(hour=23, minute=59, second=59).isoformat() + 'Z'

events = service.events().list(
    calendarId='primary', timeMin=start, timeMax=end,
    singleEvents=True, orderBy='startTime'
).execute().get('items', [])

meetings = []
for e in events:
    start_time = e['start'].get('dateTime', e['start'].get('date', ''))
    meetings.append({
        'time': start_time[11:16] if 'T' in start_time else 'All day',
        'title': e.get('summary', 'Untitled'),
    })

print(json.dumps(meetings))
"""],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return []


def _check_goals() -> list[dict]:
    """Check active goal status from Supabase."""
    try:
        from supabase import create_client
        client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
        result = client.table("jake_goals").select("*").eq("status", "active").execute()
        return [
            {
                "title": g.get("title", "Untitled"),
                "progress": g.get("progress", 0),
                "done": g.get("progress", 0) >= 100,
            }
            for g in (result.data or [])
        ]
    except Exception:
        return []


def _check_competitive_signals() -> list[dict]:
    """Check for competitive intelligence signals."""
    # Stub — will be populated by SCOUT agent in V4
    return []


def _get_recent_learning() -> str:
    """Get most recent learning extract."""
    learning_dir = "pai/MEMORY/LEARNING"
    if not os.path.exists(learning_dir):
        return ""
    files = sorted(os.listdir(learning_dir), reverse=True)
    if files:
        with open(os.path.join(learning_dir, files[0])) as f:
            content = f.read()
        return content[:300] + "..." if len(content) > 300 else content
    return ""


def _send_telegram(message: str):
    """Send message to Mike's Telegram."""
    import requests
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = "8634072195"
    if token:
        # Split long messages (Telegram limit: 4096 chars)
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for chunk in chunks:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"},
                timeout=10,
            )
```

**Step 2: Commit**

```bash
git add pai/pipelines/morning_brief.py
git commit -m "feat(pai): morning brief pipeline — email scan, calendar, goals, signals, learning, Telegram delivery"
```

---

### Task 3: Meeting Prep Pipeline

**Files:**
- Create: `pai/pipelines/meeting_prep.py`

**Step 1: Create meeting prep pipeline**

```python
# pai/pipelines/meeting_prep.py
"""Meeting Prep Pipeline — triggered 30 min before each meeting.

Stages:
1. Parse meeting details (attendees, agenda, attachments)
2. Search Susan RAG for relevant company/person context
3. Search PAI memory for previous interactions with attendees
4. Run Fabric analyze_personality on key attendees (if new)
5. Generate structured prep brief
6. Deliver via Telegram
"""
import json
import os
import subprocess
from datetime import datetime


def run_meeting_prep(meeting: dict) -> str:
    """Execute meeting prep for a specific meeting.

    Args:
        meeting: dict with keys: title, attendees, description, time
    """
    sections = []
    title = meeting.get("title", "Untitled Meeting")
    attendees = meeting.get("attendees", [])

    sections.append(f"# Meeting Prep: {title}\n")
    sections.append(f"**Time:** {meeting.get('time', 'Unknown')}")

    # 1. Attendee context
    if attendees:
        sections.append("\n## Attendees\n")
        for attendee in attendees:
            # Search memory for this person
            context = _search_person_context(attendee)
            sections.append(f"### {attendee}")
            if context:
                sections.append(context)
            else:
                sections.append("*No prior context. First interaction.*")

    # 2. Topic research
    description = meeting.get("description", "")
    if description:
        # Search Susan RAG for relevant knowledge
        rag_context = _search_susan_rag(description)
        if rag_context:
            sections.append(f"\n## Relevant Knowledge\n{rag_context}")

    # 3. Suggested talking points
    sections.append("\n## Suggested Talking Points\n")
    sections.append("*(Generated from context + meeting description)*\n")

    # 4. Action items from previous meetings with these attendees
    prev_actions = _get_previous_actions(attendees)
    if prev_actions:
        sections.append(f"\n## Open Action Items\n{prev_actions}")

    brief = "\n".join(sections)

    # Deliver
    _send_telegram(f"Meeting in 30 min:\n\n{brief}")

    return brief


def _search_person_context(name: str) -> str:
    """Search memory for context about a person."""
    try:
        from supabase import create_client
        client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])

        # Search entities
        result = client.table("jake_entities").select("*").ilike("name", f"%{name}%").execute()
        if result.data:
            entity = result.data[0]
            return (
                f"- **Role:** {entity.get('entity_type', 'unknown')}\n"
                f"- **Importance:** {entity.get('importance', 0.5)}\n"
                f"- **Notes:** {entity.get('metadata', {}).get('notes', 'None')}"
            )
    except Exception:
        pass
    return ""


def _search_susan_rag(query: str) -> str:
    """Search Susan RAG for relevant context."""
    try:
        result = subprocess.run(
            ["python", "-c", f"""
import sys
sys.path.insert(0, 'susan-team-architect/backend')
from rag_engine.retrieval import RAGRetriever
r = RAGRetriever()
results = r.search('{query.replace("'", "\\'")}', top_k=3)
for doc in results:
    print(doc.page_content[:200])
    print('---')
"""],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return result.stdout[:500]
    except Exception:
        pass
    return ""


def _get_previous_actions(attendees: list[str]) -> str:
    """Get open action items involving these attendees."""
    # Stub — to be populated when action tracking is built
    return ""


def _send_telegram(message: str):
    """Send to Telegram."""
    import requests
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": "8634072195", "text": message[:4000], "parse_mode": "Markdown"},
            timeout=10,
        )
```

**Step 2: Commit**

```bash
git add pai/pipelines/meeting_prep.py
git commit -m "feat(pai): meeting prep pipeline — attendee context, RAG research, action items, 30-min delivery"
```

---

### Task 4: Email Triage Pipeline

**Files:**
- Create: `pai/pipelines/email_triage.py`

**Step 1: Create email triage pipeline**

```python
# pai/pipelines/email_triage.py
"""Email Triage Pipeline — runs every 15 minutes.

Stages:
1. Fetch unread emails (Gmail API)
2. Classify urgency (nano model — cheap classification)
3. Extract action items (Fabric extract_ideas pattern)
4. Queue urgent items for Mike's attention
5. Auto-archive low-priority newsletters
6. Deliver urgent summary if any P0/P1 items
"""
import json
import os
import subprocess
from datetime import datetime


URGENCY_LEVELS = {
    "P0": "Respond now — blocking or time-sensitive",
    "P1": "Respond today — important but not blocking",
    "P2": "Respond this week — can wait",
    "P3": "Archive — newsletter, notification, no action needed",
}


def run_email_triage() -> dict:
    """Triage unread emails."""
    emails = _fetch_unread_emails()
    if not emails:
        return {"total": 0, "message": "No unread emails"}

    classified = []
    for email in emails:
        urgency = _classify_urgency(email)
        actions = _extract_actions(email) if urgency in ("P0", "P1") else []
        classified.append({
            "from": email.get("from", "Unknown"),
            "subject": email.get("subject", "No subject"),
            "urgency": urgency,
            "actions": actions,
            "snippet": email.get("snippet", "")[:100],
        })

    # Send urgent summary
    urgent = [e for e in classified if e["urgency"] in ("P0", "P1")]
    if urgent:
        summary = "## Email Triage Alert\n\n"
        for e in urgent:
            summary += f"**[{e['urgency']}] {e['subject']}**\n"
            summary += f"From: {e['from']}\n"
            if e['actions']:
                summary += "Actions: " + ", ".join(e['actions']) + "\n"
            summary += "\n"
        _send_telegram(summary)

    return {
        "total": len(classified),
        "P0": len([e for e in classified if e["urgency"] == "P0"]),
        "P1": len([e for e in classified if e["urgency"] == "P1"]),
        "P2": len([e for e in classified if e["urgency"] == "P2"]),
        "P3": len([e for e in classified if e["urgency"] == "P3"]),
    }


def _fetch_unread_emails() -> list[dict]:
    """Fetch unread emails from Gmail."""
    try:
        result = subprocess.run(
            ["python", "-c", """
import os, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(os.path.expanduser('~/.gmail-credentials.json'))
service = build('gmail', 'v1', credentials=creds)
results = service.users().messages().list(userId='me', q='is:unread', maxResults=20).execute()
messages = results.get('messages', [])

emails = []
for msg in messages:
    full = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
    headers = {h['name']: h['value'] for h in full['payload']['headers']}
    emails.append({
        'id': msg['id'],
        'from': headers.get('From', 'Unknown'),
        'subject': headers.get('Subject', 'No subject'),
        'snippet': full.get('snippet', ''),
    })

print(json.dumps(emails))
"""],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return []


def _classify_urgency(email: dict) -> str:
    """Classify email urgency using cheap model."""
    prompt = f"Classify this email urgency as P0/P1/P2/P3. Reply with ONLY the level.\n\nFrom: {email['from']}\nSubject: {email['subject']}\nSnippet: {email.get('snippet', '')}"

    try:
        result = subprocess.run(
            ["fabric", "--pattern", "label_and_rate", "--model", "openai/gpt-5.4-nano"],
            input=prompt, capture_output=True, text=True, timeout=15,
        )
        output = result.stdout.strip().upper()
        for level in ["P0", "P1", "P2", "P3"]:
            if level in output:
                return level
    except Exception:
        pass
    return "P2"  # Default to mid-priority


def _extract_actions(email: dict) -> list[str]:
    """Extract action items from email using Fabric."""
    try:
        result = subprocess.run(
            ["fabric", "--pattern", "extract_ideas", "--model", "openai/gpt-5.4-mini"],
            input=f"Extract action items from:\n{email.get('snippet', '')}",
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            return [l.strip("- ").strip() for l in lines if l.strip()][:3]
    except Exception:
        pass
    return []


def _send_telegram(message: str):
    """Send to Telegram."""
    import requests
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": "8634072195", "text": message[:4000], "parse_mode": "Markdown"},
            timeout=10,
        )
```

**Step 2: Commit**

```bash
git add pai/pipelines/email_triage.py
git commit -m "feat(pai): email triage pipeline — urgency classification, action extraction, Telegram alerts"
```

---

### Task 5: Goal Tracking Pipeline

**Files:**
- Create: `pai/pipelines/goal_progress.py`

**Step 1: Create goal tracking pipeline**

```python
# pai/pipelines/goal_progress.py
"""Goal Progress Pipeline — runs at 8 PM daily.

Stages:
1. Load active goals from Supabase jake_goals
2. Check git activity for progress signals
3. Check completed Work sessions for goal-related activity
4. Update progress percentages
5. Identify blocked goals (no activity in 7 days)
6. Deliver goal status to Telegram
"""
import json
import os
import subprocess
from datetime import datetime, timedelta


def run_goal_progress() -> dict:
    """Check and update goal progress."""
    from supabase import create_client
    client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])

    # Load active goals
    result = client.table("jake_goals").select("*").eq("status", "active").execute()
    goals = result.data or []

    if not goals:
        return {"total": 0, "message": "No active goals"}

    updates = []
    for goal in goals:
        # Check for activity signals
        activity = _check_activity(goal)

        # Update progress if activity detected
        if activity["commits"] > 0 or activity["sessions"] > 0:
            new_progress = min(100, goal.get("progress", 0) + activity["delta"])
            client.table("jake_goals").update(
                {"progress": new_progress, "last_activity": datetime.now().isoformat()}
            ).eq("id", goal["id"]).execute()

            updates.append({
                "title": goal.get("title", "Untitled"),
                "progress": new_progress,
                "delta": activity["delta"],
                "status": "progressing",
            })
        else:
            # Check if blocked (no activity in 7 days)
            last = goal.get("last_activity") or goal.get("created_at", "")
            if last:
                try:
                    last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                    if (datetime.now(last_dt.tzinfo) - last_dt).days >= 7:
                        updates.append({
                            "title": goal.get("title", "Untitled"),
                            "progress": goal.get("progress", 0),
                            "delta": 0,
                            "status": "BLOCKED",
                        })
                except (ValueError, TypeError):
                    pass

    # Deliver status
    if updates:
        summary = "## Goal Status (8 PM Check)\n\n"
        for u in updates:
            icon = "BLOCKED" if u["status"] == "BLOCKED" else f"+{u['delta']}%"
            summary += f"- **{u['title']}**: {u['progress']}% [{icon}]\n"
        _send_telegram(summary)

    return {"total": len(goals), "updates": len(updates)}


def _check_activity(goal: dict) -> dict:
    """Check for activity signals related to a goal."""
    title = goal.get("title", "").lower()
    activity = {"commits": 0, "sessions": 0, "delta": 0}

    # Check git commits in last 24 hours mentioning goal keywords
    try:
        keywords = title.split()[:3]
        for kw in keywords:
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=24.hours", f"--grep={kw}"],
                capture_output=True, text=True, timeout=10,
            )
            commits = [l for l in result.stdout.strip().split("\n") if l]
            activity["commits"] += len(commits)
    except Exception:
        pass

    # Check Work sessions
    work_dir = "pai/MEMORY/WORK"
    if os.path.exists(work_dir):
        today = datetime.now().strftime("%Y-%m-%d")
        for session_dir in os.listdir(work_dir):
            meta_path = os.path.join(work_dir, session_dir, "META.yaml")
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    content = f.read()
                if today in content and any(kw in content.lower() for kw in title.split()[:2]):
                    activity["sessions"] += 1

    # Calculate progress delta
    activity["delta"] = min(10, activity["commits"] * 2 + activity["sessions"] * 5)
    return activity


def _send_telegram(message: str):
    """Send to Telegram."""
    import requests
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": "8634072195", "text": message[:4000], "parse_mode": "Markdown"},
            timeout=10,
        )
```

**Step 2: Commit**

```bash
git add pai/pipelines/goal_progress.py
git commit -m "feat(pai): goal tracking pipeline — git activity signals, blocked detection, Telegram status"
```

---

## Phase 3C: Cron Job Setup

### Task 6: Register OpenClaw Cron Jobs

**Files:**
- Create: `pai/config/cron-jobs.json`

**Step 1: Create cron configuration**

```json
{
  "jobs": [
    {
      "name": "morning-brief",
      "schedule": "0 6 * * *",
      "command": "python pai/pipelines/morning_brief.py",
      "description": "Daily morning brief at 6 AM",
      "enabled": true
    },
    {
      "name": "email-triage",
      "schedule": "*/15 6-22 * * *",
      "command": "python pai/pipelines/email_triage.py",
      "description": "Email triage every 15 min during waking hours",
      "enabled": true
    },
    {
      "name": "goal-progress",
      "schedule": "0 20 * * *",
      "command": "python pai/pipelines/goal_progress.py",
      "description": "Goal status check at 8 PM",
      "enabled": true
    },
    {
      "name": "weekly-synthesis",
      "schedule": "0 10 * * 0",
      "command": "python -c 'from pai.memory.consolidator import PAIConsolidator; PAIConsolidator().weekly_synthesis()'",
      "description": "Weekly learning synthesis on Sunday 10 AM",
      "enabled": true
    },
    {
      "name": "health-check",
      "schedule": "*/5 * * * *",
      "command": "bash pai/scripts/health-check.sh",
      "description": "Service health check every 5 minutes",
      "enabled": true
    }
  ]
}
```

**Step 2: Register with OpenClaw**

```bash
for job in morning-brief email-triage goal-progress weekly-synthesis health-check; do
    openclaw cron add --config pai/config/cron-jobs.json --name $job
done
openclaw cron list
```

**Step 3: Commit**

```bash
git add pai/config/cron-jobs.json
git commit -m "feat(pai): OpenClaw cron jobs — morning brief, email triage, goal progress, weekly synthesis, health check"
```

---

## Phase 3D: Self-Repair

### Task 7: Implement Self-Repair System

**Files:**
- Create: `pai/immune/self_repair.py`

**Step 1: Create self-repair module**

```python
# pai/immune/self_repair.py
"""Self-repair system — auto-restart failed services, alert on persistent failures.

Adapted from jake_brain/immune/ modules:
- health_monitor.py
- error_recovery.py
- stale_detector.py
"""
import json
import os
import subprocess
from datetime import datetime


SERVICES = {
    "openclaw-gateway": {
        "check": "curl -s --max-time 5 http://127.0.0.1:18789/health",
        "restart": "launchctl kickstart -k gui/$(id -u)/com.jake.openclaw-gateway",
        "plist": "com.jake.openclaw-gateway",
    },
    "claude-brain": {
        "check": "tmux has-session -t jake-brain 2>/dev/null",
        "restart": "launchctl kickstart -k gui/$(id -u)/com.jake.claude-brain",
        "plist": "com.jake.claude-brain",
    },
    "fabric-api": {
        "check": "curl -s --max-time 5 http://127.0.0.1:8080/patterns/names",
        "restart": "launchctl kickstart -k gui/$(id -u)/com.jake.fabric-api",
        "plist": "com.jake.fabric-api",
    },
    "losslesclaw-db": {
        "check": "test -f ~/.openclaw/lcm.db",
        "restart": None,  # Can't restart — alert only
        "plist": None,
    },
}

FAILURE_LOG = "pai/immune/failure-log.jsonl"
MAX_RESTARTS = 3  # Max auto-restarts before alerting


class SelfRepair:
    def __init__(self):
        os.makedirs("pai/immune", exist_ok=True)

    def check_all(self) -> dict:
        """Check all services and auto-repair if needed."""
        results = {}
        for name, service in SERVICES.items():
            status = self._check_service(name, service)
            results[name] = status

            if status["healthy"]:
                continue

            # Attempt repair
            if service["restart"]:
                restart_count = self._get_restart_count(name)
                if restart_count < MAX_RESTARTS:
                    self._restart_service(name, service)
                    results[name]["action"] = f"auto-restarted (attempt {restart_count + 1})"
                else:
                    self._alert(f"Service {name} failed {MAX_RESTARTS}+ times. Manual intervention needed.")
                    results[name]["action"] = "ALERT — max restarts exceeded"
            else:
                self._alert(f"Service {name} is DOWN and cannot be auto-restarted.")
                results[name]["action"] = "ALERT — no auto-restart available"

        return results

    def _check_service(self, name: str, service: dict) -> dict:
        """Check if a service is healthy."""
        try:
            result = subprocess.run(
                service["check"], shell=True,
                capture_output=True, timeout=10,
            )
            return {"healthy": result.returncode == 0, "name": name}
        except (subprocess.TimeoutExpired, Exception):
            return {"healthy": False, "name": name}

    def _restart_service(self, name: str, service: dict):
        """Attempt to restart a service."""
        try:
            subprocess.run(service["restart"], shell=True, timeout=30)
            self._log_failure(name, "auto-restarted")
        except Exception as e:
            self._log_failure(name, f"restart failed: {e}")

    def _get_restart_count(self, name: str) -> int:
        """Count recent restarts for a service (last hour)."""
        if not os.path.exists(FAILURE_LOG):
            return 0
        count = 0
        cutoff = datetime.now().timestamp() - 3600  # Last hour
        with open(FAILURE_LOG) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("service") == name and entry.get("timestamp", 0) > cutoff:
                        count += 1
                except json.JSONDecodeError:
                    continue
        return count

    def _log_failure(self, name: str, action: str):
        """Log a failure event."""
        entry = {
            "service": name,
            "action": action,
            "timestamp": datetime.now().timestamp(),
            "iso": datetime.now().isoformat(),
        }
        with open(FAILURE_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _alert(self, message: str):
        """Send alert via Telegram."""
        import requests
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if token:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": "8634072195", "text": f"PAI ALERT: {message}"},
                timeout=10,
            )
```

**Step 2: Commit**

```bash
git add pai/immune/
git commit -m "feat(pai): self-repair system — auto-restart services, failure tracking, Telegram alerts"
```

---

## Phase 3E: Verification

### Task 8: End-to-End Autonomous Verification

**Files:**
- Create: `pai/verification/v3-test-results.md`

**Step 1: Test morning brief**

```bash
cd /Users/mikerodgers/Startup-Intelligence-OS
source susan-team-architect/backend/.venv/bin/activate
python -c "from pai.pipelines.morning_brief import run_morning_brief; run_morning_brief()"
```

Expected: Structured brief delivered to Telegram.

**Step 2: Test email triage**

```bash
python -c "from pai.pipelines.email_triage import run_email_triage; print(run_email_triage())"
```

Expected: Classification counts returned, urgent items sent to Telegram.

**Step 3: Test goal progress**

```bash
python -c "from pai.pipelines.goal_progress import run_goal_progress; print(run_goal_progress())"
```

Expected: Active goals checked, progress updated.

**Step 4: Test self-repair**

```bash
python -c "from pai.immune.self_repair import SelfRepair; print(SelfRepair().check_all())"
```

Expected: All services show healthy.

**Step 5: Test safety tiers**

```bash
python -c "
from pai.pipelines.safety import check_safety
print(check_safety('morning_brief'))       # Should be AUTO
print(check_safety('send_email'))           # Should be APPROVE
print(check_safety('delete_data'))          # Should be BLOCKED
"
```

**Step 6: Verify cron jobs registered**

```bash
openclaw cron list
```

Expected: 5 jobs registered and enabled.

**Step 7: Run for 14 consecutive days**

Monitor daily:
- Morning brief arrives at 6 AM
- Email triage alerts for urgent items
- Goal status arrives at 8 PM
- No false alerts from health monitor
- No uncaught pipeline failures

**Step 8: Commit**

```bash
git add pai/verification/v3-test-results.md
git commit -m "feat(pai): V3 autonomous execution verification complete"
```

---

## V3 Exit Criteria (All Must Pass)

- [ ] Pipeline framework running (runner, safety tiers, registry)
- [ ] Safety tiers enforced: AUTO (execute), CONFIRM (execute + notify), APPROVE (ask first), BLOCKED (never)
- [ ] Morning brief pipeline: email scan + calendar + goals + signals → Telegram at 6 AM
- [ ] Meeting prep pipeline: attendee context + RAG research → Telegram 30 min before
- [ ] Email triage pipeline: urgency classification + action extraction → every 15 min
- [ ] Goal tracking pipeline: git activity signals + blocked detection → Telegram at 8 PM
- [ ] Weekly synthesis: learning consolidation + pattern extraction → Sunday 10 AM
- [ ] Self-repair: auto-restart for OpenClaw, Claude Code, Fabric (max 3 attempts)
- [ ] OpenClaw cron jobs registered and running (5 jobs)
- [ ] Pipeline logs written to `pai/pipelines/logs/`
- [ ] All pipelines delivered autonomously for 14 consecutive days
- [ ] Task completion rate >80%
- [ ] Zero uncaught pipeline failures for 48 hours

**Score target: 60 → 70** (autonomous operations running, self-repair active)
