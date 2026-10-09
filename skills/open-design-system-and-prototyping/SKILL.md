---
skillId: open-design-system-and-prototyping
name: open-design-system-and-prototyping
description: "Author and enforce the Open Design DESIGN.md brand contract, generate interactive single-page HTML prototypes and dashboards, and refactor existing frontend codebases to strict design token alignment."
purpose: "Author and enforce the Open Design DESIGN.md brand contract, generate interactive single-page HTML prototypes and dashboards, and refactor existing frontend codebases to strict design token alignment."
whenToUse:
  - Codifying a comprehensive DESIGN.md brand contract with OKLCH color ramps, typography scales, spacing grids, and motion curves
  - Generating interactive single-page HTML prototypes, live operational dashboards, and slide decks from a product brief
  - Refreshing brownfield frontend codebases (React, Vue, HTML/CSS) to bind directly to DESIGN.md tokens without behavioral regressions
  - Auditing UI components for accessibility compliance (WCAG 2.1 AA contrast ratios, touch targets, keyboard focus)
  - Establishing an agent-native, artifact-first design workflow across Claude Code, Antigravity, and Copilot
prerequisites:
  - Product brief, user story, or existing design guidelines
  - Target DESIGN.md specification path
  - Frontend repository directory for component refactoring tasks
inputs:
  - name: designBrief
    type: string
    description: Product requirement, visual direction, or screen flow description
  - name: brandContractPath
    type: string
    description: Path to DESIGN.md brand contract (default DESIGN.md)
  - name: artifactType
    type: string
    description: Type of artifact to generate web-prototype, dashboard, slide-deck, or component-refresh
  - name: stylingEngine
    type: string
    description: Target styling implementation vanilla-css-variables, tailwind, or css-modules
procedure:
  - stepNumber: 1
    title: Brand Contract & DESIGN.md Parsing or Synthesis
    action: Formulate or parse DESIGN.md specifying OKLCH color ramps, typography scales, spacing units, border radii, and motion curves.
  - stepNumber: 2
    title: Interactive Blueprint & Template Selection
    action: Select the appropriate artifact archetype (web landing page, operational dashboard, presentation deck, or component library).
  - stepNumber: 3
    title: Single-Page Self-Contained Artifact Generation
    action: Author a self-contained, responsive HTML/CSS/JS prototype with embedded tokens, interactive state toggles, and mock datasets.
  - stepNumber: 4
    title: Codebase Token Audit & Component Refresh
    action: Scan existing project components (.tsx, .vue, .html, .css), detect arbitrary hex codes and hardcoded margins, and refactor them to use semantic tokens.
  - stepNumber: 5
    title: Accessibility & Contrast Invariant Verification
    action: Verify that text tokens achieve WCAG AA contrast (>= 4.5:1), interactive targets exceed 44x44px, and focus rings are distinct.
  - stepNumber: 6
    title: Design Contract Synchronization & Memory Update
    action: Update contracts/design/contract.json at Gate G2 and record design decisions in project memory.
expectedOutputs:
  - Canonical DESIGN.md brand contract document
  - Self-contained interactive HTML prototype or dashboard artifact in docs/prototypes/
  - Refactored codebase components adhering to CSS custom property tokens
  - Synchronized contracts/design/contract.json for Gate G2 compliance
applicableApprovalGates:
  - G0
  - G1
  - G2
  - G3
  - G4
failureAndRecovery:
  potentialFailures:
    - Hardcoded styles conflict with external component libraries
    - Color tokens fail WCAG AA contrast against dark/light surface variants
    - Component refactoring introduces layout shifts or breaks existing interactive behavior
  recoveryStrategy: Isolate conflicting third-party components behind CSS variable wrapper scopes. Run automated contrast calculation scripts and adjust OKLCH lightness/chroma until >= 4.5:1 is achieved. Keep backup characterization tests before refactoring component JSX.
verificationCriteria:
  - Every color, spacing unit, and font size in generated artifacts binds to a declared DESIGN.md token
  - Generated HTML prototype is fully self-contained, responsive across breakpoints, and opens cleanly in any browser
  - 100% of text tokens meet or exceed WCAG 2.1 AA 4.5:1 contrast in both light and dark themes
  - No regressions in existing component test suites after codebase design refresh
relevantContractsAndMemory:
  contracts:
    - contracts/design/contract.json
    - contracts/requirements/contract.json
  memoryRecords:
    - durableKnowledge.architecturalDecisions
    - durableKnowledge.domainVocabulary
---

# Open Design System & Rapid Prototyping (`open-design-system-and-prototyping`)

## 1. Purpose
The `open-design-system-and-prototyping` skill adapts the Open Design concept to Project Intelligence. It establishes an agent-native, artifact-first design workflow where:
- The **`DESIGN.md`** file acts as the executable brand contract read by coding agents before rendering any UI.
- Agents deliver **interactive single-page HTML prototypes and dashboards** instead of static prose or non-functional mockups.
- Existing brownfield codebases are refreshed to strict design token alignment, eliminating hardcoded hex codes, visual drift, and inaccessible contrast.

