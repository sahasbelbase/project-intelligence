---
skillId: documentation-and-handoff
name: documentation-and-handoff
description: "Generate comprehensive developer guides, release contracts, changelogs, operational runbooks, and synchronized memory states to clear G6."
purpose: Generate comprehensive developer guides, release contracts, changelogs, operational runbooks, and synchronized memory states to clear G6.
whenToUse:
  - Finalizing a release, milestone, or sprint deliverable (Gate G6 entry)
  - Preparing the repository for clean handoff to human engineers or next AI agent sessions
  - Writing or updating README.md, CHANGELOG.md, and operational runbooks
  - Synchronizing Git-aware memory (memory/state.json) with current HEAD commit hash
prerequisites:
  - Gate G5 approved (contracts/quality/contract.json in APPROVED status)
  - Clean working tree or ready-to-commit staging area
  - Access to release-contract.schema.json in core/schemas/
inputs:
  - name: releaseVersion
    type: string
    description: Semantic version of the release (e.g., 1.0.0, 0.1.0)
  - name: verifiedDeliverables
    type: array
    description: List of completed and verified features, skills, contracts, or modules
  - name: knownLimitations
    type: array
    description: Documented exceptions, temporary constraints, or deferred backlog items
procedure:
  - stepNumber: 1
    title: Release Deliverables and Artifact Inventory
    action: Enumerate all verified source files, schemas, tests, and contracts produced during the lifecycle. Confirm completeness against the project contract.
  - stepNumber: 2
    title: Changelog and Version Update
    action: Generate or update CHANGELOG.md following Keep a Changelog standard (Added, Changed, Deprecated, Removed, Fixed, Security) and update semver tags.
  - stepNumber: 3
    title: Developer Guides and Usage Documentation
    action: Author or update user documentation in docs/usage/ and root README.md with clear quick-start commands, configuration options, and troubleshooting steps.
  - stepNumber: 4
    title: Release Contract Assembly
    action: Synthesize data into contracts/release/contract.json conforming to core/schemas/release-contract.schema.json with status APPROVED.
  - stepNumber: 5
    title: Git-Aware Memory Reconciliation
    action: Query current git commit hash. Reconcile memory/state.json, updating lastReconciledCommit, setting executionState.currentGate to G6, and clearing activeTasks.
  - stepNumber: 6
    title: Final Handoff Summary Presentation
    action: Produce an executive summary detailing verified deliverables, known limitations, recommended next steps, and instructions for next agent session.
expectedOutputs:
  - contracts/release/contract.json adhering to release-contract.schema.json
  - Updated README.md, CHANGELOG.md, and documentation in docs/
  - Synchronized memory/state.json reflecting Gate G6 completion
applicableApprovalGates:
  - G6
failureAndRecovery:
  potentialFailures:
    - Discrepancy between declared deliverables and actual files in repository
    - Memory state commit hash out of sync with git HEAD
    - Missing documentation for newly exposed CLI commands or interfaces
  recoveryStrategy: Run git status and file check to reconcile deliverables against physical disk. Update lastReconciledCommit to git rev-parse HEAD. Generate missing API documentation before final handoff.
verificationCriteria:
  - contracts/release/contract.json passes validation against core/schemas/release-contract.schema.json
  - README.md and CHANGELOG.md accurately reflect the released version and features
  - memory/state.json lastReconciledCommit matches git HEAD
  - All known limitations are documented transparently without omissions
relevantContractsAndMemory:
  contracts:
    - contracts/release/contract.json
  memoryRecords:
    - lastReconciledCommit
    - durableKnowledge
    - executionState
    - backlogAndHistory
---

# Documentation and Handoff (`documentation-and-handoff`)

## 1. Purpose
The `documentation-and-handoff` skill orchestrates the final closure, formal release contracting, and knowledge transfer for a project or milestone. It guarantees that the codebase is completely documented, human-readable, auditable, and that Git-aware durable memory (`memory/state.json`) is precisely synchronized with the repository's git commit graph before session completion. It is the core execution driver for **Gate G6 (Release / Handoff)**.

