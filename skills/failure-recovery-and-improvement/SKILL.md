---
skillId: failure-recovery-and-improvement
name: failure-recovery-and-improvement
description: "Diagnose execution failures, gate rejections, test breakages, or memory corruption; execute rollback or remediation; update memory and post-mortem backlog."
purpose: Diagnose execution failures, gate rejections, test breakages, or memory corruption; execute rollback or remediation; update memory and post-mortem backlog.
whenToUse:
  - A task fails during Gate G4 execution or regression test suites break
  - Independent review (Gate G5) rejects a deliverable with blocking defects
  - Memory state drift or corruption is detected between memory/state.json and git HEAD
  - An unhandled runtime error or exception disrupts automated multi-agent orchestration
  - Conducting a post-mortem and updating durable memory to prevent recurring failures
prerequisites:
  - Error logs, stack trace, or gate rejection rationale available
  - Git repository access to perform inspection, reset, or branch isolation
  - Write access to memory/state.json and backlogAndHistory
inputs:
  - name: failureContext
    type: object
    description: "Details of the failure: failed task ID, error output, stack trace, or rejection report"
  - name: failureType
    type: string
    description: "Classification: TEST_FAILURE, GATE_REJECTION, BOUNDARY_VIOLATION, MEMORY_DRIFT, BUILD_ERROR"
  - name: allowRollback
    type: boolean
    description: Whether automated git stash/reset rollback is permitted
procedure:
  - stepNumber: 1
    title: Root Cause Analysis (RCA)
    action: "Analyze error stack trace, test assertion failures, or review comments. Trace error to exact root cause: logic defect, schema discrepancy, missing dependency, or race condition."
  - stepNumber: 2
    title: Blast Radius and Repository State Assessment
    action: Run git status and git diff. Assess whether uncommitted changes are safe or require stash/revert. Verify whether other modules or workstreams were impacted.
  - stepNumber: 3
    title: Safe Remediation or Rollback Execution
    action: If isolated, apply minimal targeted fix. If failure is destructive or pervasive and allowRollback is true, execute git checkout / revert to return to last known green commit.
  - stepNumber: 4
    title: Re-Verification Execution
    action: Re-run the failing test suite or gate check using testing-and-verification. Verify that the remediation resolves the root cause without introducing new regressions.
  - stepNumber: 5
    title: Memory State and Backlog Update
    action: "Record the incident in memory/state.json: add bug or technical debt item to backlogAndHistory, update executionState, and document post-mortem lesson in durableKnowledge."
  - stepNumber: 6
    title: Process Improvement Rule Formulation
    action: Formulate a defensive rule or linter check to permanently prevent this class of failure in future development cycles.
expectedOutputs:
  - Resolved codebase with clean passing verification suites
  - Post-mortem summary report documenting root cause, remediation, and prevention rule
  - Updated memory/state.json capturing incident and durable learnings
applicableApprovalGates:
  - G4
  - G5
  - G6
failureAndRecovery:
  potentialFailures:
    - Remediation attempt introduces secondary regressions in unrelated components
    - Rollback accidentally clobbers user's uncommitted manual modifications
    - Unreproducible or intermittent test failure
  recoveryStrategy: Never use destructive git reset --hard without user confirmation. Stash uncommitted changes prior to any rollback. If test is flaky, isolate test in quarantine fixture and log critical defect.
verificationCriteria:
  - Original failing condition is verified fixed by successful test execution (exit code 0)
  - No uncommitted changes outside the remediated task scope
  - Post-mortem record is logged in memory/state.json with actionable lesson learned
  - All full regression suites pass cleanly
relevantContractsAndMemory:
  contracts:
    - contracts/implementation/contract.json
    - contracts/quality/contract.json
  memoryRecords:
    - executionState.blockedTasks
    - backlogAndHistory.bugs
    - backlogAndHistory.technicalDebt
    - backlogAndHistory.decisionHistory
---

# Failure Recovery and Improvement (`failure-recovery-and-improvement`)

## 1. Purpose
The `failure-recovery-and-improvement` skill provides a systematic, blameless, and highly reliable incident response protocol for diagnosing and resolving failures occurring throughout the Project Intelligence lifecycle. Whether an automated test suite breaks, an independent review (Gate G5) rejects a deliverable, or git working tree drift corrupts durable memory, this skill performs disciplined Root Cause Analysis (RCA), executes non-destructive rollback or remediation, and commits post-mortem lessons to durable project memory.

