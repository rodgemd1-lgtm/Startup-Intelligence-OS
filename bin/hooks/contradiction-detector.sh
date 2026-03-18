#!/usr/bin/env bash
# V2 Governance — Agent Contradiction Detector
# PostToolUse hook: tracks recent Agent outputs and flags potential contradictions.
# Uses a rolling buffer of recent agent descriptions to detect conflicting signals.
set -euo pipefail

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# Only fire after Agent tool calls
if [[ "$TOOL_NAME" != "Agent" ]]; then
    exit 0
fi

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BUFFER_FILE="$ROOT_DIR/.claude/audit/agent-buffer.jsonl"

# Ensure audit directory exists
mkdir -p "$ROOT_DIR/.claude/audit"

# Extract description from tool input
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-{}}"
DESCRIPTION=$(echo "$TOOL_INPUT" | grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//' || echo "")
AGENT_TYPE=$(echo "$TOOL_INPUT" | grep -o '"subagent_type"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//' || echo "general")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Append to rolling buffer
printf '{"ts":"%s","agent":"%s","desc":"%s"}\n' "$TIMESTAMP" "$AGENT_TYPE" "$DESCRIPTION" >> "$BUFFER_FILE"

# Keep buffer to last 20 entries
if [[ -f "$BUFFER_FILE" ]]; then
    LINES=$(wc -l < "$BUFFER_FILE" | tr -d ' ')
    if [[ "$LINES" -gt 20 ]]; then
        tail -20 "$BUFFER_FILE" > "$BUFFER_FILE.tmp" && mv "$BUFFER_FILE.tmp" "$BUFFER_FILE"
    fi
fi

# Check for potential contradictions in recent buffer
# Look for agents working on the same topic with different approaches
if [[ -f "$BUFFER_FILE" ]] && [[ $(wc -l < "$BUFFER_FILE" | tr -d ' ') -ge 3 ]]; then
    # Count unique agent types in last 5 entries
    RECENT_AGENTS=$(tail -5 "$BUFFER_FILE" | grep -o '"agent":"[^"]*"' | sort -u | wc -l | tr -d ' ')

    if [[ "$RECENT_AGENTS" -ge 3 ]]; then
        echo "additionalContext: Contradiction check — 3+ different agent types dispatched recently. Verify their outputs are consistent before proceeding. Contradictions should be surfaced to Mike, never silently resolved." >&2
    fi
fi

exit 0
