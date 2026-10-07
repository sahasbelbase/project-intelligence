# Quality Profile: Standard Application (`STANDARD`)

## 1. Overview and Intent
The **Standard Application** profile is the default quality profile for production software development within the Project Intelligence framework. It balances delivery speed with rigorous software engineering discipline, making it suitable for production web applications, backend microservices, CLI developer tools, and internal infrastructure.

---

## 2. Threshold Matrix and Requirements

| Quality Dimension | Requirement | Threshold / Policy |
|---|---|---|
| **Code Coverage** | Mandatory | **>= 70%** line coverage across modified code |
| **Linting & Formatting** | Mandatory | Clean run with zero errors; warnings addressed |
| **Unit & Integration Tests** | Mandatory | Complete suite covering happy paths and common edge cases |
| **Security Vulnerability Scan** | Mandatory | Zero High or Critical CVEs in dependencies |
| **Accessibility (a11y) Audit** | Optional | Recommended for public-facing UIs |
| **Independent Review (G5)** | Mandatory | Strict review against requirements contract |
| **Mandatory Baseline Rules** | Non-Negotiable | BL-001 through BL-007 enforced without exception |

---

## 3. Engineering Guidelines for Standard Applications

### 3.1 Code Quality and Maintainability
- **Type Safety**: Enforce static type checking where language supports it (e.g., Python type hints with `mypy`, TypeScript strict mode). Function signatures must declare argument and return types.
- **Error Handling**: Follow structured exception handling. Catch specific exception classes; log meaningful contextual error messages; never swallow errors silently (BL-004).
- **Separation of Concerns**: Separate business logic from data access and presentation layers. Avoid monolithic files exceeding 500 lines of code.

### 3.2 Testing Standards
- **Minimum 70% Coverage**: Every pull request or workstream task must demonstrate at least 70% automated test coverage over new or modified code.
- **Edge Cases**: Unit tests must exercise boundary values (e.g., empty arrays, null/None parameters, negative numbers, maximum string lengths).
- **Test Isolation**: Unit tests must not depend on external live network services; mock network boundaries using local test fixtures.

### 3.3 Security & Dependency Management
- **Automated Dependency Audit**: Execute package scanners (`pip-audit`, `npm audit`, `cargo audit`) during verification.
- **Zero High/Critical Vulnerabilities**: The build must fail if any dependency contains an unpatched high or critical CVE.
- **Secret Management**: All configuration secrets must be sourced from environment variables; zero credentials in git history (BL-007).
