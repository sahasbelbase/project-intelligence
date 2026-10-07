# Architecture Overview: Project Intelligence Framework

## 1. System Mission and Principles

Project Intelligence is a local-first, platform-agnostic AI project orchestration framework designed to establish a deterministic engineering lifecycle, shared contract representations, git-aware memory management, anti-slop quality baselines, and structured multi-agent coordination.

The framework operates on five core principles:
1. **Local-First & Zero Mandated Cloud Run-time**: All schemas, contracts, memory state, and verification engines execute natively within the local project workspace using standard development runtimes (Python 3.10+ standard library).
2. **Requirements and Design Before Implementation**: Implementation is prohibited until requirements (Gate G1) and visual/domain design (Gate G2, where applicable) have been formally captured in signed contracts.
3. **Evidence-Based Acceptance**: Statuses such as PASSED require reproducible, auditable command outputs. Confidence is never accepted as a substitute for verification.
4. **Anti-Slop Engineering Standards**: Strict baseline rules (BL-001 through BL-007) eliminate decorative emojis, placeholder stubs (`TODO: implement later`, `pass`), fake credentials, and unverified assumptions.
5. **Deterministic Lifecycle FSM**: A 7-gate finite state machine (G0 through G6) governs transitions, enforcing rollback on defect discovery and preventing illegal phase skipping.

---

## 2. Directory Layout and Repository Structure

The framework is organized into decoupled layers:

```
project-intelligence/
├── core/                           # Foundation layer: schemas, lifecycle engine, quality evaluator
│   ├── schemas/                    # JSON Schemas (Draft-07) for contracts, lifecycle, memory, agents, skills
│   │   ├── contract-envelope.schema.json
│   │   ├── project-contract.schema.json
│   │   ├── requirements-contract.schema.json
│   │   ├── design-contract.schema.json
│   │   ├── architecture-contract.schema.json
│   │   ├── implementation-contract.schema.json
│   │   ├── quality-contract.schema.json
│   │   ├── release-contract.schema.json
│   │   ├── memory.schema.json
│   │   ├── lifecycle.schema.json
│   │   ├── agent-definition.schema.json
│   │   └── skill-definition.schema.json
│   ├── lifecycle/                  # Deterministic state machine specification & engine
│   │   ├── lifecycle-fsm.json      # FSM states, gates G0-G6, transitions, rollback targets
│   │   └── engine.py               # Executable Python lifecycle transition and rollback engine
│   ├── quality/                    # Anti-slop baseline and quality profile definitions
│   │   ├── profiles.json           # Baseline rules + Prototype, Standard, Production, Security, Design profiles
│   │   └── evaluator.py            # Executable code and artifact quality evaluator
│   ├── capabilities/               # Platform capability taxonomy
│   │   └── matrix.json             # Feature matrix across Claude Code, Copilot, Codex, and Generic IDE
│   └── versioning/                 # Versioning policies and schema migration rules
│       ├── semver_policy.md        # Semantic versioning contracts
│       └── migration_rules.json    # Upward migration paths between schema versions
│
├── contracts/                      # Active concrete project contracts (signed JSON envelopes)
│   ├── project/contract.json       # G0: Project initialization contract
│   ├── requirements/contract.json  # G1: Requirements contract (scope, constraints, acceptance)
│   ├── design/contract.json        # G2: Design specification contract (or formal exemption)
│   ├── architecture/contract.json  # G3: Architecture contract (components, interfaces, ADRs)
│   ├── implementation/contract.json# G4: Implementation contract (tasks, workstreams, commits)
│   ├── quality/contract.json       # G5: Quality & review contract (verification evidence, verdicts)
│   └── release/contract.json       # G6: Release and deployment contract (sign-offs, changelog)
│
├── memory/                         # Git-aware 3-tier local project memory
│   ├── schemas/                    # Schema validations for state files
│   ├── templates/                  # Blank initialization templates
│   ├── reconciliation-rules/       # Reconciliation mechanics, drift detection, rebase handling
│   │   ├── rules.md                # Theoretical and procedural rules
│   │   └── reconciler.py           # Executable Git reconciliation and drift detection tool
│   ├── durable-knowledge.json      # Long-term decisions, architecture constraints, domain vocabulary
│   ├── execution-state.json        # Short-term active gate, open tasks, active subagent assignments
│   └── backlog.json                # Medium-term debt, deferred enhancements, out-of-scope backlog
│
├── skills/                         # Canonical, portable skill definitions (SKILL.md + skill.json)
│   ├── project-discovery/
│   ├── existing-project-analysis/
│   ├── design-discovery/
│   ├── design-system-engineering/
│   ├── architecture-and-contracts/
│   ├── phase-planning/
│   ├── controlled-implementation/
│   ├── testing-and-verification/
│   ├── independent-review/
│   ├── documentation-and-handoff/
│   ├── cross-platform-adaptation/
│   └── failure-recovery-and-improvement/
│
├── instructions/                   # Hierarchical instructions for AI coding agents
│   ├── universal/                  # Core behavioral rules (anti-slop, local privacy, git discipline)
│   ├── profiles/                   # Specialized profile instructions (production, security, prototype)
│   └── tasks/                      # Bounded operational task instructions (discovery, implementation, review)
│
├── agents/                         # Logical agent definitions (agent.json + agent.md)
│   ├── orchestrator/               # Lead coordinator, scope manager, gatekeeper
│   ├── discovery/                  # Requirements engineer and project analyst
│   ├── design/                     # UI/UX designer and design system engineer
│   ├── architecture/               # Technical architect and contract author
│   ├── planning/                   # Work breakdown and dependency scheduler
│   ├── implementation/             # Controlled code author with strict file ownership
│   ├── verification/               # Test automation and evidence collection engineer
│   ├── independent-review/         # Read-only adversarial quality auditor
│   └── documentation-and-memory/   # Handoff synthesizer and memory reconciler
│
├── adapters/                       # Platform-specific adapters and graceful degradation mappings
│   ├── claude-code/                # CLAUDE.md translation, PreToolUse veto hooks, settings templates
│   ├── github-copilot/             # copilot-instructions.md, .github/agents manifests, custom skills
│   ├── codex/                      # Responses API system prompt compilation, Agents SDK handoff
│   └── other-platforms/            # Generic POSIX CLI and IDE adapter specifications
│
├── validation/                     # Automated framework verification engine
│   ├── fixtures/                   # Test fixtures (new project, existing project, corrupted memory)
│   ├── schema-tests/               # Schema validation and contract envelope tests (test_schemas.py)
│   ├── lifecycle-tests/            # Gate transitions, exemption logic, defect rollback tests (test_lifecycle.py)
│   ├── quality-tests/              # Anti-slop baseline and profile threshold tests (test_quality.py)
│   ├── memory-tests/               # Memory schema, template, drift detection tests (test_memory.py)
│   ├── adapter-conformance/        # Adapter manifest and baseline preservation tests (test_adapters.py)
│   ├── regression-tests/           # Targeted regression and edge-case test suites
│   └── test_runner.py              # Standalone zero-dependency test runner orchestrator
│
└── docs/                           # Architecture, research, guides, and validation records
    ├── architecture/               # System architecture and data flow specifications
    ├── decisions/                  # Architecture Decision Records (ADRs) and work ledger
    ├── research/                   # Platform research reports and capability matrix
    ├── usage/                      # Operational guides for developers and AI agents
    └── validation/                 # Independent review reports and test telemetry
```

