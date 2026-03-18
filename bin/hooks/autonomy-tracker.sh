#!/usr/bin/env bash
# autonomy-tracker.sh — PostToolUse hook
# Logs when AUTO-tagged agent outputs are generated to the graduation tracker
# Triggered on: Write tool calls to .startup-os/briefs/

set -euo pipefail

# Only track writes to the briefs directory
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
FILE_PATH="${CLAUDE_FILE_PATH:-}"

if [[ "$TOOL_NAME" != "Write" ]]; then
  exit 0
fi

if [[ "$FILE_PATH" != *".startup-os/briefs/"* ]]; then
  exit 0
fi

TRACKER="/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/autonomy/graduation-tracker.yaml"
DATE=$(date +%Y-%m-%d)
BRIEF_NAME=$(basename "$FILE_PATH" .md)

# Determine which workflow this brief belongs to
WORKFLOW=""
case "$BRIEF_NAME" in
  aria-brief-*)     WORKFLOW="aria-daily-brief" ;;
  oracle-brief-*)   WORKFLOW="oracle-health-morning-brief" ;;
  ledger-report-*)  WORKFLOW="ledger-funnel-report" ;;
  scout-signals-*)  WORKFLOW="scout-competitive-signals" ;;
  freshness-*)      WORKFLOW="knowledge-freshness-audit" ;;
  *)                exit 0 ;;  # Unknown brief type, skip
esac

# Log to stderr for Jake's awareness (shows in hook output)
echo "📊 Autonomy tracker: logged delivery for $WORKFLOW ($DATE)" >&2

# Append observation to tracker
# Using a simple append approach — the weekly review will parse and score
OBSERVATION_FILE="/Users/mikerodgers/Startup-Intelligence-OS/.startup-os/autonomy/observations.log"
echo "$DATE|$WORKFLOW|delivered|unrated" >> "$OBSERVATION_FILE"

exit 0
