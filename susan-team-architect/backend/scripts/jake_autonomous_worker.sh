#!/usr/bin/env bash
# jake_autonomous_worker.sh — Shell wrapper for the autonomous worker daemon.
# Called by launchd. Activates the venv and runs the Python daemon.
set -euo pipefail

BACKEND="$HOME/Startup-Intelligence-OS/susan-team-architect/backend"
VENV="$BACKEND/.venv/bin/python"
LOG="$HOME/.hermes/logs/autonomous_worker.log"
SCRIPT="$BACKEND/scripts/jake_autonomous_worker.py"

# Load environment
if [ -f "$HOME/.hermes/.env" ]; then
    # shellcheck disable=SC1091
    set -a; source "$HOME/.hermes/.env"; set +a
fi

mkdir -p "$(dirname "$LOG")"

echo "=== jake_autonomous_worker.sh START $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

exec "$VENV" "$SCRIPT" daemon --interval 60 >> "$LOG" 2>&1
