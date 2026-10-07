# Task Instructions: Discovery Task (`discovery-task`)

## 1. Role and Objective
When assigned a **Discovery Task** (typically during Gate G0 or G1 initialization), the agent acts as a systems analyst and repository scout. The primary objective is to inspect the physical environment, analyze existing code and configurations, clarify user objectives, and establish the project charter and baseline contracts without mutating application code.

---

## 2. Pre-Flight Protocol

Before formulating contracts or recommending technical choices, execute the following non-destructive reconnaissance sequence:

1. **Host Environment & Toolchain Inspection**:
   - Query operating system, CPU architecture, and active shell.
   - Run version queries for available language runtimes:
     - Python: `python --version` or `python3 --version`
     - Node.js / JavaScript: `node -v`, `npm -v`, `pnpm -v`
     - Additional compilers/tools: `git --version`, `docker --version`, `go version`, `cargo --version`
   - Document any missing tools that will be required downstream.

2. **Git Working Tree Inspection**:
   - Run `git status --porcelain` to check for uncommitted changes or untracked files.
   - Run `git log -n 5 --oneline` and `git rev-parse HEAD` to capture baseline commit.
   - **Hygiene Rule**: If uncommitted changes exist, document them. Never discard user changes.

3. **Existing Repository Reconnaissance (Brownfield)**:
   - If pre-existing source files are present, locate package manifests (`pyproject.toml`, `package.json`, `Cargo.toml`).
   - Identify existing formatters and linters (`.eslintrc`, `ruff.toml`, `prettierrc`).
   - Identify existing test runners and CI workflows (`.github/workflows/`, `Makefile`).
   - Ingest discovered rules into `memory/state.json` under `durableKnowledge.codingConventions`.

---

## 3. Scope Definition & Boundary Setting

1. **Clarify Intent**:
   - Parse user prompt and requirements.
   - Distill the core mission statement into 1-2 concise sentences.
2. **Explicit Scope Partitioning**:
   - Construct a non-empty `inScope` array containing concrete, testable deliverables.
   - Construct an explicit `outOfScope` array containing features that are explicitly deferred, unapproved, or non-goals.
   - *Rationale*: Clearly defining what is out-of-scope prevents model hallucinations and scope expansion during later implementation phases.
3. **Constraints and Assumptions**:
   - Document technical, organizational, and security constraints (e.g. zero external runtime dependencies, local-first data privacy).

---

## 4. Contract Formulation & Handoff

1. **Generate Project Contract**:
   - Populate `contracts/project/contract.json` adhering to `core/schemas/project-contract.schema.json`.
   - Set status to `UNDER_REVIEW` and lifecycleGate to `G0`.
2. **Initialize Project Memory**:
   - Populate `memory/state.json` adhering to `core/schemas/memory.schema.json`.
   - Set `lastReconciledCommit` to the current git HEAD hash.
   - Set `executionState.currentGate` to `G0` and populate `durableKnowledge.goals`.
3. **Submit for Human Approval**:
   - Present a clear, bulleted discovery summary to the human architect.
   - Gate G0 requires explicit human approval before transition to Gate G1.

---

## 5. Anti-Patterns to Avoid During Discovery
- **Premature Implementation**: Never write application code, generate UI components, or modify business logic during discovery.
- **Assumed Tooling**: Never assume a runtime or package manager is installed without running a verification command.
- **Destructive File Operations**: Never run `git reset`, `git checkout -f`, or delete directories during discovery.
- **Vague Scope**: Never leave `inScope` or `outOfScope` empty or generic (e.g. avoiding "build the app" in favor of "implement local JWT authentication module").
