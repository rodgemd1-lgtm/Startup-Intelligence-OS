#!/usr/bin/env bash
# sync-telos-to-openclaw.sh — Sync TELOS files to OpenClaw workspace
# Run after updating any TELOS file to push changes to Jake's identity layer.
#
# Usage: bash pai/scripts/sync-telos-to-openclaw.sh

set -euo pipefail

TELOS_DIR="${HOME}/Desktop/Startup-Intelligence-OS/pai/TELOS"
WORKSPACE="${HOME}/.openclaw/workspace-jake"

if [ ! -d "$TELOS_DIR" ]; then
  echo "ERROR: TELOS directory not found at $TELOS_DIR"
  exit 1
fi

if [ ! -d "$WORKSPACE" ]; then
  echo "ERROR: OpenClaw workspace not found at $WORKSPACE"
  exit 1
fi

echo "Syncing TELOS → OpenClaw workspace..."

# Build the TELOS section for IDENTITY.md from source files
MISSION=$(sed -n '3p' "$TELOS_DIR/MISSION.md" | sed 's/^## //')

echo "  Reading MISSION: ${MISSION:0:60}..."
echo "  Reading GOALS..."
echo "  Reading STRATEGIES..."
echo "  Reading BELIEFS..."
echo "  Reading PROBLEMS..."

# Copy raw TELOS files to workspace for full reference
mkdir -p "$WORKSPACE/telos"
for f in MISSION.md GOALS.md STRATEGIES.md BELIEFS.md PROBLEMS.md CHALLENGES.md \
         NARRATIVES.md MODELS.md LEARNED.md IDEAS.md WISDOM.md WRONG.md \
         PREDICTIONS.md PROJECTS.md FRAMES.md BOOKS.md; do
  if [ -f "$TELOS_DIR/$f" ]; then
    cp "$TELOS_DIR/$f" "$WORKSPACE/telos/$f"
  fi
done

echo "  Copied $(ls "$WORKSPACE/telos/" | wc -l | tr -d ' ') TELOS files to $WORKSPACE/telos/"
echo ""
echo "DONE. OpenClaw will pick up changes on next interaction."
echo ""
echo "Note: IDENTITY.md and USER.md contain curated TELOS summaries."
echo "For full TELOS content, files are in $WORKSPACE/telos/"
