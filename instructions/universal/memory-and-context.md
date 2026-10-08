# Universal Instructions — Memory and Context Management

## 1. Operational Purpose & Precedence

This document defines the rules for maintaining persistent project state, Git-aware memory synchronization, context window economy, and cross-session knowledge preservation within the Project Intelligence framework.

**Core Mandate**: Agents are ephemeral; project memory must be durable, deterministic, and Git-synchronized. Agents must never rely on fleeting LLM conversational context for authoritative project state.

---

## 2. The 3-Tier Git-Aware Memory Architecture

Project state is segregated into three distinct, structured JSON files within the `memory/` directory:

```
project-intelligence/memory/
├── durable-knowledge.json   # Tier 1: Long-term invariants, ADRs, glossary
├── execution-state.json     # Tier 2: Short-term active gate, task allocations
└── backlog.json             # Tier 3: Medium-term debt, deferred items
```

### 2.1 Tier 1: Durable Knowledge (`memory/durable-knowledge.json`)
- **Retention**: Permanent across the entire project lifecycle.
- **Contents**:
  - Architectural constraints and core design invariants.
  - Signed Architecture Decision Records (ADRs).
  - Domain vocabulary and naming conventions.
  - Approved third-party dependencies and licensing constraints.
  - Preserved council decisions and dissenting minority opinions.
- **Update Protocol**: Read frequently; updated only upon formal gate approval (G0, G1, G3) or ADR creation.

### 2.2 Tier 2: Execution State (`memory/execution-state.json`)
- **Retention**: Transient; represents immediate session and task progress.
- **Contents**:
  - Active lifecycle gate (G0 through G6).
  - Currently executing task IDs and assigned persona roles.
  - Active subagent workstream allocations.
  - Last reconciled Git commit hash (`lastReconciledCommit`).
  - Active quality profile name.
- **Update Protocol**: Updated at the start and completion of every bounded subagent task or gate transition.

### 2.3 Tier 3: Project Backlog (`memory/backlog.json`)
- **Retention**: Medium-term; tracks deferred work and technical debt.
- **Contents**:
  - Deferred enhancements from council deliberations (`recommendation: Defer`).
  - Identified technical debt, performance optimizations, or edge-case handling.
  - Prerequisite conditions and triggers required to activate backlog items.
- **Update Protocol**: Appended when work is intentionally deferred or council deliberations scope out items.

---

## 3. Git-Aware Synchronization & Reconciliation

Memory files must remain in lockstep with the Git working tree. The framework prevents state drift through the following rules:

### MC-001: Pre-Flight Commit Reconciliation
Upon initializing an agent session or launching a subagent:
1. Query current repository commit: `git rev-parse HEAD`.
2. Inspect `lastReconciledCommit` in `memory/execution-state.json`.
3. If hashes diverge, invoke `memory/reconciliation-rules/reconciler.py` to reconcile memory before mutating code.

### MC-002: Atomic State Commit
Whenever an agent updates an execution state or completes a lifecycle gate:
1. Validate modified memory files against their schemas in `memory/schemas/`.
2. Update `lastReconciledCommit` to reflect the newly created commit.
3. Commit memory state changes atomically with the corresponding code changes.

### MC-003: Conflict Resolution & Three-Way Merges
If Git conflicts occur in `memory/execution-state.json` or `memory/backlog.json` during branch merges:
- Never overwrite wholesale with remote or local versions.
- Execute structured reconciliation via `memory/reconciliation-rules/reconciler.py` to merge task arrays and preserve distinct entries.

---

## 4. Context Window Economy Standards

LLM token contexts are constrained resources. Agents must minimize context bloat while maximizing signal:

1. **Avoid Whole-File Inlining**: When referencing large source files, load or cite specific line ranges rather than echoing full file contents.
2. **Quarantine Verbose Telemetry**: Do not dump thousands of lines of raw test logs into conversation contexts. Write complete logs to disk in `validation/reports/` and quote concise exit summaries in messages.
3. **Canonical Link Formatting**: Always use standard markdown links with `file://` URIs for file paths and line numbers (e.g., `[engine.py](file:///absolute/path/core/council/engine.py#L20-L45)`).
4. **Structured Handoff Summaries**: When handing off work between subagents or across sessions, provide structured JSON summaries or concise markdown bullet points citing durable file paths.
