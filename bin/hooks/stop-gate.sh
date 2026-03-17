#!/usr/bin/env bash
# V10.0 Layer 2 — Stop Hook (Completeness Gate)
# Fires when Claude finishes responding. Checks for common incompleteness.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# Check for in-progress plans that might have been forgotten
PLANS_DIR="$ROOT_DIR/.claude/plans"
if [[ -d "$PLANS_DIR" ]]; then
    for plan in "$PLANS_DIR"/*.md; do
        [[ -f "$plan" ]] || continue
        if grep -q 'Status: in-progress' "$plan" 2>/dev/null; then
            PLAN_NAME=$(basename "$plan")
            echo "additionalContext: Reminder — plan '$PLAN_NAME' is still in-progress. Consider completing or updating it." >&2
            break
        fi
    done
fi

exit 0