## 2. When to Use It
Activate this skill whenever:
- Formulating or updating the core `DESIGN.md` brand specification for a project.
- Rapidly generating interactive web prototypes, operational dashboards, or HTML presentation slide decks from a product brief.
- Auditing frontend repositories (React, Vue, HTML/CSS) for arbitrary styles and refactoring components to semantic tokens.
- Verifying WCAG 2.1 AA accessibility invariants (minimum 4.5:1 text contrast across light and dark modes).
- Collaborating between product, design, and engineering through verifiable, self-contained artifacts.

## 3. Prerequisites
- Product brief or user story describing desired screens and interaction flows.
- Clean git working tree prior to component refactoring.
- Access to `contracts/design/contract.json` (Gate G2).

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `designBrief` | `string` | Product requirement, visual direction, or screen flow description. |
| `brandContractPath` | `string` | Location of the `DESIGN.md` brand specification (default: `DESIGN.md`). |
| `artifactType` | `string` | Blueprint type: `web-prototype`, `dashboard`, `slide-deck`, or `component-refresh`. |
| `stylingEngine` | `string` | Target implementation: `vanilla-css-variables`, `tailwind`, or `css-modules`. |

## 5. Procedure (Step-by-Step)
1. **Brand Contract & `DESIGN.md` Synthesis**:
   - Establish or read `DESIGN.md`, defining semantic OKLCH color palettes, typography scales, 4px/8px spacing grids, border radii, and motion easing curves.
   - Ensure light and dark themes are mathematically derived to maintain invariant contrast.
2. **Interactive Blueprint Selection**:
   - Choose the target artifact archetype based on the brief:
     - **Prototype**: Full-fidelity web or mobile flow with stateful transitions and navigation.
     - **Live Dashboard**: KPI wall, analytics metrics, and interactive filtering panels.
     - **Slide Deck**: Horizontal swipe presentation with keyboard navigation and slide notes.
3. **Single-Page HTML Artifact Generation**:
   - Author a clean, self-contained single-page HTML document under `docs/prototypes/`.
   - Embed CSS custom properties directly from `DESIGN.md`.
   - Implement responsive breakpoints (mobile: 360px, tablet: 768px, desktop: 1024px, wide: 1440px).
   - Include interactive states (hover, active, focus-visible) with zero third-party framework dependencies.
4. **Codebase Token Audit & Component Refresh**:
   - For brownfield repositories, scan component files (`.tsx`, `.vue`, `.html`, `.css`) for hardcoded styling anti-patterns (arbitrary hex colors, undeclared margins, ad-hoc font sizes).
   - Refactor components to reference CSS custom properties (e.g. `var(--color-accent)`, `var(--space-md)`).
5. **Accessibility & Contrast Invariant Verification**:
   - Calculate luminance contrast for all text tokens against light and dark background tokens (minimum 4.5:1 for normal text, 3:1 for large text).
   - Ensure interactive buttons and inputs meet the 44×44px touch target guideline.
   - Enforce explicit `focus-visible` outlines for keyboard accessibility.
6. **Design Contract Synchronization & Memory Update**:
   - Synchronize outputs with `contracts/design/contract.json` at Gate G2.
   - Record newly established tokens in project durable knowledge records.

## 6. Expected Outputs
- Canonical `DESIGN.md` brand contract file at the repository root.
- Self-contained interactive HTML prototype saved to `docs/prototypes/<name>.html`.
- Refactored frontend source files adhering strictly to token variables.
- Verified Gate G2 Design contract (`contracts/design/contract.json`).

## 7. Applicable Approval Gates
- **G0 (Discovery)**: Identifies existing visual brand assets and UI constraints.
- **G1 (Requirements)**: Clarifies user interaction flows and screen requirements.
- **G2 (Design Approval)**: Formulates and approves the canonical `DESIGN.md` and Design Contract.
- **G3 (Planning)**: Maps UI component inventory to discrete implementation tasks.
- **G4 (Implementation)**: Refactors and builds production components to match prototypes.

## 8. Failure and Recovery Strategies
- **Contrast Failure**: If an accent color fails 4.5:1 against surface colors, adjust OKLCH lightness ($L$) or chroma ($C$) until the mathematical ratio meets or exceeds 4.5:1 without shifting hue ($H$).
- **Component Breakage**: If refactoring breaks component layout or tests, isolate the affected primitive behind a scoped class name and test incrementally using characterization tests.

## 9. Verification Criteria
- All colors, font sizes, margins, and borders in generated prototypes map to tokens declared in `DESIGN.md`.
- Prototype HTML file opens cleanly in any standard browser without network dependencies or build steps.
- Contrast verification passes WCAG 2.1 AA across both light and dark themes.
- Existing frontend unit and component tests pass with zero regressions.

## 10. Relevant Contracts and Memory Records
- `contracts/design/contract.json`
- `contracts/requirements/contract.json`
- `durableKnowledge.architecturalDecisions`
- `durableKnowledge.domainVocabulary`
