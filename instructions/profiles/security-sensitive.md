# Quality Profile: Security-Sensitive (`SECURITY_SENSITIVE`)

## 1. Overview and Intent
The **Security-Sensitive** profile is mandatory for systems handling authentication, authorization, cryptographic operations, financial transactions, Personally Identifiable Information (PII), or security-critical kernel/network protocols. It enforces defense-in-depth, static application security testing (SAST), dependency supply chain provenance, and comprehensive threat boundary validation.

---

## 2. Threshold Matrix and Requirements

| Quality Dimension | Requirement | Threshold / Policy |
|---|---|---|
| **Code Coverage** | Mandatory | **>= 90%** line coverage across all modules |
| **Linting & SAST** | Mandatory | Zero security findings from SAST scanners (e.g. bandit, semgrep) |
| **Unit & Fuzz Tests** | Mandatory | Cryptographic, boundary, and negative input testing |
| **Dependency Supply Chain Audit**| Mandatory | Zero known CVEs; locked dependency hash manifests |
| **Accessibility (a11y) Audit** | Optional | Required only if product has user interfaces |
| **Independent Review (G5)** | Mandatory | Security specialist review with STRIDE threat verification |
| **Mandatory Baseline Rules** | Non-Negotiable | BL-001 through BL-007 enforced without exception |

---

## 3. Engineering Guidelines for Security-Sensitive Systems

### 3.1 Defensive Architecture and Principle of Least Privilege
- **Zero Trust Across Boundaries**: Treat all external inputs (HTTP requests, files, environmental parameters, RPC payloads) as potentially hostile.
- **Strict Input Validation**: Validate data types, string lengths, allowed character sets, and schema formats using strict whitelists before processing.
- **Fail-Secure Defaults**: In any error or failure state, the system must fail safe (e.g., access denied, connection closed, transaction rolled back).

### 3.2 Cryptographic Discipline & Secret Management
- **Never Implement Custom Cryptography**: Use established, audited cryptographic libraries (e.g., `cryptography` in Python, Web Crypto API, OpenSSL).
- **Constant-Time Comparison**: Protect against timing attacks when comparing hashes, tokens, or MACs (e.g., `hmac.compare_digest`).
- **Zero Secret Exposure (BL-007)**: API keys, tokens, and certificates must never appear in source code, logs, heap dumps, or error messages.

### 3.3 Static Analysis & Supply Chain Verification
- **Mandatory SAST Scanning**: Execute security linters (e.g. `bandit -r .`, `semgrep --config=p/security-audit`, `eslint-plugin-security`). Zero warnings permitted.
- **Lockfile & Hash Pinning**: All package manifests must use pinned lockfiles with cryptographic SHA-256 integrity hashes (`poetry.lock`, `package-lock.json`).

### 3.4 Audit Logging and Tamper Resistance
- All security-relevant events (authentication attempts, permission changes, administrative access, cryptographic operations) must emit structured audit logs with timestamps and actor IDs.
- Audit logs must be scrubbed of passwords, bearer tokens, and sensitive customer data.