## 2. When to Use It
Activate this skill in the following scenarios:
- Concluding a development phase, sprint, or version release after Gate G5 approval.
- Writing user guides, developer onboarding documentation, and API references.
- Updating `CHANGELOG.md` and repository `README.md`.
- Formulating `contracts/release/contract.json` to complete Gate G6.
- Synchronizing memory state for subsequent human or AI agent sessions.

## 3. Prerequisites
- Gate G5 is formally approved (`contracts/quality/contract.json` in `APPROVED` status).
- Release contract schema in `core/schemas/release-contract.schema.json` is available.
- All code and test files are committed or staged.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `releaseVersion` | `string` | Target Semantic Version (`1.0.0`, `0.2.0`). |
| `verifiedDeliverables` | `array` | Complete list of tested features, schemas, and components. |
| `knownLimitations` | `array` | Transparent list of deferred items, known constraints, or caveats. |

## 5. Procedure (Step-by-Step)
1. **Deliverables Reconciliation & Audit**:
   - Query the repository file system and git tree to verify that every item declared in `verifiedDeliverables` exists on disk.
   - Verify that all test suites pass against the release branch.

2. **Changelog & Semantic Versioning**:
   - Update `CHANGELOG.md` conforming to Keep a Changelog (1.1.0) standards:
     - Group changes under: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
     - Link the release version to the corresponding commit or git tag.

3. **User Guides & Architectural Handoff**:
   - Update repository `README.md` to reflect current capabilities, prerequisites, quick-start CLI instructions, and architecture links.
   - Author or update technical reference guides in `docs/usage/` and `docs/architecture/`.

4. **Release Contract Assembly**:
   - Assemble all verification data, version tags, deliverables list, and known limitations into `contracts/release/contract.json`.
   - Validate against `core/schemas/release-contract.schema.json`.
   - Set status to `APPROVED` upon human or orchestrator sign-off.

5. **Git-Aware Memory Synchronization**:
   - Run `git rev-parse HEAD` to capture the final commit hash.
   - Update `memory/state.json`:
     - Update `lastReconciledCommit` to the captured hash.
     - Set `lastReconciledAt` to ISO 8601 UTC timestamp.
     - Set `executionState.currentGate` to `G6`.
     - Clear `executionState.activeTasks` and move remaining items to completed.

6. **Executive Handoff Summary**:
   - Render a structured summary for the user covering:
     - Version released and commit hash.
     - Summary of verified features and test metrics.
     - Known limitations and deferred backlog items.
     - Clear instructions for the next agent session to resume work smoothly.

## 6. Expected Outputs
- `contracts/release/contract.json`: Validated canonical release contract.
- Updated `README.md`, `CHANGELOG.md`, and technical documentation.
- Synchronized `memory/state.json` matching repository HEAD.
- Executive handoff summary presented in chat.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G6 (Release or Handoff)**: Primary skill responsible for fulfilling Gate G6 entry and exit criteria.

## 8. Failure and Recovery Behavior
- **Deliverable Missing from Disk**: Halt release contract generation; verify git tree or restore missing file from implementation branch.
- **Commit Hash Desynchronization**: Execute `git log -1` and overwrite `lastReconciledCommit` with true HEAD hash.
- **Undocumented Breaking Change**: Add immediate entry in `CHANGELOG.md` under `Changed` with migration instructions.

## 9. Verification Criteria
- `contracts/release/contract.json` validates against `core/schemas/release-contract.schema.json`.
- `memory/state.json` passes validation against `core/schemas/memory.schema.json`.
- `lastReconciledCommit` matches `git rev-parse HEAD`.
- All documentation files are free of broken internal links or stale placeholders.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/release/contract.json`
- **Memory Records**:
  - `lastReconciledCommit`
  - `durableKnowledge`
  - `executionState`
  - `backlogAndHistory`
