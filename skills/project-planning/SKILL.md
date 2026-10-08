---
skillId: project-planning
name: project-planning
description: "Construct work breakdown structures, identify critical execution paths, map task dependencies, level resource allocations, and establish disjoint file boundaries for Project Managers and Coordinators."
purpose: Construct work breakdown structures, identify critical execution paths, map task dependencies, level resource allocations, and establish disjoint file boundaries for Project Managers and Coordinators.
whenToUse:
  - Decomposing approved architecture and requirements into phased execution schedules
  - Constructing task dependency graphs (DAG) and calculating project critical paths
  - Assigning mutually exclusive file ownership boundaries to prevent concurrent subagent collisions
  - Authoring or updating the canonical Implementation Contract for Gate G4 (contracts/implementation/contract.json)
prerequisites:
  - Approved Architecture Contract (contracts/architecture/contract.json)
  - Approved Requirements Contract (contracts/requirements/contract.json)
  - Access to core/schemas/implementation-contract.schema.json
inputs:
  - name: architectureContract
    type: object
    description: System components, interfaces, and technical dependencies
  - name: requirementsContract
    type: object
    description: Functional requirements and acceptance criteria
  - name: resourceConstraints
    type: object
    description: Available agent roles, concurrency limits, and milestone deadlines
procedure:
  - stepNumber: 1
    title: Phased Work Breakdown Structure (WBS) Formulation
    action: Decompose system deliverables into sequential execution phases (Foundations, Core Engines, Adapters, Verification).
  - stepNumber: 2
    title: Atomic Task Definition & Boundary Assignment
    action: Define atomic tasks with clear objectives, prerequisites, target files, and verification commands.
  - stepNumber: 3
    title: Disjoint File Ownership Mapping
    action: Assign non-overlapping directory and file paths to each task to guarantee zero write collisions during parallel execution.
  - stepNumber: 4
    title: Dependency Graph Modeling & Critical Path Analysis
    action: Model task dependencies as a Directed Acyclic Graph (DAG) and compute the critical delivery path.
  - stepNumber: 5
    title: Verification Criteria Attachment
    action: Attach concrete validation commands (test runner commands, linters, exit code 0) as mandatory completion criteria.
  - stepNumber: 6
    title: Implementation Contract Assembly
    action: Compile tasks, phases, and ownership maps into contracts/implementation/contract.json conforming to schema.
expectedOutputs:
  - contracts/implementation/contract.json conforming to core/schemas/implementation-contract.schema.json
  - Task dependency graph and critical path schedule
  - Disjoint file ownership matrix and workstream ledger
applicableApprovalGates:
  - G0
  - G1
  - G3
  - G4
failureAndRecovery:
  potentialFailures:
    - Circular dependencies in task prerequisite graph
    - Overlapping file paths assigned to concurrent tasks causing write collisions
    - Tasks defined too broadly leading to model context exhaustion
  recoveryStrategy: Run topological sort to detect and break dependency cycles. Partition contested files into separate modules or serialize task execution. Break mega-tasks into subtasks owning no more than 3 files each.
verificationCriteria:
  - contracts/implementation/contract.json passes validation against core/schemas/implementation-contract.schema.json
  - Dependency graph is strictly acyclic (valid topological sort)
  - Zero file path overlaps between concurrently executable tasks
  - Every task specifies non-empty verificationCriteria with executable commands
relevantContractsAndMemory:
  contracts:
    - contracts/architecture/contract.json
    - contracts/implementation/contract.json
  memoryRecords:
    - executionState.activePhase
    - executionState.activeTasks
    - executionState.activeWorkstreamLedger
---

# Project Planning & Critical Path Decomposition (`project-planning`)

## 1. Purpose
The `project-planning` skill empowers Project Managers and Project Coordinators to structure complex development work into phased, predictable, and risk-controlled execution roadmaps. It enforces atomic task sizing, calculates the critical path, and guarantees disjoint file ownership across concurrent subagents to prevent race conditions and merge conflicts.

## 2. When to Use It
- Transitioning from architecture sign-off (Gate G3) into active implementation (Gate G4).
- Decomposing large epics or architecture specifications into work packages.
- Partitioning tasks among parallel agents with mutually exclusive directory boundaries.
- Assembling `contracts/implementation/contract.json`.

## 3. Prerequisites
- Gate G3 approved (`contracts/architecture/contract.json` in `APPROVED` status).
- Requirements Contract (`contracts/requirements/contract.json`) approved.
- Access to `core/schemas/implementation-contract.schema.json`.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `architectureContract` | `object` | Approved architecture contract specifying system components, technologies, and interfaces. |
| `requirementsContract` | `object` | Functional requirements and acceptance criteria. |
| `resourceConstraints` | `object` | Concurrency limits, subagent capabilities, and milestone timeline bounds. |

## 5. Procedure (Step-by-Step)
1. **Milestone & Phase Partitioning**:
   - Structure implementation into 3-4 progressive phases:
     - Phase 1: Foundations (schemas, contracts, domain types).
     - Phase 2: Core Components (engines, algorithms, state machines).
     - Phase 3: Adapters & Interfaces (protocols, tools, CLI).
     - Phase 4: Verification & Integration (end-to-end tests, docs).

2. **Atomic Task Decomposition**:
   - Formulate discrete tasks with unique identifiers (`TASK-001`, `TASK-002`).
   - Limit task scope to 1-3 closely related files or a single self-contained subsystem.

3. **Disjoint File Ownership Mapping**:
   - Assign exact mutable file paths and directory globs to each task.
   - Enforce zero overlapping mutable files between concurrently executable tasks.

4. **DAG Dependency Modeling & Critical Path Analysis**:
   - Map prerequisites for each task to form a Directed Acyclic Graph (DAG).
   - Perform topological sorting to ensure zero circular dependencies and calculate the critical path.

5. **Validation Criteria Attachment**:
   - Attach mandatory test execution commands (e.g. `pytest tests/`, `npm test`) with required exit code 0 to every task.

6. **Implementation Contract Synthesis**:
   - Compile data into `contracts/implementation/contract.json` conforming to `core/schemas/implementation-contract.schema.json`.

## 6. Expected Outputs
- Canonical `contracts/implementation/contract.json`.
- Task dependency DAG and critical path schedule.
- Workstream Ledger entries in `docs/decisions/` and `memory/execution-state.json`.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G3 (Planning Approval)**: Authoring the primary implementation plan.
- **Gate G4 (Execution Governance)**: Managing active task execution and file ownership.

## 8. Failure and Recovery Behavior
- **Circular Dependencies**: Detect cycle via topological sort and break circularity by introducing intermediate interface files.
- **File Contention**: If two tasks need to touch the same file, serialize them sequentially or partition the file into distinct sub-modules.

## 9. Verification Criteria
- `contracts/implementation/contract.json` validates against schema.
- Zero file path collisions between concurrent tasks.
- Dependency graph is acyclic.
- Every task includes concrete automated verification commands.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/architecture/contract.json`
  - `contracts/implementation/contract.json`
- **Memory Records**:
  - `executionState.activePhase`
  - `executionState.activeTasks`
  - `executionState.activeWorkstreamLedger`
