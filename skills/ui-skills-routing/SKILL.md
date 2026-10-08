---
skillId: ui-skills-routing
name: ui-skills-routing
description: "Serve as the minimal-context routing layer for UI tasks, selecting the smallest useful skill context through the ui-skills registry and web scraping to prevent context bloat and optimize token efficiency across hierarchical agent tiers."
purpose: Minimal-context routing layer for UI tasks, selecting the smallest useful skill context through ui-skills and web scraping to prevent context bloat and optimize token efficiency across hierarchical agent tiers.
whenToUse:
  - Before commencing any user-interface, component, visual layout, or styling task
  - Selecting the minimal necessary UI skill context without polluting agent memory with excess tokens
  - Fetching modular craft, layout, or accessibility skills from web registries (e.g. npx ui-skills)
  - Guiding smaller, cost-efficient developer models with crystal-clear bounded instructions authored by high-reasoning lead models
prerequisites:
  - Clear UI task or component goal
  - Access to local skills/ directory or external registry via CLI/web
inputs:
  - name: uiGoal
    type: string
    description: Specific UI, layout, styling, or component goal under development
  - name: techStack
    type: string
    description: Target framework or styling stack (Tailwind, CSS Modules, React, Vanilla, Svelte)
procedure:
  - stepNumber: 1
    title: UI Relevance Decision
    action: Decide if the task involves user-facing visual interfaces. If not, return 'no skill needed' to preserve context window tokens.
  - stepNumber: 2
    title: Category & Specificity Identification
    action: Identify the narrowest matching category (e.g., layout, craft, motion, forms, tables, typography) and target stack.
  - stepNumber: 3
    title: Smallest Useful Context Selection
    action: "Enforce strict selection rules: Prefer 1 skill. Use 2 only for dual angles. Use 3 only for broad redesigns. Never use more than 3."
  - stepNumber: 4
    title: Dynamic Retrieval & Injection
    action: Fetch the exact skill slug via CLI (npx ui-skills get <slug>) or registry scrape, loading only the necessary token budget.
  - stepNumber: 5
    title: Hierarchical Task Dispatch
    action: Compile precise instructions using the lead model and dispatch to smaller, cost-efficient implementation models operating in bounded file scopes.
expectedOutputs:
  - Targeted UI skill context payload under 2,000 tokens
  - Clean, bounded implementation instructions for the worker agent
  - Reference slug and source citation
applicableApprovalGates:
  - G2
  - G4
failureAndRecovery:
  potentialFailures:
    - Context bloat from loading multiple redundant design skills
    - Vague task goal causing ambiguous skill selection
    - Worker agent exceeding file boundaries
  recoveryStrategy: If the goal is unclear, ask exactly one short clarification question. Enforce strict 1-to-3 skill limit. Reject any context injection exceeding 4,000 tokens.
verificationCriteria:
  - No more than 3 skills loaded concurrently
  - Skill matches target stack and specific component scope
  - Implementation executes within bounded file ownership
relevantContractsAndMemory:
  contracts:
    - contracts/design/contract.json
    - contracts/implementation/contract.json
  memoryRecords:
    - executionState.activeTasks
    - executionState.activePhase
---

# Modular UI Skills Routing & Dynamic Web Registry (`ui-skills-routing`)

## 1. Purpose & Architectural Foundation
The `ui-skills-routing` skill implements the **Minimal-Context Routing Protocol** (inspired by `ui-skills` by ibelick). In modern agentic software development, dumping large, monolithic design instructions or entire styleguides into the prompt wastes tokens, causes attention degradation, and degrades code output.

By establishing a hierarchical intelligence architecture:
1. **High-Reasoning Lead Model**: Inspects the UI goal, determines relevance, selects the single smallest useful skill context, and formulates rigorous, unambiguous instructions.
2. **Cost-Efficient Worker Models**: Smaller, fast models (e.g. Flash, Haiku, Mini) execute the bounded implementation within strict file ownership boundaries, achieving **up to 85% token cost savings** with zero hallucinated fluff.
3. **Adversarial Code Reviewer**: An elite, unforgiving code auditor verifies the output against Anti-Slop baselines (BL-001 through BL-007) and WCAG 2.1 AA mathematical standards before merge.

## 2. Selection Rules
- **Prefer 1 skill**: 80% of tasks need only a single targeted craft or layout context.
- **Use 2 skills**: Only when the task genuinely requires two distinct lenses (e.g., motion + accessibility, or responsive grid + dark mode tokens).
- **Use 3 skills**: Strictly reserved for full multi-surface redesigns or complex architectural overhauls.
- **Never use more than 3 skills**.
- **Route by topic, then stack, then specificity**: Prefer framework-specific over generic; prefer narrow craft over broad guidelines.

## 3. CLI Protocol
```bash
npx ui-skills start
npx ui-skills categories
npx ui-skills list --category <category>
npx ui-skills get <slug>
```

## 4. Hierarchical Multi-Model Architecture
```
┌──────────────────────────────────────────────────────────┐
│  High-Reasoning Lead Model (Architect & Council Lead)    │
│  - Selects smallest useful context via ui-skills CLI     │
│  - Authors strict bounded task specs & schemas           │
└────────────────────────────┬─────────────────────────────┘
                             │ (Precise, minimal tokens)
                             ▼
┌──────────────────────────────────────────────────────────┐
│  Cost-Efficient Worker Model (Specialized Coder)         │
│  - Executes bounded implementation in disjoint files     │
│  - Zero context drift, 85% token cost reduction          │
└────────────────────────────┬─────────────────────────────┘
                             │ (Code diff)
                             ▼
┌──────────────────────────────────────────────────────────┐
│  Elite Adversarial Code Reviewer (Gate G5 Auditor)       │
│  - Anti-Slop check (BL-001 to BL-007)                    │
│  - Mathematical WCAG 2.1 AA contrast audit               │
│  - Schema & contract adherence verification              │
└──────────────────────────────────────────────────────────┘
```
