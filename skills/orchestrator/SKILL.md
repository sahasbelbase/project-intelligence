---
skillId: orchestrator
name: Universal Master Orchestrator
purpose: Universal master orchestrator entry point. Parses intent, checks lifecycle state, dispatches to matching personas/skills or convenes council.
whenToUse:
  - Receiving any broad, ambiguous, or multi-faceted project request
  - Determining the active lifecycle gate and selecting matching specialized personas or skills
  - Convening a multi-persona council deliberation for high-stakes decisions
  - Enforcing lifecycle state transitions and quality gate sign-offs across Gates G0 through G6
prerequisites:
  - Project Intelligence workspace initialized with core/lifecycle/lifecycle-fsm.json
  - Access to persona definitions in agents/ and universal skills in skills/
  - Valid execution state in memory/execution-state.json or memory/state.json
inputs:
  - name: userIntent
    type: string
    description: Raw or structured user prompt, goal, or directive
  - name: lifecycleContext
    type: object
    description: Active lifecycle gate, approved contract states, and quality profile
  - name: availablePersonas
    type: array
    description: List of available persona specifications for task delegation or council participation
procedure:
  - stepNumber: 1
    title: Intent & Context Parsing
    action: Parse incoming user prompt to extract intent category, scope boundaries, technical domains, and required decisions.
  - stepNumber: 2
    title: Lifecycle State & Contract Audit
    action: Read memory/execution-state.json and contracts/ to determine active gate (G0-G6) and verify that prerequisite contracts are approved.
  - stepNumber: 3
    title: Council Convening Assessment
    action: Plan the request with `python3 -m core.orchestrator.dispatch "<request>"` (or `cli.js ask`, or the MCP tool `plan_task`). Tier 0 answers directly, tier 1 goes to one specialist, tiers 2 and 3 convene councils through the referee and the council-review skill.
  - stepNumber: 4
    title: Specialized Persona & Skill Selection
    action: Select the optimal persona (e.g. Business Analyst, QA Analyst, Product Manager) and skill matching the user intent.
  - stepNumber: 5
    title: Dispatch & Execution Oversight
    action: Dispatch task execution to the selected persona with explicit file ownership boundaries, contract inputs, and verification criteria.
  - stepNumber: 6
    title: State Synchronization & Memory Reconciliation
    action: Synchronize deliverable outcomes back to memory/execution-state.json and verify git alignment.
expectedOutputs:
  - Routing decision record detailing selected persona, invoked skill, and lifecycle gate
  - Executed deliverable or Council Decision Brief conforming to core/schemas/council-brief.schema.json
  - Updated memory/execution-state.json reflecting current phase and task states
applicableApprovalGates:
  - G0
  - G1
  - G2
  - G3
  - G4
  - G5
  - G6
failureAndRecovery:
  potentialFailures:
    - Ambiguous user intent preventing deterministic persona dispatch
    - Attempted lifecycle gate skip violating lifecycle-fsm.json transition rules
    - File write collision between concurrently executing subagents
  recoveryStrategy: Solicit structured clarification using multiple-choice prompts. Reject gate skips and route to prerequisite gate deliverables. Enforce strict disjoint file boundaries across concurrent tasks.
verificationCriteria:
  - Routing decision maps to an existing persona in agents/ and skill in skills/
  - Lifecycle transitions strictly comply with core/lifecycle/lifecycle-fsm.json
  - Execution state in memory/execution-state.json remains synchronized with git commit history
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/requirements/contract.json
    - contracts/architecture/contract.json
    - contracts/implementation/contract.json
    - contracts/quality/contract.json
    - contracts/release/contract.json
  memoryRecords:
    - executionState.activeLifecycleGate
    - executionState.activePhase
    - executionState.activeTasks
    - executionState.activeCouncil
---

# Universal Master Orchestrator (`orchestrator`)

## 1. Purpose
The `orchestrator` skill serves as the canonical master entry point for the Universal Role-Aware Intelligence Framework. It deterministically analyzes user intent, audits the active project lifecycle state (Gates G0 through G6), determines whether to dispatch to a specialized persona or convene a multi-persona council, and coordinates execution with strict file boundary enforcement.

