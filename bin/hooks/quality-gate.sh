#!/usr/bin/env bash
# V10.0 Layer 2 — PostToolUse Quality Gate
# Runs after Write/Edit operations. Provides feedback on code quality.
set -euo pipefail

FILE_PATH="${CLAUDE_FILE_PATH:-}"
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# Skip non-code files
case "$FILE_PATH" in
    *.md|*.yaml|*.yml|*.json|*.txt|*.gitkeep|*.lock)
        exit 0
        ;;
esac

# Python files: basic syntax check
if [[ "$FILE_PATH" == *.py ]]; then
    if command -v python3 &>/dev/null; then
        if ! python3 -c "import ast; ast.parse(open('$FILE_PATH').read())" 2>/dev/null; then
            echo "additionalContext: WARNING — Python syntax error detected in $FILE_PATH. Please fix before proceeding." >&2
        fi
    fi
    exit 0
fi

# TypeScript/JavaScript: check for common issues
if [[ "$FILE_PATH" == *.ts || "$FILE_PATH" == *.tsx || "$FILE_PATH" == *.js || "$FILE_PATH" == *.jsx ]]; then
    # Check for console.log left in production code
    if grep -q 'console\.log' "$FILE_PATH" 2>/dev/null; then
        echo "additionalContext: Note — console.log found in $FILE_PATH. Remove before committing if not intentional." >&2
    fi
    exit 0
fi

exit 0