---

## 3. Data Flow and Lifecycle Architecture

The operational flow of Project Intelligence is strictly deterministic. No step may execute out of order or bypass intermediate contracts.

```
       +-------------------------------------------------------+
       |                  G0: Project Discovery                |
       |  Output: contracts/project/contract.json              |
       +---------------------------+---------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |               G1: Requirements Alignment              |
       |  Output: contracts/requirements/contract.json         |
       +---------------------------+---------------------------+
                                   |
                                   v
               /---------------------------------------\
              <   Visual UI / User-Facing Components?   >
               \---------------------------------------/
                       /                       \
             [YES]   /                           \   [NO - Exempt]
                   v                               v
  +---------------------------------+  +-------------------------------+
  |        G2: Design Approval      |  | G2 Exemption Signed in G1     |
  | Output: contracts/design/...    |  | Reason: Backend/CLI/Service   |
  +----------------+----------------+  +---------------+---------------+
                   \                               /
                     \                           /
                       v                       v
       +-------------------------------------------------------+
       |             G3: Architecture & Contracts              |
       |  Output: contracts/architecture/contract.json         |
       +---------------------------+---------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |             G4: Controlled Implementation             |
       |  Output: contracts/implementation/contract.json       |
       +---------------------------+---------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |           G5: Verification & Quality Gates            |
       |  Output: contracts/quality/contract.json              |
       +---------------------------+---------------------------+
                                   |
                 /-----------------------------------\
                <     Defects or Blockers Found?      >
                 \-----------------------------------/
                       /                       \
             [YES]   /                           \   [NO - Passed]
                   v                               v
  +---------------------------------+  +-------------------------------+
  |   Rollback to Target Gate       |  |     G6: Release & Handoff     |
  | (G4 for code, G3 for contract)  |  | contracts/release/contract    |
  +---------------------------------+  +-------------------------------+
```

### 3.1 Contract Envelopes

