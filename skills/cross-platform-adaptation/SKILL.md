---
skillId: cross-platform-adaptation
name: Cross-Platform Adaptation
purpose: Project canonical Project Intelligence instructions, skills, and contracts into platform-specific configuration formats (Claude Code, Copilot, Codex, Antigravity) with graceful degradation.
whenToUse:
  - Exporting the project's canonical contracts, skills, and rules to Claude Code (CLAUDE.md, .claude/hooks)
  - Exporting configurations to GitHub Copilot (.github/copilot-instructions.md, .github/skills/)
  - Configuring OpenAI Codex or Agents SDK harnesses with system prompts and function declarations
  - Configuring Google Antigravity environments with system_prompt_rules and native skill discovery
  - Auditing platform capabilities and generating feature degradation reports when a target lacks native hooks or subagents
prerequisites:
  - Canonical instructions and skills established in core/, skills/, and instructions/
  - Access to platform capability matrix in core/capabilities/matrix.json
  - Platform adapter schemas and templates in adapters/
inputs:
  - name: targetPlatforms
    type: array
    description: List of AI coding platforms to adapt for (claude-code, github-copilot, codex-agents-sdk, antigravity)
  - name: exportPath
    type: string
    description: Target root directory for exported adapter configurations
  - name: includeHooks
    type: boolean
    description: Whether to export lifecycle hook scripts for platforms supporting them
procedure:
  - stepNumber: 1
    title: Platform Capabilities Query
    action: Read core/capabilities/matrix.json to determine supported features (standing instructions file, skills format, hook cadences, subagent isolation mode) for each target platform.
  - stepNumber: 2
    title: Canonical Rule and Skill Projection
    action: Map universal instructions from instructions/universal/core-rules.md into the platform's standing instructions file (e.g., CLAUDE.md or .github/copilot-instructions.md).
  - stepNumber: 3
    title: Skill Format Translation
    action: Translate canonical skills into target format: export SKILL.md for Claude Code and Antigravity, or copy to .github/skills/ for GitHub Copilot.
  - stepNumber: 4
    title: Lifecycle Hook Projection
    action: For platforms supporting hooks (Claude Code, Antigravity), generate deterministic hook scripts (e.g., SessionStart memory reconciliation, PreToolUse boundary checks).
  - stepNumber: 5
    title: Graceful Degradation Mapping
    action: For platforms lacking native hooks or subagents (e.g., standard GitHub Copilot), inject manual procedural checklists and prompt guardrails into standing instructions.
  - stepNumber: 6
    title: Degradation Report Generation
    action: Publish docs/usage/platform-degradation-report.md summarizing active features, downgraded hooks, and required manual developer checks per platform."
expectedOutputs:
  - Platform-native configuration files (CLAUDE.md, .github/copilot-instructions.md, etc.)
  - Exported skill definitions in target platform directories
  - Platform degradation report detailing capability trade-offs
applicableApprovalGates:
  - G0
  - G3
  - G6
failureAndRecovery:
  potentialFailures:
    - Target platform does not support executable hooks leading to unverified gate transitions
    - Skill folder convention incompatible with target tool
    - Platform-specific standing instructions file truncated due to context limits
  recoveryStrategy: Inject declarative fallback instructions in standing prompt. Package skills into a single indexed markdown document for constrained environments. Compress instructions by extracting secondary rules to reference docs.
verificationCriteria:
  - Generated platform config files parse without errors in respective platform parsers
  - All mandatory baseline quality rules (BL-001 through BL-007) are preserved across all platforms
  - Degradation report documents 100% of differences between canonical core and target platform capabilities
relevantContractsAndMemory:
  contracts:
    - contracts/project/contract.json
    - contracts/architecture/contract.json
  memoryRecords:
    - durableKnowledge.codingConventions
---

# Cross-Platform Adaptation (`cross-platform-adaptation`)

## 1. Purpose
The `cross-platform-adaptation` skill translates canonical Project Intelligence structures (universal rules, quality profiles, lifecycle gates, composable skills, and contracts) into platform-native configurations. It provides seamless portability across Anthropic Claude Code, GitHub Copilot, OpenAI Codex/Agents SDK, and Google Antigravity. When a target platform lacks advanced runtime capabilities (such as programmatic hooks or isolated subagents), this skill applies principled **graceful degradation** to ensure quality is maintained without breaking native workflows.

