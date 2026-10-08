---
skillId: thermo-nuclear-review
name: Thermo-Nuclear Code Quality Review & Code Judo
purpose: Conduct an uncompromising, adversarial code audit that aggressively simplifies architecture, collapses redundant indirection, eliminates dead complexity through Code Judo, and enforces the inevitability standard.
whenToUse:
  - Evaluating code changes at Gate G5 before merging into master or release branches
  - Auditing code produced by worker or subagent models to eliminate AI slop and boilerplate
  - Simplifying convoluted logic, deep nesting pyramids, and unnecessary class/wrapper abstractions
  - Enforcing strict file bloat ceilings and dead code vaporization across all repositories
prerequisites:
  - Git diff or modified file trees available for inspection
  - Access to requirements acceptance criteria or target interface contracts
  - Automated test suite passing at Gate G4 baseline
inputs:
  - name: targetDiffOrFiles
    type: string
    description: Git diff range, commit hash, or paths to modified source code files
  - name: contractRequirements
    type: object
    description: Approved architectural contracts and requirement acceptance criteria
procedure:
  - stepNumber: 1
    title: Code Judo Structural Simplification
    action: Inspect class hierarchies and helper functions. Identify trivial pass-through wrappers that forward calls without transformation. Collapse redundant abstractions directly into their calling sites.
  - stepNumber: 2
    title: Cyclomatic Depth & Nesting Flattening
    action: Measure block nesting depth. Enforce maximum nesting depth of 3. Mandate conversion of deep if-else branches and pyramid callback structures into early returns, guard clauses, and focused single-purpose subroutines.
  - stepNumber: 3
    title: File Density & Bloat Ceiling Audit
    action: Measure file line counts. Flag files exceeding 500 lines for structural decomposition; issue hard rejection for single files exceeding 1,000 lines unless authorized by an architectural exception.
  - stepNumber: 4
    title: Dead Code & Defensive Slop Vaporization
    action: Scan for unused imports, unreachable error branches, commented-out legacy code, defensive null checks where types or invariants guarantee non-nullness, and redundant try-except blocks.
  - stepNumber: 5
    title: The Inevitable Code Standard Evaluation
    action: Evaluate readability and cognitive ergonomics: verify that the code reads directly and obviously, with zero premature generalization hooks, speculative configuration flags, or excessive comment chatter.
  - stepNumber: 6
    title: Authoritative Verdict & Simplification Plan
    action: Emit formal verdict (APPROVED or REJECTED) with concrete Code Judo refactoring instructions referencing exact file paths, line ranges, and line savings.
expectedOutputs:
  - Thermo-Nuclear Review Audit Report detailing Code Judo opportunities, nesting depth metrics, and lines deleted
  - Formal Gate G5 evaluation verdict conforming to quality-contract.schema.json
  - List of actionable Code Judo simplification tickets
applicableApprovalGates:
  - G5
failureAndRecovery:
  potentialFailures:
    - Deep cyclomatic nesting exceeding depth threshold 3
    - Single file exceeding 1,000 lines without modular decomposition
    - Trivial wrapper layer introducing gratuitous indirection
    - Gratuitous AI comment chatter or unverified defensive stubs
  recoveryStrategy: Reject Gate G5 immediately. Output specific Code Judo refactor directives showing exact before-and-after code simplifications. Route back to implementing agent for consolidation.
verificationCriteria:
  - Zero files exceeding 1,000 lines in changed paths
  - Maximum nesting depth <= 3 across all functions
  - Zero trivial one-line pass-through wrappers without domain validation
  - Zero anti-slop violations (BL-001 through BL-007)
  - Code reads directly and inevitably without speculative abstractions
relevantContractsAndMemory:
  contracts:
    - contracts/quality/contract.json
    - contracts/implementation/contract.json
    - contracts/architecture/contract.json
  memoryRecords:
    - executionState.activeTasks
    - backlogAndHistory.technicalDebt
---

# Thermo-Nuclear Code Quality Review & Code Judo (`thermo-nuclear-review`)

## 1. Philosophical Origin & Mandate
Derived from the elite engineering practices pioneered by the Cursor team and the `ui-skills` ecosystem, the **Thermo-Nuclear Code Quality Review** rejects cosmetic, superficial reviews. 

