#!/usr/bin/env bash
# V10.0 Layer 2 — Stop Hook (Brain Sync)
# Fires when Claude finishes responding. Syncs Claude Code memory to Jake's Brain.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/susan-team-architect/backend"
VENV="$BACKEND_DIR/.venv/bin/python"
LOG_FILE="$HOME/.claude/metrics/brain-sync.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Brain sync starting" >> "$LOG_FILE"
"$VENV" "$BACKEND_DIR/scripts/brain_knowledge_dump.py" >> "$LOG_FILE" 2>&1 || true

exit 0
