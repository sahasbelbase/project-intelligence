---
skillId: existing-project-analysis
name: existing-project-analysis
description: "Perform deep, non-destructive reconnaissance on an existing codebase to detect architecture, build systems, conventions, tech debt, and drift."
purpose: Perform deep, non-destructive reconnaissance on an existing codebase to detect architecture, build systems, conventions, tech debt, and drift.
whenToUse:
  - Onboarding an established repository into Project Intelligence governance
  - Detecting architectural patterns, conventions, and existing dependencies prior to feature work
  - Auditing technical debt, uncommitted changes, or state drift in legacy codebases
  - Evaluating test suite maturity and build pipeline commands on existing projects
prerequisites:
  - Existing codebase with filesystem read access
  - Installed Git CLI with repository history access
  - Read access to existing configuration and package manifests
inputs:
  - name: projectRoot
    type: string
    description: Path to the existing repository root
  - name: deepScanDepth
    type: integer
    description: Maximum directory traversal depth for file tree mapping
  - name: excludePatterns
    type: array
    description: Directory or file patterns to ignore during analysis (e.g., node_modules, .git, venv)
procedure:
  - stepNumber: 1
    title: Directory Tree and Manifest Scanning
    action: Enumerate top-level directory structure and parse key build/package manifests (package.json, pyproject.toml, go.mod, Cargo.toml, pom.xml, CMakeLists.txt).
  - stepNumber: 2
    title: Coding Convention and Linter Detection
    action: Identify formatting, linting, and style configuration files (.eslintrc, ruff.toml, prettierrc, tsconfig.json). Extract existing coding conventions.
  - stepNumber: 3
    title: Build, Test, and CI Pipeline Analysis
    action: Locate test suites and CI workflows (.github/workflows, Jenkinsfile, Makefile, docker-compose.yml). Identify how tests are invoked and execution requirements.
  - stepNumber: 4
    title: Git History and Hotspot Mapping
    action: Inspect git log history to detect frequently modified files, recent author commits, unmerged branches, and existing architectural documentation (ADRs, docs/).
  - stepNumber: 5
    title: Technical Debt and Anti-Pattern Audit
    action: Identify unresolved TODO/FIXME markers, deprecated library usages, missing test coverage areas, and obvious architectural smells.
  - stepNumber: 6
    title: Memory State Ingestion
    action: Populate memory/state.json with durableKnowledge (discovered conventions, architectural decisions, domain vocabulary) and backlogAndHistory (technical debt).
expectedOutputs:
  - Comprehensive architecture and convention reconnaissance report
  - Updated memory/state.json with extracted codingConventions and technicalDebt entries
  - Baseline requirements and constraints documentation for contract formulation
applicableApprovalGates:
  - G0
  - G1
failureAndRecovery:
  potentialFailures:
    - Repository too massive leading to timeout during full traversal
    - Multiple conflicting build tools or monorepo subprojects
    - Corrupted or missing git history
  recoveryStrategy: Apply targeted subtree scanning focusing on src/ or core packages. If monorepo detected, analyze root manifest first, then partition analysis into distinct sub-packages. For shallow git clones, report limited history in findings.
verificationCriteria:
  - All detected build and test commands are validated by checking corresponding config files
  - Existing conventions are documented in memory without overwriting user rules
  - No files outside memory/ or reports are modified during analysis (strictly non-destructive)
  - Identified technical debt items are tagged with severity and location
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/requirements/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - durableKnowledge.codingConventions
    - durableKnowledge.domainVocabulary
    - backlogAndHistory.technicalDebt
---

# Existing Project Analysis (`existing-project-analysis`)

## 1. Purpose
The `existing-project-analysis` skill enables deep, non-destructive reconnaissance over an inherited, brownfield, or legacy codebase. Its objective is to extract ground-truth architectural realities, dependency graphs, formatting conventions, build/test pipelines, and existing technical debt without making unauthorized changes to the existing code.

