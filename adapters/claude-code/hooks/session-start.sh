#!/usr/bin/env bash
# ==============================================================================
# Project Intelligence — Claude Code SessionStart Hook
# Executes at the start of every Claude Code session.
# Verifies repository clean state, memory synchronization, and active lifecycle gate.
# ==============================================================================

set -euo pipefail

echo "========================================================================"
echo " [Project Intelligence] Initializing Claude Code Session Hook"
echo "========================================================================"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "[WARNING] git command not found. Running in degraded environment."
    exit 0
fi

# Detect uncommitted changes
DIRTY_COUNT=$(git status --porcelain | wc -l | tr -d ' ')
if [ "$DIRTY_COUNT" -gt 0 ]; then
    echo "[NOTE] Repository has $DIRTY_COUNT uncommitted changes."
    echo "[NOTE] Preserving pre-existing working tree modifications."
else
    echo "[OK] Working tree clean."
fi

# Check memory state file
STATE_FILE=""
if [ -f "memory/execution-state.json" ]; then
    STATE_FILE="memory/execution-state.json"
elif [ -f "memory/state.json" ]; then
    STATE_FILE="memory/state.json"
fi

if [ -n "$STATE_FILE" ]; then
    ACTIVE_GATE=$(python3 -c "import json; data=json.load(open('$STATE_FILE')); print(data.get('currentGate', 'G0'))" 2>/dev/null || echo "G0")
    echo "[LIFECYCLE] Active Lifecycle Gate: $ACTIVE_GATE"
else
    echo "[LIFECYCLE] Initial project state. Active Lifecycle Gate: G0 (Discovery)"
fi

echo "[OK] SessionStart preflight checks complete."
exit 0
