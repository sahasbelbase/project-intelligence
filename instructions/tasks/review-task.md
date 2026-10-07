# Task Instructions: Review Task (`review-task`)

## 1. Role and Mindset
When assigned a **Review Task** (during Gate G5 execution), the agent acts as an **Independent, Adversarial Reviewer**. The reviewer operates under the premise that the submitted code may contain subtle bugs, unhandled edge cases, security flaws, scope creep, or superficial "AI slop". The goal is not rubber-stamping, but rigorous quality assurance to protect system integrity before release or handoff.

---

## 2. Review Protocol: 5-Pillar Adversarial Audit

Execute the review across the following five dimensions:

### 2.1 Scope & Boundary Integrity Audit
- Execute `git diff <base_commit> HEAD` across all modified files.
- Compare changed files against the assigned `fileOwnership` in `contracts/implementation/contract.json`.
- Compare implemented functionality against `contracts/requirements/contract.json`.
- **Flag Scope Creep**: Any undocumented feature, extra endpoint, or unapproved dependency addition is an immediate defect.

### 2.2 Anti-Slop & Baseline Compliance Audit
- Audit modified lines against Mandatory Baseline rules:
  - **BL-001**: Check for decorative emojis in comments, logs, or UI text.
  - **BL-002**: Check for hardcoded mock data in production classes.
  - **BL-003**: Check for empty function stubs, unhandled buttons, or lingering `TODO` markers.
  - **BL-004**: Check for silent exception swallowing (`except Exception: pass`, empty catch).
  - **BL-005**: Check package manifests for unvetted third-party libraries.
  - **BL-007**: Scan for any committed API keys, secrets, or internal URLs.

### 2.3 Edge Case & Defensive Coding Probing
- Evaluate defensive programming across boundary conditions:
  - **Null / Undefined Handling**: Does code crash on missing keys or empty payloads?
  - **Boundary Integers / Floats**: Are zero, negative numbers, and overflow handled?
  - **String Sanitization**: Are inputs stripped and validated against regex whitelists?
  - **Concurrency & I/O**: Are file writes atomic? Are race conditions prevented?

### 2.4 Test Suite & Evidence Audit
- Re-run test commands independently to verify that test results are genuine and reproducible.
- Inspect test assertions: Verify that tests actually assert correct behavior rather than vacuous checks (e.g. asserting `assert True`).
- Verify that line coverage meets or exceeds the active quality profile threshold (e.g., 70% for STANDARD, 85% for PRODUCTION_READY).

### 2.5 Architecture & Documentation Alignment
- Verify that code changes align with architectural patterns defined in `contracts/architecture/contract.json`.
- Check that new functions or modules include clear, professional docstrings.

---

## 3. Defect Classification and Scoring

Classify every discovered issue into one of three severity levels:

| Severity | Definition | Action Required |
|---|---|---|
| **BLOCKING** | Critical logic defect, crash, security vulnerability, anti-slop violation, contract breach, broken tests | **Rejects Gate G5 immediately**. Loops back to Gate G4 for remediation. |
| **MAJOR** | Performance bottleneck, missing edge case test, suboptimal error handling, missing type hints | **Must be remediated** before final release sign-off. |
| **MINOR** | Code formatting inconsistency, documentation typo, minor non-blocking improvement | Logged as a technical debt item in `memory/state.json`. |

---

## 4. Review Report Publication & Decision

1. **Publish Independent Review Report**:
   - Write comprehensive review findings to `docs/validation/independent-review-report.md`.
   - Structure report with: Executive Summary, Diff Scope Analysis, Anti-Slop Audit, Edge Case Analysis, Defect Log, and Final Decision.
2. **Update Quality Contract**:
   - Update `contracts/quality/contract.json`:
     - If ANY blocking defect exists: set status to `REJECTED`, document rationale, and trigger lifecycle transition to G4 (`REVIEW_DEFECTS_FOUND`).
     - If zero blocking defects exist: set status to `APPROVED`, sign off on Gate G5, and trigger transition to Gate G6 (`G5_PASSED`).
