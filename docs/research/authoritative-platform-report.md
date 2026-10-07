# Authoritative Research Report: AI Coding Agent Platform Specifications & Portable Orchestrator Framework

**Date:** October 2026  
**Status:** Comprehensive Multi-Platform Technical Assessment  
**Author:** Platform Capabilities Research Specialist (Subagent)  
**Governing Standards:** AAIF AGENTS.md, Agent Skills Specification (agentskills.io), Model Context Protocol (MCP)

---

## Executive Summary

The AI software engineering landscape has coalesced around several foundational shifts:
1. **Instruction Standardization:** Proprietary rule files converge into the open **`AGENTS.md`** specification (governed by the Linux Foundation's Agentic AI Foundation - AAIF), supported by GitHub Copilot, OpenAI Codex, Google Gemini CLI, and Cursor, alongside backward-compatible vendor conventions (`CLAUDE.md`, `.github/copilot-instructions.md`).
2. **Modular Skills:** The **Agent Skills Specification** (`SKILL.md` via `agentskills.io`) has established a 3-tier progressive disclosure standard (Metadata → Instructions → Bundled Scripts/Assets) adopted across Anthropic, GitHub, and broader agent runtimes.
3. **Execution Safety via Deterministic Hooks:** Prompt-based guardrails have been superseded by deterministic, fail-closed interception layers (Claude Code `PreToolUse` exit code 2 / JSON policy, Copilot CLI hooks, OpenAI Agents SDK tool guardrails).
4. **Open Connectivity:** Anthropic's **Model Context Protocol (MCP)** has become the universal standard for tool and external resource abstraction across Claude Code, GitHub Copilot, and the OpenAI Agents SDK.
5. **State & Memory Evolution:** OpenAI has formally marked the **Assistants API as deprecated** (transitioning to the **Responses API** with native conversation compaction items), while local coding agents adopt **Git-aware memory architectures** (branch-isolated memory, `git notes` decision receipts, and reconciliation upon commit/rebase).

---

## 1. Anthropic Claude Code

### 1.1 Official Specifications
- **Documentation:** `https://docs.anthropic.com/en/docs/agents-and-tools/claude-code`, `https://claude.ai/code`
- **Status:** Generally Available (GA) for CLI and Desktop.
- **Governing Specs:** Anthropic Tool Use API, Agent Skills standard (`agentskills.io`), Model Context Protocol (MCP).

### 1.2 Exact File Paths & Naming Conventions
- Root Project Instructions: `./CLAUDE.md` (read at every session start)
- Local Instructions (gitignored): `./CLAUDE.local.md`
- Global User Instructions: `~/.claude/CLAUDE.md`
- Modular Rule Sets: `.claude/rules/*.md`
- Project Skills: `.claude/skills/<skill-name>/SKILL.md`
- Custom Subagents: `.claude/agents/<agent-name>.md`
- Settings & Hooks: `.claude/settings.json`
- Model Context Protocol: `.mcp.json` (project) or `~/.claude.json` (user)
- Auto-Memory Index: `~/.claude/projects/<project-slug>/memory/MEMORY.md` (~200 line cap)

### 1.3 Capabilities, Tool Restrictions & Hook Lifecycle
- **Hierarchical Instruction Resolution:** Precedence order: `CLAUDE.local.md` > `./CLAUDE.md` > `.claude/rules/*.md` > `~/.claude/CLAUDE.md`.
- **Deterministic Hook Architecture:** Configured in `.claude/settings.json` across events (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`).
- **Interception Contract:** On `PreToolUse`, tool context is passed via `stdin` as JSON.
  - `Exit code 0`: Tool permitted.
  - `Exit code 2`: Interrupt / Veto. Execution aborted; `stderr` returned directly to Claude as corrective feedback.
  - JSON response: `{"permissionDecision": "deny", "reason": "Protected resource"}`.

---

## 2. GitHub Copilot

### 2.1 Official Specifications
- **Documentation:** `https://docs.github.com/en/copilot`, `https://code.visualstudio.com/docs/copilot`
- **Status:** Agent Mode & Skills GA; Copilot CLI GA.
- **Governing Specs:** GitHub Copilot Agent Extensions, VS Code `chatAgents` API, Agent Skills (`agentskills.io`), MCP Registry.

### 2.2 Exact File Paths & Naming Conventions
- Repository Instructions: `.github/copilot-instructions.md`
- Path-Specific Instructions: `.github/instructions/*.instructions.md` (using `applyTo: "<glob>"`)
- Custom Agent Manifests: `.github/agents/<agent-name>.agent.md`
- Agent Skills: `.github/skills/<skill-name>/SKILL.md`
- Copilot CLI Hooks: `.github/hooks/*.json`
- VS Code Settings: `.vscode/settings.json` (`chat.tools.*`)

---

## 3. OpenAI Codex & Agents SDK

### 3.1 Official Specifications
- **Documentation:** `https://developers.openai.com/docs`, `https://platform.openai.com/docs`, `https://github.com/openai/openai-agents-python`
- **Status:** Assistants API Deprecated; Responses API (`/v1/responses`) GA; OpenAI Agents SDK open-source multi-agent standard; Codex CLI GA.

### 3.2 Key Primitives
- **Agents SDK Handoffs:** Formal transfer mechanism between specialized subagents within an execution turn.
- **Three-Tier Guardrail Pipeline:** Input Guardrails -> Tool Guardrails -> Output Guardrails.
- **Responses API Compaction:** Cryptographic compaction items chained via `previous_response_id` prevent context exhaustion.

---

## 4. Cross-Platform Architectural Synthesis

1. **Source of Truth is Vendor-Neutral:** All instructions live in `instructions/` and `skills/`. Platform adapters project them into `CLAUDE.md`, `.github/copilot-instructions.md`, or `AGENTS.md`.
2. **Tools Standardize on MCP:** Tools exposed as Model Context Protocol servers to mount identically across Claude Code, Copilot, and OpenAI SDK.
3. **Deterministic Fail-Closed Hook Interceptors:** Implement exit-code-2 and denial JSON protocol for pre-tool interception across all platforms.
4. **Decouple Generation from Verification:** LLMs plan and write code, but deterministic test engines, linters, and schema checkers certify completion.
