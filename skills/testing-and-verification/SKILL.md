---
skillId: testing-and-verification
name: testing-and-verification
description: "Execute verification suites (unit, integration, linting, security, coverage, a11y) to generate verifiable, honest proof of correctness for G4 exit."
purpose: Execute verification suites (unit, integration, linting, security, coverage, a11y) to generate verifiable, honest proof of correctness for G4 exit.
whenToUse:
  - Validating implemented features against active quality profile thresholds
  - Measuring code coverage and running end-to-end regression suites
  - Auditing dependency security vulnerabilities and static analysis lints
  - Compiling honest verification evidence (PASSED, FAILED, BLOCKED, SKIPPED, UNAVAILABLE) to satisfy Gate G4 exit criteria
prerequisites:
  - Code changes implemented within Gate G4
  - Active quality profile identified in core/quality/profiles.json or contracts/quality/contract.json
  - Test runner and verification tools installed in environment
inputs:
  - name: qualityProfile
    type: string
    description: Active profile name (PROTOTYPE, STANDARD, PRODUCTION_READY, SECURITY_SENSITIVE, DESIGN_INTENSIVE)
  - name: testTargets
    type: array
    description: List of test files, directories, or suites to execute
  - name: coverageThreshold
    type: integer
    description: Minimum required test coverage percentage as specified by active profile
procedure:
  - stepNumber: 1
    title: Quality Profile Rules Extraction
    action: "Load active profile settings from core/quality/profiles.json. Determine required suites: linting, unit tests, coverage percentage, security scans, accessibility."
  - stepNumber: 2
    title: Static Analysis and Linter Execution
    action: Run configured static analysis tools (e.g., eslint, ruff, flake8, mypy, tsc). Verify zero errors and zero unsuppressed warnings.
  - stepNumber: 3
    title: Automated Test Suite Execution
    action: Run unit and integration test runners (e.g., pytest, jest, vitest, go test). Record pass/fail counts, duration, and test output.
  - stepNumber: 4
    title: Code Coverage Measurement
    action: Execute coverage analyzer (e.g., coverage.py, istanbul/c8). Calculate line and branch coverage percentage. Verify against profile threshold.
  - stepNumber: 5
    title: Security and Dependency Vulnerability Audit
    action: If mandated by profile, execute dependency vulnerability audit (e.g., pip-audit, npm audit, trivy). Confirm zero high/critical vulnerabilities.
  - stepNumber: 6
    title: Honest Verification Evidence Compilation
    action: "Compile comprehensive evidence report. Record each check with strict honest status: PASSED, FAILED, BLOCKED, SKIPPED, or UNAVAILABLE. Never report unexecuted checks as passed."
expectedOutputs:
  - Honest verification evidence report with execution commands, exit codes, and coverage metrics
  - Contracts/quality/contract.json updated with verification results
  - Defect tickets in memory/state.json backlog if tests fail
applicableApprovalGates:
  - G4
  - G5
failureAndRecovery:
  potentialFailures:
    - Test failure in unit or integration suite
    - Code coverage below active profile threshold
    - Missing test tool in host environment
  recoveryStrategy: If tests fail, mark task as FAILED, log detailed assertion traceback, and route back to implementation. If coverage is below threshold, write tests for uncovered branches. If tool is unavailable, honestly report status as UNAVAILABLE with remediation instructions.
verificationCriteria:
  - All executed tests pass with exit code 0
  - Measured code coverage meets or exceeds active profile threshold
  - Static analysis reports zero errors
  - Verification report strictly conforms to honesty standards with zero hallucinated passes
relevantContractsAndMemory:
  contracts:
    - contracts/implementation/contract.json
    - contracts/quality/contract.json
  memoryRecords:
    - executionState.completedTasks
    - backlogAndHistory.bugs
---

# Testing and Verification (`testing-and-verification`)

## 1. Purpose
The `testing-and-verification` skill executes and evaluates all automated quality, regression, security, and accessibility verification suites. It establishes empirical proof of correctness based on real test execution outputs and exit codes. Crucially, it enforces **Strict Verification Honesty (BL-006)**: confidence is never equated with verification, and checks must be reported as `PASSED`, `FAILED`, `BLOCKED`, `SKIPPED`, or `UNAVAILABLE`.

