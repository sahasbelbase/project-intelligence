# Universal Instructions — Deliverable Standards

## 1. Operational Purpose & Precedence

This document establishes the mandatory engineering standards, completeness requirements, and anti-slop guidelines for all deliverables produced within the Project Intelligence framework.

**Core Mandate**: Deliverables must be fully functional, strictly typed, comprehensively tested, and free from cognitive shortcuts, mock fillers, or cosmetic placeholders. Partial implementations and stubbed code are strictly prohibited.

---

## 2. Anti-Slop Baseline Rules Enforcement

Every deliverable must pass automated evaluation against rules BL-001 through BL-007:

### 2.1 Zero Decorative Emoji Policy (BL-001)
- Decorative icons, Unicode emoji symbols (e.g., rocket, sparkles, fire, brain, robot), and visual fluff are strictly disallowed in:
  - Source code, comments, docstrings, and type definitions.
  - Automated test suites, assertions, and test names.
  - Commit messages, PR titles, and pull request descriptions.
  - Standard output, system logs, terminal CLIs, and structured reports.
- *Standard*: Technical documentation and terminal interfaces must prioritize density, legibility, and deterministic string parsing.

### 2.2 Zero Fake or Mock Data in Production Logic (BL-002)
- Hardcoded mock values, dummy user profiles (`john.doe@example.com`), synthetic tokens, or simulated responses are forbidden in production code paths.
- All logic must process validated parameters, real local schemas, or properly quarantined test fixtures.
- Test fixtures must be restricted entirely to `validation/` or `tests/` directories.

### 2.3 Zero Placeholders, Dead Stubs, or Truncation (BL-003)
- Deliverable code must never include:
  - Stubbed functions containing unimplemented pass statements, unhandled exceptions, or deferred task comments.
  - Incomplete conditional branches (`else: pass`).
  - LLM code truncation comments (such as claiming remaining code is unchanged).
  - Non-functional UI elements that visually render but perform no operational action.
- Every function, method, and module delivered must be completely implemented and tested.

### 2.4 Explicit Error Handling (BL-004)
- Blanket exception silencing (`except Exception: pass`, `catch (e) {}`) is prohibited.
- Arbitrary `sleep()` calls inserted to mask timing defects or race conditions are prohibited.
- Every caught exception must be handled with appropriate diagnostic context, propagated, or reported to the system failure boundary.

### 2.5 Standard Library First (BL-005)
- Prioritize Python standard library solutions (`pathlib`, `json`, `dataclasses`, `unittest`, `re`, `typing`, `enum`) over third-party packages.
- Introduction of external dependencies requires an architectural decision record and explicit approval.

### 2.6 Verification Honesty (BL-006)
- Claims of task completion or test success must be corroborated by empirical execution logs showing exit code `0`.
- Skipped or unexecuted checks must be honestly reported as `SKIPPED` or `UNAVAILABLE`.

### 2.7 Secret Hygiene (BL-007)
- Zero credentials, tokens, or private secrets in source files or persistent memory.

---

## 3. Structural Standards for Deliverables

### 3.1 Code Deliverables
1. **Type Annotations**: All public functions, classes, and methods must include standard type annotations (`typing`).
2. **Docstrings**: Modules and public interfaces must include concise, substantive docstrings explaining purpose, parameters, return types, and exceptions.
3. **Deterministic Testing**: Every production module must be accompanied by an automated test suite runnable via `python3 -m unittest`.
4. **Clean File Ownership**: Modifying files outside the explicitly assigned workstream boundary is strictly prohibited.

### 3.2 Contract Deliverables
1. **Schema Validation**: All contract files must validate against their respective JSON Schema Draft-07 specifications without warnings or errors.
2. **Traceability**: Contracts must declare valid upstream requirement IDs and downstream verification task IDs.
3. **Status Integrity**: Contracts may only transition to `APPROVED` when all required acceptance criteria are verified with empirical evidence.

### 3.3 Documentation & Report Deliverables
1. **Clear Epistemic Demarcation**: Structural separation between verified facts and assumptions per `instructions/universal/evidence-and-assumptions.md`.
2. **Reproducible Commands**: Include exact shell invocations, parameters, and observed exit codes.
3. **Direct Markdown Links**: Reference local file paths using clickable markdown links.

---

## 4. Deliverable Acceptance Checklist

Before submitting any deliverable for gate review or milestone completion, verify:

- [ ] Code passes static evaluation using `core/quality/evaluator.py` with zero anti-slop violations.
- [ ] Automated tests execute with `python3 -m unittest` and exit with code `0`.
- [ ] No placeholder stubs or unimplemented stub functions exist in deliverable code.
- [ ] No hardcoded secrets or mock values are present.
- [ ] All claims of completion cite empirical evidence logs.
- [ ] File modifications strictly respect assigned file boundaries.
