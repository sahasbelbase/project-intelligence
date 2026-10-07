# Canonical Architecture Decisions — Project Intelligence

## ADR-0001: Local-First, Schema-Driven, Contract-Centric Architecture

### Status
Accepted

### Context
AI coding agents often suffer from context degradation, uncontrolled hallucinations, scope creep ("AI slop"), lack of persistence across sessions/tools, and silent failure modes. Furthermore, modern development ecosystems span multiple AI coding assistants (Claude Code, GitHub Copilot, OpenAI Codex, Antigravity, Cursor, etc.). 

We need an engineering framework that is:
1. **Portable**: Works across AI platforms without rewriting the core project model.
2. **Local-First & Git-Centric**: All durable project memory, state, contracts, and decisions reside in version-controlled repository files. No external databases or mandatory SaaS services.
3. **Evidence-Based**: Confidence is never equated with verification. Every claim requires test/build/lint evidence.
4. **Contract-Gated**: Rigid boundaries between Discovery (G0), Requirements (G1), Design (G2), Architecture (G3), Implementation (G4), Review (G5), and Release/Handoff (G6).
5. **Multi-Agent Decomposable**: Capable of execution by a single agent or partitioned across specialized subagents with explicit handoff contracts.

### Decision

1. **Portable Core vs. Platform Adapters**:
   - The `core/` defines universal schemas, lifecycle state machines, quality profiles, capability descriptors, and semver contracts.
   - The `adapters/` directory maps the canonical definitions to platform-native idioms (e.g. `CLAUDE.md` and `.claude/hooks` for Claude Code; `.github/copilot-instructions.md` and `.github/agents/` for Copilot). Adapters declare exact capabilities, limitations, and manual fallbacks without altering the canonical contracts.

2. **JSON Schema as Contract Definition Standard**:
   - All contracts (`project`, `requirements`, `design`, `architecture`, `implementation`, `quality`, `release`) and memory structures are strictly defined using standard JSON Schema (Draft-07 / Draft 2020-12 compatible).
   - Validation can be executed natively in Python standard library or standard validator tools with zero external dependencies.

3. **Deterministic Lifecycle Gates**:
   - Lifecycle consists of G0 through G6.
   - Gate transitions are modeled as a deterministic Finite State Machine (FSM).
   - Inapplicable gates (e.g. G2 Design for a pure CLI backend) must be explicitly recorded with a structured exemption rationale; gates may never be silently skipped.

4. **Three-Tier Project Memory**:
   - `Durable Knowledge`: Project charter, architecture decisions (ADRs), domain vocabulary, style rules.
   - `Execution State`: Active phase, active gate, assigned work units, git commit hashes, evidence records.
   - `Backlog & History`: Bug log, technical debt, deferred requirements, post-mortem findings.
   - A reconciliation engine checks repository git status against execution state at session startup to detect drift or uncommitted changes.

5. **No AI Slop / Anti-Degradation Guardrails**:
   - Mandatory Baseline Quality Profile forbids decorative non-functional emoji, fake data in production paths, empty stub implementations, unexplained workarounds, and unapproved scope expansion.
   - Visual designs must pass design token verification, responsive breakpoints, contrast checks, and reference asset validation before code is accepted.

### Consequences
- Requires strict adherence to schema files and contract validations.
- Provides absolute auditability, reproducible handoffs, and deterministic agent execution across any compliant AI tool.