## 2. When to Use It
Activate this skill in the following scenarios:
- Verifying code changes at the conclusion of implementation tasks in Gate G4.
- Running continuous regression tests before requesting human or independent review.
- Measuring test coverage against the thresholds defined in the active quality profile.
- Generating the formal quality evidence bundle required for Gate G4 exit and Gate G5 entry.

## 3. Prerequisites
- Implementation changes completed in assigned source directories.
- Active quality profile configured in `core/quality/profiles.json`.
- Test runners and linters available in the execution environment.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `qualityProfile` | `string` | The active profile (`PROTOTYPE`, `STANDARD`, `PRODUCTION_READY`, `SECURITY_SENSITIVE`, `DESIGN_INTENSIVE`). |
| `testTargets` | `array` | Paths to test files or test suites to execute. |
| `coverageThreshold` | `integer` | Minimum required line coverage percentage. |

## 5. Procedure (Step-by-Step)
1. **Quality Profile Requirements Loading**:
   - Query `core/quality/profiles.json` for active profile specifications:
     - `minCoveragePercent`: (e.g. 70% for STANDARD, 85% for PRODUCTION_READY).
     - `requiresLinting`: Boolean.
     - `requiresUnitTests`: Boolean.
     - `requiresSecurityScan`: Boolean.
     - `requiresAccessibilityAudit`: Boolean.

2. **Static Analysis & Linting Check**:
   - Execute project linter and type checker (e.g., `ruff check .`, `mypy --strict .`, `eslint .`).
   - Parse exit code. If non-zero, capture violations and record status `FAILED`.

3. **Automated Unit & Integration Test Execution**:
   - Execute the test suite with verbose reporting (e.g., `pytest -v`, `npm test -- --reporter=verbose`).
   - Capture standard output, standard error, duration, and test counts (passed, failed, skipped).
   - If any test fails, record failure details and mark suite `FAILED`.

4. **Code Coverage Measurement**:
   - Run coverage collection tool (e.g., `pytest --cov=src`, `jest --coverage`).
   - Extract total line and branch coverage percentage.
   - If measured coverage < `coverageThreshold`, record coverage check as `FAILED`.

5. **Security & Dependency Vulnerability Scan**:
   - If required by profile, execute scanner (`pip-audit`, `npm audit --audit-level=high`).
   - Check for known CVEs. Any high or critical vulnerability results in `FAILED` status.

6. **Honest Verification Evidence Compilation**:
   - Collate all results into a structured evidence table:
     - **Check Name**: Linter, Unit Tests, Coverage, Security Scan.
     - **Command Executed**: Full CLI command line.
     - **Status**: Exactly one of `PASSED`, `FAILED`, `BLOCKED`, `SKIPPED`, `UNAVAILABLE`.
     - **Evidence**: Exit code, test counts, key output snippets.
   - Never report a check as `PASSED` if it was not executed or tools were missing.

## 6. Expected Outputs
- Empirical Verification Evidence Bundle with exact execution commands and logs.
- Quality contract update in `contracts/quality/contract.json`.
- Automated bug logging in `memory/state.json` under `backlogAndHistory.bugs` if failures occur.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G4 (Implementation Verification)**: Delivers test verification evidence to exit G4.
- **Gate G5 (Independent Review)**: Provides empirical telemetry for the independent reviewer.

## 8. Failure and Recovery Behavior
- **Test Assertion Failure**: Immediately halt progression to Gate G5. Log defect with stack trace, set task status to `FAILED`, and trigger `controlled-implementation` remediation.
- **Coverage Deficit**: Identify uncovered functions from coverage report and generate targeted unit tests.
- **Missing CLI Tool**: Report status honestly as `UNAVAILABLE` and provide command instructions for host installation. Never fake a pass.

## 9. Verification Criteria
- All executed test suites exit with code 0.
- Measured coverage satisfies active profile threshold.
- Verification status values are 100% honest and backed by terminal logs.
- Zero unresolved high/critical security scan findings.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/implementation/contract.json`
  - `contracts/quality/contract.json`
- **Memory Records**:
  - `executionState.completedTasks`
  - `backlogAndHistory.bugs`
