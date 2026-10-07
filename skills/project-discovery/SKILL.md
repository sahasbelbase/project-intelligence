---
skillId: project-discovery
name: Project Discovery
purpose: Inspect the development environment, baseline repository state, tools, and constraints to establish the project charter and G0 contract.
whenToUse:
  - Initializing a greenfield project without an established Project Intelligence configuration
  - Bootstrapping framework governance in an empty repository or workspace
  - Establishing the project charter, mission statement, stakeholders, and initial constraints before requirements definition
prerequisites:
  - Local file system read access to workspace root
  - Command execution capability for environment inspection (Git CLI, language runtimes)
  - Access to core schemas in core/schemas/ for contract initialization
inputs:
  - name: workspaceRoot
    type: string
    description: Absolute path to repository or project workspace root directory
  - name: userBrief
    type: string
    description: User intent, project description, goals, and initial constraints provided at kickoff
  - name: targetPlatforms
    type: array
    description: List of AI coding platforms to support (e.g., Claude Code, Copilot, Codex, Antigravity)
procedure:
  - stepNumber: 1
    title: Environment and Toolchain Inspection
    action: Query host OS, shell environment, installed language runtimes (python, node, go, rust), package managers, and container runtimes. Document toolchain availability.
  - stepNumber: 2
    title: Git Working Tree Inspection
    action: Check git repository status using 'git status --porcelain' and 'git log -n 5'. Verify if the directory is a git repo, clean branch baseline, and capture current HEAD commit hash.
  - stepNumber: 3
    title: Scope and Boundaries Formulation
    action: Analyze userBrief against toolchain capabilities. Explicitly define inScope features and outOfScope boundaries to prevent premature scope creep.
  - stepNumber: 4
    title: Constraints and Assumptions Cataloging
    action: Catalog technical, organizational, and security constraints (e.g., local-first privacy, zero external runtime dependencies, target deployment environments).
  - stepNumber: 5
    title: Project Contract Generation
    action: Synthesize findings into contracts/project/contract.json adhering to core/schemas/project-contract.schema.json with initial status UNDER_REVIEW and lifecycleGate G0.
  - stepNumber: 6
    title: Memory Initialization
    action: Initialize memory/state.json with schemaVersion, lastReconciledCommit set to HEAD, durableKnowledge goals, and executionState pointing to G0.
expectedOutputs:
  - contracts/project/contract.json adhering to project-contract.schema.json
  - memory/state.json initialized with baseline goals and execution state G0
  - Environment discovery summary detailing runtime versions and git HEAD status
applicableApprovalGates:
  - G0
failureAndRecovery:
  potentialFailures:
    - Missing git binary or repository not initialized
    - Conflicting or ambiguous user brief instructions
    - Write permissions failure when creating contracts directory
  recoveryStrategy: If git is missing, fall back to directory inspection and prompt user to initialize git. For ambiguous scope, halt at G0 and request user clarification before contract signing. If permissions fail, verify directory ownership.
verificationCriteria:
  - contracts/project/contract.json passes validation against core/schemas/project-contract.schema.json
  - memory/state.json passes validation against core/schemas/memory.schema.json
  - Working tree status is captured and verified clean or noted with uncommitted changes
  - In-scope and out-of-scope lists contain non-empty, actionable entries
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
  memoryRecords:
    - durableKnowledge.goals
    - executionState.currentGate
    - executionState.activePhase
    - lastReconciledCommit
---

# Project Discovery (`project-discovery`)

## 1. Purpose
The `project-discovery` skill provides a deterministic, rigorous methodology to inspect the project host environment, inspect repository git state, analyze user intent, and establish the canonical **Project Contract** (`contracts/project/contract.json`) along with initial durable memory (`memory/state.json`). It guarantees that no development begins on ungrounded assumptions, conflicting goals, or undiscovered environment bottlenecks.

## 2. When to Use It
Activate this skill in the following circumstances:
- **Greenfield Project Initiation**: Bootstrapping an empty directory or new repository.
- **Framework Initialization**: Establishing Project Intelligence governance, schemas, and lifecycle gates in an existing empty folder.
- **Scope & Charter Formalization**: When user goals are stated casually or ambiguously, and require translation into structured in-scope and out-of-scope contractual commitments.

