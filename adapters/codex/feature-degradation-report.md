# Feature Degradation Report — OpenAI Codex & Agents SDK

## 1. Executive Summary
- **Platform**: OpenAI Codex / OpenAI Agents SDK
- **Adapter Version**: 1.0.0
- **Overall Compatibility Rating**: **HIGH (Degradation Level: LOW)**
- **Primary Strengths**: Native programmatic agent handoffs via `Handoff` objects, strict schema validation support (`"strict": true` for JSON function calling), programmatic guardrails, and flexible system prompt compilation.
- **Key Limitations**: Unlike Claude Code, Codex lacks a single standardized repository root file (such as `CLAUDE.md`) that is automatically picked up without an SDK runner or developer CLI integration.

---

## 2. Feature-by-Feature Capability Evaluation

| Framework Capability | Canonical Requirement | Codex / Agents SDK Native Support | Degradation Status | Mitigation / Strategy |
|---|---|---|---|---|
| **Standing Instructions** | Read rules and state at startup | Injected via System Prompt / Constitution | **FULL SUPPORT** | Adapter compiles system prompt dynamically |
| **Lifecycle Hooks** | Intercept pre/post execution | Supported via Python SDK event listeners | **FULL SUPPORT** | Pre-tool hooks implemented in Python runner |
| **Tool Denial** | Block unauthorized operations | Supported via Strict Function Calling schemas & Guardrail exceptions | **FULL SUPPORT** | Read-only agents simply omit file editing tools |
| **Composable Skills** | Modular on-demand workflow instructions | Injected as tool definitions or dynamic prompts | **FULL SUPPORT** | Skills parsed and loaded into agent toolkits |
| **Multi-Agent Handoffs** | Programmatic delegation across 9 roles | Native `Handoff` primitives in Agents SDK | **FULL SUPPORT** | Handoff targets mapped directly to SDK functions |
| **Persistent 3-Tier Memory** | Durable knowledge, state, backlog | Reads/writes local JSON files | **FULL SUPPORT** | Handled natively via local file access |
| **Automated Verification** | Test runner execution & telemetry | Standard subprocess tool calls | **FULL SUPPORT** | Verification agent executes tests via terminal runner |

---

## 3. Graceful Degradation Strategy
1. **Headless Execution Runner**: Because Codex can be executed via headless scripts or CLI integrations, the adapter provides a standalone Python bootstrap script (`python -m adapters.codex.runner`) that initializes the agent swarm and loads repository state from `memory/state.json`.
2. **Strict Schema Constraints**: Uses OpenAI strict JSON schema mode for all contract generation tasks, completely preventing malformed contract envelopes.

---

## 4. Manual Fallback Guidance
When running Codex without the Agents SDK (e.g., standard ChatGPT or generic Codex CLI):
1. Copy the compiled system prompt from `adapters/codex/templates/system-prompt.template` into the custom instructions or initial message.
2. Manually execute verification tests using standard shell commands.
3. Validate output contracts against `core/schemas/` before committing.
