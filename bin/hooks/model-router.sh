#!/usr/bin/env bash
# V10.0 Layer 2 — Model Routing Advisor
# PreToolUse hook that suggests model routing for cost optimization.
# This is advisory — adds context, doesn't block.
set -euo pipefail

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-}"

# For Agent tool calls, suggest model tier based on task complexity
if [[ "$TOOL_NAME" == "Agent" ]]; then
    # Check if a model is already specified
    if echo "$TOOL_INPUT" | grep -q '"model"'; then
        exit 0  # Model already specified, don't interfere
    fi

    # Advisory: suggest haiku for simple searches, sonnet for implementation
    DESCRIPTION=$(echo "$TOOL_INPUT" | grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 || echo "")
    if echo "$DESCRIPTION" | grep -qi 'search\|find\|list\|check\|verify\|count'; then
        echo "additionalContext: Cost optimization tip — this looks like a search/validation task. Consider using model: haiku for 5x cost savings." >&2
    fi
fi

exit 0
