# Claude Code Skill Mapping Architecture

## 1. Skill Discovery & Directory Layout
Claude Code discovers skills placed in directory hierarchies containing a `SKILL.md` file with standard YAML frontmatter.
Project Intelligence defines 12 canonical skills in `skills/`. Each skill directory satisfies both the canonical Project Intelligence schema (`core/schemas/skill-definition.schema.json`) and the Claude Code runtime format.

```
project-intelligence/
└── skills/
    ├── project-discovery/
    │   └── SKILL.md
    ├── existing-project-analysis/
    │   └── SKILL.md
    ├── design-discovery/
    │   └── SKILL.md
    ├── design-system-engineering/
    │   └── SKILL.md
    ├── architecture-and-contracts/
    │   └── SKILL.md
    ├── phase-planning/
    │   └── SKILL.md
    ├── controlled-implementation/
    │   └── SKILL.md
    ├── testing-and-verification/
    │   └── SKILL.md
    ├── independent-review/
    │   └── SKILL.md
    ├── failure-recovery-and-improvement/
    │   └── SKILL.md
    ├── cross-platform-adaptation/
    │   └── SKILL.md
    └── documentation-and-handoff/
        └── SKILL.md
```

---

## 2. YAML Frontmatter Specification for Claude Code

Every `SKILL.md` in the `skills/` directory includes standard YAML frontmatter:

```yaml
---
name: architecture-and-contracts
description: Design decoupled system architectures, define component boundaries and interface contracts, formulate ADRs, and specify security postures.
triggers:
  - "architect system"
  - "draft ADR"
  - "define interfaces"
  - "gate G3"
---
```

When Claude Code detects these natural language patterns in user queries or orchestrator commands, it auto-loads the skill instructions into the prompt context.

---

## 3. Skill Invocation Matrix

| Canonical Skill ID | Claude Code Trigger Phrases | Primary Invoking Role |
|---|---|---|
| `orchestrator` | `orchestrator`, `govern gates`, `lifecycle status`, `next action` | `orchestrator` |
| `project-discovery` | `discovery`, `init project`, `inspect environment`, `gate G0` | `discovery` / `orchestrator` |
| `requirements-analysis` | `requirements`, `user stories`, `acceptance criteria`, `gate G1` | `orchestrator` |
| `existing-project-analysis` | `analyze codebase`, `extract conventions`, `brownfield` | `discovery` |
| `design-discovery` | `visual requirements`, `design tokens`, `gate G2` | `design` |
| `design-system-engineering`| `design system`, `component states`, `accessibility audit`, `WCAG` | `design` |
| `architecture-and-contracts`| `architect system`, `draft ADR`, `interface contracts`, `gate G3` | `architecture` |
| `phase-planning` | `plan phases`, `task decomposition`, `file ownership`, `WBS` | `planning` |
| `controlled-implementation`| `implement task`, `write code`, `bounded edit`, `gate G4` | `implementation` |
| `testing-and-verification` | `run tests`, `verify implementation`, `collect evidence`, `lint` | `verification` |
| `independent-review` | `independent review`, `code audit`, `anti-slop check`, `gate G5` | `independent-review` |
| `failure-recovery-and-improvement` | `test failure`, `fix defect`, `task retry`, `recovery` | `implementation` / `verification` |
| `cross-platform-adaptation` | `adapt platform`, `compile CLAUDE.md`, `compile copilot instructions` | `orchestrator` |
| `documentation-and-handoff`| `generate release notes`, `sync memory`, `gate G6 handoff` | `documentation-and-memory` |
