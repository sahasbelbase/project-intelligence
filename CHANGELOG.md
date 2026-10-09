# Changelog

All notable changes to the Project Intelligence framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.1] - 2026-10-09

Summary: The advisor works like a chat and only states facts from the repository; every command on the website works; Windows support.

### Fixed
- **Advisor facts**: Contract paths and gate names come from the real gate data (no invented `contracts/g0/...`, no "Next lifecycle gate" placeholder, no G7). Skills show as Claude Code slash commands (`/project-intelligence:<skill>`) instead of shell commands.
- **Advisor answers**: Filler words no longer drive matches; each answer says why it matched and whether it is confident ("I'm not sure" otherwise). With the local server running, the orchestrator's plan is shown when it routes the work.
- **Website commands**: The Councils page and demo "next" commands use `npx -y @sahasbelbase/project-intelligence ...`; the skills bundle uses `init --mcp false` instead of a Unix-only `cp`; the plugin install is two commands instead of `&&`, which older PowerShell rejects.
- **Shortcuts**: Hints show the Command key on Apple devices and Ctrl elsewhere; Cmd/Ctrl+J focuses the advisor box when already on the page.

### Changed
- **Advisor layout**: Conversation first with the input pinned at the bottom, starter prompts only when empty, a thinking indicator, New conversation, Copy answer, "More detail" folded away, follow-up suggestions, and history kept for the browser session.
- **Header**: The site name and nav no longer wrap; Advisor appears once.
- **Windows**: Python is found as `py -3`, `python` or `python3` (or `PYTHON`); the MCP server starts through Node in the plugin and in `init`; the Stop hook no longer needs `python3`; the Install page explains Windows setup.

## [1.5.0] - 2026-10-09

Summary: Nine specialist agents and skills for legacy code, security, databases, APIs, CI/CD, performance, research and open design, an orchestrator harness, and an advisor on the website.

### Added
- **Agents**: legacy code analyst, modernization architect, security auditor, database migration specialist, API contract engineer, DevOps automation engineer, performance engineer, web-scraping researcher and open design architect, with router entries.
- **Skills**: `api-contract-and-openapi-spec`, `ci-cd-pipeline-engineering`, `database-migration-and-schema-evolution`, `legacy-codebase-knowledge-base`, `open-design-system-and-prototyping`, `runtime-performance-profiling`, `safe-refactoring-and-migration`, `security-audit-and-hardening` and `web-scraping-and-research`.
- **Orchestrator harness (`core/orchestrator/harness.py`)**: Step traces written to `memory/orchestrator-traces/`; step output is simulated.
- **Website advisor**: A local `/api/advisor` endpoint and an index of advisor documents; new PNG favicons.

### Fixed
- **Skill frontmatter**: Quoted values containing ": " in seven new skills, which otherwise loaded in Claude Code with empty metadata; a new test rejects unquoted colon values in any skill.

## [1.4.1] - 2026-10-08

Summary: Published to npm as @sahasbelbase/project-intelligence.

### Changed
- **Install commands**: `npx -y @sahasbelbase/project-intelligence <command>` replaces the `npx -y github:...` form on the website, in the README and in files written by `init` when it runs through npx.

## [1.4.0] - 2026-10-08

Summary: A code reviewer, an idea-to-PRD flow, and six more third-party skills for writing, testing and reviewing code.

### Added
- **Third-party skills**: `ponytail`, `ponytail-review` and `ponytail-audit` from dietrichgebert/ponytail, and `grilling`, `domain-modeling` and `tdd` from mattpocock/skills, copied verbatim with their MIT licenses at pinned commits. mattpocock's `to-spec`, `to-tickets` and `code-review` are listed as install-separately because they depend on his issue-tracker setup.
- **`idea-to-prd` skill**: Questions an idea in rounds until every decision is settled, agrees the vocabulary in a glossary and decision records, writes a PRD that lists the exact CLI commands users will run, and slices it into vertical tickets, all in local files.
- **`code-reviewer` agent** on the development council (now 13 personas): reads the connected code, reports numbered findings with a concrete failing case and the smallest fix, and ends with a verdict.

