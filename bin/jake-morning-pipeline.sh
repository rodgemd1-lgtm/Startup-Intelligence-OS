#!/usr/bin/env bash
# jake-morning-pipeline.sh — Jake's unified 6:00 AM morning brief.
# Replaces: brain_morning_brief.sh + jake_morning_brief.sh (Hermes-era)
#
# Pipeline: Overnight Intel → Email Triage → Calendar → Goals → Brain → Assemble → Telegram
# Schedule: daily at 6:00 AM via com.jake.proactive-morning-pipeline.plist

set -euo pipefail

REPO_ROOT="$HOME/Startup-Intelligence-OS"
SUSAN_BACKEND="$REPO_ROOT/susan-team-architect/backend"
VENV="$SUSAN_BACKEND/.venv/bin/python"
LOG_DIR="$REPO_ROOT/.startup-os/logs"
LOG="$LOG_DIR/morning-pipeline.log"
BRIEFS_DIR="$REPO_ROOT/.startup-os/briefs"

mkdir -p "$LOG_DIR" "$BRIEFS_DIR"

echo "=== jake-morning-pipeline.sh $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

# Load env (API keys, Telegram tokens)
# Vault is canonical source; hermes/openclaw are fallbacks
for envfile in "$HOME/.jake-vault/secrets.env" "$HOME/.hermes/.env" "$HOME/.openclaw/.env"; do
    if [ -f "$envfile" ]; then
        set -a
        # shellcheck disable=SC1090
        source "$envfile"
        set +a
    fi
done

TODAY=$(date '+%Y-%m-%d')
DAY_OF_WEEK=$(date '+%A')
HOUR=$(date '+%-H')

# ── Helper: escape HTML entities for Telegram ──
escape_html() {
    local text="$1"
    text="${text//&/&amp;}"
    text="${text//</&lt;}"
    text="${text//>/&gt;}"
    echo "$text"
}

# ── Helper: send to Telegram ──
# Uses HTML parse mode — more forgiving than Markdown with special chars in
# email subjects, calendar events, and brain highlights.
send_telegram() {
    local msg="$1"
    if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
        echo "[WARN] Telegram not configured, printing to stdout" >> "$LOG"
        echo "$msg"
        return 0
    fi
    # Split long messages (Telegram limit: 4096 chars)
    local len=${#msg}
    if [ "$len" -le 4096 ]; then
        local resp
        resp=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            --data-urlencode "text=${msg}" \
            -d "parse_mode=HTML" 2>&1)
        echo "$resp" >> "$LOG"
        # Fallback: if HTML parse fails, retry without parse_mode
        if echo "$resp" | grep -q '"ok":false'; then
            echo "[WARN] HTML parse failed, retrying plain text" >> "$LOG"
            curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                -d "chat_id=${TELEGRAM_CHAT_ID}" \
                --data-urlencode "text=${msg}" >> "$LOG" 2>&1
        fi
    else
        # Send in chunks
        local chunk_size=4000
        local offset=0
        while [ "$offset" -lt "$len" ]; do
            local chunk="${msg:$offset:$chunk_size}"
            curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                -d "chat_id=${TELEGRAM_CHAT_ID}" \
                --data-urlencode "text=${chunk}" \
                -d "parse_mode=HTML" >> "$LOG" 2>&1
            offset=$((offset + chunk_size))
            sleep 1  # Rate limit
        done
    fi
}

# ── Section 1: Overnight Intel (if available) ──
INTEL_FILE="$BRIEFS_DIR/scout-signals-${TODAY}.md"
INTEL_SECTION=""
if [ -f "$INTEL_FILE" ]; then
    # Extract P0 and P1 signals only
    INTEL_SECTION=$(grep -E "^(P0|P1|🔴|🟡)" "$INTEL_FILE" 2>/dev/null | head -5)
    if [ -n "$INTEL_SECTION" ]; then
        INTEL_SECTION="🔍 <b>COMPETITIVE SIGNALS</b>
${INTEL_SECTION}"
    fi
fi

