---
skillId: architecture-and-contracts
name: Architecture and Contracts
purpose: Formulate system architecture, component boundaries, schemas, API contracts, threat models, and architectural decision records (ADRs) to clear G3.
whenToUse:
  - Defining software subsystem boundaries, data models, and component interfaces
  - Selecting technologies, frameworks, and third-party dependencies with formal rationale
  - Writing Architecture Decision Records (ADRs) for critical technical trade-offs
  - Drafting contracts/architecture/contract.json to fulfill Gate G3 approval criteria
prerequisites:
  - Gate G1 approved (contracts/requirements/contract.json in APPROVED status)
  - Gate G2 approved or formally exempted (contracts/design/contract.json)
  - Access to architecture-contract.schema.json in core/schemas/
inputs:
  - name: requirementsContract
    type: object
    description: Approved requirements contract containing functional and non-functional specifications
  - name: designContract
    type: object
    description: Approved design contract or formal exemption record
  - name: systemConstraints
    type: array
    description: Performance, security, modularity, and operational constraints
procedure:
  - stepNumber: 1
    title: Subsystem Decomposition and Component Mapping
    action: Partition system functionality into decoupled components with clear single responsibilities, inputs, outputs, and failure boundaries.
  - stepNumber: 2
    title: Data Flow and Interface Contract Specification
    action: Specify interface schemas (JSON Schema, OpenAPI, TypeScript types, or protobuf) for communication between components and external services.
  - stepNumber: 3
    title: Technology Selection and Dependency Vetting
    action: Select runtime libraries and tools against quality criteria (license compatibility, maintenance activity, security history, zero unnecessary dependencies).
  - stepNumber: 4
    title: Threat Modeling and Security Boundary Analysis
    action: Conduct STRIDE threat analysis. Identify trust boundaries, secret management strategies, authentication checkpoints, and input sanitization layers.
  - stepNumber: 5
    title: Architectural Decision Record (ADR) Generation
    action: Author ADR markdown documents in docs/decisions/ capturing context, alternatives considered, chosen solution, and positive/negative trade-offs.
  - stepNumber: 6
    title: Architecture Contract Assembly
    action: Assemble findings into contracts/architecture/contract.json adhering to core/schemas/architecture-contract.schema.json and submit for G3 review.
expectedOutputs:
  - contracts/architecture/contract.json adhering to architecture-contract.schema.json
  - Component diagram and subsystem specification in docs/architecture/
  - New ADR entries in docs/decisions/ documenting architectural choices
applicableApprovalGates:
  - G3
failureAndRecovery:
  potentialFailures:
    - Circularity in component dependency graph
    - Attempting to add unvetted third-party dependencies without architectural approval
    - Ambiguous interface contracts without explicit schema definitions
  recoveryStrategy: Refactor component boundaries using Dependency Inversion or Event-Driven patterns to eliminate cycles. Run dependency vulnerability audit before approving new packages. Enforce strict JSON Schema or TypeScript typing for all interfaces.
verificationCriteria:
  - contracts/architecture/contract.json passes validation against core/schemas/architecture-contract.schema.json
  - All components declare explicit dependencies with no circular references
  - Technology selections explicitly document license compatibility and rationale
  - Every major architectural trade-off is accompanied by an ADR in docs/decisions/
relevantContractsAndMemory:
  contracts:
    - contracts/requirements/contract.json
    - contracts/design/contract.json
    - contracts/architecture/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - durableKnowledge.goals
    - backlogAndHistory.decisionHistory
---

# Architecture and Contracts (`architecture-and-contracts`)

## 1. Purpose
The `architecture-and-contracts` skill drives the engineering architecture definition, interface contract formulation, threat modeling, and formal decision-making for the project. It synthesizes requirements and design constraints into a decoupled, modular system topology codified in `contracts/architecture/contract.json`, serving as the mandatory gateway to exit Gate G3 (Architecture & Plan Approval).

