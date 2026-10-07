# Changelog

All notable changes to the Project Intelligence framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-07

### Added
- **Core Schemas (`core/schemas/`)**: 12 JSON Schema Draft-07 canonical schemas covering contract envelopes, project contracts, requirements contracts, design contracts, architecture contracts, implementation contracts, quality contracts, release contracts, memory, lifecycle, agent definitions, and skill definitions.
- **Deterministic Lifecycle Engine (`core/lifecycle/`)**: 7-gate finite state machine (G0 through G6) with formal design exemption handling and defect rollback logic implemented in `core/lifecycle/engine.py`.
- **Quality Evaluator and Profiles (`core/quality/`)**: Anti-slop engineering baseline (BL-001 through BL-007) forbidding decorative emojis, fake credentials, and unimplemented stubs (`TODO: implement later`, `pass`). Executable evaluator supporting 5 specialized quality profiles (Prototype, Standard, Production-Ready, Security-Sensitive, Design-Intensive).
- **Git-Aware 3-Tier Memory (`memory/`)**: Long-term durable knowledge (`durable-knowledge.json`), short-term execution state (`execution-state.json`), and medium-term backlog (`backlog.json`). Executable drift detection and reconciliation engine (`reconciler.py`) with secret exposure auditing.
- **Canonical Concrete Contracts (`contracts/`)**: Concrete signed JSON contracts representing all 7 lifecycle gates (G0 through G6).
- **12 Canonical Skills (`skills/`)**: Portable skills complete with both `SKILL.md` specifications and companion `skill.json` manifests:
  - `skills/project-discovery`
  - `skills/existing-project-analysis`
  - `skills/design-discovery`
  - `skills/design-system-engineering`
  - `skills/architecture-and-contracts`
  - `skills/phase-planning`
  - `skills/controlled-implementation`
  - `skills/testing-and-verification`
  - `skills/independent-review`
  - `skills/documentation-and-handoff`
  - `skills/cross-platform-adaptation`
  - `skills/failure-recovery-and-improvement`
- **Hierarchical Instructions (`instructions/`)**: Layered instructions structured into Universal Core Rules (`instructions/universal/`), Profile-Specific Rules (`instructions/profiles/`), and Task-Specific Execution Rules (`instructions/tasks/`).
- **9 Logical Agent Definitions (`agents/`)**: Declarative definitions (`agent.json`) and system prompt instructions (`agent.md`) for:
  - Orchestrator Agent
  - Discovery Agent
  - Design Agent
  - Architecture Agent
  - Planning Agent
  - Implementation Agent
  - Verification Agent
  - Independent Review Agent
  - Documentation and Memory Agent
- **Platform Adapters (`adapters/`)**: Native translation rules, manifests, templates, and feature degradation reports for:
  - Anthropic Claude Code (`adapters/claude-code/`) with `PreToolUse` shell enforcement hooks.
  - GitHub Copilot (`adapters/github-copilot/`) with `.github/agents` and `.github/copilot-instructions.md`.
  - OpenAI Codex (`adapters/codex/`) with Responses API prompt compilation and Agents SDK handoff rules.
  - Other Platforms (`adapters/other-platforms/`) with POSIX CLI and IDE automation scripts.
- **Automated Validation Engine (`validation/`)**: Comprehensive test runner (`test_runner.py`) executing 23 automated tests across 5 test suites (schemas, lifecycle transitions, anti-slop rules, memory drift, adapter conformance) with zero external pip dependencies.
- **Documentation (`docs/`)**: Architecture overview, usage and operations guide, authoritative platform research reports, architecture decision records (ADRs), work ledger, and independent review audit report.
