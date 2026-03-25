#!/bin/bash
# PAI V3: Morning Briefing Pipeline
# Collects unread email summary + today's calendar, outputs structured brief
# Usage: ./morning_briefing.sh [--json]

set -euo pipefail

MAIL_CLI="${HOME}/go/bin/mail-app-cli"
OUTPUT_FORMAT="${1:---text}"

echo "=== JAKE MORNING BRIEFING ==="
echo "Date: $(date '+%A, %B %d %Y %I:%M %p')"
echo ""

# --- EMAIL SUMMARY ---
echo "## Email"

# iCloud unread count + top 5
ICLOUD_UNREAD=$($MAIL_CLI messages list --account "iCloud" --mailbox "INBOX" --unread 2>/dev/null | python3 -c "
import sys, json
try:
    msgs = json.load(sys.stdin)
    print(f'iCloud: {len(msgs)} unread')
    for m in msgs[:5]:
        sender = m.get('Sender','?')[:40]
        subj = m.get('Subject','(no subject)')[:55]
        print(f'  - {sender}: {subj}')
except: print('iCloud: error reading')
" 2>&1)
echo "$ICLOUD_UNREAD"
echo ""

# Exchange unread count + top 5
EXCHANGE_UNREAD=$($MAIL_CLI messages list --account "Exchange" --mailbox "INBOX" --unread 2>/dev/null | python3 -c "
import sys, json
try:
    msgs = json.load(sys.stdin)
    print(f'Oracle/Exchange: {len(msgs)} unread')
    for m in msgs[:5]:
        sender = m.get('Sender','?')[:40]
        subj = m.get('Subject','(no subject)')[:55]
        print(f'  - {sender}: {subj}')
except: print('Exchange: error reading')
" 2>&1)
echo "$EXCHANGE_UNREAD"
echo ""

# --- CALENDAR ---
echo "## Calendar"

# Get today's events from Work calendar (bounded to prevent timeout)
WORK_EVENTS=$(osascript -e '
tell application "Calendar"
    set today to current date
    set time of today to 0
    set endDay to today + (1 * days)
    set results to ""
    try
        set evts to every event of calendar "Work" whose start date >= today and start date < endDay
        if (count of evts) > 0 then
            repeat with e in evts
                set h to hours of (start date of e)
                set m to minutes of (start date of e)
                if m < 10 then
                    set timeStr to (h as string) & ":0" & (m as string)
                else
                    set timeStr to (h as string) & ":" & (m as string)
                end if
                set results to results & timeStr & " " & (summary of e) & linefeed
            end repeat
        else
            set results to "No Work events today"
        end if
    on error
        set results to "Could not read Work calendar"
    end try
    return results
end tell' 2>&1 &)
CAL_PID=$!

# Wait up to 12 seconds for calendar
WAITED=0
while kill -0 $CAL_PID 2>/dev/null && [ $WAITED -lt 12 ]; do
    sleep 1
    WAITED=$((WAITED + 1))
done

if kill -0 $CAL_PID 2>/dev/null; then
    kill $CAL_PID 2>/dev/null
    echo "Work: Calendar query timed out"
else
    wait $CAL_PID
    echo "Work: $WORK_EVENTS"
fi

# Home calendar
HOME_EVENTS=$(osascript -e '
tell application "Calendar"
    set today to current date
    set time of today to 0
    set endDay to today + (1 * days)
    set results to ""
    try
        set evts to every event of calendar "Home" whose start date >= today and start date < endDay
        if (count of evts) > 0 then
            repeat with e in evts
                set h to hours of (start date of e)
                set m to minutes of (start date of e)
                if m < 10 then
                    set timeStr to (h as string) & ":0" & (m as string)
                else
                    set timeStr to (h as string) & ":" & (m as string)
                end if
                set results to results & timeStr & " " & (summary of e) & linefeed
            end repeat
        else
            set results to "No Home events today"
        end if
    on error
        set results to "Could not read Home calendar"
    end try
    return results
end tell' 2>&1 &)
CAL_PID2=$!
WAITED=0
while kill -0 $CAL_PID2 2>/dev/null && [ $WAITED -lt 12 ]; do
    sleep 1
    WAITED=$((WAITED + 1))
done
if kill -0 $CAL_PID2 2>/dev/null; then
    kill $CAL_PID2 2>/dev/null
    echo "Home: Calendar query timed out"
else
    wait $CAL_PID2
    echo "Home: $HOME_EVENTS"
fi

echo ""
echo "=== END BRIEFING ==="
