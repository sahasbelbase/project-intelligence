# Universal Instructions — Decision Framework

## 1. Operational Purpose & Precedence

This framework establishes a deterministic, evidence-based methodology for evaluating technical, architectural, and lifecycle decisions. It governs how personas formulate proposals, evaluate trade-offs, define tripwires, and generate formal recommendations.

---

## 2. Decision Classification: Type 1 vs Type 2

Every proposed action or architecture choice must be categorized by reversibility and blast radius:

| Attribute | Type 1 (Irreversible / High Blast Radius) | Type 2 (Reversible / Low Blast Radius) |
|---|---|---|
| **Reversibility** | Difficult or prohibitively expensive to undo | Easy to reverse or modify with localized commits |
| **Blast Radius** | Repo-wide, state persistence, security model, core API | Internal function, localized helper, CSS styling, unit test |
| **Governance Required** | Multi-Persona Council + Formal ADR + Gate Approval | Single Persona + Local Automated Verification |
| **Pre-requisite** | Empirical evidence + Round 2 adversarial challenge | Clean unit test pass + lint verification |

---

## 3. The 6 Canonical Recommendation Outcomes

Every council deliberation or architectural evaluation must resolve into exactly one of the six canonical recommendations:

### 3.1 Build
- **Trigger**: Requirements are verified, risks are mitigated, empirical proof confirms feasibility, and architectural boundaries are defined.
- **Action**: Advance to Gate G4 (Implementation) and author implementation contracts.

### 3.2 Test further
- **Trigger**: The fundamental concept is sound, but critical empirical data, benchmarks, or security invariants remain unverified.
- **Action**: Quarantine current phase; author targeted empirical test scripts or spikes; gather missing telemetry before reconsidering.

### 3.3 Pilot
- **Trigger**: Moderate complexity or unproven scaling characteristics, but high expected value.
- **Action**: Author an isolated, feature-flagged proof-of-concept; define strict pass/fail metrics; run in quarantine before repo-wide integration.

### 3.4 Pivot
- **Trigger**: Analysis or spike testing reveals that core assumptions are invalidated, or an alternative architectural approach offers superior trade-offs.
- **Action**: Reformulate requirements; author revised proposal; re-route through Architecture and Discovery personas.

### 3.5 Defer
- **Trigger**: Unresolved upstream blockers, pending external dependencies, or conflicting current milestone priorities.
- **Action**: Record in `memory/backlog.json` with documented revisit criteria and prerequisite triggers.

### 3.6 Stop
- **Trigger**: Fatal architectural defects, unacceptable security vulnerabilities, violation of core anti-slop rules, or zero demonstrable value.
- **Action**: Terminate initiative; archive rationale in durable knowledge; prevent further resource expenditure.

---

## 4. Trade-Off Evaluation Principles

Technical decisions always incur trade-offs. Pretending a choice has no drawbacks is a violation of epistemic honesty (EA-001). Every decision brief must explicitly record:

1. **Aspect**: The dimension under tension (e.g., *Latency vs Simplicity*, *Rigor vs Speed*).
2. **Chosen Option**: The specific technical path selected.
3. **Sacrificed Option**: The benefit deliberately foregone.
4. **Rationale**: Why the chosen option aligns with system mission and active quality profiles.

### Core Architectural Invariants:
- **Local-First over Cloud Dependency**: Always favor local, offline-capable computation over remote SaaS APIs unless mandated by user requirements.
- **Simplicity over Speculative Generalization**: Do not construct premature abstractions, micro-frameworks, or plugin systems for hypothetical future features.
- **Verification Rigor over Rushed Velocity**: A fast implementation that lacks automated test verification is technical debt, not progress.

---

## 5. Conditions to Change (Operational Tripwires)

No decision is permanent. Every approved decision brief must specify **Conditions to Change** — explicit, observable triggers that mandate immediate re-opening of the deliberation:

1. **Empirical Performance Failure**: Latency, CPU, or memory consumption exceeds specified threshold by >25%.
2. **Security Vulnerability Discovery**: Identification of an unmitigated attack surface or credential exposure risk.
3. **Verification Defect Rate**: Regression suite failure or persistent test flakiness.
4. **Scope Creep Alert**: Implementation expansion exceeding >20% of agreed MVP boundary.
5. **Requirement Invalidation**: Upstream product mission or human directives contradict prior assumptions.
