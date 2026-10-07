# Platform Capability Matrix & Research Analysis

## 1. Executive Summary
This document establishes the verified capability landscape for modern AI coding agent platforms (Anthropic Claude Code, GitHub Copilot, OpenAI Codex/Agents SDK, and Google Antigravity). It identifies the canonical integration touchpoints, limitations, tool restriction models, hook cadences, and execution boundaries needed to architect the portable, local-first **Project Intelligence** framework.

**Research Date:** October 2026  
**Status:** All referenced capabilities are documented from official developer portals and documentation.

---

## 2. Multi-Platform Capability Matrix

| Capability Dimension | Anthropic Claude Code | GitHub Copilot | OpenAI Codex / Agents SDK | Google Antigravity | Portable Framework Strategy |
|---|---|---|---|---|---|
| **Standing Instructions** | `CLAUDE.md` (root, project, global ~/.claude) | `.github/copilot-instructions.md`, path `.github/instructions/**/*.instructions.md` | System Prompt / Constitution, `AGENTS.md` | Built-in rules, system instructions | Canonical `instructions/universal/` compiled to platform instruction files |
| **Reusable Skills** | `SKILL.md` in directory with YAML frontmatter | `.github/skills/` or `.agents/skills/` | `SKILL.md` / Agent Skills specification | `SKILL.md` with YAML frontmatter + scripts | Universal `skills/*/SKILL.md` portable across all engines |
| **Custom Agents** | Subagents configured with YAML frontmatter + prompt | `.github/agents/*.agent.md` (`@agent-name`) | Agent definitions via Agents SDK / AgentKit | Agent definitions (tools, model, system prompt) | Declarative agent specs in `agents/*/agent.json` and `.md` |
| **Subagent Delegation** | Supported; isolated context, returns summary | Supported via `@agent` delegation in IDE/CLI | Supported via Handoffs in Agents SDK | Supported via `invoke_subagent` / `define_subagent` | Canonical orchestrator decomposition contract with isolated boundaries |
| **Lifecycle Hooks** | Deterministic hooks (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`) | GitHub Actions CI, pre-commit, extension hooks | Python/TS event listeners in SDK loop | Pre/post tool execution, SessionStart hooks | Canonical gate validation engine runnable as CLI or hook script |
| **Tool Restrictions** | Hook exit code 2 / `permissionDecision: deny` | Tool permissions, safe mode, enterprise policy | Tool declaration schemas & strict function calling | Sandboxed CLI execution & tool authorization | Explicit tool permission manifests in agent & task contracts |
| **Persistent Memory** | `CLAUDE.md`, auto-memory, local project files | Repo workspace files, `.github/` context | State variables, local storage, vector store | Repository files, conversation transcripts | Git-aware durable memory in `memory/` (durable, execution, backlog) |
| **Deterministic Automation** | `.claude/settings.json` hook scripts | Workflow YAMLs, VS Code tasks | Custom Python runtime scripts | Shell command execution, scheduled cron/timers | Standard Python validation CLI zero-dependency test runner |
| **Local-First Privacy** | Operates on local filesystem via CLI | Operates on local workspace | Local script or client execution | Local filesystem & sandbox execution | Zero remote data leakage; all memory and state stored in Git repo |

---

## 3. Detailed Platform Analysis

### 3.1 Anthropic Claude Code
- **Primary Documentation Sources:**
  - Anthropic Documentation: *Claude Code Overview & Architecture* (`https://docs.anthropic.com/en/docs/claude-code`)
  - Anthropic Engineering: *Extending Claude Code with Skills and Hooks* (`https://docs.anthropic.com`)
  - Status: General Availability (CLI & Desktop).
- **Configuration Conventions:**
  - Root configuration: `CLAUDE.md` in repository root. Read automatically at the start of every session.
  - Settings: `.claude/settings.json` (project-level) or `~/.claude/settings.json` (user-level).
  - Skills: Subdirectories containing `SKILL.md` with YAML frontmatter (`name`, `description`, `trigger`).
  - Hooks: Deterministic JSON configuration supporting `SessionStart`, `PreToolUse`, `PostToolUse`, and `Stop`. Tool blocking supported via exit code 2 or JSON `{"permissionDecision": "deny"}`.
- **Key Constraints:**
  - Skills are probabilistically selected unless invoked via slash commands.
  - Subagents run in isolated context windows and cannot share uncommitted memory except through files or final summaries.

### 3.2 GitHub Copilot
- **Primary Documentation Sources:**
  - GitHub Docs: *Customizing Copilot with instructions and agents* (`https://docs.github.com/copilot`)
  - GitHub Next: *Agent Skills and Workspace Rules* (`https://github.com/features/copilot`)
  - Status: GA in VS Code, JetBrains, and GitHub CLI.
- **Configuration Conventions:**
  - Root instructions: `.github/copilot-instructions.md`.
  - Modular/path-specific instructions: `.github/instructions/**/*.instructions.md`.
  - Custom Agents: `.github/agents/*.agent.md`. Invoked explicitly via `@agent-name`.
  - Skills: `.github/skills/` directory.
- **Key Constraints:**
  - Different behavior between GitHub.com web chat, VS Code extension, and Copilot CLI.
  - Subagent invocation requires explicit configuration in IDE settings.

### 3.3 OpenAI Codex & Agents SDK
- **Primary Documentation Sources:**
  - OpenAI Developer Docs: *Agents SDK & Agentic Workflows* (`https://platform.openai.com/docs`)
  - OpenAI Cookbook: *Orchestrating Multi-Agent Systems* (`https://cookbook.openai.com`)
  - Status: Documented / GA SDK.
- **Configuration Conventions:**
  - System prompt acts as the "Constitution" (role, behavioral boundaries, rules).
  - Modular workflows via Agent Skills (`SKILL.md`).
  - Agent handoffs and subagent hierarchies handled via programmatic orchestration.
- **Key Constraints:**
  - No single standardized root markdown file across all 3rd party tools (some use `AGENTS.md` or system prompts), necessitating a translation adapter.

### 3.4 Google Antigravity
- **Primary Documentation Sources:**
  - Antigravity Customizations Guide & Built-in Skills (`agy-customizations`, `antigravity-guide`).
  - Status: Active Runtime Environment.
- **Configuration Conventions:**
  - Built-in subagent invocation: `invoke_subagent`, `define_subagent`, `manage_subagents`.
  - Skills: `SKILL.md` with YAML frontmatter + optional scripts.
  - Rules and system prompts in agent configuration.

---

## 4. Architectural Implications for Project Intelligence

1. **Decouple Core from Runtimes**: The core framework cannot depend on any single vendor's CLI or configuration file. Universal contracts must be stored in standard JSON / Markdown.
2. **Compile-Down Adapters**: Provide declarative adapter definitions in `adapters/` that translate canonical rules into `CLAUDE.md`, `.github/copilot-instructions.md`, or system prompt files without modifying canonical sources.
3. **Dual Execution Mode**: Support both **automated deterministic validation** (via hooks or CLI validation tests) and **in-chat agent guidance** (via skills and instructions).
4. **Git-Aware Durable Memory**: Because context windows reset across sessions and platforms, the git working tree and structured memory files (`memory/state.json`, `memory/durable-knowledge.json`, `memory/backlog.json`) represent the single source of truth.
5. **Quality Gates (G0-G6)**: Deterministic approval gates prevent hallucinated completions, unverified claims, and scope expansion across all platforms.
