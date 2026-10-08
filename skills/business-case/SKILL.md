---
skillId: business-case
name: business-case
description: "Formulate commercial business cases, quantify return on investment (ROI), articulate differentiated value propositions, model monetization options, and anticipate buyer objections for Sales, Commercial, and Finance Analysts."
purpose: Formulate commercial business cases, quantify return on investment (ROI), articulate differentiated value propositions, model monetization options, and anticipate buyer objections for Sales, Commercial, and Finance Analysts.
whenToUse:
  - Evaluating commercial viability and investment justification during Gate G0 and G1
  - Developing pricing models, monetization strategies, and unit economics estimates
  - Constructing enterprise objection-handling playbooks and go-to-market battlecards
  - Quantifying customer total cost of ownership (TCO) and projected financial return
prerequisites:
  - Project Mission Statement or draft Project Contract (contracts/project/contract.json)
  - Target customer profiles and preliminary product capabilities
  - Market pricing data or competitor benchmarking information
inputs:
  - name: projectContract
    type: object
    description: Approved or draft Project Contract specifying scope and strategic objectives
  - name: targetAudienceData
    type: object
    description: Buyer personas, economic decision maker roles, and target market segments
  - name: costAndRevenueParameters
    type: object
    description: Estimated engineering costs, operational expenses, and target pricing models
procedure:
  - stepNumber: 1
    title: Target Audience & Buyer Persona Profiling
    action: Profile the economic buyer, technical evaluation lead, and end-user personas with their respective pain points and success metrics.
  - stepNumber: 2
    title: Value Proposition Canvas Mapping
    action: Map proposed product features to direct customer gains and pain relievers to establish differentiated value pillars.
  - stepNumber: 3
    title: Customer Objection Anticipation & Defense Playbook
    action: Systematically catalog anticipated objections across security, pricing, migration cost, and vendor risk, pairing each with evidence-backed rebuttals.
  - stepNumber: 4
    title: Quantitative ROI & TCO Financial Modeling
    action: Construct a financial model showing customer cost baseline, savings from solution adoption, payback period, and 3-year ROI.
  - stepNumber: 5
    title: Pricing & Monetization Strategy Formulation
    action: Model recommended pricing structures (per-seat, usage-based, tiered) and align them with customer value realization.
  - stepNumber: 6
    title: Commercial Risk Assessment & Go-to-Market Brief Synthesis
    action: Compile commercial risks, regulatory constraints, and sales cycle friction into an executive Commercial Business Case.
expectedOutputs:
  - Comprehensive Commercial Business Case and Financial ROI Model
  - Value Proposition Matrix and Customer Messaging Framework
  - Enterprise Objection Handling Playbook and Risk Register
applicableApprovalGates:
  - G0
  - G1
  - G3
failureAndRecovery:
  potentialFailures:
    - Unsubstantiated ROI figures based on speculative efficiency gains
    - Ignoring enterprise procurement objections (security, compliance, data lock-in)
    - Pricing models misaligned with customer budget and value consumption
  recoveryStrategy: Require transparent formulas with conservative baseline parameters. Solicit input from security and legal stakeholders to address compliance objections. Benchmark pricing against established market alternatives.
verificationCriteria:
  - ROI calculations include explicit formulas and stated assumptions
  - Every listed customer objection includes a concrete, factual rebuttal strategy
  - Target buyer personas clearly identify the economic decision-maker with budget authority
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/requirements/contract.json
  memoryRecords:
    - executionState.activeLifecycleGate
    - executionState.activeCommercialLedger
---

# Commercial Business Case Formulation (`business-case`)

## 1. Purpose
The `business-case` skill equips commercial, sales, and financial analysts to construct rigorous, evidence-grounded commercial business cases. It articulates differentiated customer value propositions, quantifies financial return on investment (ROI), designs sustainable pricing models, and prepares objection-handling strategies to ensure projects generate genuine commercial returns.

## 2. When to Use It
- Justifying capital expenditure and development investment at Gate G0 and G1.
- Formulating customer value propositions and market differentiation vectors.
- Modeling pricing structures (seat-based, consumption, tiered packaging).
- Designing objection-handling playbooks for enterprise procurement, security, and finance hurdles.

## 3. Prerequisites
- Project charter or initial concept draft in `contracts/project/contract.json`.
- Preliminary product capabilities and target customer segments identified.
- Market pricing and competitor benchmarks available.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `projectContract` | `object` | Approved or draft Project Contract outlining scope, mission, and deliverables. |
| `targetAudienceData` | `object` | Target customer personas, buyer roles, and industry vertical profiles. |
| `costAndRevenueParameters` | `object` | Build costs, operational maintenance estimates, and target pricing models. |

## 5. Procedure (Step-by-Step)
1. **Target Audience & Buyer Persona Profiling**:
   - Differentiate the Economic Buyer (budget authority), Technical Evaluator (security/integration), and End User (daily operator).
   - Document the specific business pain and metric each persona is held accountable for.

2. **Value Proposition Canvas Mapping**:
   - Map software features directly to customer pain relievers and business gain creators.
   - Formulate 3 distinct value pillars backed by quantifiable claims.

3. **Customer Objection Anticipation**:
   - Identify top enterprise objections:
     - Security & Compliance ("Where is data stored?").
     - Integration Friction ("How hard is it to connect to our legacy ERP?").
     - Vendor Lock-in ("Can we export our data easily?").
     - Budget & TCO ("Why shouldn't we keep doing this manually in spreadsheets?").
   - Pair each objection with an evidence-backed factual rebuttal.

4. **Financial ROI & Payback Modeling**:
   - Build a transparent ROI calculation:
     - Baseline annual cost without solution.
     - Annual cost with solution (subscription + implementation).
     - Net annual savings and efficiency gains.
     - Payback period (target: < 6 months).

5. **Pricing & Monetization Strategy**:
   - Evaluate pricing models and define tier limits (Starter, Professional, Enterprise).

6. **Commercial Business Case Synthesis**:
   - Synthesize findings into an executive report with explicit sensitivity analysis.

## 6. Expected Outputs
- Commercial Business Case document with transparent ROI financial model.
- Value Proposition Matrix and Messaging Framework.
- Enterprise Objection Handling Playbook.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G0 (Inception)**: Investment justification and market viability check.
- **Gate G1 (Requirements)**: Commercial scope alignment and willingness-to-pay validation.
- **Gate G3 (Architecture/Planning)**: Verifying that architecture costs fit unit economics.

## 8. Failure and Recovery Behavior
- **Wild ROI Numbers**: Flag models promising 1000% ROI without clear proof. Recalibrate against conservative industry benchmarks.
- **Unaddressed Security Objections**: Require explicit security answers before clearing commercial review.

## 9. Verification Criteria
- ROI formulas specify explicit numeric parameters and formulas.
- Every anticipated objection includes a concrete counter-measure.
- Target buyer personas identify the budget holder.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json`
  - `contracts/requirements/contract.json`
- **Memory Records**:
  - `executionState.activeLifecycleGate`
  - `executionState.activeCommercialLedger`
