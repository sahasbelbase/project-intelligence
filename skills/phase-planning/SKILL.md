---
skillId: phase-planning
name: Phase Planning
purpose: Decompose architectural specifications into bounded, sequential phases, work breakdown structures (WBS), and atomic tasks with strict file ownership.
whenToUse:
  - Translating an approved architecture contract into an actionable implementation plan
  - Partitioning complex development work into discrete sequential phases (e.g., Foundations, Core Logic, Integration, Polish)
  - Assigning exclusive file ownership boundaries to prevent conflicts during parallel subagent operations
  - Formulating the implementation contract (contracts/implementation/contract.json) required to enter Gate G4
prerequisites:
  - Gate G3 approved (contracts/architecture/contract.json in APPROVED status)
  - Access to implementation-contract.schema.json in core/schemas/
  - Available agent roles identified in core/schemas/agent-definition.schema.json
inputs:
  - name: architectureContract
    type: object
    description: Approved architecture contract with system components and technology stack
  - name: workstreamId
    type: string
    description: Identifier for the target workstream (e.g., WS-04, WS-Implementation)
  - name: availableSubagents
    type: array
    description: List of available agent definitions for task delegation
procedure:
  - stepNumber: 1
    title: Work Breakdown Structure (WBS) Formulation
    action: Deconstruct architecture components into sequential implementation phases (Phase 1: Foundations, Phase 2: Core, Phase 3: Integration, Phase 4: Polish).
  - stepNumber: 2
    title: Atomic Task Decomposition
    action: Break each phase into discrete atomic tasks. For each task, define explicit preconditions, deliverables, and acceptance criteria.
  - stepNumber: 3
    title: Exclusive File Ownership Boundary Mapping
    action: Assign exact file paths and directory globs to each task. Ensure zero overlapping file write permissions between concurrent tasks or subagents.
  - stepNumber: 4
    title: Dependency Graph and Critical Path Construction
    action: Map task prerequisites to create a DAG. Calculate critical path and identify tasks eligible for concurrent execution.
  - stepNumber: 5
    title: Verification Criteria Attachment
    action: Attach concrete validation commands (test suites, linter checks, type checking) to every task as mandatory completion criteria.
  - stepNumber: 6
    title: Implementation Contract Assembly
    action: Assemble data into contracts/implementation/contract.json conforming to core/schemas/implementation-contract.schema.json with initial status UNDER_REVIEW.
expectedOutputs:
  - contracts/implementation/contract.json adhering to implementation-contract.schema.json
  - Task dependency graph and workstream ledger in docs/decisions/0001-work-ledger.md
  - Updated memory/state.json with activePhase and activeTasks
applicableApprovalGates:
  - G3
failureAndRecovery:
  potentialFailures:
    - File ownership collisions between concurrent tasks
    - Circular dependencies in task prerequisite graph
    - Tasks defined too broadly leading to model context exhaustion
  recoveryStrategy: Split contested files into distinct modules or serialize the tasks. Resolve circular dependencies by creating intermediate interface definitions. Break tasks larger than 3 target files into smaller atomic subtasks.
verificationCriteria:
  - contracts/implementation/contract.json passes validation against core/schemas/implementation-contract.schema.json
  - Zero overlapping file write paths between concurrent workstream tasks
  - Every task specifies non-empty title, fileOwnership, and verificationCriteria
  - Task dependency graph is acyclic and terminates with verification tasks
relevantContractsAndMemory:
  contracts:
    - contracts/architecture/contract.json
    - contracts/implementation/contract.json
  memoryRecords:
    - executionState.activePhase
    - executionState.activeTasks
    - executionState.activeWorkstreamLedger
---

# Phase Planning (`phase-planning`)

## 1. Purpose
The `phase-planning` skill transforms approved high-level architecture into an actionable, granular, and risk-controlled roadmap. It establishes work breakdown structures (WBS), sequence dependencies, and critically, **exclusive file ownership boundaries** for every task. This eliminates code collisions when multiple subagents operate simultaneously and provides deterministic verification gates for implementation.

