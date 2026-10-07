# GitHub Copilot Skill Mapping Architecture

## 1. Skill Representation in GitHub Copilot
GitHub Copilot supports skills via workspace configurations located at `.github/skills/` or `.agents/skills/`.
When migrating or deploying Project Intelligence into a GitHub Copilot environment, the canonical skills defined in `skills/` are symlinked or copied to `.github/skills/`.

---

## 2. Structure & Packaging

Each Copilot skill directory includes:
- `SKILL.md`: The primary skill prompt with instructions and step-by-step guidance.
- Optional helper scripts or validation templates in a `scripts/` subdirectory.

```
.github/
└── skills/
    ├── project-discovery/
    │   └── SKILL.md
    ├── architecture-and-contracts/
    │   └── SKILL.md
    ├── controlled-implementation/
    │   └── SKILL.md
    ├── testing-and-verification/
    │   └── SKILL.md
    ├── independent-review/
    │   └── SKILL.md
    └── documentation-and-handoff/
        └── SKILL.md
```

---

## 3. Skill Invocation Workflow in Copilot
1. **Explicit Tagging**: In Copilot Chat (VS Code / JetBrains / CLI), users can type `#skill:<skill-name>` or reference `@agent` which internally incorporates the skill instructions.
2. **Natural Language Triggers**: The root `.github/copilot-instructions.md` guides Copilot to load skill instructions when specific phrases (e.g., "run tests", "verify implementation", "independent review") are observed in the prompt context.
