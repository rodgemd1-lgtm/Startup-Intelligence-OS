#!/usr/bin/env bash
# PreCompact Hook — Save state before context compaction.
# Logs compaction events so you can track context loss across sessions.
set -uo pipefail

SESSIONS_DIR="$HOME/.claude/sessions"
COMPACTION_LOG="$SESSIONS_DIR/compaction-log.txt"
mkdir -p "$SESSIONS_DIR"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Context compaction triggered — $(basename "$PWD")" >> "$COMPACTION_LOG"

# If an active session file exists, annotate it
ACTIVE_SESSION=$(ls -t "$SESSIONS_DIR"/*-session.tmp 2>/dev/null | head -1)
if [ -n "$ACTIVE_SESSION" ]; then
  TIME=$(date '+%H:%M')
  echo "" >> "$ACTIVE_SESSION"
  echo "---" >> "$ACTIVE_SESSION"
  echo "**[Compaction occurred at $TIME]** — Context was summarized" >> "$ACTIVE_SESSION"
fi

exit 0