### Changed
- **`independent-review`**: New review findings standard (concrete case per finding, must/should/nice groups, verdict, what was not checked), adapted from ponytail-review.
- **`controlled-implementation`**: New "smallest complete change" section and test-first guidance, adapted from ponytail and tdd.
- **Council skills**: The developer, test, maintainability, architect, business analyst and product manager personas now carry the new skills; "PRD" and "spec" route to the business analyst, and code-review requests to the code reviewer.
- **Website**: New "From idea to plan" and "Coding craft" skill groups.

## [1.3.0] - 2026-10-08

Summary: Councils run one agent per persona, routing is measured and says when it is unsure, and the demo plays at reading pace.

### Added
- **Independent council agents**: A read-only `council-member` subagent (in the plugin and written to `.claude/agents/` by `init`). The orchestrator starts one per persona for Round 1, each with only its own prompt, so the first round is genuinely blind, then continues the same agents for challenges and revisions. Records state `"blinding": "separate-agents"` or `"single-agent"`; the website shows which. Earlier records are marked `single-agent`.
- **Council CLI**: `council sheet` (every convened persona's Round 1 prompt as JSON), `council prompt --context` (shared background such as a hand-off), `council handoff <decisionId>` (pass one council's decision to the next in tier 3).
- **First independent session**: `dec-routing-keywords-vs-model`, run by four separate agents. Recommendation Pilot, with the test and quality engineer's Test further kept as dissent.
- **Routing evaluation**: 50 labelled requests (`validation/fixtures/routing/cases.json`) and 20 held-out requests never tuned against (`holdout.json`). Accuracy went from 28/50 to 50/50 on the tuning set; held-out accuracy is 16/20 (80%).
- **Routing confidence and overrides**: Every plan reports `confidence` and `evidence`; low-confidence plans tell the agent to confirm or re-plan with `--council`, `--persona` or `--include`.

### Changed
- **Routing**: Keywords are weighted by how many personas share them, specialists are chosen across all councils, and escalation to a council or to tier 3 needs clear signals. Questions ending in "?" are answered directly.
- **Gates (from the council decision)**: Every wrong tier or specialist on either routing set must be flagged low confidence; failures name the request, the expected and actual route and the keywords that fired. Four known held-out misses are recorded as regression cases. The shared routing instructions and CONTRIBUTING.md explain the low-confidence rule and how to fix a routing mistake without tuning the held-out set.
- **Demo playback**: Play appends each message instead of re-rendering the window, fades it in, scrolls smoothly from the current position, and paces at about 2.2 seconds per step with longer pauses at round dividers and decisions. A new "Independent agents" example shows the override in the command.

## [1.2.0] - 2026-10-08

Summary: Install in one step: a Claude Code plugin, an npx command for every other tool, and a no-path MCP setup for Copilot CLI.

### Added
- **Claude Code plugin and marketplace (`.claude-plugin/`)**: `claude plugin marketplace add sahasbelbase/project-intelligence` then `claude plugin install project-intelligence@sahasbelbase`. Loads every framework and third-party skill, the `/project-intelligence:ask` skill and the MCP server. Generated by `npm run build:plugin` from the same instructions the installer uses; a test fails if the generated files are stale.
- **`project-intelligence` command (`bin/project-intelligence`)**: Runs with `npx -y github:sahasbelbase/project-intelligence <command>` today, and is packaged as `@sahasbelbase/project-intelligence` for npm.
- **`mcp` command**: Starts the MCP server on stdio, so Copilot CLI and other clients need no file path: `copilot mcp add project-intelligence -- npx -y github:sahasbelbase/project-intelligence mcp`.

### Changed
- **Runs from the user's project**: `ask`, `council` and the MCP `plan_task` tool read the lifecycle gate from the current project and save council records to its `memory/council-briefs/`, not to the framework's install folder. Suggested next commands use the CLI by full path instead of `python3 -m`, so they work from any folder.
- **Skill frontmatter**: Every skill now has `name` (its folder name) and `description`, the format Claude Code, Antigravity and skill registries expect.
- **Website and README**: Install instructions lead with the plugin and npx.

