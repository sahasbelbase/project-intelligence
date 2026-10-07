# Quality Profile: Prototype (`PROTOTYPE`)

## 1. Overview and Intent
The **Prototype** profile optimizes for velocity, rapid architectural hypothesis testing, and early feedback while strictly upholding the non-negotiable **Mandatory Engineering Baseline (BL-001 through BL-007)**. It is intended for exploratory spikes, proof-of-concepts, hackathons, and early research prototypes where formal test coverage overhead would impede innovation.

---

## 2. Threshold Matrix and Requirements

| Quality Dimension | Requirement | Threshold / Policy |
|---|---|---|
| **Code Coverage** | Optional | `0%` minimum requirement |
| **Linting & Formatting** | Mandatory | Must pass with zero fatal syntax errors |
| **Unit Tests** | Mandatory (Core Paths) | Basic sanity tests for core algorithms |
| **Security Vulnerability Scan** | Optional | Recommended if handling network I/O |
| **Accessibility (a11y) Audit** | Optional | Semantic elements recommended |
| **Independent Review (G5)** | Mandatory | Must verify anti-slop rules and scope boundaries |
| **Mandatory Baseline Rules** | Non-Negotiable | BL-001 through BL-007 enforced without exception |

---

## 3. Engineering Guidelines for Prototypes

### 3.1 Velocity Without Slop
- **Clean Architecture Over Throwaway Hacks**: Even in a prototype, code must be structured modularly. Do not write spaghetti code under the guise of prototyping.
- **No Decorative Fillers**: BL-001 strictly applies. Do not add decorative emojis in code, commits, or CLI outputs.
- **No Fake Data in Production Paths**: BL-002 applies. Use structured configuration files or test fixtures rather than hardcoding fake names, emails, or credentials in operational logic.
- **Working Stubs Only**: If an endpoint or feature is incomplete, either omit it from the deliverable or have it raise an explicit `NotImplementedError` with clear error logging. Do not render non-functional fake UI buttons (BL-003).

### 3.2 Testing and Verification Discipline
- While overall line coverage is not mandated to exceed a percentage threshold, critical core functions must include basic unit test sanity checks to verify that the core concept executes without crashing.
- Verification status must be honestly recorded. If integration tests are omitted, report them as `SKIPPED (Profile: PROTOTYPE)` rather than faking a pass.

### 3.3 Path to Production Promotion
- Prototype code is strictly isolated. Before any prototype component is promoted to `STANDARD` or `PRODUCTION_READY`, it must undergo:
  1. Full unit and integration test creation meeting the target profile coverage threshold.
  2. Formal security scanning and dependency vetting.
  3. Re-execution of Gate G4 verification and Gate G5 independent review.
