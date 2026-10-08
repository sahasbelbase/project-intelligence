# Universal Instructions — Task Routing and Execution Planning

## 1. Operational Purpose & Precedence

This document governs how incoming requests, task directives, and user queries are parsed and routed to optimal personas and skill combinations. It operationalizes Sections 3, 14, and 15 of the Universal Role-Aware Intelligence Framework.

**Guiding Architectural Axiom**:
> **"Minimum necessary complexity, maximum useful expertise."**
> Execute every task with the least process overhead required to achieve deterministic quality and correctness. Never invoke a multi-persona council for a task a single persona can resolve, and never allow a solitary persona to make an irreversible, high-stakes architectural decision.

---

## 2. Intent Categorization Taxonomy

Incoming requests must be categorized into one of five canonical intent types:

```
┌─────────────────────────────────────────────────────────────┐
│  Intent Category        Target Archetype                    │
├─────────────────────────────────────────────────────────────┤
│  SINGLE_PERSONA         Direct single-discipline execution  │
│  SEQUENTIAL_WORKFLOW    Ordered multi-phase pipeline        │
│  COUNCIL                Multi-persona deliberation & debate │
│  VERIFICATION           Automated test execution & proofs   │
│  REVIEW                 Read-only adversarial quality audit │
└─────────────────────────────────────────────────────────────┘
```

### 2.1 SINGLE_PERSONA
- **Characteristics**: Focused, well-bounded, single-domain tasks with low risk and high clarity.
- **Complexity Range**: 1 to 4.
- **Workflow**: Direct execution by one specialized persona; zero coordination overhead.
- **Typical Tasks**: Localized bug fixes, refactoring a single helper function, documentation edits, schema creation, explaining a code block.

### 2.2 SEQUENTIAL_WORKFLOW
- **Characteristics**: Multi-stage features or deliverables requiring sequential lifecycle progression.
- **Complexity Range**: 5 to 7.
- **Workflow**: Ordered handoff across specialized personas (e.g., Discovery → Architecture → Implementation → Verification).
- **Typical Tasks**: Implementing a new subsystem, creating a platform adapter, full feature engineering across lifecycle gates.

### 2.3 COUNCIL
- **Characteristics**: High-stakes, irreversible choices, fundamental architectural trade-offs, security model changes, or explicit requests for debate.
- **Complexity Range**: 8 to 10.
- **Workflow**: 4-Round Council Protocol (Independent Analysis → Challenge → Revision → Decision Brief).
- **Typical Tasks**: Choosing a primary database or state persistence layer, major framework refactoring, high-impact security boundaries.

### 2.4 VERIFICATION
- **Characteristics**: Running test suites, checking assertions, capturing empirical execution evidence, and validating exit codes.
- **Workflow**: Direct handoff to Testing & Verification Engineer with `testing-and-verification` skill.
- **Typical Tasks**: Executing unit tests, running regression suites, gathering exit code proofs.

### 2.5 REVIEW
- **Characteristics**: Independent, read-only quality inspection, anti-slop audits, and PR evaluations.
- **Workflow**: Direct handoff to Independent Reviewer with `independent-review` skill.
- **Typical Tasks**: Pre-merge code audits, quality contract validation, architectural compliance audits.

---

## 3. Complexity Scoring and Routing Heuristics

The Task Router computes an objective complexity score (1 to 10) based on observable factors:

| Complexity Factor | Score Impact |
|---|---|
| Single domain, localized file change | -2 to -4 |
| Clarification, lookup, or docstring fix | -3 |
| Multi-discipline span (e.g., UI + Backend + Security) | +1 to +3 |
| Cross-cutting lifecycle gates involved | +3 |
| Irreversible change (data model, storage engine, security) | +4 |
| Explicit council or trade-off debate requested | +3 |

### Routing Decision Matrix:

```
Complexity Score <= 4  ──► Route to SINGLE_PERSONA (Direct)
Complexity Score 5-7   ──► Route to SEQUENTIAL_WORKFLOW (Pipeline)
Complexity Score >= 8  ──► Route to COUNCIL (Multi-Persona Deliberation)
Verification-specific  ──► Route to VERIFICATION (Direct)
Audit/Review-specific  ──► Route to REVIEW (Direct)
```

---

## 4. Routing Anti-Patterns (TR-001 through TR-004)

### TR-001: The Council Over-Engineering Trap
Invoking a multi-persona council for routine bugs, localized syntax adjustments, or simple utilities. This introduces massive latency, consumes excessive tokens, and violates the Principle of Minimum Necessary Complexity.

### TR-002: The Solitary Architect Trap
Allowing a single persona to unilaterally decide foundational, irreversible architectural choices (e.g., choosing SQLite vs Postgres, restructuring directory topology, or deprecating public contracts) without cross-examination.

### TR-003: The Unverified Pipeline Trap
Executing a sequential workflow without terminating in automated test verification by the Verification Engineer. Every code modification pipeline must conclude with empirical test execution.

### TR-004: Self-Review Conflict of Interest
Assigning the Implementation Engineer to perform the independent adversarial review of their own deliverables. Review tasks must strictly route to the Independent Review persona.

## Low-confidence plans

Every plan reports `confidence` and the `evidence` behind it. When confidence is `low`, read the evidence and either confirm the route or re-plan with `--council <design|development|product>` or `--persona <id>`, and say why. Measured accuracy is 80% on requests the router has not seen, so this check matters (decision `dec-routing-keywords-vs-model`).