## 2. When to Use It
Activate this skill in the following situations:
- Initial project setup when generating platform configuration files (`CLAUDE.md`, `.github/copilot-instructions.md`, etc.).
- Exporting canonical skills into platform-specific directories (`.claude/skills/`, `.github/skills/`, Antigravity builtin skills).
- Generating deterministic hook scripts for platforms that support runtime lifecycle triggers.
- Auditing multi-platform compatibility and compiling degradation reports for engineering teams.

## 3. Prerequisites
- Canonical definitions exist in `core/`, `instructions/`, and `skills/`.
- The capability matrix in `core/capabilities/matrix.json` is loaded.
- Adapters templates are available in `adapters/`.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `targetPlatforms` | `array` | List of target platforms (`claude-code`, `github-copilot`, `codex-agents-sdk`, `antigravity`). |
| `exportPath` | `string` | Root path to write the adapted configurations. |
| `includeHooks` | `boolean` | Flag to generate executable hook scripts where supported. |

## 5. Procedure (Step-by-Step)
1. **Query Platform Capabilities Matrix**:
   - Inspect `core/capabilities/matrix.json` for target platform capabilities:
     - Standing instructions format (`CLAUDE.md`, `.github/copilot-instructions.md`, `system_prompt`).
     - Skills discovery mechanism (`SKILL.md` in subdirectories vs `.github/skills/`).
     - Hook support (`SessionStart`, `PreToolUse`, `PostToolUse`).
     - Subagent model (context-isolated subagent, IDE delegation, or single-agent sequential).

2. **Standing Instructions Projection**:
   - Synthesize `instructions/universal/core-rules.md` and active quality profile into the target file:
     - **Claude Code**: Generate `CLAUDE.md` in workspace root.
     - **GitHub Copilot**: Generate `.github/copilot-instructions.md`.
     - **Codex / Agents SDK**: Generate `system_prompt.txt` or Python agent definition.
     - **Antigravity**: Generate `system_prompt_rules.md` or workspace instructions.

3. **Skill Format Adaptation**:
   - For platforms supporting standard `SKILL.md` (Claude Code, Antigravity): Copy or symlink `skills/<skill-id>/SKILL.md`.
   - For GitHub Copilot: Copy skills into `.github/skills/<skill-id>/SKILL.md`.
   - For single-file prompt environments: Compile an aggregated skills reference table.

4. **Lifecycle Hook Code Generation**:
   - For platforms supporting hooks:
     - Generate `SessionStart` hook: runs `git status` check, verifies working tree, loads memory state.
     - Generate `PreToolUse` hook: checks file ownership boundaries before edits.
     - Generate `PostToolUse` hook: runs linter on edited files.

5. **Graceful Degradation Mapping**:
   - Where programmatic hooks are absent (e.g. GitHub Copilot):
     - Convert hook checks into mandatory, highlighted markdown instructions at the top of `.github/copilot-instructions.md`.
     - Instruct the model to self-execute pre-flight git checks and boundary verifications before file edits.
   - Where subagent isolation is absent:
     - Format tasks as sequential, atomic phases for single-agent execution with explicit pause checkpoints.

6. **Platform Degradation Report**:
   - Author `docs/usage/platform-degradation-report.md` detailing:
     - Full capability matrix across supported platforms.
     - Exact degradation policies applied.
     - Manual verifications required by developers on degraded platforms.

## 6. Expected Outputs
- Generated platform configuration files (`CLAUDE.md`, `.github/copilot-instructions.md`).
- Adapted skill directories matching platform expectations.
- Comprehensive platform degradation report in `docs/usage/platform-degradation-report.md`.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G0 (Discovery)**: Bootstraps platform-native configuration at project kickoff.
- **Gate G3 (Architecture)**: Codifies multi-platform integration strategies.
- **Gate G6 (Handoff)**: Finalizes exported configs for user distribution.

## 8. Failure and Recovery Behavior
- **Context Length Overflow in Standing Instructions**: Condense verbose prose into bulleted imperatives; reference external docs for non-critical explanations.
- **Hook Script Execution Denied**: Degrade gracefully to prompt-based instructions and log warning in the degradation report.
- **Unsupported Custom Tool Syntax**: Map custom tools to standard CLI execution patterns.

## 9. Verification Criteria
- All generated platform files conform to the target tool's official documentation specifications.
- Anti-slop baseline rules (BL-001 through BL-007) are preserved across all platforms without omission.
- Degradation report clearly distinguishes automated hook enforcement from manual prompt compliance.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/project/contract.json`
  - `contracts/architecture/contract.json`
- **Memory Records**:
  - `durableKnowledge.codingConventions`
