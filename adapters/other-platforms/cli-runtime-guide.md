# CLI & Manual Runtime Guide

## 1. Overview
This guide provides executable workflows for driving the **Project Intelligence** framework from any standard POSIX shell (Bash, Zsh), Windows PowerShell, or terminal-based AI assistant (Aider, CLI tools) with **zero external dependencies**.

---

## 2. Command-Line Lifecycle Operations

### Step 1: Pre-Flight Environment Inspection (Gate G0)
Inspect the working tree and verify python environment:
```bash
git status --porcelain
python -V
```

### Step 2: Validate Core Schemas & Contracts
Verify that all canonical JSON schemas in `core/schemas/` and contract payloads in `contracts/` are valid:
```bash
python -m unittest validation/schema-tests/test_schemas.py
```
Expected output:
```text
Ran 3 tests in 0.016s
OK
```

### Step 3: Run Deterministic Lifecycle State Checks
Run the lifecycle transition engine to inspect the active gate:
```bash
python core/lifecycle/engine.py --status
```
Alternatively, inspect memory telemetry directly via Python:
```bash
python -c "
import json, pathlib
p = pathlib.Path('memory/execution-state.json') if pathlib.Path('memory/execution-state.json').exists() else pathlib.Path('memory/state.json')
state = json.load(open(p))
print('Active Gate:', state.get('currentGate', 'G0'))
print('Active Phase:', f'Phase {state.get(\"activePhase\", 0)}')
"
```

---

## 3. Git Pre-Commit Hook Integration

To enforce gate validation deterministically without IDE hooks, install the standard Git `pre-commit` hook:

```bash
cat << 'EOF' > .git/hooks/pre-commit
#!/usr/bin/env bash
set -e

echo "[Project Intelligence] Running pre-commit schema & contract verification..."
python -m unittest validation/schema-tests/test_schemas.py

echo "[Project Intelligence] Pre-commit validation passed."
EOF

chmod +x .git/hooks/pre-commit
```

Now, any attempt to commit invalid contract envelopes, malformed JSON schemas, or broken contract payloads will be blocked by Git before entering version history.

---

## 4. Driving Multi-Role Workflows in Single-Agent Tools (e.g., Aider, Cursor)

When using a single-agent interface:
1. **Declare Active Role**: Tell the model:
   > "For this turn, assume the role of `architecture` under Gate G3. Consult `agents/architecture/agent.json` and generate `contracts/architecture/contract.json`."
2. **Review Output**: Verify the generated contract against `core/schemas/architecture-contract.schema.json`.
3. **Transition to Implementation**:
   > "For this turn, assume the role of `implementation` under Gate G4. Modify only the assigned files in `src/`."
4. **Transition to Verification**:
   > "Run `pytest` or `python -m unittest` in terminal and capture the raw output."
5. **Transition to Review**:
   > "Assume the role of `independent-review` under Gate G5. Audit `git diff` against acceptance criteria and sign off `contracts/quality/contract.json`."
