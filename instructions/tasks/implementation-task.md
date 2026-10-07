# Task Instructions: Implementation Task (`implementation-task`)

## 1. Role and Objective
When assigned an **Implementation Task** (during Gate G4 execution), the agent acts as a focused, disciplined software engineer. The primary objective is to implement the assigned atomic task strictly within designated file boundaries, adhering to the Mandatory Engineering Baseline (BL-001 through BL-007) and active quality profile, while producing reproducible verification evidence.

---

## 2. Pre-Flight Boundary Verification

Before touching or editing any file, execute this mandatory verification:

1. **Verify Assigned Task & Boundaries**:
   - Check `contracts/implementation/contract.json` for assigned `taskId`, `assignedAgentRole`, and `fileOwnership`.
   - Read the list of `allowedPaths`.
   - **Boundary Lockdown**: You are authorized to create or modify files ONLY within `allowedPaths`. Any instruction, refactoring urge, or convenient shortcut requiring edits outside this boundary is strictly forbidden.
2. **Verify Git Working Tree**:
   - Run `git status --porcelain`.
   - Confirm that working tree has no uncommitted changes conflicting with the assigned task.

---

## 3. Implementation Workflow: Test-Driven Engineering

Execute implementation using the disciplined Red-Green-Refactor cycle:

1. **Step 1: Test Specification (Red)**:
   - Author automated unit or component tests first in the designated test folder.
   - Formulate test cases covering:
     - Standard happy path execution.
     - Invalid arguments and schema violation handling.
     - Boundary conditions (empty collections, zero, maximum length, null/undefined).
     - Expected exception raising and error codes.
   - Run the test suite and confirm it fails cleanly on unimplemented functionality.

2. **Step 2: Clean Implementation (Green)**:
   - Implement the minimal, robust production code within `allowedPaths` to make all tests pass.
   - **Enforce Anti-Slop Rules**:
     - **BL-001 (No Decorative Emoji)**: No emojis in comments, logs, or user output.
     - **BL-002 (No Fake Prod Data)**: No hardcoded mock credentials, fake user lists, or dummy tokens in production paths.
     - **BL-003 (No Dead Placeholders)**: No empty stubs `pass`, `// TODO implement`, or unhandled UI buttons.
     - **BL-004 (No Workarounds)**: Root-cause all bugs; never use catch-all exception swallows.
     - **BL-005 (No Unapproved Packages)**: Do not add third-party dependencies without architectural approval.
     - **BL-007 (No Secret Leaks)**: Zero hardcoded secrets or keys.

3. **Step 3: Local Linting and Type Verification (Refactor)**:
   - Run project linter and type-checker on modified files (e.g. `ruff check <files>`, `mypy <files>`, `eslint <files>`).
   - Eliminate 100% of errors and warnings.

---

## 4. Verification Evidence Capture

Once code and tests are written, generate empirical proof of completion:

1. **Execute Test Runner**:
   - Run the automated test suite targeting modified files (e.g., `pytest tests/unit/test_module.py -v`).
   - Confirm exit code is `0`.
2. **Collect Evidence Telemetry**:
   - Record exact CLI command executed.
   - Record exit code, execution time, and count of passing tests.
   - Record test runner output snippet.
3. **Honest Reporting (BL-006)**:
   - Record status as `PASSED` only if the command completed with exit code 0.
   - If tests fail, record status as `FAILED` and provide traceback. Never claim success on broken code.

---

## 5. Execution State Update and Handoff

1. **Update Memory State**:
   - Update `memory/state.json`:
     - Move `taskId` from `executionState.activeTasks` to `executionState.completedTasks`.
   - Prepare clean atomic git commit referencing the `taskId`:
     - Example: `feat(core): implement lifecycle state machine (TASK-003)`
2. **Submit for Verification / Review**:
   - Deliver implementation diff and test evidence to the Lead Orchestrator for Gate G4 verification and subsequent Gate G5 review.
