#!/usr/bin/env bash
# Hook Profile Gate — wraps another hook and only runs it if the current
# profile allows it.
#
# Usage: hook-profile.sh <profiles> <script> [args...]
#   profiles: comma-separated list of profiles that enable this hook
#             valid values: minimal, standard, strict
#   script:   path to the hook script to run (relative to repo root or absolute)
#
# Environment:
#   INTELLIGENCE_HOOK_PROFILE=minimal|standard|strict (default: standard)
#   INTELLIGENCE_DISABLED_HOOKS=comma,separated,hook,names
#
# Examples:
#   hook-profile.sh "standard,strict" bin/hooks/pre-compact.sh
#   hook-profile.sh "strict" bin/hooks/some-strict-only-hook.sh
set -uo pipefail

PROFILES="${1:-standard,strict}"
SCRIPT="${2:-}"
shift 2 2>/dev/null || true

# Get current profile (default: standard)
CURRENT_PROFILE="${INTELLIGENCE_HOOK_PROFILE:-standard}"

# Check if hook name is explicitly disabled
HOOK_NAME=$(basename "$SCRIPT" .sh 2>/dev/null || echo "unknown")
DISABLED="${INTELLIGENCE_DISABLED_HOOKS:-}"
if echo ",$DISABLED," | grep -qi ",$HOOK_NAME,"; then
  # Pass through stdin and exit
  cat
  exit 0
fi

# Check if current profile is in the allowed profiles list
MATCH=0
IFS=',' read -ra ALLOWED <<< "$PROFILES"
for p in "${ALLOWED[@]}"; do
  if [ "$(echo "$p" | tr '[:upper:]' '[:lower:]' | tr -d ' ')" = "$(echo "$CURRENT_PROFILE" | tr '[:upper:]' '[:lower:]')" ]; then
    MATCH=1
    break
  fi
done

if [ "$MATCH" -eq 0 ]; then
  # Profile doesn't match — pass through stdin and skip
  cat
  exit 0
fi

# Profile matches — run the actual hook
if [ -n "$SCRIPT" ] && [ -f "$SCRIPT" ]; then
  exec bash "$SCRIPT" "$@"
elif [ -n "$SCRIPT" ]; then
  # Try relative to repo root
  REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
  if [ -f "$REPO_ROOT/$SCRIPT" ]; then
    exec bash "$REPO_ROOT/$SCRIPT" "$@"
  fi
fi

# Script not found — pass through
cat
exit 0