## 2. When to Use It
Activate this skill whenever:
- Designing a new system architecture or decomposing monolithic services.
- Defining strict API interfaces, JSON schemas, RPC methods, or data persistence models.
- Evaluating and vetting new libraries or dependencies (ensuring no unauthorized dependency bloat).
- Documenting architectural trade-offs using Architecture Decision Records (ADRs).
- Submitting the architecture baseline for formal Gate G3 approval.

## 3. Prerequisites
- Gate G1 is formally approved (`contracts/requirements/contract.json` is `APPROVED`).
- Gate G2 is approved or formally exempted with documented justification (`contracts/design/contract.json`).
- Core schemas in `core/schemas/` are loaded and immutable.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `requirementsContract` | `object` | Approved requirements specifications, acceptance criteria, and edge cases. |
| `designContract` | `object` | Approved design system tokens, responsive tiers, or exemption rationale. |
| `systemConstraints` | `array` | Non-functional constraints: memory, latency, security, zero-dependency requirements. |

## 5. Procedure (Step-by-Step)
1. **Subsystem Decomposition & Modularity**:
   - Divide system domain logic into isolated components following Single Responsibility and Clean Architecture principles.
   - Enforce explicit boundaries between transport/presentation, domain business logic, and infrastructure/storage.
   - Formulate a Directed Acyclic Graph (DAG) of component dependencies to guarantee zero cyclic imports.

2. **Interface Schema Specification**:
   - Write machine-verifiable interface contracts for all cross-component boundaries (JSON Schema Draft-07, OpenAPI 3.0, TypeScript interfaces, or Rust traits).
   - Require explicit schema validation at every system boundary (input validation, deserialization, output filtering).

3. **Dependency Vetting & Anti-Bloat Audit**:
   - Audit proposed third-party libraries against:
     - Permissive open-source licenses (MIT, Apache 2.0, BSD; disallow GPL in proprietary targets).
     - Minimal transitive dependency footprints.
     - Known security vulnerabilities (CVEs) and active maintenance.
   - Forbid convenience dependencies where standard library capabilities suffice.

4. **Threat Modeling & Security Architecture**:
   - Model attack surfaces using STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
   - Codify security controls: secret storage via environment variables, strict input validation, authorization checkpoints, and audit logging.

5. **Architecture Decision Record (ADR) Authoring**:
   - Author a standardized ADR markdown in `docs/decisions/` (e.g., `0003-component-isolation-model.md`).
   - Structure each ADR with: Status, Context, Decision, Alternatives Considered, and Consequences.

6. **Architecture Contract Synthesis & Gate G3 Submission**:
   - Compile all architecture data into `contracts/architecture/contract.json` matching `core/schemas/architecture-contract.schema.json`.
   - Update `memory/state.json` with new architectural decisions in `durableKnowledge.architecturalDecisions`.

## 6. Expected Outputs
- `contracts/architecture/contract.json`: Validated canonical architecture contract.
- ADR files in `docs/decisions/` documenting all major architectural choices.
- Interface schemas and component definitions ready for phase planning.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G3 (Architecture & Plan Approval)**: Core skill that produces the required architecture contract artifact to satisfy Gate G3 exit criteria.

## 8. Failure and Recovery Behavior
- **Cyclic Dependency Detected**: Decompose interdependent modules or introduce mediator/event bus patterns to break cycles.
- **Vulnerable or Unapproved Dependency**: Reject package addition and evaluate standard library alternative or implement minimal in-house utility.
- **Contract Schema Mismatch**: Validate payload against `core/schemas/architecture-contract.schema.json` and fix missing fields before review.

## 9. Verification Criteria
- `contracts/architecture/contract.json` validates against `core/schemas/architecture-contract.schema.json`.
- Dependency graph is acyclic and verified.
- Every external dependency is documented with license type and rationale.
- All interface boundaries define machine-readable schemas.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/requirements/contract.json`
  - `contracts/design/contract.json`
  - `contracts/architecture/contract.json`
- **Memory Records**:
  - `durableKnowledge.architecturalDecisions`
  - `durableKnowledge.goals`
  - `backlogAndHistory.decisionHistory`
