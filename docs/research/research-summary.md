# Research Summary — AI Coding Agents & Multi-Agent Orchestration

## 1. Scope of Investigation
This research investigated official documentation, best practices, and runtime architectures across major AI coding platforms:
- Anthropic Claude Code
- GitHub Copilot
- OpenAI Codex & Agents SDK
- Google Antigravity & Agentic Workspaces
- Portable Multi-Agent Patterns (Actor Model, Workflow Contracts, Finite State Machines, Git-backed memory)

## 2. Key Synthesis & Insights

### 2.1 The Principle of "Instructions vs. Skills vs. Hooks"
Across all modern platforms, a 3-tier operational taxonomy has emerged:
1. **Always-On Standing Brief (Instructions)**: System prompt, `CLAUDE.md`, `.github/copilot-instructions.md`. Must remain concise, high-level, and focused on behavioral boundaries, coding standards, and architectural conventions.
2. **On-Demand Repeatable Procedures (Skills)**: Folder-based `SKILL.md` documents with YAML frontmatter. Loaded conditionally or invoked explicitly when a multi-step procedure is needed.
3. **Deterministic Guardrails (Hooks/Validation)**: Programmatic scripts executing at lifecycle checkpoints (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`, or CI tests). Cannot be bypassed by model hallucinations.

### 2.2 Subagent Delegation & Isolation
- Uncontrolled single-agent execution on complex codebases leads to "context collapse", forgotten constraints, and tool spam.
- Effective multi-agent execution requires **bounded work units**, **exclusive file ownership**, and **explicit handoff contracts**.
- Subagents must return structured evidence (what was changed, what was tested, exit code, diff) rather than open-ended prose.

### 2.3 Durable Memory & Git Reconciliation
- Chat history is ephemeral; repository files are durable.
- If an agent starts a new session after external Git modifications (e.g. human developer commits, rebases, or branch changes), the agent must reconcile its recorded execution state with `git status` and `git log` before taking action.

### 2.4 Anti-Slop & Quality Enforcement
- Common AI failure modes: gratuitous decorative emoji, empty TODOs, untested mocks presented as working features, unnecessary dependency bloat, and silent deletion of unrelated code.
- Mitigation requires **Mandatory Baseline Quality Profiles** and **Evidence-Based Completion Gates (G0 through G6)**. Every claimed check must record an honest status: `Passed`, `Failed`, `Blocked`, `Skipped`, or `Unavailable`.

---

## 3. Bibliographic Citations
1. Anthropic, *Claude Code Documentation: Architecture, Skills, and Hooks*, 2026. `https://docs.anthropic.com`
2. GitHub, *GitHub Copilot Custom Instructions and Multi-Agent Orchestration*, 2026. `https://docs.github.com/copilot`
3. OpenAI, *OpenAI Agents SDK and Agentic Design Patterns*, 2026. `https://platform.openai.com/docs`
4. Google DeepMind, *Antigravity Customization Architecture & Skills Framework*, 2026.
