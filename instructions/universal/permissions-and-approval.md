# Universal Instructions — Permissions, Safety, and Approval Gates

## 1. Operational Purpose & Precedence

This document defines the universal permission matrix, safety boundaries, and human approval gates governing all AI agent operations in the Project Intelligence framework.

**Core Mandate**: Agents must operate under the Principle of Least Privilege. Tool capabilities and filesystem access are granted strictly according to assigned role boundaries. Irreversible or destructive operations require explicit human authorization.

---

## 2. Role-Based Permission Matrix

Every agent persona operates within declared tool permissions:

| Persona Role | File System Read | File System Write | Shell Command Execution | Web Search | Permitted Write Targets |
|---|---|---|---|---|---|
| **Orchestrator** | Full Read | Restricted | Restricted | Allowed | `contracts/**`, `memory/**` |
| **Discovery** | Full Read | Read-Only | Denied | Allowed | None (Read-only analysis) |
| **Architecture** | Full Read | Restricted | Denied | Denied | `contracts/architecture/**`, `docs/decisions/**` |
| **Design** | Full Read | Restricted | Denied | Allowed | `contracts/design/**`, `design/**` |
| **Planning** | Full Read | Restricted | Denied | Denied | `contracts/implementation/**`, `memory/backlog.json` |
| **Implementation** | Full Read | Scoped Write | Sandboxed Execution | Denied | Assigned task files only |
| **Verification** | Full Read | Scoped Write | Sandboxed Execution | Denied | `tests/**`, `validation/**` |
| **Independent Review**| Full Read | Read-Only | Denied | Denied | `docs/validation/**` (Audit reports only) |
| **Documentation** | Full Read | Scoped Write | Sandboxed Execution | Denied | `docs/**`, `README.md`, `CHANGELOG.md` |

---

## 3. Destructive Command Guardrails (PA-001 through PA-005)

### PA-001: Prohibition of Destructive Git Mutations
Agents are strictly forbidden from executing destructive Git operations, including but not limited to:
- `git reset --hard`
- `git clean -fd` or `git clean -f`
- `git push --force` or `git push --delete`
- `git checkout -- .` (wiping working tree without stash)
- *Required Alternative*: Before making changes, check `git status --porcelain`. Preserve ambiguous state with non-destructive stashes (`git stash create`).

### PA-002: Prohibition of Broad Recursive Deletions
Commands invoking `rm -rf` or broad glob deletions (`rm -f *`, `shutil.rmtree`) targeting top-level, source, or repository root directories are strictly prohibited. File removals must be targeted to explicit, individual file paths within assigned boundaries.

### PA-003: Irreversible Data Destruction Safeguards
Agents must obtain explicit user confirmation before executing:
- SQL statements with `DROP TABLE`, `DROP DATABASE`, `TRUNCATE`, or `DELETE` without `WHERE` clauses.
- Storage bucket destruction commands (`gsutil rm -r`, `aws s3 rm --recursive`).
- Cloud project or instance termination commands (`gcloud projects delete`).

### PA-004: Strict Secret & Credential Quarantine
In accordance with Rule BL-007:
- Agents must never write private keys, API tokens, passwords, database credentials, or secret connection strings into repository files, contracts, commit messages, or memory files.
- Credentials must be sourced solely via environment variables.

### PA-005: Sandboxed Command Execution Baseline
All command executions must run within the standard execution sandbox by default. Bypassing sandbox mode requires prior evaluation, minimal command scope, and explicit human consent.

---

## 4. Mandatory Human Approval Gates

The following events halt autonomous execution and require human sign-off:
1. **Gate G2 Exemption**: Formally bypassing visual/domain design requires explicit human approval with documented rationale.
2. **Gate G6 Release Sign-off**: Deploying deliverables to production or tagging public releases.
3. **Introduction of New External Dependencies**: Adding any external package or third-party library to project manifests.
4. **Substantive Scope Modification**: Altering `contracts/requirements/contract.json` after Gate G1 approval.
5. **Council Consensus Deadlock**: Irreconcilable council disputes where no supermajority is reached and critical risks remain contested.
