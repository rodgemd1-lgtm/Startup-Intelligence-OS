#!/usr/bin/env bash
# Stop Hook — Track session token usage and estimated costs.
# Appends one JSON line per session stop to ~/.claude/metrics/costs.jsonl.
# Non-blocking: errors are silently ignored.
set -uo pipefail

METRICS_DIR="$HOME/.claude/metrics"
COSTS_FILE="$METRICS_DIR/costs.jsonl"
mkdir -p "$METRICS_DIR"

# Read stdin (Claude passes session info as JSON)
INPUT=$(cat 2>/dev/null || echo '{}')

# Extract fields with lightweight parsing (no jq dependency)
# Claude Code passes: session_id, model, usage.input_tokens, usage.output_tokens
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
SESSION_ID="${CLAUDE_SESSION_ID:-default}"

# Try to parse input tokens and output tokens from the JSON
INPUT_TOKENS=$(echo "$INPUT" | grep -o '"input_tokens"[[:space:]]*:[[:space:]]*[0-9]*' | grep -o '[0-9]*$' || echo "0")
OUTPUT_TOKENS=$(echo "$INPUT" | grep -o '"output_tokens"[[:space:]]*:[[:space:]]*[0-9]*' | grep -o '[0-9]*$' || echo "0")
MODEL=$(echo "$INPUT" | grep -o '"model"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"model"[[:space:]]*:[[:space:]]*"//' | sed 's/"$//' || echo "unknown")

# Default to 0 if empty
INPUT_TOKENS=${INPUT_TOKENS:-0}
OUTPUT_TOKENS=${OUTPUT_TOKENS:-0}
MODEL=${MODEL:-unknown}

# Write JSONL row (append-only, never truncate)
echo "{\"timestamp\":\"$TIMESTAMP\",\"session_id\":\"$SESSION_ID\",\"model\":\"$MODEL\",\"input_tokens\":$INPUT_TOKENS,\"output_tokens\":$OUTPUT_TOKENS}" >> "$COSTS_FILE" 2>/dev/null

# Pass through stdin unchanged
echo "$INPUT"
exit 0
