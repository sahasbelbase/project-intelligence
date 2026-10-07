#!/usr/bin/env bash
# ==============================================================================
# Project Intelligence — Claude Code PreToolUse Hook
# Intercepts Bash command tool calls before execution.
# Enforces command prefix allowlists and blocks prohibited destructive commands.
# Return code 2 signals deterministic permission denial to Claude Code.
# ==============================================================================

set -euo pipefail

# In Claude Code, the command payload is passed via environment variable or stdin
COMMAND="${TOOL_INPUT_COMMAND:-${1:-}}"

if [ -z "$COMMAND" ]; then
    # No command string provided, allow execution to proceed
    exit 0
fi

# 1. Block destructive operations unconditionally
BLOCKED_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "git push --force"
    "git reset --hard"
    "git clean -fdx"
    ":(){ :|:& };:"
    "drop database"
    "drop table"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$pattern"* ]]; then
        echo "========================================================================" >&2
        echo " [SECURITY VIOLATION] Command contains prohibited destructive pattern: '$pattern'" >&2
        echo " Execution denied by Project Intelligence PreToolUse hook." >&2
        echo "========================================================================" >&2
        # Exit code 2 instructs Claude Code to deny tool execution
        exit 2
    fi
done

# 2. Check for unvetted package installations outside virtual environments
if [[ "$COMMAND" =~ ^pip\ install\  ]] && [[ -z "${VIRTUAL_ENV:-}" ]]; then
    echo "[WARNING] Global pip install detected outside virtual environment." >&2
    echo "Please activate or create a virtual environment first." >&2
    exit 2
fi

# Allow execution
exit 0
