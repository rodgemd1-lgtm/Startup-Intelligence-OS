#!/usr/bin/env bash
# V2 Governance — Decision Audit Trail
# PostToolUse hook: logs every Agent tool call to .claude/audit/decisions.jsonl
# Silent logging — does not produce user-visible output.
set -euo pipefail

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# Only log Agent tool calls
if [[ "$TOOL_NAME" != "Agent" ]]; then
    exit 0
fi

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
AUDIT_DIR="$ROOT_DIR/.claude/audit"
AUDIT_FILE="$AUDIT_DIR/decisions.jsonl"

# Ensure audit directory exists
mkdir -p "$AUDIT_DIR"

# Extract what we can from environment
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-{}}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"

# Parse description and subagent_type from tool input (best-effort)
DESCRIPTION=$(echo "$TOOL_INPUT" | grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//' || echo "unknown")
AGENT_TYPE=$(echo "$TOOL_INPUT" | grep -o '"subagent_type"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//' || echo "general-purpose")
MODEL=$(echo "$TOOL_INPUT" | grep -o '"model"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*: *"//;s/"$//' || echo "default")

# Append audit entry (one JSON line per agent call)
printf '{"timestamp":"%s","tool":"Agent","agent_type":"%s","model":"%s","description":"%s","session":"%s"}\n' \
    "$TIMESTAMP" "$AGENT_TYPE" "$MODEL" "$DESCRIPTION" "$SESSION_ID" \
    >> "$AUDIT_FILE"

exit 0