### Fixed
- **Invalid YAML in 11 skills**: Unquoted values containing ": " made their frontmatter unparseable for strict readers.

## [1.1.0] - 2026-10-08

Summary: Councils with 37 personas, wired into the orchestrator for Claude Code, Copilot CLI and terminals, plus four imported design skills and a rebuilt website with a dark theme.

### Added
- **Orchestrator dispatch (`core/orchestrator/dispatch.py`)**: One planner for every client. Combines the referee's tier and convened personas with the current lifecycle gate and returns the next commands. Exposed as `cli.js ask "<request>"`, the read-only `plan_task` MCP tool (for Copilot CLI and other MCP clients), the installed Claude Code `/orchestrator` command and orchestrator skill, and the website's local `/api/plan` endpoint.
- **SEO and reach**: A new `seo-specialist` agent (`agents/growth/`) on the product council, with two skills: `seo-audit` (titles, social previews, structured data, sitemaps, repository metadata) and `project-reach` (positioning, community launches and measuring results, with no fake reviews or vote rings).
- **Site SEO**: Page metadata, Open Graph and Twitter cards, JSON-LD for the project and its author, a favicon, a social preview image, `robots.txt` and `sitemap.xml`.
- **CLI**: `ask` and `council <plan|prompt|record|list|check>` commands. `council record` validates a finished session file and saves it.
- **Website "How it works" page**: A flowchart of how requests reach skills, agents and councils, and a step-through demo in Claude Code, Copilot CLI and terminal styles, with council rounds from recorded sessions and a follow-up improvement.
- **Dark theme**: Follows the system setting, with a header toggle that remembers the choice. Contrast tests cover both themes.
- **Council referee (`core/council/referee.py`)**: Routes tasks to tiers 0–3, convenes a chair, a critic and up to three relevant specialists, builds persona prompts, validates every round (blinding, a challenge budget of two per persona, answers to every challenge) and assembles schema-valid decision briefs with dissent preserved. CLI: `python3 -m core.council.referee plan|prompt|list|check`.
- **Persona registry (`core/council/personas/`, `core/council/councils.json`)**: Design (13), development (12) and product (12) councils. The product council reuses the existing product manager, business analyst, customer advocate, strategy analyst and SEO specialist agents.
- **Council session records (`memory/council-briefs/`)**: Validated session records that the website displays read-only.
- **Third-party skills (`vendor/skills/`)**: `fixing-accessibility` and `fixing-motion-performance` (ibelick/ui-skills, MIT), `emil-design-eng` and `review-animations` (emilkowalski/skills, MIT), copied verbatim with their licenses and installed alongside the framework skills. Recommended but not redistributed skills are listed in `vendor/skills/registry.json`.
- **Schema checker (`core/council/schema_lite.py`)**: A small Draft-07 subset validator with no dependencies.

### Changed
- **Website (`web/`)**: Rebuilt from the approved mockup with Skills, Councils, Agents, Gates and Install pages. All counts, commands and records are read from repository files at build time. Removed hard-coded test counts, invented benchmarks and unmeasured savings figures.
- **Council protocol**: Councils convene 3–5 personas by relevance instead of the full roster, and each persona raises at most two challenges.
- **Installer**: Copies vendored skills, including their `LICENSE` files, for Claude Code and Antigravity. The installed orchestrator command and skill call this package's CLI by absolute path.
- **MCP server**: 11 tools (adds `plan_task`).

### Fixed
- **CLI exit codes**: `bin/cli.js` now exits with the command's status; previously every command exited 0.
- **Local server**: Binds to 127.0.0.1 by default (set `HOST` to change it).

## [1.0.0] - 2026-10-07

Summary: First release: lifecycle gates, contracts, quality baseline, memory, skills, agents and adapters.

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
