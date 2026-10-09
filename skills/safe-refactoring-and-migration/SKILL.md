---
skillId: safe-refactoring-and-migration
name: safe-refactoring-and-migration
description: "Plan and execute verified, incremental refactoring and migration of legacy systems using characterization tests, the strangler-fig pattern, and automated codemods with zero behavioral regressions."
purpose: "Plan and execute verified, incremental refactoring and migration of legacy systems using characterization tests, the strangler-fig pattern, and automated codemods with zero behavioral regressions."
whenToUse:
  - Modernizing legacy codebase modules after knowledge base analysis
  - Decoupling tightly coupled monolithic full-stack applications into clean layers
  - Migrating from legacy language idioms (callbacks, CommonJS) to modern standards (async/await, ESM, TypeScript)
  - Applying the Strangler-Fig pattern to incrementally replace deprecated services behind facades
  - Extracting reusable domain services from bloated controller or view components
prerequisites:
  - Baseline test runner or characterization test harness to capture input/output behavior
  - Clean git working tree to allow atomic rollbacks between incremental steps
  - Documented domain vocabulary or knowledge base from legacy analysis
inputs:
  - name: targetModule
    type: string
    description: Path to legacy file or module targeted for refactoring
  - name: migrationStrategy
    type: string
    description: "Selected architectural approach: strangler-fig, facade-extraction, or modular-split"
  - name: codemodRule
    type: string
    description: Automated transformation pattern or typing migration rule
  - name: safetyThreshold
    type: string
    description: "Required regression verification baseline (default: 100% golden master pass)"
procedure:
  - stepNumber: 1
    title: Characterization & Golden Master Test Capture
    action: Wrap the legacy module with black-box characterization tests recording real inputs and outputs across edge cases before touching any production source code.
  - stepNumber: 2
    title: Facade & Boundary Seam Construction
    action: Introduce a typed interface or facade seam separating callers from the legacy implementation, ensuring zero caller-side breaking changes.
  - stepNumber: 3
    title: Incremental Slice Extraction & Codemod Application
    action: Extract one bounded sub-component or apply automated AST codemod transforms inside the newly isolated seam.
  - stepNumber: 4
    title: Parallel Run & Parity Verification
    action: Execute the characterization test suite against the new implementation to prove exact behavioral parity and verify zero regressions.
  - stepNumber: 5
    title: Caller Re-pointing & Deprecated Code Removal
    action: Route callers directly to the modernized component and cleanly delete superseded legacy code and temporary facade scaffolding.
expectedOutputs:
  - Modernized, decoupled source files adhering to prevailing project standards
  - Passing characterization test suite validating behavioral parity
  - Migration log recording deleted legacy lines, removed dependencies, and architectural debt reduced
applicableApprovalGates:
  - G2
  - G3
  - G4
  - G5
failureAndRecovery:
  potentialFailures:
    - Characterization tests fail due to subtle legacy side-effects
    - Scope explosion where refactoring touches too many files simultaneously
    - Performance regression introduced by new abstraction layers
  recoveryStrategy: Immediately git checkout to the previous atomic commit. Narrow the refactoring boundary to a smaller single function or class seam and re-run characterization tests.
verificationCriteria:
  - 100% of characterization tests pass without modifying test assertions
  - Changes are partitioned into atomic, independently reviewable commits
  - No deprecated APIs or unused dead code remains in the codebase
relevantContractsAndMemory:
  contracts:
    - contracts/architecture/contract.json
    - contracts/implementation/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - backlogAndHistory.technicalDebt
---

# Safe Refactoring & Migration (`safe-refactoring-and-migration`)

## 1. Purpose
The `safe-refactoring-and-migration` skill provides deterministic, regression-free modernization procedures for brownfield and legacy software. It establishes safe modification seams using characterization testing, applies the Strangler-Fig architectural pattern, and executes atomic AST codemods without altering external observable behavior.

## 2. When to Use It
Activate this skill whenever:
- Refactoring brownfield code discovered during legacy analysis.
- Decoupling mixed full-stack monoliths into modular client/server architectures.
- Converting deprecated syntax or patterns (e.g., CommonJS to ESM, callbacks to promises).
- Replacing obsolete third-party libraries with modern zero-dependency alternatives.

## 3. Prerequisites
- Executable test runner and clean Git working tree.
- Documented domain knowledge or baseline architecture overview.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `targetModule` | `string` | File or folder targeted for modernization. |
| `migrationStrategy` | `string` | Chosen migration pattern (`strangler-fig`, `facade-extraction`, `codemod`). |
| `codemodRule` | `string` | Specific transformation rule to execute. |
| `safetyThreshold` | `string` | Verification criteria threshold. |

## 5. Procedure (Step-by-Step)
1. **Characterization & Golden Master Test Capture**: Author tests that capture the exact current behavior (including quirks) of the target module.
2. **Facade & Boundary Seam Construction**: Define an abstraction layer or interface so consumers interact through a clear contract.
3. **Incremental Slice Extraction**: Migrate one isolated slice, function, or class at a time inside the boundary seam.
4. **Parallel Run & Parity Verification**: Run characterization tests to guarantee output matches expectations verbatim.
5. **Caller Re-pointing & Deprecated Code Removal**: Update callers and delete old code, avoiding zombie artifacts.

## 6. Expected Outputs
- Refactored code files matching clean architecture conventions.
- Characterization test suite confirming parity.
- Technical debt reduction record.

## 7. Applicable Approval Gates
- **G2 (Architecture)**: Approval of facade seam and migration strategy.
- **G3 (Planning)**: Atomic step task breakdown.
- **G4 (Implementation)**: Execution of code transforms.
- **G5 (Quality)**: Characterization test pass confirmation.

## 8. Failure and Recovery Strategies
- If unexpected regressions occur, immediately revert to the last verified commit with `git reset --hard HEAD~1` and reduce the refactoring scope.

## 9. Verification Criteria
- All characterization tests pass with 0 regressions.
- No unused dead code or deprecated imports remain.
- Changes are verified against project anti-slop baselines.

## 10. Relevant Contracts and Memory Records
- `contracts/architecture/contract.json`
- `contracts/implementation/contract.json`
- `durableKnowledge.architecturalDecisions`
- `backlogAndHistory.technicalDebt`
