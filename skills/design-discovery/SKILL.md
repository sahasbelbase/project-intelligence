---
skillId: design-discovery
name: design-discovery
description: "Capture visual identity, user flows, UI/UX aesthetics, layout constraints, and formal design system requirements or evaluate G2 exemption rationale."
purpose: Capture visual identity, user flows, UI/UX aesthetics, layout constraints, and formal design system requirements or evaluate G2 exemption rationale.
whenToUse:
  - Initiating a project or feature that includes a user-facing visual interface (Web, Mobile, Desktop, TV, Watch)
  - Evaluating whether Gate G2 is applicable or whether a formal exemption rationale must be recorded
  - Translating brand guidelines, mood boards, or Figma mockups into structured design criteria
  - Discovering responsive viewport requirements and accessibility constraints (WCAG 2.1 AA)
prerequisites:
  - Gate G1 approved (requirements contract signed off)
  - Identified user personas and primary user journeys
  - Access to design-contract schema in core/schemas/design-contract.schema.json
inputs:
  - name: uiScope
    type: string
    description: Definition of visual interfaces to be created or modified
  - name: brandGuidelines
    type: object
    description: Brand aesthetic rules, primary color palette, typography references, and visual tone
  - name: targetFormFactors
    type: array
    description: Target devices and viewports (mobile, tablet, desktop, ultra-wide)
procedure:
  - stepNumber: 1
    title: Visual Interface Applicability Evaluation
    action: Assess whether the project deliverables include visual user interfaces. If the project is headless, CLI-only, or backend library, formulate the formal G2 exemption record.
  - stepNumber: 2
    title: Aesthetic Direction and Persona Mapping
    action: Map target user personas to visual hierarchy, content density, mood (e.g., modern minimalist, enterprise dense, playful, dark-mode first), and motion philosophy.
  - stepNumber: 3
    title: User Flow and Screen Taxonomy Definition
    action: Enumerate critical user flows, page layouts, modal interactions, navigation hierarchies, and responsive breakpoint requirements.
  - stepNumber: 4
    title: Accessibility Target Formulation
    action: Define required accessibility compliance level (WCAG 2.1 AA standard), minimum contrast ratios (4.5:1 text, 3:1 UI components), keyboard focus behavior, and screen-reader semantics.
  - stepNumber: 5
    title: Design Contract Formulation
    action: Generate contracts/design/contract.json adhering to core/schemas/design-contract.schema.json with initial status UNDER_REVIEW.
expectedOutputs:
  - contracts/design/contract.json adhering to design-contract.schema.json
  - Visual discovery summary detailing user flows, responsive viewport tiers, and aesthetic rules
  - Formal exemption rationale if project has no visual interface
applicableApprovalGates:
  - G1
  - G2
failureAndRecovery:
  potentialFailures:
    - Ambiguous visual aesthetic leading to contradictory design tokens
    - Attempting to bypass Gate G2 on visual products without formal justification
    - Missing accessibility criteria for enterprise products
  recoveryStrategy: If visual guidelines are ambiguous, present interactive mood options to the user before finalizing tokens. If G2 bypass is attempted for visual apps, reject transition and enforce token formulation.
verificationCriteria:
  - contracts/design/contract.json passes validation against core/schemas/design-contract.schema.json
  - If isApplicable is false, exemptionRationale is documented with technical justification
  - If isApplicable is true, all target viewports (mobile, desktop) have explicit breakpoint specifications
  - Accessibility targets include measurable contrast ratios and WCAG level
relevantContractsAndMemory:
  contracts:
    - contracts/requirements/contract.json
    - contracts/design/contract.json
  memoryRecords:
    - durableKnowledge.codingConventions
    - executionState.currentGate
---

# Design Discovery (`design-discovery`)

## 1. Purpose
The `design-discovery` skill orchestrates the upfront visual, ergonomic, and aesthetic discovery phase for user-facing applications. It ensures that user interface decisions, visual hierarchy, theme palettes, typography hierarchies, and responsive layout constraints are thoroughly planned and formally signed off before code is written. For headless or non-visual systems, it generates the formal, auditable Gate G2 exemption record.

