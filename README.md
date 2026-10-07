# Project Intelligence

> **A portable, local-first AI Project Orchestrator framework establishing a deterministic engineering lifecycle, shared contracts, git-aware memory, anti-slop quality gates, and multi-agent coordination across modern AI coding environments.**

---

## Table of Contents
1. [Overview and Mission](#overview-and-mission)
2. [Core Principles](#core-principles)
3. [Architecture and Repository Layout](#architecture-and-repository-layout)
4. [The 7 Lifecycle Gates (G0–G6)](#the-7-lifecycle-gates-g0g6)
5. [Anti-Slop Quality Engine and Profiles](#anti-slop-quality-engine-and-profiles)
6. [3-Tier Git-Aware Memory Architecture](#3-tier-git-aware-memory-architecture)
7. [Canonical Skills and Logical Agents](#canonical-skills-and-logical-agents)
8. [Cross-Platform Adapters and Degradation Rules](#cross-platform-adapters-and-degradation-rules)
9. [Quick Start and Validation](#quick-start-and-validation)
10. [Documentation Sitemap](#documentation-sitemap)

---

## 1. Overview and Mission

AI coding assistants frequently suffer from context drift, hallucinated completions, lack of requirements discipline, premature coding without design, and session amnesia. When transitioning between AI platforms (such as Claude Code, GitHub Copilot, OpenAI Codex, or terminal-based agents), context is lost and engineering standards degrade.

**Project Intelligence** solves this by establishing a portable, local-first engineering foundation. It does not depend on proprietary cloud orchestrators or third-party paid runtimes. It uses standardized JSON schemas (Draft-07), signed contract envelopes, deterministic finite state machines, and Git-aware drift reconciliation engines to govern AI coding agents with the same rigor expected of senior human engineering leads.

---

## 2. Core Principles

- **Local-First & Zero Mandated Cloud Dependencies**: All engines, validators, memory states, and contracts execute locally using standard Python 3.10+ without external pip package requirements.
- **Requirements & Design Before Code**: Implementation is strictly prohibited until Gate G1 (Requirements) and Gate G2 (Design or formal exemption) have been formally signed.
- **Evidence-Based Acceptance**: Status claims such as `PASSED` require auditable command execution logs, timestamps, and verifiable terminal outputs. Confidence is rejected as evidence.
- **Anti-Slop Engineering Baseline**: Mandatory rules (BL-001 through BL-007) eliminate decorative emojis, placeholder stubs (`TODO: implement later`), fake production data, and unverified assumptions.
- **Deterministic Lifecycle Transitions & Rollback**: An executable 7-gate finite state machine validates preconditions before gate progression and enforces deterministic rollbacks upon defect discovery.

---

## 3. Architecture and Repository Layout

```
project-intelligence/
├── core/                           # Foundation: Schemas, FSM engine, quality evaluator
│   ├── schemas/                    # 12 JSON Schemas (Draft-07)
│   ├── lifecycle/                  # Lifecycle state machine (lifecycle-fsm.json, engine.py)
│   ├── quality/                    # Anti-slop baseline and profiles (profiles.json, evaluator.py)
│   ├── capabilities/               # Platform capability taxonomy (matrix.json)
│   └── versioning/                 # SemVer policy and schema migration rules
├── contracts/                      # Active concrete project contracts (G0 to G6)
├── memory/                         # Git-aware 3-tier local project memory & drift reconciler
├── skills/                         # 12 canonical skills (SKILL.md + skill.json)
├── instructions/                   # Hierarchical agent instructions (universal, profiles, tasks)
├── agents/                         # 9 logical agent definitions (agent.json + agent.md)
├── adapters/                       # Platform adapters (Claude Code, Copilot, Codex, Other)
├── validation/                     # Automated framework test runner and fixtures
└── docs/                           # Architecture, guides, research, ADRs, and review reports
```

---

## 4. The 7 Lifecycle Gates (G0–G6)

| Gate | Phase Name | Output Contract | Gate Description & Requirements |
|---|---|---|---|
| **G0** | Project Discovery | `contracts/project/contract.json` | Stakeholder alignment, problem statement, scope boundaries, platform targets. |
| **G1** | Requirements Alignment | `contracts/requirements/contract.json` | Functional/non-functional requirements, acceptance criteria, G2 exemption check. |
| **G2** | Design Approval | `contracts/design/contract.json` | Design tokens, layouts, accessibility rules (or signed exemption for CLI/services). |
| **G3** | Architecture & Contracts | `contracts/architecture/contract.json` | Component boundaries, data models, API schemas, ADRs, file ownership plan. |
| **G4** | Controlled Implementation | `contracts/implementation/contract.json` | Bounded tasks, subagent delegations, unit tests, commit history logging. |
| **G5** | Verification & Quality | `contracts/quality/contract.json` | Automated test telemetry, anti-slop evaluation, independent review verdict. |
| **G6** | Release & Handoff | `contracts/release/contract.json` | Release manifest, migration notes, changelog, durable knowledge update. |

---

## 5. Anti-Slop Quality Engine and Profiles

The framework enforces seven non-negotiable baseline rules across all projects:
- **BL-001**: `disallowGratuitousEmoji` — Zero decorative emojis in professional code, logs, and commit messages.
- **BL-002**: `disallowFakeDataInProd` — Hardcoded mock values and fake production data are forbidden in production logic.
- **BL-003**: `disallowUnimplementedPlaceholders` — No empty stubs (`pass`), placeholder buttons, or unresolved `TODO` comments in deliverables.
- **BL-004**: `disallowUnexplainedWorkarounds` — Error swallowing and workarounds without documented root cause and tests are prohibited.
- **BL-005**: `disallowUnapprovedDependencies` — Adding third-party dependencies without architectural approval and rationale is forbidden.
- **BL-006**: `strictVerificationHonesty` — Strictly honest verification statuses (`PASSED`, `FAILED`, `BLOCKED`, `SKIPPED`, `UNAVAILABLE`).
- **BL-007**: `secretLeakagePrevention` — Zero API keys, credentials, or private tokens committed or stored in repository memory.

### Quality Profiles (`core/quality/profiles.json`)
- **Prototype**: Rapid proof-of-concept development, 0% test coverage minimum.
- **Standard**: Robust production-oriented development, 70% test coverage minimum, linting, security scans.
- **Production-Ready**: Mission-critical enterprise applications, 85% test coverage minimum, strict accessibility and security audits.
- **Security-Sensitive**: Hardened environments handling credentials/PII, 90% test coverage minimum, SAST, dependency audits.
- **Design-Intensive**: User-facing interfaces, 75% test coverage minimum, design token conformance, WCAG 2.1 AA accessibility.

---

## 6. 3-Tier Git-Aware Memory Architecture

To balance persistence against context window limitations:
1. **Durable Knowledge (`memory/durable-knowledge.json`)**: Persistent architectural patterns, confirmed user requirements, and project vocabulary. Updated only on gate transitions.
2. **Execution State (`memory/execution-state.json`)**: Ephemeral operational state tracking current gate, open tasks, subagent workstreams, and active Git commit SHA.
3. **Backlog (`memory/backlog.json`)**: Medium-term repository tracking deferred enhancements, technical debt, and review findings.

The executable reconciler (`memory/reconciliation-rules/reconciler.py`) checks for working tree drift against `git status` and protects against secret exposure.

---

## 7. Canonical Skills and Logical Agents

### Canonical Skills (`skills/`)
Each skill is packaged with a human-readable `SKILL.md` (purpose, procedure, verification, recovery) and a machine-readable `skill.json` manifest:
1. `project-discovery`
2. `existing-project-analysis`
3. `design-discovery`
4. `design-system-engineering`
5. `architecture-and-contracts`
6. `phase-planning`
7. `controlled-implementation`
8. `testing-and-verification`
9. `independent-review`
10. `documentation-and-handoff`
11. `cross-platform-adaptation`
12. `failure-recovery-and-improvement`

### Logical Agents (`agents/`)
Defined with role boundaries, tool permissions, input/output contracts, and system prompt instructions:
- **Orchestrator Agent**: Master coordinator, gatekeeper, and scope manager.
- **Discovery Agent**: Requirements analyst and problem investigator.
- **Design Agent**: UI/UX designer and design system specialist.
- **Architecture Agent**: Systems architect and contract author.
- **Planning Agent**: Work breakdown scheduler and file ownership coordinator.
- **Implementation Agent**: Controlled code author operating in bounded workstreams.
- **Verification Agent**: Test engineer and evidence collector.
- **Independent Review Agent**: Adversarial quality auditor.
- **Documentation & Memory Agent**: Handoff synthesizer and state reconciler.

---

## 8. Cross-Platform Adapters and Degradation Rules

Project Intelligence maps canonical rules to platform-specific configuration formats while maintaining the baseline quality standards:
- **Anthropic Claude Code (`adapters/claude-code/`)**: Generates `CLAUDE.md`, configures deterministic `PreToolUse` shell hooks to veto unapproved gate transitions (exit code 2), and maps skills to slash commands.
- **GitHub Copilot (`adapters/github-copilot/`)**: Generates `.github/copilot-instructions.md`, maps multi-agent roles to `.github/agents/*.agent.md`, and documents tool degradation in IDE environments.
- **OpenAI Codex (`adapters/codex/`)**: Implements Responses API system prompt compilation, context compaction thresholds, and OpenAI Agents SDK handoff rules.
- **Other Platforms (`adapters/other-platforms/`)**: POSIX shell scripts (`agy-orchestrate.sh`) and IDE task configurations for Cursor, Windsurf, and terminal-first workflows.

---

## 9. Quick Start and Validation

### Step 1: Run the Self-Validation Test Suite
From the root of the repository, execute:
```bash
python validation/test_runner.py
```
This runs 23 comprehensive tests verifying schemas, state machine logic, quality evaluators, memory reconciliation, and adapter compliance.

### Step 2: Initialize Project Memory
```bash
python memory/reconciliation-rules/reconciler.py --update
```

### Step 3: Advance Lifecycle Gates
```bash
python core/lifecycle/engine.py --advance G0
```

---

## 10. Documentation Sitemap

- [Architecture Overview](docs/architecture/overview.md)
- [Usage & Operations Guide](docs/usage/guide.md)
- [Authoritative Platform Research](docs/research/authoritative-platform-report.md)
- [Platform Capability Matrix](docs/research/platform-matrix.md)
- [Architecture Decision Records (ADRs)](docs/decisions/)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Independent Review Report](docs/validation/independent-review-report.md)