Every contract in the `contracts/` directory follows the canonical `contract-envelope.schema.json` format:
- `schemaVersion`: SemVer string matching `"1.0.0"`.
- `contractId`: Unique identifier (e.g. `proj-contract-001`).
- `contractType`: One of `project`, `requirements`, `design`, `architecture`, `implementation`, `quality`, `release`.
- `title`: Human-readable title for the contract.
- `status`: Lifecycle approval status (`DRAFT`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`, `SUPERSEDED`, `DEPRECATED`).
- `lifecycleGate`: Associated gate ID (`G0` through `G6`).
- `createdAt` / `updatedAt`: ISO 8601 UTC timestamp.
- `author`: Object containing author `role` and `identifier`.
- `approval`: Object containing `approvedBy`, `approvedAt`, `rationale`, and optional `exemption`.
- `traceability`: Object linking `parentContractId`, `upstreamRequirements`, `downstreamTasks`, `verificationIds`.
- `data`: Typed payload matching the specific schema for that contract type.

---

## 4. Anti-Slop Quality Engine and Profiles

The framework implements a mandatory baseline (BL-001 through BL-007) and five specialized quality profiles defined in `core/quality/profiles.json`.

### 4.1 Mandatory Baseline Rules

1. **BL-001: disallowGratuitousEmoji**: Technical artifacts, instructions, schemas, contracts, and code files must not include decorative icons or emojis.
2. **BL-002: disallowFakeDataInProd**: Hardcoded mock values and fake production data are forbidden in production logic.
3. **BL-003: disallowUnimplementedPlaceholders**: Non-functional placeholder buttons, empty stubs, and unresolved TODOs are prohibited in approved deliverables.
4. **BL-004: disallowUnexplainedWorkarounds**: Workarounds without documented root cause and tests are prohibited.
5. **BL-005: disallowUnapprovedDependencies**: Adding third-party dependencies without architectural approval and rationale is forbidden.
6. **BL-006: strictVerificationHonesty**: Verification statuses must be honest (`PASSED`, `FAILED`, `BLOCKED`, `SKIPPED`, `UNAVAILABLE`). A skipped check may never be reported as passed.
7. **BL-007: secretLeakagePrevention**: API keys, passwords, and tokens must never be written to repository memory, contracts, or commits.

### 4.2 Quality Profiles

- **Prototype**: Fast exploratory work, 0% minimum test coverage, linting and unit tests required.
- **Standard**: Professional default, 70% minimum test coverage, full linting, unit tests, security scans.
- **Production-Ready**: Enterprise grade, 85% minimum test coverage, strict types, accessibility audit, security scans, zero high-severity CVEs.
- **Security-Sensitive**: Hardened environment, 90% minimum test coverage, automated SAST, secret audits, dependency audits.
- **Design-Intensive**: Design-first workflow, 75% minimum test coverage, strict design token synchronization, responsive layout auditing, WCAG 2.1 AA accessibility compliance.

---

## 5. 3-Tier Git-Aware Memory Architecture

Project state is divided into three distinct operational tiers to prevent context rot, token exhaustion, and drift across developer handoffs:

| Memory Tier | File Location | Retention Scope | Update Frequency |
|---|---|---|---|
| **Durable Knowledge** | `memory/durable-knowledge.json` | Long-term: architecture patterns, confirmed user requirements, domain vocabulary, design tokens | Updated only at gate approvals |
| **Execution State** | `memory/execution-state.json` | Short-term: active gate, open tasks, assigned subagent workstreams, current Git commit SHA | Updated after each completed task |
| **Backlog** | `memory/backlog.json` | Medium-term: technical debt, deferred features, out-of-scope items, review recommendations | Updated during review and release |

### 5.1 Drift Detection and Reconciliation Engine

The executable `memory/reconciliation-rules/reconciler.py` connects project memory to Git:
- Detects stale memory by comparing `execution-state.json.last_reconciled_commit` with `git rev-parse HEAD`.
- Prevents overwriting uncommitted human edits by validating clean working tree status.
- Scans memory contents for accidental secrets (`sk-proj-...`, `AKIA...`, `BEGIN PRIVATE KEY`) and vetoes persistence if detected.
- Safely initializes on unborn branches with zero prior commits.

---

## 6. Multi-Platform Adaptation Layer

To preserve identical engineering rigor across differing AI tools, Project Intelligence compiles canonical assets into platform-native formats:

- **Anthropic Claude Code (`adapters/claude-code/`)**: Translates core rules to `CLAUDE.md`, configures deterministic `PreToolUse` shell hooks to veto unapproved gate transitions (exit code 2), and maps skills to slash commands.
- **GitHub Copilot (`adapters/github-copilot/`)**: Translates instructions into `.github/copilot-instructions.md`, compiles logical agents into `.github/agents/*.agent.md`, and documents IDE-versus-CLI tool degradation.
- **OpenAI Codex (`adapters/codex/`)**: Compiles system prompts via Responses API structure, manages token compaction thresholds, and maps subagent handoffs to OpenAI Agents SDK models.
- **Other Platforms (`adapters/other-platforms/`)**: Provides POSIX CLI wrapper scripts (`agy-orchestrate.sh`) and IDE tasks for Cursor, Windsurf, and standard terminal environments.
