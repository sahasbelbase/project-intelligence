# Feature Degradation Report — Anthropic Claude Code

## 1. Executive Summary
- **Platform**: Anthropic Claude Code (CLI & Desktop)
- **Adapter Version**: 1.0.0
- **Overall Compatibility Rating**: **HIGH (Degradation Level: LOW)**
- **Primary Strengths**: Strong lifecycle hook support (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`), native `SKILL.md` skill discovery, tool denial via exit code 2, robust subagent isolation.
- **Key Limitations**: Subagent communication is isolated (context windows do not share live memory; state must pass via files or final summaries), skills are loaded probabilistically unless triggered explicitly.

---

## 2. Feature-by-Feature Capability Evaluation

| Framework Capability | Canonical Requirement | Claude Code Native Support | Degradation Status | Mitigation / Strategy |
|---|---|---|---|---|
| **Standing Instructions** | Read canonical rules and state at startup | Native `CLAUDE.md` in root read on every session | **FULL SUPPORT** | Adapter compiles `CLAUDE.md` with active gate and rules |
| **Lifecycle Hooks** | Deterministic pre/post execution checks | Supported via `.claude/settings.json` | **FULL SUPPORT** | Native bash scripts run at `SessionStart` and `PreToolUse` |
| **Tool Denial** | Block unapproved commands or file edits | Supported via hook exit code 2 or `{"permissionDecision": "deny"}` | **FULL SUPPORT** | `pre-tool-use.sh` halts destructive commands deterministically |
| **Composable Skills** | Modular on-demand workflow instructions | Native `SKILL.md` directory format with YAML frontmatter | **FULL SUPPORT** | Canonical `skills/*/SKILL.md` directly compatible |
| **Multi-Agent Execution** | Partition work across 9 specialized roles | Isolated subagent spawning via CLI | **PARTIAL SUPPORT** | Subagents cannot share uncommitted memory across processes; rely on local JSON files (`contracts/`, `memory/`) |
| **Persistent 3-Tier Memory** | Durable knowledge, execution state, backlog | Reads and writes local repository files | **FULL SUPPORT** | All state resides in Git-tracked `memory/` files |
| **Automated Verification** | Execute test runners and capture evidence | Bash tool execution with stdout/stderr capture | **FULL SUPPORT** | Verification specialist runs `pytest`/`unittest` directly |

---

## 3. Graceful Degradation Strategy
1. **Subagent Context Sharing**: Because Claude Code subagents run in isolated contexts, subagents communicate asynchronously by committing or writing their outputs to `contracts/` JSON files rather than depending on in-memory message buses.
2. **Hook Execution Environments**: On platforms where bash is unavailable (e.g. Windows without Git Bash or WSL), hook scripts fall back to Python execution (`python .claude/hooks/session-start.py`).
3. **Probabilistic Skill Loading**: To prevent Claude Code from missing skills, `CLAUDE.md` explicitly lists trigger keywords and instructs the model to review the relevant `skills/` path before commencing work.

---

## 4. Manual Fallback Guidance
If Claude Code hooks are disabled by enterprise configuration:
1. Run the Python lifecycle preflight check manually:
   ```bash
   python -m core.lifecycle.engine --verify
   ```
2. Inspect `memory/state.json` to confirm the active gate before issuing prompts.
3. Use slash commands or explicit prompt prefixes: `"Activate skill skills/testing-and-verification"`.
