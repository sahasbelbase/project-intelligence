# Contributing to Project Intelligence

Thank you for contributing to Project Intelligence. This project is a local-first, platform-agnostic AI project orchestration framework governed by strict quality standards, deterministic lifecycle gates, and anti-slop engineering principles.

To maintain the architectural integrity of the framework, all contributors (both human developers and AI coding agents) must adhere to the rules outlined in this document.

---

## 1. Core Contribution Principles

1. **Evidence-Based Acceptance**: Any contribution that adds or modifies code, schemas, or contracts must include automated test coverage and reproducible verification evidence. Self-reported claims of confidence are not acceptable evidence.
2. **Deterministic Lifecycle Gates**: Code modifications must adhere to the 7-gate lifecycle state machine (G0 to G6). Never bypass gates or skip validation phases.
3. **Anti-Slop Baseline (BL-001 through BL-007)**:
   - Zero decorative emojis in code, documentation, schemas, or commit messages.
   - Zero unimplemented placeholders (`TODO: implement later`, `pass # placeholder`, `FIXME`).
   - Zero fake production data, dummy credentials, or synthetic mocks disguised as verified integrations.
   - Zero secret exposure. Never commit API keys, private tokens, or credentials.
   - Strictly honest verification statuses: `PASSED`, `FAILED`, `BLOCKED`, `SKIPPED`, `UNAVAILABLE`.
4. **Zero External PIP Dependencies for Core**: The core schemas, lifecycle engine, quality evaluator, memory reconciler, and test runner must remain runnable on standard Python 3.10+ without requiring third-party package installations.

---

## 2. Development and Testing Workflow

### 2.1 Branching and Workstream Allocation
- Create a dedicated feature branch from `main`:
  ```bash
  git checkout -b feature/your-feature-name
  ```
- If operating as a multi-agent team or delegating subtasks, each subagent or workstream must maintain exclusive file ownership. Coordinated edits across multiple agents must be synchronized through shared schemas and contracts.

### 2.2 Running Automated Validation
Before submitting any pull request or committing changes, run the validation test runner from the repository root:
```bash
python validation/test_runner.py
```
All existing and newly added test cases must report `PASSED`.

### 2.3 Memory and Git Synchronization
Ensure that project memory is updated and synchronized with your current branch and commit:
```bash
python memory/reconciliation-rules/reconciler.py --update
```
Verify that no working tree drift is reported:
```bash
python memory/reconciliation-rules/reconciler.py --reconcile
```

---

## 3. Extending Framework Components

### 3.1 Adding or Modifying Schemas (`core/schemas/`)
- Schemas must strictly follow JSON Schema Draft-07.
- Every schema modification must maintain backward compatibility or provide an upward migration rule in `core/versioning/migration_rules.json`.
- Add test coverage in `validation/schema-tests/test_schemas.py`.

### 3.2 Adding or Modifying Skills (`skills/`)
- Each skill must reside in its own subdirectory (`skills/<skill-name>/`).
- Each skill requires both a markdown specification (`SKILL.md`) conforming to the 10 canonical sections, and a companion JSON definition (`skill.json`).
- Ensure the skill specifies its applicable lifecycle gates, prerequisites, expected inputs, and recovery procedures.

### 3.3 Adding or Modifying Agents (`agents/`)
- Each logical agent must reside in `agents/<agent-name>/`.
- Provide both `agent.json` (declaring role ID, mission, tool permissions, input/output contracts) and `agent.md` (system prompt instructions and handoff targets).
- Update the capability taxonomy in `core/capabilities/matrix.json`.

### 3.4 Adding or Modifying Adapters (`adapters/`)
- Adapters must map canonical skills and instructions to platform-native configuration files (e.g. `CLAUDE.md`, `.github/copilot-instructions.md`, Codex Responses API).
- Every adapter must include a `feature-degradation-report.md` detailing which capabilities are natively supported, degraded, or unsupported.
- Adapters must never strip or relax mandatory baseline quality rules (BL-001 through BL-007).

---

## 4. Pull Request and Gate Review Process

Every pull request undergoes an independent review process equivalent to Gate G5:
1. **Automated Verification**: Automated tests execute via `validation/test_runner.py`.
2. **Quality Evaluation**: `core/quality/evaluator.py` executes against the changes.
3. **Independent Audit**: An independent reviewer or maintainer audits the changes against requirements, checks for regressions, and verifies documentation completeness.
4. **Approval**: Once verified, the release contract (`contracts/release/contract.json`) is updated, and the PR is approved for merge.

## Fixing a routing mistake

1. Reproduce it: `node bin/cli.js ask --json "<the request>"` and read `confidence` and `evidence`.
2. Add the request to `validation/fixtures/routing/cases.json` with the route it should get. Never edit `holdout.json`; it measures accuracy on requests the router was not tuned on.
3. Adjust keywords in `core/council/councils.json` only if the fix is general, not a single-word patch for one request.
4. Run `python3 -m unittest validation/universal-tests/test_routing_eval.py`. Failures name the request, the expected and actual route, and the keywords that fired.
5. If the held-out score drops, the change overfits; revert it.

