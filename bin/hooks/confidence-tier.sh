#!/usr/bin/env bash
# V1 Governance — Confidence Tier Reminder
# PostToolUse hook: reminds agents to tag substantive outputs with AUTO/DRAFT/FLAG.
# Runs after Agent tool calls complete. Advisory only — does not block.
set -euo pipefail

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# Only fire after Agent tool calls (where substantive outputs happen)
if [[ "$TOOL_NAME" != "Agent" ]]; then
    exit 0
fi

echo "additionalContext: Confidence tier check — tag this output AUTO (ship it), DRAFT (review needed), or FLAG (needs Mike's call)." >&2

exit 0
