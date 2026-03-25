#!/bin/bash
# Install Jake's morning briefing LaunchAgent
# Run this once to set up automatic 7:00 AM briefings

set -euo pipefail

PLIST_NAME="com.jake.morning-briefing.plist"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_SRC="${SCRIPT_DIR}/${PLIST_NAME}"
PLIST_DST="${HOME}/Library/LaunchAgents/${PLIST_NAME}"
LOG_DIR="${HOME}/.jake/logs"

echo "=== Jake Morning Briefing Installer ==="

# Create log directory
mkdir -p "$LOG_DIR"
echo "  Log dir: $LOG_DIR"

# Unload existing if present
if launchctl list | grep -q "com.jake.morning-briefing"; then
    echo "  Unloading existing agent..."
    launchctl unload "$PLIST_DST" 2>/dev/null || true
fi

# Copy plist
cp "$PLIST_SRC" "$PLIST_DST"
echo "  Installed: $PLIST_DST"

# Load
launchctl load "$PLIST_DST"
echo "  Loaded: com.jake.morning-briefing"

echo ""
echo "  Morning briefing will run daily at 7:00 AM"
echo "  Logs: $LOG_DIR/morning-briefing.log"
echo ""
echo "  To test now:  python3 pai/pipelines/run.py briefing"
echo "  To uninstall: launchctl unload ~/Library/LaunchAgents/$PLIST_NAME"
echo ""
echo "=== Done ==="
