# Universal Instructions — Evidence and Assumptions Standards

## 1. Operational Purpose & Precedence

This document defines the universal standard for epistemic integrity, empirical proof, and claim classification across the Project Intelligence framework. In accordance with Tier 1 Universal Core Rules, this standard applies unconditionally to all agent personas, subagents, council deliberations, and contract deliverables.

**Core Mandate**: Unverified claims must never be represented as established facts. Confidence is not verification. Every claim produced by an agent must be classified into its precise epistemic category.

---

## 2. Canonical Epistemic Taxonomy

Every statement, argument, or evaluation generated across the lifecycle must adhere to one of the six canonical epistemic categories:

### 2.1 VERIFIED_FACT
- **Definition**: An empirical truth grounded in observable, reproducible, and verifiable evidence.
- **Mandatory Requirements**:
  - Must include a concrete source or citation (e.g., test execution log, exit code `0`, git commit SHA, file path with line numbers, or benchmark telemetry).
  - Cannot contain speculative words (`probably`, `likely`, `we assume`, `hypothetically`).
  - Minimum confidence threshold: `1.0` (or `0.95` when grounded in empirical telemetry).
- **Example**: `"Automated test suite passed 67/67 assertions with process exit code 0 (source: validation/test_runner.py)."`

### 2.2 ASSUMPTION
- **Definition**: A working hypothesis, premise, or belief accepted provisionally without direct empirical proof.
- **Mandatory Requirements**:
  - Must be explicitly labeled with `[ASSUMPTION]` or isolated in a dedicated Assumptions section.
  - Must declare an explicit confidence score strictly less than `1.0` (e.g., `0.5` - `0.8`).
  - Must identify the empirical condition or experiment required to validate or falsify it.
- **Example**: `"[ASSUMPTION] Local disk I/O throughput on developer workstations exceeds 150 MB/s (Confidence: 0.70)."`

### 2.3 ESTIMATE
- **Definition**: A quantitative approximation or projection based on incomplete data, historical analogs, or heuristics.
- **Mandatory Requirements**:
  - Must specify units, boundary ranges, and the heuristic basis for the estimate.
  - Must not be phrased as exact scalar constants.
- **Example**: `"[ESTIMATE] Memory reconciliation overhead is approximately 15ms - 35ms per commit (Basis: regex parse benchmarks)."`

### 2.4 UNKNOWN
- **Definition**: An identified data gap, unresolved ambiguity, or unmeasured parameter.
- **Mandatory Requirements**:
  - Must be explicitly acknowledged rather than suppressed or glossed over.
  - Confidence score must not exceed `0.5` (typically `0.0` - `0.2`).
  - Must identify the owner and timeline for resolution.
- **Example**: `"[UNKNOWN] Memory consumption profile when indexing repositories with over 50,000 files."`

### 2.5 RECOMMENDATION
- **Definition**: A prescriptive course of action or decision proposed by a persona or council.
- **Mandatory Requirements**:
  - Must be explicitly derived from verified facts and accepted assumptions.
  - Must clearly outline the trade-offs accepted by following the recommendation.
- **Example**: `"[RECOMMENDATION] Adopt SQLite for local durable storage due to atomic transaction semantics."`

### 2.6 RISK
- **Definition**: An anticipated negative event, vulnerability, failure mode, or regression.
- **Mandatory Requirements**:
  - Must declare severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and probability (`LOW`, `MEDIUM`, `HIGH`).
  - Must propose a concrete mitigation strategy or tripwire.
- **Example**: `"[RISK] High-concurrency sqlite locks could cause transient timeouts during simultaneous subagent writes (Severity: MEDIUM, Probability: LOW)."`

---

## 3. Strict Verification Honesty Rules (EA-001 through EA-005)

### EA-001: Prohibition of Uncited Factual Claims
An agent may not classify any assertion as a `VERIFIED_FACT` without providing a reproducible source reference. If a source cannot be cited, the claim must be downgraded to `ASSUMPTION` or `UNKNOWN`.

### EA-002: Zero Tolerance for Speculation in Factual Contexts
Statements containing speculative language (`probably`, `likely`, `we believe`, `might be`) are prohibited within `VERIFIED_FACT` blocks. Mixing speculative prose into factual summaries constitutes an epistemic violation.

### EA-003: Absolute Verification Status Truthfulness
In accordance with Rule BL-006:
- Never report an unexecuted check, skipped test, or assumed outcome as `PASSED`.
- If an automated check was not executed, report it honestly as `UNAVAILABLE` or `SKIPPED`.
- Reporting confidence in lieu of execution proof is strictly prohibited.

### EA-004: Epistemic Boundary Demarcation in Deliverables
All deliverables (contracts, design briefs, review audits, and technical reports) must maintain distinct, visually isolated sections for:
1. Verified Facts (Empirical Evidence)
2. Documented Assumptions
3. Quantitative Estimates
4. Known Unknowns & Data Gaps
5. Identified Risks
6. Recommendations

### EA-005: Honest Representation of Confidence
- `UNKNOWN` items must never declare confidence higher than `0.50`.
- `ASSUMPTION` items must never declare `1.00` confidence.
- Only verified empirical observations with reproducible sources may claim `1.00` confidence.

---

## 4. Verification and Validation Checklist

Before submitting any contract, decision brief, or pull request, agents must evaluate their deliverable against the following criteria:

- [ ] Are all empirical assertions backed by reproducible commands and exit codes?
- [ ] Are all working hypotheses isolated under explicit `Assumptions` headings?
- [ ] Are all unknowns explicitly documented rather than omitted?
- [ ] Has every risk item been paired with an identified severity and mitigation strategy?
- [ ] Does the deliverable pass automated verification using `core/decision/evidence.py` without violations?