## 2. When to Use It
Activate this skill in the following contexts:
- Moving from architecture sign-off (Gate G3) into execution (Gate G4).
- Partitioning a large feature or refactor across multiple autonomous subagents.
- Sequencing implementation milestones into testable increments (e.g., Phase 1: Schemas, Phase 2: Business Logic, Phase 3: Adapters, Phase 4: Integration).
- Assembling `contracts/implementation/contract.json`.

## 3. Prerequisites
- Gate G3 must be approved (`contracts/architecture/contract.json` in `APPROVED` status).
- The implementation contract schema in `core/schemas/implementation-contract.schema.json` must be accessible.
- Subagent role definitions in `agents/` must be referenced for task delegation.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `architectureContract` | `object` | Approved architecture contract containing components, dependencies, and interfaces. |
| `workstreamId` | `string` | Unique identifier for the planned workstream (e.g., `WS-04`, `WS-05`). |
| `availableSubagents` | `array` | List of target subagents eligible for assignment. |

## 5. Procedure (Step-by-Step)
1. **Milestone & Phase Partitioning**:
   - Deconstruct architecture deliverables into 3-4 progressive phases:
     - **Phase 1: Foundations**: Schemas, contracts, domain models, base types.
     - **Phase 2: Core Components**: Business logic, algorithms, state engines.
     - **Phase 3: Integration & Adapters**: CLI, API routes, external platform integrations.
     - **Phase 4: Verification & Polish**: End-to-end tests, performance tuning, documentation.

2. **Atomic Task Decomposition**:
   - Break each phase into atomic work units.
   - Limit task scope to 1-3 related files or a single self-contained module.
   - Formulate clear acceptance criteria and explicit inputs/outputs for each task.

3. **Exclusive File Ownership Mapping**:
   - Define exact, non-overlapping directory or file paths for each task.
   - Example: Task A owns `src/auth/*`; Task B owns `src/billing/*`. Neither task may write to the other's directory.
   - Enforce this rule strictly in the work ledger to prevent race conditions during parallel subagent execution.

4. **Dependency Graph Formulation (DAG)**:
   - For each task, declare `prerequisites` referencing other task IDs.
   - Verify that the dependency graph contains zero cycles.
   - Identify concurrent execution tracks versus serialized bottlenecks.

5. **Validation Suite Attachment**:
   - Attach mandatory verification commands to each task (e.g., `pytest tests/unit/test_auth.py`, `npm run lint`).
   - Specify required exit codes (code 0) and expected test output patterns.

6. **Implementation Contract Synthesis**:
   - Compile tasks, phases, and ownership maps into `contracts/implementation/contract.json` complying with `core/schemas/implementation-contract.schema.json`.
   - Update `memory/state.json` with active phase index and initial task list.

## 6. Expected Outputs
- `contracts/implementation/contract.json`: Validated canonical implementation contract.
- Workstream Ledger entries in `docs/decisions/0001-work-ledger.md` mapping tasks, assigned agents, and paths.
- Initialized execution state in `memory/state.json`.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G3 (Architecture & Plan Approval)**: Completes the planning half of Gate G3, authoring the implementation plan required before Gate G4 unlocks.

## 8. Failure and Recovery Behavior
- **Path Collisions Detected**: If two concurrent tasks require modifying the same file (e.g., `routes.ts`), serialize the tasks or introduce an automated registration mechanism to separate concerns.
- **Overly Broad Tasks**: If a task requires modifying more than 5 distinct subsystems, decompose it into sequential subtasks.
- **Missing Verifier**: If a task lacks automated tests, mandate creation of unit test fixtures as part of task criteria.

## 9. Verification Criteria
- `contracts/implementation/contract.json` validates against `core/schemas/implementation-contract.schema.json`.
- Zero file path overlap exists between concurrently executable tasks.
- Every task includes an explicit `verificationCriteria` array with concrete commands.
- The task dependency graph forms a valid Directed Acyclic Graph.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/architecture/contract.json`
  - `contracts/implementation/contract.json`
- **Memory Records**:
  - `executionState.activePhase`
  - `executionState.activeTasks`
  - `executionState.activeWorkstreamLedger`
