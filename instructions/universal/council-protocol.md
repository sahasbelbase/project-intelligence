# Universal Instructions — Multi-Persona Council Protocol

## 1. Operational Purpose & Precedence

The Multi-Persona Council Protocol governs collective deliberation and decision-making for complex, irreversible, or high-stakes architectural and strategic choices. It operationalizes Sections 11 and 12 of the Universal Role-Aware Intelligence Framework.

**Core Mandate**: High-stakes decisions must never be resolved by a single persona operating in isolation. Councils ensure multi-disciplinary scrutiny, adversarial cross-examination, and the rigorous preservation of dissenting perspectives.

---

## 2. Council Trigger Criteria

A multi-persona council must be convened when any of the following triggers are met:
1. **Irreversible Architectural Decisions (Type 1)**: Core framework abstractions, storage engines, serialization protocols, or foundational dependency selections.
2. **Security & Permission Boundaries**: Changes to authentication models, filesystem access permissions, sandboxing policies, or credential handling.
3. **Competing Disciplinary Priorities**: Fundamental tensions between velocity, maintainability, visual design, verification rigor, and operational complexity.
4. **Lifecycle State Transitions at G3 or G5**: High-risk gate advancements where multiple domain perspectives diverge.
5. **Explicit Human Request**: Whenever the human user requests multi-perspective debate, trade-off analysis, or a formal council brief.

*Negative Trigger*: Trivial bug fixes, localized refactoring, documentation updates, and standard unit test additions must NOT convene a council. Over-engineering simple tasks violates the Principle of Minimum Necessary Complexity.

---

## 3. Convening a Council

Councils are defined in `core/council/councils.json`, with persona definitions in `core/council/personas/` (and, for the product council, the existing agents in `agents/`). The referee (`core/council/referee.py`) runs the process; the model speaking as each persona supplies the reasoning. The referee never generates opinions.

- **Tiers**: 0 answer directly, 1 one specialist, 2 one council, 3 product, design and development councils in sequence followed by quality review. Plan with `python3 -m core.council.referee plan "<task>"`.
- **Convene size**: the chair, the critic and up to three specialists chosen by relevance (at most five). The full roster is opt-in for major redesigns only.
- **Prompts**: build each persona's instruction with `python3 -m core.council.referee prompt <council> <persona> <round> "<task>"`.
- **Records**: the referee validates every round and the brief, adds any unrecorded dissent, and saves the session to `memory/council-briefs/<decisionId>.json`. The website displays these records read-only. Check them with `python3 -m core.council.referee check`.
- **Hand-offs**: in tier 3, each council passes a compact hand-off (recommendation, scope, assumptions, risks, open dissent) to the next, not its full transcript: `council handoff <decisionId>` produces it, and `--context` passes it into the next council's prompts.
- **Separate agents**: where the client can start subagents (Claude Code's `council-member` agent), each persona runs as its own agent. Round 1 prompts come from `council sheet`, all agents start at once, and each sees only its own prompt, so Round 1 is genuinely blind. Later rounds continue the same agents. Records state `"blinding": "separate-agents"`; sessions written by one agent state `"single-agent"`, and the website shows which.

## 4. The 4-Round Deliberation Protocol

Councils execute in four strictly ordered, deterministic rounds:

```
┌─────────────────────────────────────────────────────────────┐
│  Round 1: Independent Analysis (Blinded Evaluation)         │
├─────────────────────────────────────────────────────────────┤
│  Round 2: Challenge Round (Adversarial Cross-Examination)   │
├─────────────────────────────────────────────────────────────┤
│  Round 3: Revision Round (Accountability & Defense)         │
├─────────────────────────────────────────────────────────────┤
│  Round 4: Decision Synthesis & Dissent Preservation         │
└─────────────────────────────────────────────────────────────┘
```

### 4.1 Round 1: Independent Analysis (Blinded Evaluation)
- **Objective**: Establish uncorrupted, discipline-specific assessments from each persona's unique vantage point.
- **Protocol Rules**:
  - Each persona evaluates the problem brief strictly through their mission, expertise, typical questions, and boundaries.
  - Personas must not read or respond to peer analyses during Round 1.
  - Each persona delivers:
    1. Initial Recommendation (`Build`, `Test further`, `Pilot`, `Pivot`, `Defer`, `Stop`).
    2. Primary stance and rationale.
    3. Disciplinary arguments and evidence requirements.
    4. Identified risks and unexamined assumptions.
    5. Proposed scope constraints.

### 4.2 Round 2: Challenge Round (Adversarial Cross-Examination)
- **Objective**: Expose cognitive blind spots, unexamined assumptions, competing priorities, and overlooked risks.
- **Protocol Rules**:
  - Personas review peer analyses produced in Round 1.
  - Each persona raises at most two challenges, aimed at the peer claims it disagrees with most. The council's critic must raise at least one, including the case for the simplest option.
  - Personas with nothing material to challenge may raise none; silence is recorded, not padded.
  - Single-persona councils must execute an internal Devil's Advocate self-challenge.
  - Each challenge must specify:
    1. Target persona.
    2. Challenge type (`BLIND_SPOT`, `OVERLOOKED_RISK`, `COMPETING_PRIORITY`, `UNEXAMINED_ASSUMPTION`, `SCOPE_CREEP`).
    3. Concrete critique.
    4. Severity level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
    5. Actionable counter-proposal.

### 4.3 Round 3: Revision Round (Accountability & Defense)
- **Objective**: Transparently address challenges, state concessions, defend critical invariants, and revise recommendations.
- **Protocol Rules**:
  - Personas must evaluate all incoming challenges received in Round 2.
  - Personas must explicitly declare:
    - **What Changed**: Specific concessions made, scope reduced, or new constraints accepted.
    - **Why It Changed**: Epistemic reasoning linking back to the challenger's argument or evidence.
    - **What Remained Unchanged**: Defended core positions and non-negotiable domain invariants.
    - **Revised Recommendation**: Updated stance following cross-examination.
    - **Persisting Objections**: Unresolved concerns regarding peer proposals.

### 4.4 Round 4: Decision Synthesis & Dissent Preservation
- **Objective**: Synthesize a canonical Council Decision Brief conforming to `core/schemas/council-brief.schema.json`.
- **Protocol Rules**:
  - The Lead Orchestrator aggregates revised recommendations and consensus metrics.
  - If critical security, quality, or data-loss risks remain unmitigated, the council recommendation must default conservatively to `Test further` or `Stop`.
  - **Preservation of Dissent**: Any persona whose revised stance differs from the synthesized outcome, or who voiced high-severity unresolved concerns, must be recorded in the `dissent` section with full rationale and their proposed alternative. Forced unanimity is strictly forbidden.

---

## 5. Anti-Groupthink Governance Rules (CP-001 through CP-004)

### CP-001: Prohibition of Premature Consensus
No persona may declare immediate consensus in Round 1. Independent analysis must precede agreement.

### CP-002: Mandatory Devil's Advocate Scrutiny
In any deliberation where all personas initially agree on a single outcome, the council's critic must formally assume a devil's advocate posture during Round 2, probing worst-case failure modes.

### CP-003: Sacred Right to Dissent
Persisting disagreement must never be scrubbed, suppressed, or averaged out. Dissenting opinions serve as critical risk records and tripwires for future project milestones.

### CP-004: Anti-Slop Language in Deliberations
Deliberation prose must adhere to Rule BL-001 (Zero decorative emojis) and Rule BL-004 (Explicit rationale for all concessions). Empty agreeable fluff (`Great point!`, `I totally agree`) is prohibited; all contributions must provide substantive technical argumentation.
