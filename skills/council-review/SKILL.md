---
skillId: council-review
name: council-review
description: "Execute the canonical 4-round multi-persona council workflow to deliberate high-stakes architectural, scope, or strategic decisions, achieve reasoned consensus, preserve minority dissent, and generate a validated Council Decision Brief."
purpose: Execute the canonical 4-round multi-persona council workflow to deliberate high-stakes architectural, scope, or strategic decisions, achieve reasoned consensus, preserve minority dissent, and generate a validated Council Decision Brief.
whenToUse:
  - Deliberating major strategic or architectural decisions with high reversibility costs (Type 1 decisions)
  - Resolving irreconcilable cross-discipline trade-offs between speed, cost, quality, and user experience
  - Conducting formal gate reviews at major lifecycle gates (G0 Inception, G1 Requirements, G3 Architecture, G5 Quality)
  - Synthesizing multiple persona perspectives into a unified Council Decision Brief
prerequisites:
  - Clear decision statement or topic under deliberation
  - Participating personas identified from core/schemas/persona-definition.schema.json
  - Access to core/schemas/council-brief.schema.json
inputs:
  - name: deliberationTopic
    type: string
    description: Decision statement, architecture question, or trade-off under review
  - name: participatingPersonas
    type: array
    description: List of persona IDs participating in the deliberation (minimum 2 personas)
  - name: supportingArtifacts
    type: array
    description: Relevant contracts, design docs, benchmark data, or market reports
procedure:
  - stepNumber: 1
    title: "Round 1: Independent Initial Stances"
    action: Each participating persona independently presents its initial stance, affirmative arguments, primary concerns, cited evidence, and stated assumptions.
  - stepNumber: 2
    title: "Round 2: Cross-Examination & Adversarial Critique"
    action: Personas review peer stances, challenge ungrounded claims, expose blind spots and failure modes, and demand evidence for shaky assumptions.
  - stepNumber: 3
    title: "Round 3: Convergence Synthesis & Trade-off Mapping"
    action: Synthesize areas of consensus, isolate remaining contested issues, and explicitly map irreducible trade-offs (what is chosen vs what is sacrificed).
  - stepNumber: 4
    title: "Round 4: Recommendation Formulation & Dissent Preservation"
    action: Formulate final recommendation (Build, Test further, Pilot, Pivot, Defer, Stop), document explicit dissenting opinions, establish tripwires to change decision, and author Council Decision Brief.
expectedOutputs:
  - Council Decision Brief conforming to core/schemas/council-brief.schema.json
  - Preserved record of dissenting minority arguments and suggested alternatives
  - Decision tripwires and validation experiments manifest
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
    - Groupthink or superficial agreement without genuine cross-examination
    - Unresolved deadlock between competing personas blocking progress
    - Council Decision Brief failing validation against council-brief.schema.json
  recoveryStrategy: Appoint an adversarial devil's advocate to stress-test consensus. If deadlock persists, defer decision or commission a time-boxed validation experiment. Validate output JSON against schema before completing deliberation.
verificationCriteria:
  - Council Decision Brief strictly conforms to core/schemas/council-brief.schema.json
  - All 4 rounds are documented with active participation from every convened persona, and the record passes `python3 -m core.council.referee check`
  - Any minority objections are formally recorded in the dissent array with rationale and suggested alternatives
  - Decision includes explicit conditionsToChange and validationExperiments
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/requirements/contract.json
    - contracts/architecture/contract.json
    - contracts/quality/contract.json
  memoryRecords:
    - executionState.activeLifecycleGate
    - executionState.activeCouncil
    - executionState.councilDecisions
---

# Multi-Persona Council Deliberation & Decision Workflow (`council-review`)

## 1. Purpose
The `council-review` skill executes the canonical 4-round multi-persona council workflow of the Universal Role-Aware Intelligence Framework. It brings together distinct, specialized persona viewpoints (engineering, business, quality, commercial, strategy) to thoroughly deliberate high-stakes, irreversible decisions (Type 1 decisions), pressure-test assumptions, achieve reasoned consensus, and preserve principled minority dissent in a structured, schema-validated Council Decision Brief.

