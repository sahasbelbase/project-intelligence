---
skillId: idea-to-prd
name: idea-to-prd
description: "Turn a rough idea into a product requirements document (PRD) that matches how the code and the CLI actually work: question the idea until every decision is settled, agree the vocabulary, write the PRD with the exact commands users will run, and slice it into vertical tickets."
purpose: "Turn a rough idea into a product requirements document (PRD) that matches how the code and the CLI actually work: question the idea until every decision is settled, agree the vocabulary, write the PRD with the exact commands users will run, and slice it into vertical tickets."
whenToUse:
  - Someone has an idea or feature request but the scope, users or behaviour are still fuzzy
  - Before G1 (requirements) for anything bigger than a single specialist task
  - When the words people use for a feature differ from the names in the code
  - When a plan must become tickets an agent can build one at a time
prerequisites:
  - Read access to the repository (README, contracts/, existing glossary and decision records)
  - A person who can answer product decisions
  - "Optional: the vendored grilling and domain-modeling skills, and project-intelligence on the PATH"
inputs:
  - name: idea
    type: string
    description: The idea in the requester's own words
  - name: constraints
    type: array
    description: Known limits such as deadline, platforms, budget or compatibility
procedure:
  - stepNumber: 1
    title: Ground it in the code first
    action: Read the README, the contracts and any GLOSSARY.md or docs/adr/ before asking anything. Run `project-intelligence ask "<idea>"` to see which tier and council the idea touches. Look up facts yourself; only decisions go to the person.
  - stepNumber: 2
    title: Question the idea in rounds
    action: Map the decisions as a tree. Each round, ask every question whose prerequisites are already settled, numbered, each with your recommended answer, worded so that "yes" accepts it. Recompute after each answer. Stop when nothing is left silently assumed and the person confirms. (The vendored grilling skill describes this in full.)
  - stepNumber: 3
    title: Agree the vocabulary
    action: Write each term the conversation settles into GLOSSARY.md and each hard-to-reverse choice into a decision record, so the PRD, tickets, code names and CLI flags use the same words. (See the vendored domain-modeling skill.)
  - stepNumber: 4
    title: Write the PRD
    action: Save it to docs/specs/<slug>.md using the template below. Describe behaviour from the user's side, list the exact CLI commands, flags and output users will see, and keep file paths and code snippets out because they go stale.
  - stepNumber: 5
    title: Choose the test seams
    action: Name the highest point where the feature can be tested through its public behaviour, preferring seams that already exist. Fewer seams are better; confirm them with the person.
  - stepNumber: 6
    title: Slice into vertical tickets
    action: Break the PRD into thin end-to-end slices, each demoable on its own and small enough for one fresh agent session, with the tickets that block it. Put any preparatory refactor first. For one mechanical change across the whole codebase, use expand, migrate in batches, then contract. Save one file per ticket under docs/specs/<slug>/tickets/NN-<slug>.md.
  - stepNumber: 7
    title: Route and record
    action: "Run `project-intelligence ask` on the PRD title: council-sized work goes to the product council before G1 is signed. Record the PRD and tickets in contracts/requirements/ or link them from it."
expectedOutputs:
  - "docs/specs/<slug>.md: the PRD"
  - "docs/specs/<slug>/tickets/NN-<slug>.md: one file per vertical ticket with its blockers and acceptance criteria"
  - GLOSSARY.md entries and docs/adr/ records for settled terms and decisions
  - A route from `project-intelligence ask` and, for council-sized work, a council brief
applicableApprovalGates:
  - G0
  - G1
failureAndRecovery:
  potentialFailures:
    - The person is asked for facts the agent could have looked up
    - Questions are asked before the decisions they depend on are settled
    - The PRD names features that the CLI or code cannot express
    - Tickets are horizontal layers that cannot be demonstrated on their own
  recoveryStrategy: Look the facts up and drop those questions; move dependent questions to a later round; reconcile the PRD's commands with the CLI help output and the glossary; re-slice tickets so each one runs end to end.
verificationCriteria:
  - Every user story has at least one Given/When/Then acceptance criterion and appears in at least one ticket
  - Every CLI command in the PRD exists or is listed as new in Implementation decisions
  - Every domain term in the PRD is in GLOSSARY.md
  - No file paths or code snippets in the PRD, apart from a prototype-derived shape marked as such
  - The person confirmed shared understanding before the PRD was written
relevantContractsAndMemory:
  contracts:
    - contracts/requirements/contract.json
  memoryRecords:
    - backlog
    - durableKnowledge.architecturalDecisions
---

# Idea to PRD (`idea-to-prd`)

## 1. Purpose
Turn a rough idea into a product requirements document (PRD) that matches how the code and the CLI actually work: question the idea until every decision is settled, agree the vocabulary, write the PRD with the exact commands users will run, and slice it into vertical tickets.

