---
skillId: requirements-analysis
name: requirements-analysis
description: "Elicit, structure, analyze, and formalize functional requirements, acceptance criteria, business rules, edge cases, and ambiguity logs for Business Analysts."
purpose: Elicit, structure, analyze, and formalize functional requirements, acceptance criteria, business rules, edge cases, and ambiguity logs for Business Analysts.
whenToUse:
  - Deconstructing high-level project goals and stakeholder concepts into testable requirements
  - Authoring or updating the canonical Requirements Contract for Gate G1 (contracts/requirements/contract.json)
  - Formulating Behavior-Driven Development (BDD) Given-When-Then acceptance criteria
  - Conducting gap analysis and identifying unstated assumptions or business rule contradictions
prerequisites:
  - Gate G0 approved (contracts/project/contract.json in APPROVED or DRAFT status)
  - Access to core/schemas/requirements-contract.schema.json
  - Domain glossaries or stakeholder problem statements available
inputs:
  - name: projectContract
    type: object
    description: Approved Project Contract containing project mission, in-scope capabilities, and boundaries
  - name: stakeholderBriefs
    type: array
    description: Raw stakeholder requirements, interview transcripts, or feature requests
  - name: domainRules
    type: object
    description: Existing business policies, regulatory rules, or operational constraints
procedure:
  - stepNumber: 1
    title: Stakeholder Input & Goal Deconstruction
    action: Analyze raw inputs to extract atomic business objectives, target user roles, and core operational workflows.
  - stepNumber: 2
    title: Functional Requirements Specification
    action: Formulate atomic functional requirements (REQ-001, REQ-002, etc.) with explicit priority, description, and source.
  - stepNumber: 3
    title: Non-Functional Requirements Definition
    action: Define measurable non-functional requirements covering latency, throughput, availability, security, and accessibility.
  - stepNumber: 4
    title: BDD Acceptance Criteria Authoring
    action: Write executable Given-When-Then acceptance scenarios covering primary success paths and edge cases.
  - stepNumber: 5
    title: Business Rules & Boundary Invariant Modeling
    action: Catalog explicit business rules, calculation invariants, permission matrices, and system constraint thresholds.
  - stepNumber: 6
    title: Gap Analysis & Ambiguity Resolution
    action: Log open questions, unresolved ambiguities, and missing specifications with designated resolution owners.
  - stepNumber: 7
    title: Requirements Contract Synthesis
    action: Compile all sections into contracts/requirements/contract.json conforming to core/schemas/requirements-contract.schema.json.
expectedOutputs:
  - contracts/requirements/contract.json conforming to core/schemas/requirements-contract.schema.json
  - Requirements Traceability Matrix (RTM) initial schema
  - Business rules catalog and ambiguity log
applicableApprovalGates:
  - G0
  - G1
  - G2
failureAndRecovery:
  potentialFailures:
    - Vague or conflicting stakeholder requirements
    - Untestable or subjective acceptance criteria (e.g. 'system must be intuitive')
    - Missing error handling and boundary conditions
  recoveryStrategy: Generate structured ambiguity clarification queries with multiple-choice options. Replace qualitative phrases with verifiable quantitative thresholds. Perform boundary value stress tests to surface missing error cases.
verificationCriteria:
  - contracts/requirements/contract.json passes validation against core/schemas/requirements-contract.schema.json
  - Every functional requirement contains at least two Given-When-Then acceptance criteria
  - Zero unquantified adjectives in non-functional requirement specifications
  - All open questions have assigned owners and impact assessments
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/requirements/contract.json
  memoryRecords:
    - executionState.activeLifecycleGate
    - executionState.activeRequirementsLedger
---

# Requirements Analysis & Specification (`requirements-analysis`)

## 1. Purpose
The `requirements-analysis` skill enables Business Analysts to systematically discover, deconstruct, and formalize stakeholder needs into rigorous, unambiguous, and testable engineering specifications. It produces the canonical `contracts/requirements/contract.json` required to clear Gate G1.

## 2. When to Use It
- Translating high-level project charters from Gate G0 into concrete requirements.
- Specifying new feature requirements, business logic, or regulatory workflows.
- Authoring Behavior-Driven Development (BDD) Given-When-Then acceptance criteria.
- Conducting gap analysis to uncover unstated assumptions, missing edge cases, or contradictory rules.

## 3. Prerequisites
- Gate G0 Project Contract accessible at `contracts/project/contract.json`.
- `core/schemas/requirements-contract.schema.json` available for validation.
- Stakeholder briefs, customer interview notes, or domain policy documents.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `projectContract` | `object` | Approved Project Contract specifying project mission, in-scope domains, and exclusions. |
| `stakeholderBriefs` | `array` | Qualitative stakeholder requests, transcripts, or feature ideas. |
| `domainRules` | `object` | Existing business policies, calculation formulas, or regulatory compliance rules. |

## 5. Procedure (Step-by-Step)
1. **Stakeholder Input & Goal Deconstruction**:
   - Extract primary user goals, system actors, and core workflow triggers.
   - Map each goal to the project mission statement to prevent scope creep.

2. **Functional Requirements Specification**:
   - Formulate atomic requirements with format: `[REQ-xxx] The system shall [capability] when [condition]`.
   - Assign priority levels (CRITICAL, HIGH, MEDIUM, LOW).

3. **Non-Functional Requirements Definition**:
   - Define exact operational parameters: maximum response latency (p95 < 250ms), concurrent user scale, availability targets (99.9%), security standards (SOC2, HIPAA).

4. **BDD Acceptance Criteria Authoring**:
   - Express criteria in strict Given-When-Then syntax:
     - `Given [authenticated user with role Admin]`
     - `When [user triggers account export]`
     - `Then [system produces encrypted JSON and logs audit record]`.

5. **Business Rules & Boundary Invariant Modeling**:
   - Create a structured business rules table specifying input invariants, authorization checks, and calculation edge cases.

6. **Gap Analysis & Ambiguity Resolution**:
   - Compile an ambiguity log highlighting unaddressed failure modes, unresolved dependencies, and open stakeholder questions.

7. **Requirements Contract Synthesis**:
   - Assemble all sections into `contracts/requirements/contract.json` complying with `core/schemas/requirements-contract.schema.json`.

## 6. Expected Outputs
- `contracts/requirements/contract.json` conforming to `requirements-contract.schema.json`.
- Business Rules Catalog and Ambiguity Log.
- Baseline Requirements Traceability Matrix (RTM).

## 7. Applicable Approval Gates (G0-G6)
- **Gate G1 (Requirements & Scope Approval)**: Authoring the primary gating deliverable.
- **Gate G0 / G2**: Inception framing and design validation alignment.

## 8. Failure and Recovery Behavior
- **Subjective Criteria Detected**: Automatically reject qualitative words ("fast", "easy"). Require numerical bounds.
- **Conflicting Requirements**: Flag contradictions in the ambiguity log and schedule a decision council or request clarification.

## 9. Verification Criteria
- Contract passes JSON Schema validation against `core/schemas/requirements-contract.schema.json`.
- Every functional requirement links to at least one happy-path and one error-path acceptance scenario.
- Zero ungrounded requirements: every item links to an approved project goal.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json`
  - `contracts/requirements/contract.json`
- **Memory Records**:
  - `executionState.activeLifecycleGate`
  - `executionState.activeRequirementsLedger`
