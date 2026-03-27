#!/usr/bin/env bash
# jake-meeting-scanner.sh — Auto-prep context 30 min before meetings.
# Checks Google Calendar for upcoming meetings, sends prep to Telegram.
#
# Schedule: every 15 min, 8 AM - 6 PM weekdays via com.jake.proactive-meeting-scanner.plist

set -euo pipefail

REPO_ROOT="$HOME/Startup-Intelligence-OS"
SUSAN_BACKEND="$REPO_ROOT/susan-team-architect/backend"
VENV="$SUSAN_BACKEND/.venv/bin/python"
LOG_DIR="$REPO_ROOT/.startup-os/logs"
LOG="$LOG_DIR/meeting-scanner.log"
STATE_FILE="$REPO_ROOT/.startup-os/runs/meeting-scanner-state.json"

mkdir -p "$LOG_DIR" "$(dirname "$STATE_FILE")"

# Load env
for envfile in "$HOME/.jake-vault/secrets.env" "$HOME/.hermes/.env" "$HOME/.openclaw/.env"; do
    if [ -f "$envfile" ]; then
        set -a
        # shellcheck disable=SC1090
        source "$envfile"
        set +a
    fi
done

# Only run during business hours (8 AM - 6 PM, weekdays)
HOUR=$(date '+%-H')
DOW=$(date '+%u')  # 1=Monday, 7=Sunday
if [ "$DOW" -gt 5 ] || [ "$HOUR" -lt 8 ] || [ "$HOUR" -ge 18 ]; then
    exit 0
fi

# ── Check for upcoming meetings (next 45 min) ──
MEETING_INFO=$("$VENV" -c "
import sys, os, json
sys.path.insert(0, '$SUSAN_BACKEND')

STATE_FILE = '$STATE_FILE'

# Load state to avoid re-notifying for same meeting
try:
    with open(STATE_FILE) as f:
        state = json.load(f)
except:
    state = {'notified': []}

try:
    from scripts.brain_gcal_ingest import get_calendar_service
    from datetime import datetime, timedelta, timezone

    service = get_calendar_service()
    now = datetime.now(timezone.utc)
    # Look 15-45 min ahead (so we catch meetings approaching in the next window)
    start = (now + timedelta(minutes=15)).isoformat()
    end = (now + timedelta(minutes=45)).isoformat()
    events_result = service.events().list(
        calendarId='primary', timeMin=start, timeMax=end,
        maxResults=3, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    for event in events:
        event_id = event.get('id', '')
        if event_id in state['notified']:
            continue  # Already sent prep for this meeting

        summary = event.get('summary', 'Meeting')
        start_time = event.get('start', {}).get('dateTime', '')
        attendees = [a.get('email', '') for a in event.get('attendees', [])]
        location = event.get('location', '')

        # Build prep context
        prep = f'📋 <b>MEETING PREP — {summary}</b>\n'
        if start_time:
            time_str = start_time.split('T')[1][:5] if 'T' in start_time else start_time
            prep += f'⏰ Starts at {time_str}\n'
        if location:
            prep += f'📍 {location}\n'
        if attendees:
            prep += f'👥 {len(attendees)} attendees: {\" / \".join(attendees[:5])}\n'

        # Search brain for relevant context about attendees
        try:
            from jake_brain.retriever import BrainRetriever
            r = BrainRetriever()
            for attendee in attendees[:3]:
                name = attendee.split('@')[0].replace('.', ' ').title()
                mems = r.search(name, top_k=1)
                if mems:
                    prep += f'🧠 {name}: {mems[0].get(\"content\", \"\")[:100]}\n'
        except:
            pass

        # Search Susan RAG for topic context
        try:
            from susan_core.rag import search_knowledge
            results = search_knowledge(summary, top_k=2)
            if results:
                prep += '\n📚 <b>Context</b>\n'
                for r in results[:2]:
                    prep += f'  • {r.get(\"content\", \"\")[:120]}\n'
        except:
            pass

        print(prep)

        # Mark as notified
        state['notified'].append(event_id)

    # Clean up old notifications (keep last 50)
    state['notified'] = state['notified'][-50:]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

except Exception as e:
    print(f'(meeting scanner error: {e})', file=sys.stderr)
" 2>/dev/null)

# Send to Telegram if there's a meeting prep
if [ -n "$MEETING_INFO" ] && [ "$MEETING_INFO" != "" ]; then
    echo "[$(date '+%H:%M')] Sending meeting prep" >> "$LOG"

    if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            --data-urlencode "text=${MEETING_INFO}" \
            -d "parse_mode=HTML" >> "$LOG" 2>&1
    else
        echo "$MEETING_INFO"
    fi
fi
