---
skillId: controlled-implementation
name: controlled-implementation
description: "Execute atomic implementation tasks within strictly assigned file boundaries, adhering to mandatory baseline quality and test-driven cycles to achieve G4."
purpose: Execute atomic implementation tasks within strictly assigned file boundaries, adhering to mandatory baseline quality and test-driven cycles to achieve G4.
whenToUse:
  - Writing production source code or unit test suites during Gate G4 execution
  - Implementing assigned tasks from the active implementation contract
  - Executing bug fixes, feature extensions, or refactoring within designated file boundaries
  - Enforcing strict anti-slop rules (no decorative emoji, no fake prod data, no unapproved dependencies)
prerequisites:
  - Gate G3 approved (contracts/architecture/contract.json in APPROVED status)
  - Assigned task from contracts/implementation/contract.json with defined fileOwnership
  - Clean git working tree or documented uncommitted changes
inputs:
  - name: taskId
    type: string
    description: Identifier of the atomic task to implement (e.g., TASK-001)
  - name: allowedPaths
    type: array
    description: Exclusive list of file paths and directories this implementation task is permitted to modify
  - name: acceptanceCriteria
    type: array
    description: Testable conditions and behavior required for task completion
procedure:
  - stepNumber: 1
    title: Pre-Flight Boundary and Hygiene Check
    action: Verify git status is clean. Confirm all files to be edited reside strictly within allowedPaths. Reject any instruction requiring edits outside boundary.
  - stepNumber: 2
    title: Test-Driven Scaffold Construction
    action: Author unit or contract test specifications defining expected inputs, outputs, and edge cases before implementing core logic.
  - stepNumber: 3
    title: Clean Code Implementation
    action: "Implement production logic adhering to Mandatory Baseline Quality (BL-001 through BL-007): zero decorative emoji, zero fake data in prod paths, full error handling, clean typings."
  - stepNumber: 4
    title: Local Compilation and Lint Verification
    action: Run local formatters, linters, and type-checkers on modified files. Ensure zero syntax errors, type mismatches, or lint violations.
  - stepNumber: 5
    title: Test Suite Execution and Evidence Capture
    action: Execute unit test runner. Capture stdout, stderr, and exit code. Verify all test assertions pass with 100% success on modified units.
  - stepNumber: 6
    title: Execution State Update
    action: Update memory/state.json marking taskId as completed in executionState.completedTasks and recording Git diff summary.
expectedOutputs:
  - Production source code and tests strictly confined to allowedPaths
  - Command execution evidence log demonstrating zero compiler/test errors
  - Updated memory/state.json reflecting completed task status
applicableApprovalGates:
  - G4
failureAndRecovery:
  potentialFailures:
    - Task requires touching a file outside assigned allowedPaths
    - Unit tests fail after code changes
    - Linter fails due to style or unused import violations
  recoveryStrategy: If out-of-boundary edit needed, halt task and request architecture contract update. For failing tests, revert breaking change and re-evaluate logic. Run automated formatter (e.g., ruff format, prettier) to resolve style errors.
verificationCriteria:
  - git status shows zero modified files outside assigned allowedPaths
  - All unit and regression tests pass with exit code 0
  - Zero anti-slop violations (no decorative emoji, no hardcoded mocks in prod paths)
  - Implementation contract data tracks task status as VERIFIED
relevantContractsAndMemory:
  contracts:
    - contracts/implementation/contract.json
    - contracts/quality/contract.json
  memoryRecords:
    - executionState.activeTasks
    - executionState.completedTasks
    - executionState.blockedTasks
---

# Controlled Implementation (`controlled-implementation`)

## 1. Purpose
The `controlled-implementation` skill provides a disciplined, defensive, test-driven coding protocol for executing tasks in Gate G4. It guarantees that code changes strictly respect assigned file boundaries, satisfy pre-agreed acceptance criteria, adhere to the **Mandatory Engineering Baseline** (BL-001 through BL-007), and generate concrete execution evidence rather than speculative assertions of completion.

