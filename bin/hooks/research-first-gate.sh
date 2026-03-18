#!/usr/bin/env bash
# V2 Governance — Research-First Gate
# PreToolUse hook: warns when writing code without a plan/research doc.
# V2 = advisory warning. V3 will upgrade to blocking.
set -euo pipefail

TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
FILE_PATH="${CLAUDE_FILE_PATH:-}"

# Only check Write/Edit operations
case "$TOOL_NAME" in
    Write|Edit) ;;
    *) exit 0 ;;
esac

# Skip non-code files (docs, configs, plans are fine without research)
case "$FILE_PATH" in
    *.md|*.yaml|*.yml|*.json|*.txt|*.gitkeep|*.lock|*.sh)
        exit 0
        ;;
esac

# Skip files inside .claude/ (these are system files, not project code)
if echo "$FILE_PATH" | grep -q '\.claude/'; then
    exit 0
fi

# Skip test files (tests don't need research gates)
if echo "$FILE_PATH" | grep -qi 'test'; then
    exit 0
fi

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PLANS_DIR="$ROOT_DIR/.claude/plans"

# Check if any plan exists that's marked in-progress
HAS_ACTIVE_PLAN=false
if [[ -d "$PLANS_DIR" ]]; then
    for plan in "$PLANS_DIR"/*.md; do
        [[ -f "$plan" ]] || continue
        if grep -qi 'status.*in.progress\|status.*approved\|status.*executing' "$plan" 2>/dev/null; then
            HAS_ACTIVE_PLAN=true
            break
        fi
    done
fi

if [[ "$HAS_ACTIVE_PLAN" == "false" ]]; then
    echo "additionalContext: Research-first gate — writing code without an active plan. Consider running /plan-feature first. (V2 advisory, not blocking)" >&2
fi

exit 0