## 3. Prerequisites
Before invoking this skill, ensure the following capabilities and assets are available:
- Local read and write access to the workspace root directory.
- Shell access to execute inspection commands (`git`, `python --version`, `node -v`, etc.).
- The schema files located in `core/schemas/`, specifically `project-contract.schema.json` and `memory.schema.json`.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `workspaceRoot` | `string` | Absolute path to the repository root directory. |
| `userBrief` | `string` | The user's explicit prompt, mission statement, or kickoff intent. |
| `targetPlatforms` | `array` | The AI platforms targeted for orchestration (Claude Code, GitHub Copilot, Codex, Antigravity). |

## 5. Procedure (Step-by-Step)
1. **Host Environment & Toolchain Inspection**:
   - Detect host operating system (Windows, Linux, macOS) and active shell (PowerShell, Bash, Zsh).
   - Enumerate available runtimes, compilers, and package managers:
     - Python (`python --version`, `python3 --version`, `pip --version`)
     - Node.js & JavaScript (`node -v`, `npm -v`, `pnpm -v`, `yarn -v`, `bun -v`)
     - Go, Rust, Java, or C/C++ toolchains where applicable.
   - Record discovered tool versions in the discovery log.

2. **Git Working Tree Inspection**:
   - Execute `git status --porcelain` to determine if a Git repository exists and whether uncommitted changes are present.
   - Run `git rev-parse HEAD` and `git log -n 5 --oneline` to establish the baseline commit hash.
   - If the repository is uninitialized, execute `git init` or record the uninitialized state and advise the user.

3. **Scope & Boundaries Formulation**:
   - Parse the `userBrief` to identify primary deliverables, core functionality, and user goals.
   - Explicitly define `inScope` items as measurable, testable objectives.
   - Explicitly define `outOfScope` items to eliminate ambiguity and prevent model hallucinations or premature feature bloat.

4. **Cataloging Constraints & Assumptions**:
   - Document technical constraints (e.g., zero external dependencies, minimum runtime versions).
   - Document security constraints (e.g., local-first data privacy, secret leakage prevention).
   - Document organizational constraints (e.g., preservation of existing file naming conventions).

5. **Project Contract Synthesis**:
   - Assemble all gathered information into `contracts/project/contract.json` complying with `core/schemas/project-contract.schema.json`.
   - Set envelope status to `UNDER_REVIEW` and lifecycleGate to `G0`.
   - Include clear traceability IDs (`proj-contract-001`).

6. **Memory Initialization**:
   - Generate `memory/state.json` matching `core/schemas/memory.schema.json`.
   - Populate `durableKnowledge.goals` from the project mission statement.
   - Record `executionState.currentGate` as `G0` and `lastReconciledCommit` as the current HEAD hash.

## 6. Expected Outputs
- `contracts/project/contract.json`: Validated canonical project contract.
- `memory/state.json`: Initialized project memory file capturing baseline goals and execution state.
- Structured execution summary presented to the user detailing discovered runtimes and Git status.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G0 (Discovery Gate)**: This skill is the primary engine for satisfying Gate G0 entry and exit criteria. Gate G0 requires human approval before advancing to Gate G1 (Requirements).

## 8. Failure and Recovery Behavior
- **Uninitialized Git Repository**: If `git status` fails, prompt the user or run `git init` if permitted, setting `lastReconciledCommit` to `"INITIAL_UNCOMMITTED"`.
- **Ambiguous or Contradictory Requirements**: Halt contract finalization at `UNDER_REVIEW`. Generate specific clarifying questions for the human architect before marking G0 approved.
- **Permission Errors**: If writing to `contracts/` fails, check directory file permissions and verify user execution context.

## 9. Verification Criteria
- `contracts/project/contract.json` validates with zero errors against `core/schemas/project-contract.schema.json`.
- `memory/state.json` validates with zero errors against `core/schemas/memory.schema.json`.
- Both `inScope` and `outOfScope` contain non-trivial, distinct statements.
- `lastReconciledCommit` accurately matches git HEAD or documented initial baseline.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json`
- **Memory Records**:
  - `durableKnowledge.goals`
  - `executionState.currentGate`
  - `executionState.activePhase`
  - `lastReconciledCommit`
