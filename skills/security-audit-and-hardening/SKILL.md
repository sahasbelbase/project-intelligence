---
skillId: security-audit-and-hardening
name: security-audit-and-hardening
description: "Audit codebases for secrets exposure, CVE dependencies, OWASP Top 10 vulnerabilities, and security configuration flaws, generating verified hardening remediations."
purpose: "Audit codebases for secrets exposure, CVE dependencies, OWASP Top 10 vulnerabilities, and security configuration flaws, generating verified hardening remediations."
whenToUse:
  - Pre-commit and pre-release security validation audits
  - Scanning repositories for leaked API keys, tokens, or plaintext credentials
  - Auditing package manifests and lockfiles for known CVE vulnerabilities
  - Inspecting authentication, authorization, and permission enforcement logic
  - Reviewing input validation to prevent SQL injection, XSS, and path traversal
  - Validating secure defaults for headers, CORS, cookies, and network transport
prerequisites:
  - Read-only access to repository source code, configuration, and lockfiles
  - Package manager CLI (npm, pip, cargo, go) to inspect dependency trees
inputs:
  - name: auditScope
    type: string
    description: "Scope of analysis: full-repo, dependencies, secrets, or endpoint-auth"
  - name: severityThreshold
    type: string
    description: "Minimum vulnerability severity to flag: LOW, MEDIUM, HIGH, or CRITICAL"
  - name: secretsScanningRegexes
    type: array
    description: Custom patterns for detecting proprietary credentials and tokens
procedure:
  - stepNumber: 1
    title: Secrets & Credential Exposure Scan
    action: Scan all tracked files, commit history, and environment templates for hardcoded API keys, private certificates, JWT secrets, and database passwords.
  - stepNumber: 2
    title: Dependency Supply-Chain CVE Audit
    action: Inspect package lockfiles (package-lock.json, poetry.lock, Cargo.lock, go.sum) using package audit tooling to identify unpatched high and critical CVEs.
  - stepNumber: 3
    title: OWASP Top 10 Injection & Sanitization Inspection
    action: Trace data inputs from HTTP parameters, headers, and file uploads to database queries, shell executions, and HTML renders to verify strict sanitization.
  - stepNumber: 4
    title: Authentication & Authorization Boundary Audit
    action: Verify that every privileged route, handler, and database query enforces role-based access checks, token expiration, and secure session handling.
  - stepNumber: 5
    title: Hardening Specification & Remediation Generation
    action: "Formulate concrete, non-breaking remediation patches: dependency upgrades, environment variable abstractions, and secure header configurations."
expectedOutputs:
  - Structured security audit report with categorized findings by severity (CRITICAL, HIGH, MEDIUM, LOW)
  - Remediation patch recommendations for dependency CVEs and insecure configurations
  - Pre-commit security hook configuration preventing credential leakage
applicableApprovalGates:
  - G1
  - G2
  - G4
  - G5
failureAndRecovery:
  potentialFailures:
    - False positive secret flags on test mock fixtures or public example keys
    - Dependency upgrades introduce breaking API changes
    - Incomplete input tracing in dynamic languages
  recoveryStrategy: Allow documented security exemptions for verified mock test fixtures with explicit comments. Where dependency upgrades introduce breaking changes, isolate the upgrade behind a compatibility adapter.
verificationCriteria:
  - Zero plaintext credentials or live tokens exist anywhere in the tracked working tree
  - No unpatched CRITICAL or HIGH severity CVEs exist in the production dependency tree
  - All input parameters fed into queries or system commands use parameterized APIs
relevantContractsAndMemory:
  contracts:
    - contracts/architecture/contract.json
    - contracts/quality/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - backlogAndHistory.technicalDebt
---

# Security Audit & Hardening (`security-audit-and-hardening`)

## 1. Purpose
The `security-audit-and-hardening` skill inspects repositories for vulnerabilities, accidental credential leakage, and insecure software architecture. It enforces strict AppSec baselines, scans dependency manifests for CVEs, reviews authentication/authorization guards, and generates verified hardening patches.

## 2. When to Use It
Activate this skill whenever:
- Running pre-release or continuous security audits.
- Checking for accidentally committed tokens, API keys, private certificates, or database credentials.
- Auditing dependencies for reported CVE vulnerabilities.
- Reviewing sensitive user data flows, JWT authorization, password hashing, and session management.

## 3. Prerequisites
- Read access to codebase files and lockfiles (`package-lock.json`, `poetry.lock`, etc.).

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `auditScope` | `string` | Scope (`full-repo`, `dependencies`, `secrets`, `auth`). |
| `severityThreshold` | `string` | Minimum severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). |
| `secretsScanningRegexes` | `array` | Custom credential regexes. |

## 5. Procedure (Step-by-Step)
1. **Secrets & Credential Exposure Scan**: Scan working tree and commit diffs for entropy and key patterns.
2. **Dependency Supply-Chain CVE Audit**: Run lockfile checks against vulnerability databases.
3. **OWASP Top 10 Inspection**: Verify parameterized queries, context-aware HTML escaping, and path sanitization.
4. **Auth Boundary Audit**: Confirm protected endpoints validate tokens and permissions before execution.
5. **Hardening Remediation**: Generate minimally invasive security patches and configuration hardening.

## 6. Expected Outputs
- Detailed vulnerability report with severity tags and remediation code.
- Pre-commit hook configuration for ongoing secret leakage prevention.

## 7. Applicable Approval Gates
- **G1 (Requirements)**: Security non-functional requirements.
- **G2 (Architecture)**: Threat model and security boundaries.
- **G4 (Implementation)**: Verification of secure coding practices.
- **G5 (Quality)**: Zero critical/high vulnerability certification.

## 8. Failure and Recovery Strategies
- False positives in test mocks are handled with explicit exclusion comments. Breaking dependency updates are encapsulated behind adapters.

## 9. Verification Criteria
- Zero leaked credentials or unmasked tokens.
- Zero known high/critical CVEs in production dependencies.
- SQL queries and shell executions are parameterized.

## 10. Relevant Contracts and Memory Records
- `contracts/architecture/contract.json`
- `contracts/quality/contract.json`
- `durableKnowledge.architecturalDecisions`
- `backlogAndHistory.technicalDebt`
