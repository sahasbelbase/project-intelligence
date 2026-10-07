# Universal Core Rules — Project Intelligence

## 1. Operational Hierarchy and Precedence

The Project Intelligence governance model enforces a strict, four-tier normative hierarchy. When resolving behavioral conflicts between guidelines, the higher-tier rule unconditionally supersedes the lower-tier rule:

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: Universal Core Rules (instructions/universal/)     │  <-- Absolute Precedence
├─────────────────────────────────────────────────────────────┤
│  Tier 2: Quality Profile Directives (instructions/profiles/)│
├─────────────────────────────────────────────────────────────┤
│  Tier 3: Task-Specific Instructions (instructions/tasks/)   │
├─────────────────────────────────────────────────────────────┤
│  Tier 4: Subagent & Platform Preferences                    │
└─────────────────────────────────────────────────────────────┘
```

**Non-Negotiable Rule**: No task instruction, user prompt, quality profile, or platform adapter may weaken, suspend, or bypass any Universal Core Rule without a signed architectural decision record (ADR) and explicit human approval.

---

## 2. Anti-Slop Policy (Mandatory Engineering Baseline)

AI coding assistants are prone to cognitive laziness, superficial implementations, and cosmetic filler. The following baseline rules (BL-001 through BL-007) are permanently active across all projects, profiles, and phases:

### BL-001: Disallow Gratuitous Decorative Emoji & Icons
- Decorative emoji (e.g. 🚀, ✨, 🎉, 🧠, 🤖, 💡, 🔥) are strictly prohibited in:
  - Production source code and code comments.
  - Test suites and test assertions.
  - Commit messages and PR descriptions.
  - System logs, standard out (stdout), and standard error (stderr).
  - Terminal CLI output and operational dashboards.
- *Rationale*: Professional engineering systems prioritize legibility, precise parsing, and clean terminal output over decorative fluff.

### BL-002: Disallow Fake / Mock Data in Production Logic
- Never inject fake mock values, placeholder user accounts, dummy email addresses (`john.doe@example.com`), or hardcoded dummy tokens into production code paths.
- All data ingestion, persistence, and computation must operate over validated schemas, real user parameters, or properly isolated test fixtures.
- Test data must be strictly quarantined within `tests/` or `test_fixtures/` directories and never imported into production modules.

### BL-003: Disallow Unimplemented Placeholders & Dead Stubs
- Prohibited:
  - Stub functions containing only `pass`, `throw new NotImplementedError()`, or `// TODO: implement later`.
  - Non-functional UI elements (e.g., buttons, tabs, or menus that render visually but do nothing when clicked).
  - Incomplete conditional branches (`else: pass` or ignoring return values).
- If a feature is scheduled for a future milestone, it must be excluded from the current deliverable entirely or gated behind a disabled configuration flag with documented rationale.

### BL-004: Disallow Unexplained Workarounds & Error Swallowing
- Prohibited:
  - Catch-all exception blocks that discard errors (`except Exception: pass`, `catch (e) {}`).
  - Arbitrary `sleep()` delays inserted to mask race conditions or asynchronous timing defects.
  - Silencing compiler, linter, or type-checker warnings using blanket suppression flags (`# type: ignore`, `eslint-disable`) without an attached root-cause comment and issue ticket.
- Every error must be explicitly handled, logged with context, or propagated to the appropriate failure boundary.

### BL-005: Disallow Unapproved Third-Party Dependencies
- Agents may not introduce external packages, npm modules, or PyPI libraries without prior architectural evaluation.
- Prefer standard library solutions (e.g., `pathlib`, `json`, `dataclasses`, `unittest` in Python; native web APIs in JavaScript).
- When a new dependency is required:
  - It must be recorded in `contracts/architecture/contract.json`.
  - Its license must be verified (permissive: MIT, Apache 2.0, BSD).
  - Its transitive footprint and vulnerability record must be audited.

### BL-006: Strict Verification Honesty
- Verification status values are restricted to the canonical taxonomy:
  - `PASSED`: The check was executed and verified successful with exit code 0 and passing assertions.
  - `FAILED`: The check was executed and produced an error, non-zero exit code, or failed assertion.
  - `BLOCKED`: The check could not execute due to an unresolved upstream prerequisite.
  - `SKIPPED`: The check was deliberately omitted per approved profile exemption.
  - `UNAVAILABLE`: The required tool or runtime is missing from the host environment.
- **Absolute Prohibition**: Never report an unexecuted, assumed, or skipped check as `PASSED`. Confidence is not verification.

### BL-007: Secret Leakage Prevention
- Hardcoded secrets, API keys, private tokens, passwords, database connection URIs, and certificate strings are strictly forbidden anywhere in the repository.
- Secrets must be injected exclusively via environment variables or secret vaults.
- Never write credentials into durable memory files (`memory/state.json`), contract envelopes, or commit messages.

---

## 3. Evidence-Based Verification Standards

Claims of completion must be backed by empirical evidence. An agent may not declare a task completed, a contract approved, or a gate passed without providing reproducible proof:

1. **Concrete Command Evidence**:
   - Always record the exact command executed (e.g., `python -m unittest discover tests/`).
   - Always record the process exit code (must be `0` for passing checks).
   - Always capture execution telemetry (test count, duration, output summaries).
2. **Diff and File Integrity**:
   - Inspect `git diff` before and after modifications.
   - Confirm that only intended files within the assigned boundary were changed.
3. **No Hallucinated Pass**:
   - If an automated test suite was not run, report it as `UNAVAILABLE` or `SKIPPED` with the exact command for human execution.

---

## 4. Local-First Privacy and Data Integrity

1. **Local Isolation Guarantee**:
   - Project Intelligence is local-first. Repository source code, contracts, and memory states must remain on the host machine.
   - No telemetry, project source code, or internal architecture documents may be transmitted to external endpoints without user permission.
2. **Zero SaaS Dependency**:
   - Core framework execution, schema validation, lifecycle transitions, and memory reconciliation must function entirely offline using standard local tooling.

---

## 5. Git Cleanliness & Working Tree Hygiene

1. **Working Tree Protection**:
   - Never run destructive git commands (`git reset --hard`, `git clean -fd`) without explicit user instruction.
   - Before applying automated patches or running rollback procedures, check `git status --porcelain`.
   - Preserve uncommitted user work by creating non-destructive stashes (`git stash create`) if tree state is ambiguous.
2. **Atomic, Purposeful Commits**:
   - Group related changes into atomic commits.
   - Commit messages must follow conventional imperative style:
     - `feat(auth): implement token refresh rotation`
     - `fix(schema): resolve contract validation error in G3`
     - `test(core): add regression test suite for memory drift`
   - Never use decorative emoji in commit titles or bodies.
3. **Pre-Flight Git Reconciliation**:
   - Upon session start or before mutating files, compare `memory/state.json`'s `lastReconciledCommit` with current `git rev-parse HEAD`.
   - If drift is detected, perform reconciliation before proceeding with tasks.

---

## 6. Scope Discipline & Boundary Enforcement

1. **Exclusive File Ownership**:
   - In multi-agent or partitioned task execution, agents must respect assigned file paths.
   - Writing to files owned by other workstreams or tasks is strictly prohibited.
2. **Zero Scope Creep**:
   - Implement only what is declared in `contracts/requirements/contract.json` and `contracts/implementation/contract.json`.
   - Do not proactively refactor unrelated modules, add unrequested features, or alter stylistic formatting outside the immediate working boundary.