## 2. When to Use It
- Gating transitions across major lifecycle milestones (Gate G0 Inception, Gate G1 Requirements, Gate G3 Architecture, Gate G5 Quality Gate).
- Resolving contentious architectural or product trade-offs (e.g. monolithic vs microservices, custom auth vs SaaS, latency vs cost).
- Deciding whether to build, pilot, pivot, defer, or kill an initiative.
- Evaluating major technical or commercial risk events.

## 3. Prerequisites
- A clearly formulated decision statement or deliberation topic.
- A quorum of at least 2 relevant personas from the persona catalog.
- JSON schema available at `core/schemas/council-brief.schema.json`.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `deliberationTopic` | `string` | The clear decision topic, problem statement, or trade-off to resolve. |
| `participatingPersonas` | `array` | List of persona IDs participating (e.g. `["business-analyst", "qa-analyst", "product-manager"]`). |
| `supportingArtifacts` | `array` | Relevant contracts, research docs, performance benchmarks, or customer reports. |

## 5. Procedure (The 4-Round Council Workflow)
1. **Round 1: Independent Initial Stances**:
   - Each participating persona examines the topic through its specific domain lens and outputs:
     - Recommended position.
     - Strongest affirmative arguments.
     - Primary risks, concerns, and objections.
     - Empirical evidence cited and explicit assumptions stated.

2. **Round 2: Cross-Examination & Adversarial Critique**:
   - Personas directly interrogate and stress-test the stances of their peers.
   - The QA Analyst challenges developers on untested failure modes.
   - The Sales Strategist challenges product on customer procurement friction.
   - The Strategy Analyst challenges the team on defensibility and unit economics.
   - Hidden assumptions and cognitive blind spots are dragged into the light.

3. **Round 3: Convergence Synthesis & Trade-off Mapping**:
   - The council moderator maps out where personas agree and where irreducible friction remains.
   - Explicitly documents trade-offs: *What are we choosing? What are we sacrificing? Why is this acceptable?*

4. **Round 4: Recommendation Formulation & Dissent Preservation**:
   - Synthesizes the final recommendation from the six canonical council outcomes:
     - `Build` (proceed with full implementation)
     - `Test further` (conduct targeted validation experiment first)
     - `Pilot` (small-scale release to limited audience)
     - `Pivot` (redirect approach based on council findings)
     - `Defer` (postpone until external dependency resolves)
     - `Stop` (kill initiative to prevent wasted investment)
   - Documents principled minority dissent: participating personas who disagree have their objections, rationales, and suggested alternatives preserved permanently.
   - Sets tripwires (`conditionsToChange`): events that automatically force reopening the decision.
   - Emits the completed Council Decision Brief conforming to `core/schemas/council-brief.schema.json`.

## 6. Expected Outputs
- Canonical Council Decision Brief conforming to `core/schemas/council-brief.schema.json`.
- Full 4-round deliberation transcript preserved in project memory.
- Updated `executionState.councilDecisions` in `memory/execution-state.json`.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G0**: Investment & viability go/no-go.
- **Gate G1**: Requirements completeness and scope lock.
- **Gate G3**: Architecture ratification and WBS sign-off.
- **Gate G5**: Quality and release readiness approval.

## 8. Failure and Recovery Behavior
- **Superficial Groupthink**: If all personas immediately agree without debate, mandate an adversarial critique round by assigning a devil's advocate.
- **Irreconcilable Deadlock**: Select `Test further` or `Pilot`, design a falsification experiment, and set an evaluation date.

## 9. Verification Criteria
- Council Decision Brief passes validation against `core/schemas/council-brief.schema.json`.
- All 4 deliberation rounds are documented.
- Explicit `confidenceLevel` (HIGH, MEDIUM, LOW) is recorded.
- Dissenting views are faithfully preserved in the `dissent` array.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json`
  - `contracts/requirements/contract.json`
  - `contracts/architecture/contract.json`
  - `contracts/quality/contract.json`
- **Memory Records**:
  - `executionState.activeLifecycleGate`
  - `executionState.activeCouncil`
  - `executionState.councilDecisions`
