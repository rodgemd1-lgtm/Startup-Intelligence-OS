"""Meeting Prep Employee — autonomous pre-meeting research and briefing.

Runs daily at 7 AM weekdays. For each meeting on today's calendar:
1. Identifies attendees and their roles
2. Searches brain memory for context on attendees
3. Pulls relevant intel from Susan RAG
4. Generates a concise pre-meeting brief
5. Sends to Telegram if Hermes is available
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def load_env() -> None:
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def get_today_meetings() -> list[dict]:
    """Fetch today's calendar events via osascript."""
    script = '''
    tell application "Calendar"
        set today to current date
        set tomorrow to today + 1 * days
        set output to ""
        repeat with cal in calendars
            try
                set evts to (every event of cal whose start date >= today and start date < tomorrow)
                repeat with e in evts
                    set output to output & summary of e & "|" & start date of e & "|" & (description of e as string) & linefeed
                end repeat
            end try
        end repeat
        return output
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        meetings = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) >= 2:
                meetings.append({
                    "title": parts[0].strip(),
                    "start": parts[1].strip(),
                    "description": parts[2].strip() if len(parts) > 2 else "",
                })
        return meetings
    except Exception:
        return []


def search_brain_for_context(query: str) -> list[dict]:
    """Search jake_brain for relevant memories about a meeting topic/person."""
    try:
        from jake_brain.retriever import BrainRetriever
        retriever = BrainRetriever()
        results = retriever.search(query, top_k=5)
        return [{"content": r.content, "source": r.source, "score": r.score} for r in results]
    except Exception:
        return []


def search_susan_rag(query: str) -> list[dict]:
    """Search Susan RAG for intel on meeting topics."""
    try:
        from supabase import create_client
        from rag_engine.embedder import Embedder
        from susan_core.config import config

        client = create_client(config.supabase_url, config.supabase_key)
        embedder = Embedder()
        embedding = embedder.embed(query)

        result = client.rpc("search_knowledge", {
            "query_embedding": embedding,
            "match_threshold": 0.75,
            "match_count": 5,
        }).execute()
        return result.data or []
    except Exception:
        return []


def generate_brief(meeting: dict, brain_context: list[dict], rag_context: list[dict]) -> str:
    """Generate a pre-meeting brief using Anthropic Claude."""
    try:
        import anthropic
        from jake_cost.router import ModelRouter, ModelTier
        from jake_cost.tracker import cost_tracker

        router = ModelRouter()
        decision = router.route("meeting_prep", complexity="medium")

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        brain_text = "\n".join([f"- {c['content'][:200]}" for c in brain_context[:3]])
        rag_text = "\n".join([f"- {c.get('content', '')[:200]}" for c in rag_context[:3]])

        prompt = f"""You are Jake, Mike Rodgers' AI co-founder. Generate a concise pre-meeting brief.

MEETING: {meeting['title']}
TIME: {meeting['start']}

BRAIN MEMORY CONTEXT:
{brain_text or 'No specific context found'}

INTEL FROM SUSAN RAG:
{rag_text or 'No specific intel found'}

Generate a brief with these sections:
1. Meeting Purpose (1-2 sentences)
2. Key Context (what Jake knows about attendees/topic)
3. Watch For (potential issues or opportunities)
4. Talking Points (3 bullet points max)
5. Jake's Take (1 sentence hot take)

Keep it under 200 words total. Be direct, useful, and Jake-flavored."""

        response = client.messages.create(
            model=decision.model_id,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        usage = response.usage
        cost_tracker.record_anthropic_call(
            decision.tier, usage.input_tokens, usage.output_tokens, actor="meeting_prep"
        )
        return response.content[0].text
    except Exception as e:
        return f"[Brief generation unavailable: {e}]"


def send_telegram(message: str) -> None:
    """Send brief to Telegram via Hermes bot."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    try:
        import urllib.request, json as _json
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = _json.dumps({"chat_id": chat_id, "text": message[:4000], "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def store_episodic(content: str, meeting_title: str) -> None:
    """Store brief in jake_episodic for memory."""
    try:
        from jake_brain.store import BrainStore
        store = BrainStore()
        store.store_episodic(
            content=content,
            source=f"meeting_prep:{meeting_title}",
            data_type="meeting_brief",
            importance=0.7,
        )
    except Exception:
        pass


def run() -> dict:
    """Main entry point for the Meeting Prep employee."""
    load_env()
    from jake_security.audit import audit, AuditEvent
    from jake_security.rate_limiter import rate_limiter

    audit.log(AuditEvent.EMPLOYEE_RUN, actor="meeting_prep", resource="calendar")

    if not rate_limiter.acquire("employee_run", actor="meeting_prep"):
        return {"status": "rate_limited", "meetings": 0}

    meetings = get_today_meetings()
    if not meetings:
        audit.log(AuditEvent.EMPLOYEE_COMPLETE, actor="meeting_prep", context={"meetings": 0})
        return {"status": "no_meetings", "meetings": 0}

    results = []
    for meeting in meetings[:5]:  # Max 5 meetings per run
        title = meeting["title"]

        # Search for context
        brain_ctx = search_brain_for_context(title)
        rag_ctx = search_susan_rag(title)

        # Generate brief
        brief = generate_brief(meeting, brain_ctx, rag_ctx)

        # Store in episodic memory
        store_episodic(brief, title)

        # Send to Telegram
        msg = f"📋 *Meeting Prep: {title}*\n\n{brief}"
        send_telegram(msg)

        results.append({"meeting": title, "brief_length": len(brief), "status": "done"})

    audit.log(
        AuditEvent.EMPLOYEE_COMPLETE,
        actor="meeting_prep",
        context={"meetings_prepped": len(results)},
    )
    return {"status": "complete", "meetings": len(results), "results": results}


if __name__ == "__main__":
    result = run()
    print(f"Meeting Prep complete: {result['meetings']} meetings prepped")
    if result.get("results"):
        for r in result["results"]:
            print(f"  ✓ {r['meeting']}")
