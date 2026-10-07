# Feature Degradation Report — GitHub Copilot

## 1. Executive Summary
- **Platform**: GitHub Copilot (VS Code Extension, JetBrains, and GitHub CLI)
- **Adapter Version**: 1.0.0
- **Overall Compatibility Rating**: **MODERATE (Degradation Level: MEDIUM)**
- **Primary Strengths**: Widespread developer adoption, native multi-agent chat support via `@agent` syntax in `.github/agents/`, workspace instruction hierarchies (`.github/instructions/`), local workspace file access.
- **Key Limitations**: **Absence of deterministic client-side hooks**. Unlike Claude Code or Antigravity, GitHub Copilot does not provide deterministic `PreToolUse` or `SessionStart` hooks in the local IDE to block shell commands or intercept file edits programmatically.

---

## 2. Feature-by-Feature Capability Evaluation

| Framework Capability | Canonical Requirement | GitHub Copilot Native Support | Degradation Status | Mitigation / Strategy |
|---|---|---|---|---|
| **Standing Instructions** | Read rules and state at startup | Native `.github/copilot-instructions.md` | **FULL SUPPORT** | Adapter generates high-signal root instructions |
| **Path-Specific Rules** | Context rules based on active files | Native `.github/instructions/**/*.instructions.md` | **FULL SUPPORT** | Maps rules to `contracts/` and `src/` paths |
| **Custom Agents** | 9 distinct agent definitions | Native `.github/agents/*.agent.md` | **FULL SUPPORT** | Maps all 9 agents to `@agent` chat personas |
| **Lifecycle Hooks** | Intercept pre/post execution | **UNSUPPORTED** in local IDE client | **HIGH DEGRADATION** | Compensate via pre-commit git hooks and GitHub Actions CI validation workflows |
| **Tool Denial** | Exit code 2 / block unapproved commands | **UNSUPPORTED** at client level | **HIGH DEGRADATION** | Rely on system prompt constraints and external pre-commit filters |
| **Persistent Memory** | 3-tier memory across sessions | Reads/writes repository files | **FULL SUPPORT** | Memory stored in Git-tracked `memory/` files |
| **Multi-Agent Subtasks** | Parallel task execution with isolated context | Manual `@agent` switching in IDE | **PARTIAL SUPPORT** | User or IDE extension switches agents across lifecycle gates |

---

## 3. Graceful Degradation Strategy
1. **Hook Emulation via Pre-Commit**: Because Copilot cannot intercept tools in real-time, the adapter provides a Git `pre-commit` hook that executes `python -m unittest validation/schema-tests/test_schemas.py` and verifies lifecycle gate compliance before any commit is accepted.
2. **CI Enforcement**: GitHub Actions workflows run the full test suite (`validation/`) and check that locked contracts were not altered without approval.
3. **Prompt Guardrail Reinforcement**: The root `.github/copilot-instructions.md` includes explicit negative constraints (anti-slop directives, command allowlists) to minimize non-compliant tool executions.

---

## 4. Manual Fallback Guidance
When operating within GitHub Copilot:
1. Always tag the appropriate agent for the active lifecycle gate (e.g., `@orchestrator` for gate checks, `@implementation` for coding).
2. Manually execute verification tests in the terminal before committing:
   ```bash
   python -m unittest validation/schema-tests/test_schemas.py
   ```
3. Never bypass failed pre-commit hooks using `--no-verify`.