Most code reviews waste time debating whitespace, formatting, and naming conventions while leaving sprawling, over-engineered architectures untouched. The Thermo-Nuclear reviewer takes the opposite approach: **it treats every added line of code as a liability, every abstraction layer as guilty until proven innocent, and every nested block as a cognitive burden.**

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away." — Antoine de Saint-Exupéry

---

## 2. The 6 Core "Code Judo" Moves

Code Judo uses the momentum of existing code complexity to collapse and eliminate it.

### Move 1: Abstraction Collapse (Delete Trivial Indirection)
- **The Anti-Pattern**: An interface with only one implementation, a repository that wraps an ORM method without modification, or a utility function that forwards arguments to another function verbatim:
  ```python
  # SLOPPY INDIRECTION
  def fetch_user_by_id(user_id):
      return db.get_user(user_id)
  ```
- **The Judo Move**: Collapse the wrapper. Call `db.get_user(user_id)` directly at call sites. Delete the file, the function, and the unit test mocking the wrapper.

### Move 2: Guard Clause Flattening (Nesting Depth <= 3)
- **The Anti-Pattern**: Nested "pyramid of doom" where the main happy path is indented 4 to 6 levels deep inside successive `if` conditions:
  ```javascript
  // PYRAMID OF DOOM
  function processOrder(order) {
    if (order) {
      if (order.items && order.items.length > 0) {
        if (order.paymentStatus === 'PAID') {
          // core logic indented 5 levels
        }
      }
    }
  }
  ```
- **The Judo Move**: Invert conditions and return early. The happy path stays at indentation depth 1:
  ```javascript
  // INEVITABLE CODE
  function processOrder(order) {
    if (!order || !order.items?.length) return;
    if (order.paymentStatus !== 'PAID') return;
    // core logic at depth 1
  }
  ```

### Move 3: File Bloat Ceilings
- **Threshold 1 (Warning at 500 lines)**: Files over 500 lines are flagged for potential violation of Single Responsibility Principle.
- **Threshold 2 (Hard Rejection at 1,000 lines)**: Any single source file over 1,000 lines is rejected at Gate G5 unless an explicit, architectural exemption is documented in an ADR.

### Move 4: Dead Code & Defensive Slop Vaporization
- Eliminate:
  - Chatty comments that explain what the code already says (e.g., `// increment count by 1`, `count++`).
  - Apologetic docstrings and excessive LLM commentary.
  - Unused imports, unreachable `else` branches, and dead error fallbacks.
  - Redundant null-coalescing on fields guaranteed non-null by schema contracts.

### Move 5: The "Inevitable Code" Principle
- If three engineers were asked to solve the problem, would all three converge on this exact structure?
- If the solution requires mental gymnastics, speculative inheritance, or visitor patterns for a 2-branch scenario, it fails the Inevitable Code standard.

### Move 6: Adversarial Test Rigor
- Verify that test assertions test reality, not mocks mocking mocks.
- A test suite with 100% coverage that only asserts `expect(result).toBeDefined()` is rejected as dishonest verification.

---

## 3. Integration with the Hierarchical Multi-Model Workflow

```
┌────────────────────────────────────────────────────────┐
│  High-Reasoning Lead Model (Architect)                 │
│  - Authors exact contracts & interfaces                │
│  - Decomposes problem into disjoint files              │
│  - Selects minimal context (ui-skills router)          │
└───────────────────────────┬────────────────────────────┘
                            │ Bounded task spec (~2k tokens)
                            ▼
┌────────────────────────────────────────────────────────┐
│  Cost-Efficient Worker Model (Coder)                   │
│  - Implements bounded file in isolation                │
│  - High throughput, 80%+ token savings                 │
└───────────────────────────┬────────────────────────────┘
                            │ Git Diff
                            ▼
┌────────────────────────────────────────────────────────┐
│  Adversarial Thermo-Nuclear Reviewer (Gate G5)         │
│  - Scans diff with AST & Code Judo analyzer            │
│  - Enforces Nesting <= 3, Lines <= 1000, 0 Slop        │
│  - Returns APPROVED or REJECTED with line deletions    │
└────────────────────────────────────────────────────────┘
```