## 2. When to Use It
Activate this skill in the following scenarios:
- **Visual Application Bootstrapping**: Projects featuring web applications, mobile apps, desktop UIs, or terminal user interfaces (TUIs).
- **Evaluating Gate G2 Exemption**: Formulating the necessary technical justification to bypass Gate G2 when developing pure backends, CLI utilities, or protocol libraries.
- **UI Architecture Planning**: Translating loose wireframes, mood boards, or visual requirements into structured contract specifications.

## 3. Prerequisites
- Gate G1 must be approved (`contracts/requirements/contract.json` in `APPROVED` status).
- Core schemas accessible, specifically `core/schemas/design-contract.schema.json`.
- User personas and key user journeys documented.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `uiScope` | `string` | Scope description of user interface requirements and screens. |
| `brandGuidelines` | `object` | Styling direction, color palettes, fonts, and visual brand identity. |
| `targetFormFactors` | `array` | Targeted screen classes (mobile: 360-480px, tablet: 768-1024px, desktop: 1280px+). |

## 5. Procedure (Step-by-Step)
1. **Applicability Evaluation**:
   - Check whether the project deliverables contain user-facing interfaces.
   - If non-visual:
     - Set `isApplicable: false` in `contracts/design/contract.json`.
     - Provide a concrete `exemptionRationale` (e.g., "Pure command-line tool with stdout/stderr JSON streaming; no visual layout or DOM rendering required").
     - Advance contract status to `APPROVED` upon confirmation.
   - If visual: Proceed through the remaining steps.

2. **Aesthetic Direction & Mood Framing**:
   - Establish content density: compact (data-heavy dashboard), standard (productivity), or relaxed (consumer).
   - Establish color scheme philosophy: single-theme, light/dark dual mode, high-contrast accessible mode.
   - Define motion guidelines: reduced motion support, standard transition timings (150ms-300ms cubic-bezier).

3. **Screen Taxonomy & User Journey Mapping**:
   - Enumerate key views, navigation trees, dialogs, drawers, and state transitions (loading, empty, partial, error, populated).
   - Define layout grid systems (e.g., 4px/8px baseline grid, 12-column responsive layout).

4. **Accessibility (a11y) Target Formulation**:
   - Formalize WCAG target (minimum WCAG 2.1 Level AA).
   - Specify contrast ratios: 4.5:1 for normal text, 3:1 for large text and critical UI boundaries.
   - Enforce visible keyboard focus rings, semantic landmark tags, and aria-live announcements.

5. **Design Contract Synthesis**:
   - Draft `contracts/design/contract.json` complying with `core/schemas/design-contract.schema.json`.
   - Submit contract for Gate G2 review.

## 6. Expected Outputs
- `contracts/design/contract.json`: Validated design contract or formal G2 exemption record.
- Design Discovery Summary detailing visual hierarchy, user journey screens, and accessibility targets.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G1 (Requirements)**: Reads approved functional requirements.
- **Gate G2 (Design Approval)**: Produces the required design contract artifact to exit G2.

## 8. Failure and Recovery Behavior
- **Undefined Aesthetic Tone**: Request user feedback with concrete options (e.g. minimalist, dense data table, card-based).
- **Unauthorized Gate Bypass**: The lifecycle engine rejects transition to G3 if `contracts/design/contract.json` is missing or invalid.
- **Inconsistent Theme Contrast**: Run mathematical contrast calculation against background colors; adjust token luminance if contrast ratio falls below 4.5:1.

## 9. Verification Criteria
- `contracts/design/contract.json` validates against `core/schemas/design-contract.schema.json`.
- If `isApplicable` is true, design tokens for color, typography, and spacing are specified.
- Responsive breakpoints define exact min-width or max-width thresholds.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/requirements/contract.json`
  - `contracts/design/contract.json`
- **Memory Records**:
  - `durableKnowledge.codingConventions`
  - `executionState.currentGate`