# ── Section 2: Email Summary ──
EMAIL_SECTION=""
# Try Apple Mail via osascript (Exchange + iCloud)
UNREAD_COUNT=$(osascript -e 'tell application "Mail" to count of (messages of inbox whose read status is false)' 2>/dev/null || echo "?")
if [ "$UNREAD_COUNT" != "?" ] && [ "$UNREAD_COUNT" -gt 0 ]; then
    EMAIL_SECTION="📧 <b>EMAIL</b> — ${UNREAD_COUNT} unread"
    # Get top 3 unread subjects
    TOP_EMAILS=$(osascript -e '
        tell application "Mail"
            set msgs to (messages of inbox whose read status is false)
            set output to ""
            set maxCount to 3
            if (count of msgs) < maxCount then set maxCount to (count of msgs)
            repeat with i from 1 to maxCount
                set msg to item i of msgs
                set output to output & "  • " & (subject of msg) & " — " & (sender of msg) & linefeed
            end repeat
            return output
        end tell
    ' 2>/dev/null || echo "  (could not read subjects)")
    TOP_EMAILS=$(escape_html "$TOP_EMAILS")
    EMAIL_SECTION="${EMAIL_SECTION}
${TOP_EMAILS}"
fi

# ── Section 3: Calendar ──
CALENDAR_SECTION=""
# Google Calendar events for today
if command -v "$VENV" &>/dev/null; then
    CAL_EVENTS=$("$VENV" -c "
import sys, os
sys.path.insert(0, '$SUSAN_BACKEND')
try:
    from scripts.brain_gcal_ingest import get_calendar_service
    from datetime import datetime, timedelta, timezone
    service = get_calendar_service()
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0).isoformat() + 'Z'
    end = now.replace(hour=23, minute=59, second=59).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=start, timeMax=end,
        maxResults=10, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    for e in events:
        start_t = e.get('start', {}).get('dateTime', e.get('start', {}).get('date', ''))
        summary = e.get('summary', 'No title')
        if 'T' in start_t:
            time_str = start_t.split('T')[1][:5]
            print(f'  📅 {time_str} — {summary}')
        else:
            print(f'  📅 All day — {summary}')
    if not events:
        print('  📅 No events today — clear calendar!')
except Exception as ex:
    print(f'  (calendar unavailable: {ex})')
" 2>/dev/null || echo "  (calendar unavailable)")
    if [ -n "$CAL_EVENTS" ]; then
        CAL_EVENTS=$(escape_html "$CAL_EVENTS")
        CALENDAR_SECTION="📆 <b>TODAY'S CALENDAR</b>
${CAL_EVENTS}"
    fi
fi

# Also check Apple Calendar via osascript
APPLE_CAL=$(osascript -e "
    set today to current date
    set todayStr to (year of today as text) & \"-\" & text -2 thru -1 of (\"0\" & ((month of today as number) as text)) & \"-\" & text -2 thru -1 of (\"0\" & (day of today as text))
    return todayStr
" 2>/dev/null || echo "")

# ── Section 4: Goals ──
GOALS_SECTION=""
if command -v "$VENV" &>/dev/null; then
    GOALS=$("$VENV" -c "
import os, sys
sys.path.insert(0, '$SUSAN_BACKEND')
from supabase import create_client
url = os.environ.get('SUPABASE_URL', '')
key = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')
if url and key:
    sb = create_client(url, key)
    res = sb.table('jake_goals').select('title,current_value,target_value,status').eq('status','active').order('created_at').limit(5).execute()
    for g in res.data:
        pct = int((g['current_value'] / g['target_value'] * 100)) if g['target_value'] else 0
        bar = '█' * (pct // 10) + '░' * (10 - pct // 10)
        print(f'  {bar} {pct}% — {g[\"title\"]}')
else:
    print('  (Supabase not configured)')
" 2>/dev/null || echo "  (goals unavailable)")
    if [ -n "$GOALS" ]; then
        GOALS_SECTION="🎯 <b>ACTIVE GOALS</b>
${GOALS}"
    fi
fi

# ── Section 5: Brain Highlights ──
BRAIN_SECTION=""
if command -v "$VENV" &>/dev/null; then
    BRAIN_HIGHLIGHTS=$("$VENV" -c "
import sys, os
sys.path.insert(0, '$SUSAN_BACKEND')
try:
    from jake_brain.retriever import BrainRetriever
    from datetime import datetime, timedelta, timezone
    r = BrainRetriever()
    mems = r.search('priorities deadlines meetings important', top_k=3,
                     time_start=datetime.now(timezone.utc) - timedelta(hours=48))
    for m in mems:
        content = m.get('content', '')[:120]
        print(f'  • {content}')
except Exception as e:
    print(f'  (brain unavailable: {e})')
" 2>/dev/null || echo "  (brain unavailable)")
    if [ -n "$BRAIN_HIGHLIGHTS" ]; then
        BRAIN_HIGHLIGHTS=$(escape_html "$BRAIN_HIGHLIGHTS")
        BRAIN_SECTION="🧠 <b>BRAIN HIGHLIGHTS</b>
${BRAIN_HIGHLIGHTS}"
    fi
fi

# ── Section 6: Deadlines This Week ──
DEADLINE_SECTION=""
if [ "$DAY_OF_WEEK" = "Monday" ] || [ "$DAY_OF_WEEK" = "Friday" ]; then
    # Check for upcoming deadlines (calendar events with "due", "deadline", "submit" in title)
    DEADLINE_SECTION="⏰ <b>DEADLINES THIS WEEK</b>
  (run /whats-due in Claude Code for full scan)"
fi

# ── Assemble Brief ──
BRIEF="☀️ <b>JAKE MORNING BRIEF — ${DAY_OF_WEEK}, $(date '+%B %d')</b>
<i>$(date '+%-I:%M %p')</i>
"

# Add sections (skip empty ones)
for section in "$INTEL_SECTION" "$EMAIL_SECTION" "$CALENDAR_SECTION" "$GOALS_SECTION" "$BRAIN_SECTION" "$DEADLINE_SECTION"; do
    if [ -n "$section" ]; then
        BRIEF="${BRIEF}
${section}
"
    fi
done

BRIEF="${BRIEF}
<i>Reply to Jake with updates or priorities.</i>"

# ── Deliver ──
echo "$BRIEF" >> "$LOG"
send_telegram "$BRIEF"

EXIT_CODE=$?
echo "[EXIT] morning-pipeline exited with code $EXIT_CODE" >> "$LOG"
echo "=== DONE $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

# Save brief to file for other agents to reference
echo "$BRIEF" > "$BRIEFS_DIR/morning-brief-${TODAY}.md"
