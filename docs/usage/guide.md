# Usage and Operations Guide: Project Intelligence Framework

## 1. Quick Start

### 1.1 Prerequisites
- Python 3.10 or later (standard library only; zero external pip dependencies required).
- Git 2.30 or later.
- An AI coding environment (Claude Code, GitHub Copilot, OpenAI Codex, Cursor, or POSIX terminal).

### 1.2 Verification of Local Environment
Run the framework self-validation suite from the project root:
```bash
python validation/test_runner.py
```
Expected output:
```
Total Tests Run   : 23
Passed Checks     : 23
Failed Checks     : 0
Execution Duration: < 0.1 seconds
Overall Status    : PASSED
```

---

## 2. Starting a New Project from Scratch

When initializing a greenfield project with Project Intelligence:

### Step 1: Initialize Project Memory and Repository
```bash
git init
python memory/reconciliation-rules/reconciler.py --update
```
This initializes `memory/execution-state.json` and records the initial commit state.

### Step 2: Select a Quality Profile
Inspect available profiles in `core/quality/profiles.json`:
- `prototype`: Minimal friction, fast discovery (0% test coverage threshold).
- `standard`: Balanced engineering rigor (recommended default, 70% coverage threshold).
- `production-ready`: Strict types, zero CVE tolerance, 85% coverage threshold, accessibility audit.
- `security-sensitive`: Cryptographic verification, SAST, secret auditing (90% coverage threshold).
- `design-intensive`: UI/UX design tokens, accessibility, visual reviews (75% coverage threshold).

### Step 3: Execute Gate G0 (Project Discovery)
Invoke the Discovery Agent with the `skills/project-discovery/` skill:
1. Clarify project goals, primary stakeholders, and target platforms.
2. Populate `contracts/project/contract.json`.
3. Sign and advance the lifecycle gate:
```bash
python core/lifecycle/engine.py --advance G0
```

### Step 4: Execute Gate G1 (Requirements Alignment)
1. Elicit functional requirements, non-functional constraints, and acceptance criteria.
2. Determine whether visual/UI components are required. If not, record a formal G2 design exemption in `contracts/requirements/contract.json`.
3. Advance the lifecycle:
```bash
python core/lifecycle/engine.py --advance G1
```

### Step 5: Execute Gate G2 (Design) or Skip via Exemption
- **If Visual UI exists**: Develop design tokens, layout specifications, and component contracts in `contracts/design/contract.json`.
- **If Backend/CLI/Service**: The lifecycle engine automatically recognizes the exemption signed in G1 and allows advancing directly to G3:
```bash
python core/lifecycle/engine.py --advance G2
```

### Step 6: Execute Gate G3 (Architecture & Contracts)
1. Define component architecture, interfaces, data models, and ADRs in `contracts/architecture/contract.json`.
2. Advance the lifecycle:
```bash
python core/lifecycle/engine.py --advance G3
```

### Step 7: Execute Gate G4 (Controlled Implementation)
1. Break down implementation tasks into discrete workstreams.
2. Delegate tasks to subagents with explicit file ownership.
3. Record progress and commits in `contracts/implementation/contract.json`.
4. Reconcile memory:
```bash
python memory/reconciliation-rules/reconciler.py --update
```
5. Advance to verification:
```bash
python core/lifecycle/engine.py --advance G4
```

### Step 8: Execute Gate G5 (Verification & Independent Review)
1. Run automated test suites and quality evaluations:
```bash
python core/quality/evaluator.py --target . --profile standard
```
2. Spawn an independent reviewer agent to inspect artifacts against `skills/independent-review/`.
3. Record verdicts in `contracts/quality/contract.json`.
4. Advance the gate:
```bash
python core/lifecycle/engine.py --advance G5
```

### Step 9: Execute Gate G6 (Release & Handoff)
1. Generate release manifest, changelog, and handoff documentation in `contracts/release/contract.json`.
2. Advance the lifecycle to completion:
```bash
python core/lifecycle/engine.py --advance G6
```

---

## 3. Adopting the Framework in an Existing Repository

To bring an existing codebase under Project Intelligence governance without disrupting existing code:

