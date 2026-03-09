#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/Startup-Intelligence-OS"
  exit 1
fi

TARGET_REPO="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKET_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AGGRESSIVE_ROOT="$PACKET_ROOT/assets/decision_capability_os_aggressive_pack"

if [[ ! -d "$TARGET_REPO/.git" ]]; then
  echo "Target does not look like a git repo: $TARGET_REPO"
  exit 1
fi

DEST="$TARGET_REPO/docs/plans/decision-capability-os"
mkdir -p "$DEST"

# Copy aggressive plan docs
cp "$AGGRESSIVE_ROOT/README.md" "$DEST/README.md"
cp "$AGGRESSIVE_ROOT/docs/aggressive-plan.md" "$DEST/aggressive-plan.md"
cp "$AGGRESSIVE_ROOT/docs/operating-model.md" "$DEST/operating-model.md"
cp "$AGGRESSIVE_ROOT/docs/interface-spec.md" "$DEST/interface-spec.md"
cp "$AGGRESSIVE_ROOT/docs/capability-gap-map.md" "$DEST/capability-gap-map.md"
cp "$AGGRESSIVE_ROOT/docs/implementation-backlog.md" "$DEST/implementation-backlog.md"

mkdir -p "$DEST/prototype"
cp "$AGGRESSIVE_ROOT/prototype/jake-console.html" "$DEST/prototype/jake-console.html"

# Copy scaffold seed as reference material
mkdir -p "$DEST/scaffold-seed"
cp -R "$AGGRESSIVE_ROOT/scaffold/." "$DEST/scaffold-seed/"

# Copy this Codex handoff packet
mkdir -p "$DEST/codex-handoff"
cp "$PACKET_ROOT/README.md" "$DEST/codex-handoff/README.md"
cp -R "$PACKET_ROOT/docs/." "$DEST/codex-handoff/"
mkdir -p "$DEST/codex-handoff/scripts"
cp "$PACKET_ROOT/scripts/stage-into-repo.sh" "$DEST/codex-handoff/scripts/stage-into-repo.sh"

echo "Imported plan artifacts into:"
echo "  $DEST"
echo
echo "Suggested next commands:"
echo "  cd \"$TARGET_REPO\""
echo "  git status"
echo "  git add docs/plans/decision-capability-os"
echo "  git commit -m \"Add Decision & Capability OS aggressive plan and Codex handoff packet\""
