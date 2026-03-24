#!/bin/bash
# fabric-run.sh — Wrapper for OpenClaw deterministic dispatch
# Parses "PATTERN: TEXT" or "PATTERN URL" format and runs fabric
#
# Usage:
#   fabric-run.sh summarize: The best way to predict the future is to create it.
#   fabric-run.sh w https://paulgraham.com/ds.html
#   fabric-run.sh extract_wisdom https://example.com/article

set -eo pipefail

FABRIC_BIN="/Users/michaelrodgers/go/bin/fabric"

# Parse first arg as pattern
RAW_PATTERN="${1:-summarize}"
# Remove trailing colon if present
RAW_PATTERN="${RAW_PATTERN%:}"
shift || true

# Resolve aliases
case "$RAW_PATTERN" in
  w) PATTERN="extract_wisdom" ;;
  s) PATTERN="summarize" ;;
  a) PATTERN="analyze_claims" ;;
  i) PATTERN="extract_ideas" ;;
  r) PATTERN="analyze_risk" ;;
  p) PATTERN="create_prd" ;;
  f) PATTERN="find_logical_fallacies" ;;
  c) PATTERN="compare_and_contrast" ;;
  q) PATTERN="extract_questions" ;;
  *) PATTERN="$RAW_PATTERN" ;;
esac

# Remaining args are the input
INPUT="$*"

if [ -z "$INPUT" ]; then
  echo "Error: No input provided. Usage: /fabric PATTERN text or URL"
  exit 1
fi

# Detect if input is a URL
if [[ "$INPUT" =~ ^https?:// ]]; then
  # URL mode
  exec env -i HOME=/Users/michaelrodgers \
    PATH=/usr/local/bin:/usr/bin:/bin:/Users/michaelrodgers/go/bin \
    "$FABRIC_BIN" -u "$INPUT" --pattern "$PATTERN"
else
  # Text mode — pipe through stdin
  echo "$INPUT" | exec env -i HOME=/Users/michaelrodgers \
    PATH=/usr/local/bin:/usr/bin:/bin:/Users/michaelrodgers/go/bin \
    "$FABRIC_BIN" --pattern "$PATTERN"
fi
