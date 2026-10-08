---
skillId: feature-prioritization
name: feature-prioritization
description: "Score, prioritize, and partition product features using Value vs Risk vs Complexity frameworks, establish strict MVP scope boundaries, and enforce explicit exclusion lists for Product Managers."
purpose: Score, prioritize, and partition product features using Value vs Risk vs Complexity frameworks, establish strict MVP scope boundaries, and enforce explicit exclusion lists for Product Managers.
whenToUse:
  - Prioritizing candidate features during product discovery and Gate G1 scope formulation
  - Defining the lean Minimum Viable Product (MVP) boundary and phasing future capabilities
  - Resolving stakeholder scope contention and preventing creeping feature expansion
  - Constructing an explicit Out-of-Scope Exclusions ledger to protect engineering focus
prerequisites:
  - Raw feature list or candidate user stories from Requirements Analysis
  - Strategic opportunity parameters from Strategy Analyst or Project Contract
  - High-level technical complexity estimates from engineering architecture
inputs:
  - name: candidateFeatures
    type: array
    description: List of proposed capabilities, user stories, or feature ideas
  - name: strategicObjectives
    type: object
    description: Organizational goals, target user metrics, and North Star criteria
  - name: engineeringConstraints
    type: object
    description: Timeline constraints, technical complexity indices, and team capacity
procedure:
  - stepNumber: 1
    title: Candidate Feature Inventory & Normalization
    action: Catalog all proposed features with standardized descriptions, target user personas, and intended outcomes.
  - stepNumber: 2
    title: Customer & Business Value Scoring
    action: Score each feature on User Value (1-5) and Business Value (1-5) based on frequency, reach, and user impact.
  - stepNumber: 3
    title: Technical Complexity & Execution Risk Assessment
    action: Score each feature on Technical Complexity (1-5) and Implementation/Security Risk (1-5).
  - stepNumber: 4
    title: Value vs Risk vs Complexity Matrix Mapping
    action: "Plot features into quadrant tiers: Quick Wins (High Value, Low Complexity), Strategic Bets (High Value, High Complexity), Nice-to-Haves (Low Value, Low Complexity), and Time Sinks (Low Value, High Complexity)."
  - stepNumber: 5
    title: MVP Scope Boundary Demarcation
    action: Select the minimal cohesive set of Quick Wins and essential Strategic Bets required to deliver end-to-end user value in Phase 1.
  - stepNumber: 6
    title: Explicit Out-of-Scope Exclusion Ledger Formulation
    action: Document every omitted feature in an explicit Exclusions List with documented rationale and future phase targets.
expectedOutputs:
  - Quantitative Feature Prioritization Matrix with quadrant classifications
  - Minimal Viable Product (MVP) Scope Definition Manifest
  - Explicit Out-of-Scope Exclusions Ledger with justification notes
applicableApprovalGates:
  - G0
  - G1
  - G2
  - G3
failureAndRecovery:
  potentialFailures:
    - Subjective scoring driven by executive preference rather than customer evidence
    - Overly broad MVP scope that attempts to deliver 100% of wish-list items in Phase 1
    - Ambiguity in scope exclusions leading to stealth feature creep during development
  recoveryStrategy: Enforce weighted multi-variable scoring algorithms (Value / (Complexity * Risk)). Mandate that MVP scope constitutes no more than 40% of proposed feature volume. Require explicit written sign-off on excluded features.
verificationCriteria:
  - Every candidate feature is scored across Value, Risk, and Complexity dimensions
  - MVP scope contains a coherent, end-to-end user journey without broken workflow dependencies
  - The Out-of-Scope Exclusions list is non-empty and provides explicit rationale for each deferred item
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/requirements/contract.json
  memoryRecords:
    - executionState.activeLifecycleGate
    - executionState.activeProductLedger
---

# Feature Prioritization & MVP Scoping (`feature-prioritization`)

## 1. Purpose
The `feature-prioritization` skill provides Product Managers with a structured, quantitative mechanism to evaluate competing feature ideas, balance user value against engineering complexity and technical risk, define a tightly bounded Minimum Viable Product (MVP), and enforce explicit out-of-scope exclusions.

## 2. When to Use It
- Sifting through a large list of feature requests during Gate G1 (Requirements & Scope Approval).
- Resolving conflicting priorities between executive requests, customer feedback, and technical debt.
- Drawing a defensible line between what must be built now (Phase 1 MVP) versus what is deferred (Phase 2+).
- Formulating the Out-of-Scope section for `contracts/project/contract.json` and `contracts/requirements/contract.json`.

## 3. Prerequisites
- Backlog of candidate features or user stories.
- High-level architectural feasibility assessment.
- Approved strategic objectives in `contracts/project/contract.json`.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `candidateFeatures` | `array` | List of proposed capabilities, feature concepts, or user stories. |
| `strategicObjectives` | `object` | Business goals, target audience needs, and success KPIs. |
| `engineeringConstraints` | `object` | Team capacity, architectural constraints, and target delivery windows. |

## 5. Procedure (Step-by-Step)
1. **Feature Cataloging & Normalization**:
   - Normalize feature requests into standard format: Feature Name, Problem Solved, Target User, Intended Outcome.

2. **Customer & Business Value Scoring (1 to 5)**:
   - Score *Reach* (how many users benefit) and *Impact* (how significantly it improves their workflow).
   - Compute aggregate Value Score: `(User Impact * Reach Weight)`.

3. **Complexity & Risk Scoring (1 to 5)**:
   - Score *Engineering Effort* (days/weeks required) and *Architectural/Security Risk* (novel tech, compliance, external API reliance).

4. **Matrix Mapping & Quadrant Classification**:
   - Categorize features into the 2x2 Priority Matrix:
     - **Tier 1 (Quick Wins)**: High Value, Low Complexity -> Automatic MVP Candidates.
     - **Tier 2 (Strategic Bets)**: High Value, High Complexity -> Select only 1-2 core differentiators for MVP.
     - **Tier 3 (Fill-ins)**: Low Value, Low Complexity -> Backlog for post-MVP iterations.
     - **Tier 4 (Money Pits)**: Low Value, High Complexity -> Deprioritize or eliminate completely.

5. **MVP Boundary Formulation**:
   - Select the minimal subset of Tier 1 and essential Tier 2 capabilities that form a complete, unbroken user loop.

6. **Exclusions Ledger Formulation**:
   - Document every feature NOT in the MVP with explicit explanation: why it was omitted and when it will be re-evaluated.

## 6. Expected Outputs
- Quantitative Prioritization Matrix table with scores and tiering.
- MVP Scope Definition Manifest specifying Phase 1 boundaries.
- Explicit Out-of-Scope Exclusions Ledger.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G0 (Inception)**: Preliminary scope filtering.
- **Gate G1 (Requirements Approval)**: Formal MVP definition and exclusions sign-off.
- **Gate G2 / G3**: Design and architecture alignment on phased capabilities.

## 8. Failure and Recovery Behavior
- **Everything Is Priority 1**: If all features are scored as CRITICAL, force rank-order ordering (1 to N) with strict quotas.
- **Creeping Exclusions**: If engineers or designers start implementing excluded items, immediately flag an anti-slop violation.

## 9. Verification Criteria
- All features receive numerical scores across Value, Complexity, and Risk.
- MVP scope is coherent and provides an unbroken end-to-end user workflow.
- Out-of-scope exclusions list is non-empty with written justifications.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json`
  - `contracts/requirements/contract.json`
- **Memory Records**:
  - `executionState.activeLifecycleGate`
  - `executionState.activeProductLedger`