## 2. When to Use It
Activate this skill when:
- Authoring production code or unit tests for tasks scheduled in `contracts/implementation/contract.json`.
- Performing refactoring, bug fixes, or feature development within an assigned workstream.
- Working under multi-agent orchestration where strict file ownership isolation is enforced.
- Producing verifiable artifacts to exit Gate G4.

## 3. Prerequisites
- Gate G3 is formally approved.
- The active task is clearly identified with an assigned `taskId`, `fileOwnership` bounds, and acceptance criteria.
- The Git working tree is in an inspected, known state.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `taskId` | `string` | The unique ID of the task being implemented (e.g., `TASK-004`). |
| `allowedPaths` | `array` | Exclusive list of file paths/directories permitted to be modified. |
| `acceptanceCriteria` | `array` | Explicit functional, behavioral, and verification criteria for the task. |

## 5. Procedure (Step-by-Step)
1. **Pre-Flight Boundary Check**:
   - Check `git status --porcelain`.
   - Validate that every target file to be created or modified is explicitly listed inside `allowedPaths`.
   - **Boundary Lockdown**: If an implementation idea requires editing files outside `allowedPaths`, do NOT modify them. Stop and report a boundary conflict to the Lead Orchestrator.

2. **Test-Driven Specification (Red Phase)**:
   - Create or update the unit test file first (e.g., in `tests/` or alongside source files).
   - Write tests covering standard execution, invalid inputs, edge cases (empty collections, boundary integers, null/undefined inputs), and error handling.
   - Run the test suite to confirm it fails cleanly on the unimplemented logic.

3. **Production Implementation (Green Phase)**:
   - Implement the minimal, robust code necessary to satisfy all test cases.
   - Enforce Mandatory Baseline rules:
     - **BL-001 (No Decorative Emoji)**: No smiley faces, rockets, checkmark emojis in code comments, logs, or user-facing CLI text.
     - **BL-002 (No Fake Prod Data)**: No hardcoded `temp_user_123` or mock credentials in production logic paths.
     - **BL-003 (No Placeholder Code)**: No empty stubs `pass`, `// TODO implement later`, or unhandled non-functional buttons.
     - **BL-004 (No Unexplained Workarounds)**: Root cause all errors; never use empty `try/catch` or silently suppress exceptions.
     - **BL-005 (No Unapproved Dependencies)**: Do not install external libraries without architectural approval.

4. **Linting and Type-Check Verification**:
   - Run the project's official linter and type-checker (e.g., `ruff check`, `mypy`, `eslint`, `tsc --noEmit`).
   - Resolve all warnings and errors. Zero-warning policy is enforced.

5. **Test Suite Execution & Evidence Capture**:
   - Execute the test runner (e.g., `pytest`, `npm test`, `go test -v`).
   - Record the exact command, exit code (must be 0), and pass count in the verification log.

6. **Execution State Transition**:
   - Update `memory/state.json`: move `taskId` from `executionState.activeTasks` to `executionState.completedTasks`.
   - Prepare clean atomic git commit message describing what was changed and citing the `taskId`.

## 6. Expected Outputs
- Completed production code and automated tests strictly located within `allowedPaths`.
- Honest verification record documenting command outputs, passing test counts, and exit code 0.
- Updated `memory/state.json` recording task progress.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G4 (Implementation Verification)**: Primary skill for executing tasks and generating evidence to satisfy Gate G4.

## 8. Failure and Recovery Behavior
- **Out-of-Bounds File Required**: Record task as `BLOCKED` in `memory/state.json` under `executionState.blockedTasks` with rationale. Do not bypass file ownership.
- **Test Failure / Regression**: Revert breaking modifications. Inspect assertion failure, fix root cause, and re-run test suite.
- **Build / Lint Breakage**: Fix formatting or typing issues immediately before submitting task evidence.

## 9. Verification Criteria
- `git status --porcelain` reveals zero changes outside `allowedPaths`.
- All tests pass with exit code 0.
- Code passes all baseline quality rules (no decorative emojis, no mock data in prod, no unresolved TODOs).
- Evidence captured contains actual terminal logs and exit codes.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/implementation/contract.json`
  - `contracts/quality/contract.json`
- **Memory Records**:
  - `executionState.activeTasks`
  - `executionState.completedTasks`
  - `executionState.blockedTasks`
