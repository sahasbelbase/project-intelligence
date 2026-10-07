# Quality Profile: Production-Ready (`PRODUCTION_READY`)

## 1. Overview and Intent
The **Production-Ready** profile governs mission-critical enterprise systems, core platform infrastructure, and high-availability production services. It prioritizes resilience, fault tolerance, long-term maintainability, full accessibility compliance, and exhaustive test coverage over rapid prototyping velocity.

---

## 2. Threshold Matrix and Requirements

| Quality Dimension | Requirement | Threshold / Policy |
|---|---|---|
| **Code Coverage** | Mandatory | **>= 85%** line coverage and >= 80% branch coverage |
| **Linting & Formatting** | Mandatory | Zero-warning policy (`--max-warnings=0`) |
| **Unit, Integration & E2E Tests**| Mandatory | Exhaustive suite covering all user journeys |
| **Security Vulnerability Scan** | Mandatory | Zero High, Medium, or Critical CVEs |
| **Accessibility (a11y) Audit** | Mandatory | 100% WCAG 2.1 Level AA compliance on all UI views |
| **Independent Review (G5)** | Mandatory | Adversarial review with strict gate criteria |
| **Mandatory Baseline Rules** | Non-Negotiable | BL-001 through BL-007 enforced without exception |

---

## 3. Engineering Guidelines for Production-Ready Systems

### 3.1 Strict Zero-Warning Discipline
- Linters, formatters, and static analyzers must be configured in strict mode.
- Any compiler warning, unused variable, deprecated method call, or lint violation fails the build immediately.
- Blanket suppression comments (`# noqa`, `eslint-disable`) are prohibited without formal ADR approval.

### 3.2 High-Reliability Testing Protocols
- **85% Coverage Floor**: High line and branch coverage is strictly verified by automated coverage tools before Gate G4 exit.
- **End-to-End (E2E) Journey Tests**: Critical user flows must have automated end-to-end integration tests validating multi-step workflows.
- **Failure-Mode & Chaos Testing**: Test suites must deliberately simulate degraded dependencies (network timeouts, disk full, corrupted payloads) to verify graceful degradation and circuit breakers.

### 3.3 Enterprise Accessibility (WCAG 2.1 AA)
- All user-facing views must pass automated accessibility audits (e.g. `axe-core`, Lighthouse a11y score >= 95).
- Visible keyboard focus rings (minimum 2px with 2px offset) must be present on all interactive controls.
- Color contrast ratios must meet or exceed 4.5:1 for normal text and 3:1 for graphical elements.
- Screen reader landmarks (`main`, `nav`, `header`, `footer`) and ARIA live regions must be explicitly structured.

### 3.4 Operational Resilience & Observability
- All production code must include structured logging (JSON format) with trace IDs, log levels (INFO, WARN, ERROR), and zero sensitive PII.
- Health check endpoints (`/healthz`, `/readyz`) and metric telemetry hooks must be implemented.