## 2. When to Use It
- Receiving any incoming prompt or request where the exact lifecycle gate or specialist is undetermined.
- Evaluating whether a decision warrants single-persona execution versus a full multi-persona council review.
- Routing tasks to specialized domain personas (e.g., Business Analyst, QA Analyst, Product Manager, Project Manager).
- Enforcing gate progression and transition rules defined in `core/lifecycle/lifecycle-fsm.json`.

## 3. Prerequisites
- Workspace initialized with `core/lifecycle/lifecycle-fsm.json`.
- Access to the persona catalog in `agents/` and universal skills in `skills/`.
- Valid project state in `memory/execution-state.json` or `memory/state.json`.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `userIntent` | `string` | Raw or structured user prompt, goal, or directive. |
| `lifecycleContext` | `object` | Active lifecycle gate, approved contract states, and active quality profile. |
| `availablePersonas` | `array` | List of available persona specifications for task delegation or council participation. |

## 5. Procedure (Step-by-Step)
1. **Intent & Context Parsing**:
   - Parse the incoming request to identify target domains (business, architecture, quality, commercial, strategy).
   - Detect whether the user is proposing a new initiative, refining requirements, requesting architecture design, asking for test cases, or seeking a release sign-off.

2. **Lifecycle State & Contract Audit**:
   - Inspect `memory/execution-state.json` to identify the current lifecycle gate (`activeLifecycleGate`).
   - Validate that prerequisite contracts are approved before permitting downstream work.

3. **Council Convening Assessment**:
   - Evaluate against council trigger criteria:
     - Cross-functional ambiguity affecting multiple stakeholders.
     - Architecture or design decisions with high reversibility costs (Type 1 decisions).
     - Gate transitions requiring human and multi-stakeholder consensus (G0, G1, G3, G5, G6).
   - If triggered, invoke the `council-review` skill.

4. **Specialized Persona & Skill Selection**:
   - If a single specialist is sufficient, route to the corresponding persona:
     - Requirements elicitation -> `business-analyst` using `requirements-analysis`.
     - Test case design -> `qa-analyst` using `test-case-generation`.
     - Delivery planning & WBS -> `project-manager` using `project-planning`.
     - Feature trade-offs & MVP -> `product-manager` using `feature-prioritization`.
     - Business case & pricing -> `sales-strategist` using `business-case`.

5. **Dispatch & Execution Oversight**:
   - Provide the dispatched persona with bounded inputs, disjoint file ownership, and explicit verification criteria.

6. **State Synchronization & Memory Reconciliation**:
   - Record outputs in the project ledger and synchronize `memory/execution-state.json`.

## 6. Expected Outputs
- Routing decision record detailing selected persona, invoked skill, and lifecycle gate.
- Executed deliverable or Council Decision Brief conforming to `core/schemas/council-brief.schema.json`.
- Updated `memory/execution-state.json` reflecting current phase and task states.

## 7. Applicable Approval Gates (G0-G6)
- Applicable across all gates from **G0 (Inception)** through **G6 (Release & Memory Sync)**.

## 8. Failure and Recovery Behavior
- **Ambiguous Intent**: Prompt the user with a focused multiple-choice clarification question instead of guessing.
- **Illegal Gate Jump**: If a user attempts to skip from G1 directly to G4, refuse the jump and explain prerequisite contracts required for G2 and G3.
- **Subagent Contention**: If two subagents require modifying the same file, serialize execution or partition the file into distinct modules.

## 9. Verification Criteria
- Routing decision maps to a valid persona in `agents/` and skill in `skills/`.
- Lifecycle transitions strictly comply with `core/lifecycle/lifecycle-fsm.json`.
- State file `memory/execution-state.json` remains consistent with git repository status.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json`
  - `contracts/requirements/contract.json`
  - `contracts/architecture/contract.json`
  - `contracts/implementation/contract.json`
  - `contracts/quality/contract.json`
  - `contracts/release/contract.json`
- **Memory Records**:
  - `executionState.activeLifecycleGate`
  - `executionState.activePhase`
  - `executionState.activeTasks`
  - `executionState.activeCouncil`