### Step 1: Analyze Existing Codebase (Gate G0)
Invoke `skills/existing-project-analysis/`:
1. Discover existing tech stack, test frameworks, linting tools, and CI/CD pipelines.
2. Identify existing architectural patterns and legacy conventions.
3. Record initial state in `memory/durable-knowledge.json`.

### Step 2: Establish Quality Baseline
Configure `contracts/project/contract.json` to acknowledge existing technical debt. Set debt items in `memory/backlog.json` to prevent legacy code from failing new strict gates.

### Step 3: Run Drift Reconciliation
Ensure the working tree is clean and baseline memory is synchronized:
```bash
python memory/reconciliation-rules/reconciler.py --reconcile
```

---

## 4. Handling Defects and Review Rollbacks

When an independent reviewer or verification test identifies a defect in Gate G5:
1. **Never bypass or ignore test failures.**
2. Roll back the lifecycle engine to the appropriate gate:
   - For code defects: Roll back to G4 (`IMPLEMENTATION_IN_PROGRESS`).
   - For architecture flaws: Roll back to G3 (`ARCHITECTURE_REVIEW`).
   - For scope misunderstandings: Roll back to G1 (`REQUIREMENTS_ALIGNMENT`).
```bash
python core/lifecycle/engine.py --rollback G4 --defect-id DEF-001 --reason "Unit test failed in authentication provider"
```
3. The engine logs the defect in `contracts/quality/contract.json`, updates `memory/execution-state.json`, and restores the active gate to G4.
4. Correct the defect, re-verify with evidence, and re-advance through G4 to G5.

---

## 5. Working with Different AI Platforms

### 5.1 Anthropic Claude Code
- **Configuration**: Copy `adapters/claude-code/templates/CLAUDE.md.template` to `CLAUDE.md` in your project root.
- **Enforcement Hooks**: Install `adapters/claude-code/templates/settings.json.template` as `.claude/settings.json`. The included `PreToolUse` hook intercepts file writes and bash commands, verifying gate status before allowing execution.
- **Skills**: Canonical skills in `skills/*/SKILL.md` are directly consumable as custom skills.

### 5.2 GitHub Copilot
- **Instruction File**: Copy `adapters/github-copilot/templates/copilot-instructions.md.template` to `.github/copilot-instructions.md`.
- **Custom Agents**: Agent manifests in `adapters/github-copilot/agents/` map to `.github/agents/` for specialized multi-agent routing.
- **Tool Fallbacks**: Review `adapters/github-copilot/feature-degradation-report.md` for CLI command degradation when operating in IDE-only environments.

### 5.3 OpenAI Codex & Agents SDK
- **Prompt Compilation**: Use `adapters/codex/system-prompt-compilation.md` to format system prompts with memory snapshots.
- **Agent Handoffs**: Review `adapters/codex/handoff-mapping.json` for deterministic agent transfers via OpenAI Agents SDK.

### 5.4 Other Platforms (Cursor, Windsurf, Generic POSIX CLI)
- Use `adapters/other-platforms/cli-runtime-guide.md` and execute transitions directly via `python core/lifecycle/engine.py` and `python memory/reconciliation-rules/reconciler.py`.

---

## 6. Extending the Framework

### 6.1 Adding a New Skill
1. Create a directory `skills/<skill-name>/`.
2. Author `SKILL.md` following the specification in `core/schemas/skill-definition.schema.json`.
3. Author companion `skill.json` declaring inputs, outputs, prerequisites, and gate associations.
4. Validate schema conformance:
```bash
python validation/test_runner.py
```

### 6.2 Adding a New Logical Agent
1. Create a directory `agents/<agent-name>/`.
2. Author `agent.json` conforming to `core/schemas/agent-definition.schema.json`.
3. Author companion `agent.md` with system prompt instructions and handoff contracts.
4. Update `core/capabilities/matrix.json` with the agent's tool permissions.

### 6.3 Adding a New Quality Profile
1. Open `core/quality/profiles.json`.
2. Add a new profile entry specifying coverage thresholds, lint severity, and security policies.
3. Validate profile syntax:
```bash
python core/quality/evaluator.py --selftest
```
