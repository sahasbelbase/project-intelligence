---
skillId: test-case-generation
name: test-case-generation
description: "Design, formalize, and generate comprehensive positive, negative, boundary, regression, and security test cases with 100% requirements traceability for QA Analysts."
purpose: Design, formalize, and generate comprehensive positive, negative, boundary, regression, and security test cases with 100% requirements traceability for QA Analysts.
whenToUse:
  - Transforming Given-When-Then acceptance criteria into executable test cases
  - Designing adversarial test suites targeting security vulnerabilities, auth bypass, and injection
  - Constructing boundary value analysis and equivalence partition matrices for inputs
  - Building regression suites and assembling the Quality Contract for Gate G4 and G5
prerequisites:
  - Approved Requirements Contract (contracts/requirements/contract.json)
  - Architecture component interfaces or API definitions
  - Active Quality Profile in core/quality/profiles.json
inputs:
  - name: requirementsContract
    type: object
    description: Approved Requirements Contract containing functional requirements and acceptance criteria
  - name: architectureContract
    type: object
    description: Architecture Contract defining component interfaces, data models, and dependencies
  - name: qualityProfile
    type: object
    description: Active quality standards, anti-slop rules, and testing coverage mandates
procedure:
  - stepNumber: 1
    title: Acceptance Criteria Parsing & Extraction
    action: Parse all acceptance criteria from the Requirements Contract to establish the verification baseline.
  - stepNumber: 2
    title: Positive & Happy-Path Test Case Generation
    action: Generate deterministic positive test scenarios verifying expected behavior under normal, valid operating conditions.
  - stepNumber: 3
    title: Equivalence Partitioning & Boundary Value Analysis
    action: Identify input domain partitions and generate test cases targeting exact boundary thresholds (min, max, min-1, max+1, null, empty).
  - stepNumber: 4
    title: Negative & Adversarial Scenario Formulation
    action: Design negative test cases exercising invalid types, malformed payloads, rate limit exhaustion, and service outage simulations.
  - stepNumber: 5
    title: Security & Authorization Scenario Mapping
    action: Formulate targeted security scenarios verifying authentication enforcement, role isolation, tenant segregation, and input sanitization.
  - stepNumber: 6
    title: Traceability Matrix & Verification Suite Synthesis
    action: Compile test catalog into a structured test suite linking every requirement to concrete tests in contracts/quality/contract.json.
expectedOutputs:
  - Comprehensive Test Case Catalog (Positive, Negative, Boundary, Security, Regression)
  - Requirements-to-Test Traceability Matrix (RTM)
  - Quality Contract payload for contracts/quality/contract.json
applicableApprovalGates:
  - G1
  - G3
  - G4
  - G5
failureAndRecovery:
  potentialFailures:
    - Missing requirement coverage leaving critical acceptance criteria untested
    - Ambiguous test assertions that pass trivially without verifying payload state
    - Flaky test definitions reliant on unseeded random numbers or uncontrolled race conditions
  recoveryStrategy: Run automated RTM coverage audit to flag untested requirement IDs. Require exact assert invariants rather than status-code only checks. Enforce deterministic test fixtures and mock external clock dependencies.
verificationCriteria:
  - 100% of functional requirements link to at least one positive and one negative test case
  - Every test case declares unambiguous Preconditions, Inputs, Execution Steps, and Expected Assertions
  - Security test cases cover OWASP injection, broken access control, and data leakage risks
relevantContractsAndMemory:
  contracts:
    - contracts/requirements/contract.json
    - contracts/architecture/contract.json
    - contracts/quality/contract.json
  memoryRecords:
    - executionState.activeLifecycleGate
    - executionState.activeTestLedger
---

# Test Case Generation & Verification Suite Design (`test-case-generation`)

## 1. Purpose
The `test-case-generation` skill equips QA Analysts to construct comprehensive, adversarial, and verifiable test suites. It systematically converts high-level requirements into deterministic positive, negative, boundary, security, and regression test cases, providing rigorous evidence for Gate G4 and G5 transitions.

## 2. When to Use It
- Converting approved acceptance criteria from Gate G1 into formal test specifications.
- Designing boundary value analysis (BVA) suites for complex input models and APIs.
- Formulating adversarial negative test cases to verify error resilience and rate limiting.
- Auditing test coverage and building the Requirements-to-Test Traceability Matrix (RTM).
- Assembling `contracts/quality/contract.json`.

## 3. Prerequisites
- Approved `contracts/requirements/contract.json`.
- Architecture component specifications from `contracts/architecture/contract.json`.
- Quality standards declared in `core/quality/profiles.json`.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `requirementsContract` | `object` | Approved Requirements Contract with functional requirements and Given-When-Then criteria. |
| `architectureContract` | `object` | System component interfaces, endpoints, schemas, and dependencies. |
| `qualityProfile` | `object` | Active quality baseline rules, coverage thresholds, and anti-slop policies. |

## 5. Procedure (Step-by-Step)
1. **Acceptance Criteria Extraction**:
   - Extract all Given-When-Then scenarios and invariant rules from `contracts/requirements/contract.json`.
   - Assign test case IDs (`TC-xxx`) linked directly to parent requirement IDs (`REQ-xxx`).

2. **Positive (Happy Path) Test Case Formulation**:
   - Specify deterministic valid inputs and expected successful state mutations.
   - Assert exact return structures, response codes, and database persistences.

3. **Boundary Value Analysis (BVA)**:
   - Identify domain limits for all inputs (strings, integers, arrays, dates).
   - Generate test cases for boundary values: min, min-1, max, max+1, empty, null, unicode, and extreme length.

4. **Negative & Exception Handling Scenarios**:
   - Test invalid credentials, malformed JSON, missing required fields, and expired tokens.
   - Assert that system returns correct, safe error responses without leaking internal stack traces.

5. **Security & Authorization Scenarios**:
   - Verify tenant boundary enforcement (cross-tenant access attempts fail with 403 Forbidden).
   - Test SQL/NoSQL injection, prompt injection, and unauthorized role escalation vectors.

6. **Traceability Matrix & Suite Synthesis**:
   - Assemble test cases into the canonical RTM table.
   - Ensure 100% of requirements map to both positive and negative verification coverage.

## 6. Expected Outputs
- Detailed Test Case Catalog formatted with Preconditions, Steps, Inputs, and Assertions.
- Requirements Traceability Matrix (RTM) linking requirements to test suites.
- Quality Contract payload for `contracts/quality/contract.json`.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G1 (Requirements)**: Initial test planning and acceptance criteria validation.
- **Gate G3 (Architecture)**: Component interface and integration test design.
- **Gate G4 (Implementation)**: Execution evidence collection and defect logging.
- **Gate G5 (Quality Gate)**: Formal verification sign-off.

## 8. Failure and Recovery Behavior
- **Untested Requirements**: Automated check flags unlinked requirements. Require test addition before signing off.
- **Vague Assertions**: Flag assertions like `assert response is not None`. Require exact field value comparisons.

## 9. Verification Criteria
- 100% of approved functional requirements link to at least one positive and one negative test case.
- Test cases specify deterministic inputs with zero unseeded random values.
- Security test cases explicitly address authorization bypass and payload injection.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/requirements/contract.json`
  - `contracts/architecture/contract.json`
  - `contracts/quality/contract.json`
- **Memory Records**:
  - `executionState.activeLifecycleGate`
  - `executionState.activeTestLedger`