## 2. When to Use It
- Someone has an idea or feature request but the scope, users or behaviour are still fuzzy
- Before G1 (requirements) for anything bigger than a single specialist task
- When the words people use for a feature differ from the names in the code
- When a plan must become tickets an agent can build one at a time

## 3. Prerequisites
- Read access to the repository (README, contracts/, existing glossary and decision records)
- A person who can answer product decisions
- Optional: the vendored grilling and domain-modeling skills, and project-intelligence on the PATH

## 4. Inputs
- `idea` (string): The idea in the requester's own words
- `constraints` (array): Known limits such as deadline, platforms, budget or compatibility

## 5. Procedure
1. **Ground it in the code first.** Read the README, the contracts and any GLOSSARY.md or docs/adr/ before asking anything. Run `project-intelligence ask "<idea>"` to see which tier and council the idea touches. Look up facts yourself; only decisions go to the person.
2. **Question the idea in rounds.** Map the decisions as a tree. Each round, ask every question whose prerequisites are already settled, numbered, each with your recommended answer, worded so that "yes" accepts it. Recompute after each answer. Stop when nothing is left silently assumed and the person confirms. (The vendored grilling skill describes this in full.)
3. **Agree the vocabulary.** Write each term the conversation settles into GLOSSARY.md and each hard-to-reverse choice into a decision record, so the PRD, tickets, code names and CLI flags use the same words. (See the vendored domain-modeling skill.)
4. **Write the PRD.** Save it to docs/specs/<slug>.md using the template below. Describe behaviour from the user's side, list the exact CLI commands, flags and output users will see, and keep file paths and code snippets out because they go stale.
5. **Choose the test seams.** Name the highest point where the feature can be tested through its public behaviour, preferring seams that already exist. Fewer seams are better; confirm them with the person.
6. **Slice into vertical tickets.** Break the PRD into thin end-to-end slices, each demoable on its own and small enough for one fresh agent session, with the tickets that block it. Put any preparatory refactor first. For one mechanical change across the whole codebase, use expand, migrate in batches, then contract. Save one file per ticket under docs/specs/<slug>/tickets/NN-<slug>.md.
7. **Route and record.** Run `project-intelligence ask` on the PRD title: council-sized work goes to the product council before G1 is signed. Record the PRD and tickets in contracts/requirements/ or link them from it.

### PRD template

```markdown
# <Feature name>

## Problem
What the user struggles with today, in their words.

## Users
Who this is for, and who it is not for.

## Solution
What changes for the user, described from their side.

## User stories
1. As a <user>, I want <capability>, so that <benefit>.
(Cover every path, including errors and first-time use.)

## Acceptance criteria
- AC-1 (story 1): Given <state>, when <action>, then <observable result>.

## CLI and interface
The exact commands, flags, prompts and output a user will see, for example:
`project-intelligence <command> --flag value` prints `<expected output>`.

## Implementation decisions
Modules and interfaces that change, contracts, schema changes and architectural choices.
No file paths or code snippets.

## Testing decisions
The seams where behaviour is tested, and prior tests to follow. Test behaviour, not internals.

## Out of scope
What this PRD deliberately does not cover.

## Open questions and assumptions
Each labelled ASSUMPTION or UNKNOWN, with who will answer it.
```

### Credits
The questioning rounds, vertical tickets and glossary practice adapt ideas from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT): `grilling`, `to-spec`, `to-tickets` and `domain-modeling`. `grilling` and `domain-modeling` are vendored unchanged in `vendor/skills/`.

## 6. Expected Outputs
- docs/specs/<slug>.md: the PRD
- docs/specs/<slug>/tickets/NN-<slug>.md: one file per vertical ticket with its blockers and acceptance criteria
- GLOSSARY.md entries and docs/adr/ records for settled terms and decisions
- A route from `project-intelligence ask` and, for council-sized work, a council brief

## 7. Applicable Approval Gates
G0, G1

## 8. Failure and Recovery
- The person is asked for facts the agent could have looked up
- Questions are asked before the decisions they depend on are settled
- The PRD names features that the CLI or code cannot express
- Tickets are horizontal layers that cannot be demonstrated on their own

Look the facts up and drop those questions; move dependent questions to a later round; reconcile the PRD's commands with the CLI help output and the glossary; re-slice tickets so each one runs end to end.

## 9. Verification Criteria
- Every user story has at least one Given/When/Then acceptance criterion and appears in at least one ticket
- Every CLI command in the PRD exists or is listed as new in Implementation decisions
- Every domain term in the PRD is in GLOSSARY.md
- No file paths or code snippets in the PRD, apart from a prototype-derived shape marked as such
- The person confirmed shared understanding before the PRD was written

## 10. Relevant Contracts and Memory
- contracts/requirements/contract.json
- backlog
- durableKnowledge.architecturalDecisions
