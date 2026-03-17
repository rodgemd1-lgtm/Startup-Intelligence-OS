#!/usr/bin/env bash
# V10.0 Layer 1 — Zero-Touch Session Start Hook
# Fires on every session start. Auto-configures the project in background.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
CLAUDE_DIR="$ROOT_DIR/.claude"
MEMORY_DIR="$HOME/.claude/projects/-Users-mikerodgers-$(basename "$ROOT_DIR")/memory"
ENV_FILE="${CLAUDE_ENV_FILE:-}"

# --- Phase 1: Inject persistent context ---

# Read HANDOFF.md if it exists
if [[ -f "$ROOT_DIR/HANDOFF.md" ]]; then
    echo "additionalContext: Found HANDOFF.md — reading for session continuity." >&2
    echo "SESSION_HAS_HANDOFF=true" >> "${ENV_FILE:-/dev/null}" 2>/dev/null || true
fi

# Read memory summary if it exists
if [[ -f "$MEMORY_DIR/MEMORY.md" ]]; then
    echo "SESSION_HAS_MEMORY=true" >> "${ENV_FILE:-/dev/null}" 2>/dev/null || true
fi

# --- Phase 2: Auto-detect project optimization ---

if [[ ! -d "$CLAUDE_DIR/rules" ]]; then
    echo "additionalContext: Project not optimized. Run /optimize-startup to set up WISC context engineering." >&2
fi

# --- Phase 3: Check for stale data ---

# Check if simulated maturity is stale (>24h)
MATURITY_FILE="$ROOT_DIR/.startup-os/artifacts/simulated-maturity/simulated-maturity-harness-summary.md"
if [[ -f "$MATURITY_FILE" ]]; then
    FILE_AGE=$(( $(date +%s) - $(stat -f %m "$MATURITY_FILE" 2>/dev/null || echo 0) ))
    if (( FILE_AGE > 86400 )); then
        echo "additionalContext: Simulated maturity surface is stale (>24h). Consider running bin/run_simulated_maturity_harness.py" >&2
    fi
fi

# --- Phase 4: Inject V10 memory tips ---

TIPS_DIR="$ROOT_DIR/susan-team-architect/backend/data/memory/tips"
if [[ -d "$TIPS_DIR" ]] && [[ -n "$(ls -A "$TIPS_DIR" 2>/dev/null)" ]]; then
    TIP_COUNT=$(ls -1 "$TIPS_DIR"/*.yaml 2>/dev/null | wc -l | tr -d ' ')
    echo "additionalContext: V10 Memory system active. $TIP_COUNT learned tips available. Use 'python -m memory query <topic>' to retrieve." >&2
fi

# --- Phase 5: Report research daemon status ---

DAEMON_STATUS="$ROOT_DIR/susan-team-architect/backend/data/memory/daemon_status.yaml"
if [[ -f "$DAEMON_STATUS" ]]; then
    echo "additionalContext: Research daemon has run previously. Check status with 'python -m research_daemon --command status'" >&2
fi

exit 0
