# Feature Degradation Report — Generic POSIX CLI & IDEs

## 1. Executive Summary
- **Platform Scope**: Generic IDEs (Cursor, Windsurf, JetBrains AI), Terminal Tools (Aider, CLI scripts), and Headless Shells.
- **Adapter Version**: 1.0.0
- **Overall Compatibility Rating**: **ACCESSIBLE WITH MANUAL OVERSIGHT (Degradation Level: HIGH)**
- **Primary Strengths**: Universal ubiquity, zero external runtime requirements, direct filesystem access, standard terminal execution.
- **Key Limitations**: No native agent-to-agent delegation, no client-side tool denial hooks, no automated context partitioning between roles.

---

## 2. Multi-Environment Capability Matrix

| Platform / Tool | Standing Rules Support | Skill Support | Agent Persona Support | Hook Interception | Primary Degradation Mode |
|---|---|---|---|---|---|
| **Cursor** | `.cursorrules` / `.cursor/rules` | Manual reference | System prompt prompts | None | Prompts must manually specify active role and gate |
| **Windsurf** | `.windsurfrules` | Manual reference | System prompt prompts | None | Relies on Git pre-commit hooks for gate blocking |
| **Aider** | `--message-file`, `.aider.conf.yml` | Read files on demand | Single agent switching | None | User switches role prompts across lifecycle phases |
| **Cline (VS Code)** | Custom instructions in extension settings | Manual reference | Single agent | None | Requires manual contract inspection |
| **POSIX Shell / CI** | Environment variables | CLI scripts | Headless Python runners | Pre-commit hooks | Fully deterministic via Python validation suite |

---

## 3. Graceful Degradation Strategy
1. **Fallback to Single-Agent Sequential Mode**: Instead of spawning concurrent subagents, the single model executes the lifecycle gates sequentially (G0 -> G1 -> G2 -> G3 -> G4 -> G5 -> G6), pausing between gates for human review.
2. **Git-Centric Verification**: Because real-time tool denial hooks are absent, enforcement moves to Git commit time via `.git/hooks/pre-commit` and repository CI checks.
3. **File-Based Communication**: All state passing occurs through durable JSON files in `contracts/` and `memory/`, eliminating reliance on proprietary inter-agent messaging protocols.