## 2. When to Use It
Activate this skill in the following scenarios:
- **Build / Test Breakage in G4**: A task implementation triggers compilation errors, linter violations, or failed test assertions.
- **Gate G5 Review Rejection**: The independent reviewer flags blocking architectural defects, security issues, or anti-slop violations.
- **Git State Drift**: The repository has external uncommitted changes or diverged branches that conflict with `memory/state.json`.
- **Unhandled Agent Crash**: A subagent terminates abnormally or violates file ownership boundaries.
- **Post-Mortem Continuous Improvement**: Extracting defensive guardrails and updating conventions after resolving an unexpected bug.

## 3. Prerequisites
- Failure symptoms, logs, stack traces, or review rejection reports are accessible.
- Git CLI is installed with access to repository commit history.
- Write access to `memory/state.json`.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `failureContext` | `object` | Structured error payload: failing task, error output, stack trace, diff. |
| `failureType` | `string` | Classification (`TEST_FAILURE`, `GATE_REJECTION`, `BOUNDARY_VIOLATION`, `MEMORY_DRIFT`, `BUILD_ERROR`). |
| `allowRollback` | `boolean` | Permission flag indicating whether git revert/stash operations are authorized. |

## 5. Procedure (Step-by-Step)
1. **Root Cause Analysis (RCA)**:
   - Isolate the failing step or assertion.
   - Trace backward through recent git commits and edits:
     - Is it a regression introduced by recent edits?
     - Is it an environment mismatch (missing dependencies, wrong runtime version)?
     - Is it an ambiguous specification or contract violation?
   - Formulate a succinct Root Cause statement.

2. **Blast Radius & Working Tree Quarantine**:
   - Check `git status --porcelain`.
   - Protect uncommitted developer work by creating a safe stash: `git stash create`.
   - Determine which files are clean versus mutated.

3. **Remediation & Targeted Rollback**:
   - **For Targeted Bugs**: Apply the minimal diff directly resolving the root cause. Avoid broad, unfocused refactorings during incident recovery.
   - **For Severe Regressions / Corrupted State**: If `allowRollback` is enabled, revert to the last known green commit:
     - Never use destructive `git reset --hard` without verifying that uncommitted changes are safely stashed.
     - Prefer `git revert` or restoring specific files via `git checkout <commit> -- <file>`.

4. **Defensive Verification & Regression Testing**:
   - Execute the targeted test that originally failed to verify the fix.
   - Execute the entire project regression suite to guarantee zero collateral damage.
   - Require exit code 0 and clean output before declaring recovery complete.

5. **Durable Memory & Backlog Updates**:
   - Record the bug in `memory/state.json`:
     - Add ticket under `backlogAndHistory.bugs` with root cause and resolution.
     - If a workaround or debt was accepted, add to `backlogAndHistory.technicalDebt`.
   - Update `durableKnowledge.architecturalDecisions` if an architectural adjustment was made.

6. **Process Improvement & Rule Codification**:
   - Synthesize a defensive rule (e.g., a new linter check, strict type annotation, or pre-commit hook) to ensure the bug cannot be reintroduced.

## 6. Expected Outputs
- Restored, green codebase with all verification tests passing cleanly.
- Incident post-mortem document summarizing RCA, remediation, and preventive guardrails.
- Updated `memory/state.json` recording the defect resolution and memory learnings.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G4 (Implementation Verification)**: Recovers broken tasks and repairs failing tests.
- **Gate G5 (Independent Review)**: Resolves review rejection items before re-submitting for review.
- **Gate G6 (Release / Handoff)**: Handles last-mile reconciliation and defect tracking.

## 8. Failure and Recovery Behavior
- **Cascading Test Failures**: If remediation breaks other components, immediately revert remediation diff to return to known state. Re-evaluate architecture with lead orchestrator.
- **Accidental User Data Clobbering**: In all operations, verify working tree before mutating files. Stash untracked/uncommitted files before git tree operations.

## 9. Verification Criteria
- The original failing test now passes consistently with exit code 0.
- Entire project test suite passes with zero regressions.
- No files outside the failing component's boundary are modified.
- Incident is logged in durable memory with explicit root cause.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/implementation/contract.json`
  - `contracts/quality/contract.json`
- **Memory Records**:
  - `executionState.blockedTasks`
  - `backlogAndHistory.bugs`
  - `backlogAndHistory.technicalDebt`
  - `backlogAndHistory.decisionHistory`