## 2. When to Use It
Activate this skill whenever:
- An established repository is being onboarded into Project Intelligence.
- An AI agent begins a new session in a project with pre-existing source files.
- Refactoring, modernization, or feature extension is planned on existing systems.
- Drift between existing documentation and actual code implementation must be audited.

## 3. Prerequisites
- Read access to the repository directory tree.
- Git CLI availability with access to commit history and branches.
- Read access to package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.).

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `projectRoot` | `string` | Absolute path to the repository being analyzed. |
| `deepScanDepth` | `integer` | Directory traversal depth limit (default: 4). |
| `excludePatterns` | `array` | Glob patterns to ignore (`node_modules`, `dist`, `.venv`, `.git`). |

## 5. Procedure (Step-by-Step)
1. **Directory Structure & Manifest Scanning**:
   - Traverse the root directory up to `deepScanDepth`.
   - Identify language ecosystem by locating package files (`pyproject.toml`, `setup.py`, `package.json`, `go.mod`, `pom.xml`, `Cargo.toml`).
   - Extract declared dependencies, production libraries, and development tools.

2. **Coding Conventions & Linter Discovery**:
   - Detect active code linters and formatters (`.eslintrc`, `.prettierrc`, `ruff.toml`, `flake8`, `checkstyle.xml`, `rustfmt.toml`).
   - Extract rules for indentation, quote styles, import sorting, and strict typing modes.
   - Record discovered rules as non-negotiable coding conventions in durable memory.

3. **Build, Test, and CI Pipeline Analysis**:
   - Scan for continuous integration definitions (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`).
   - Locate test directories (`tests/`, `__tests__/`, `spec/`) and test frameworks (`pytest`, `jest`, `vitest`, `go test`).
   - Determine exact CLI commands for running test suites and linters.

4. **Git History & Churn Analysis**:
   - Query `git log --stat -n 20` to discover active feature branches, top contributors, and high-churn code hotspots.
   - Look for existing Architecture Decision Records (`docs/adr/`, `decisions/`).

5. **Technical Debt & Anti-Pattern Audit**:
   - Grep for markers such as `TODO`, `FIXME`, `HACK`, `DEPRECATED`.
   - Audit legacy files for broken patterns, missing error handling, or dead code paths.

6. **Durable Memory Ingestion**:
   - Store discovered conventions in `memory/state.json` under `durableKnowledge.codingConventions`.
   - Record discovered technical debt items into `backlogAndHistory.technicalDebt`.

## 6. Expected Outputs
- Detailed Brownfield Analysis Report documenting language ecosystem, dependencies, build commands, and conventions.
- Updated `memory/state.json` reflecting the existing project realities.
- Validated inputs for formulation of `contracts/project/contract.json` (Gate G0) or `contracts/requirements/contract.json` (Gate G1).

## 7. Applicable Approval Gates (G0-G6)
- **Gate G0 (Discovery)**: Supplies environmental baseline and existing repository context.
- **Gate G1 (Requirements)**: Establishes existing system capabilities and constraints.

## 8. Failure and Recovery Behavior
- **Excessive Traversal Size**: If node_modules or large build folders slow traversal, enforce strict exclude filters.
- **Monorepo Complexity**: If multiple package manifests are found at varying subpaths, partition the analysis per workspace package.
- **Missing or Incomplete Manifests**: Cross-reference source file headers, imports, and lockfiles to reconstruct dependencies.

## 9. Verification Criteria
- Analysis execution is strictly read-only; no existing application code files are mutated.
- Build and test commands documented in the output correspond to verifiable configuration files in the repository.
- Identified conventions are stored in durable knowledge without overriding user-specified project charter rules.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json`
  - `contracts/requirements/contract.json`
- **Memory Records**:
  - `durableKnowledge.architecturalDecisions`
  - `durableKnowledge.codingConventions`
  - `durableKnowledge.domainVocabulary`
  - `backlogAndHistory.technicalDebt`
