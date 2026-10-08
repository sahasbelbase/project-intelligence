---
skillId: design-system-engineering
name: design-system-engineering
description: "Translate design decisions into concrete design tokens, component APIs, responsive breakpoints, accessible themes, and CSS/styling contracts."
purpose: Translate design decisions into concrete design tokens, component APIs, responsive breakpoints, accessible themes, and CSS/styling contracts.
whenToUse:
  - Transforming high-level design concepts into executable CSS variables, Tailwind tokens, or theme structures
  - Standardizing UI components (buttons, dialogs, inputs, tables) with deterministic interactive states
  - Enforcing design token compliance and responsive layout rules during frontend engineering
  - Implementing dark/light theme switching with zero layout shift (CLS) and WCAG AA contrast compliance
prerequisites:
  - Approved design contract or active G2 transition
  - Identified frontend styling framework (CSS Modules, Tailwind, Styled Components, vanilla CSS)
  - Access to design-contract.schema.json
inputs:
  - name: designContract
    type: object
    description: Active design contract data containing colors, typography, spacing, and breakpoints
  - name: stylingFramework
    type: string
    description: Selected styling engine (e.g., tailwindcss, css-variables, styled-components, scss)
  - name: componentInventory
    type: array
    description: List of core UI primitives required (Button, Input, Modal, Card, Table, Toast)
procedure:
  - stepNumber: 1
    title: Design Token Codification
    action: Formulate design tokens for spacing (4px, 8px, 16px, 24px, 32px), typography (scales, font-family, line-height), color scales (50-900), shadows, and z-index layers.
  - stepNumber: 2
    title: Token File Generation
    action: Export tokens to framework-native configuration files (e.g., globals.css with CSS custom properties, tailwind.config.js, or tokens.ts).
  - stepNumber: 3
    title: Component State Specification
    action: "Specify interactive states for all component inventory items: default, hover, active, focus-visible, disabled, loading, and error."
  - stepNumber: 4
    title: Responsive Layout and Breakpoint Implementation
    action: "Codify responsive media queries and container query rules for small (sm: 640px), medium (md: 768px), large (lg: 1024px), and extra-large (xl: 1280px) viewports."
  - stepNumber: 5
    title: Accessibility and Motion Tokens Integration
    action: Ensure prefers-reduced-motion media query tokens are established and text-to-background contrast tokens meet WCAG 2.1 AA standards.
expectedOutputs:
  - Generated design token stylesheets or configuration files (tokens.css, theme.ts)
  - Component specification matrix documenting props and states
  - Design system compliance verification report for G2 exit
applicableApprovalGates:
  - G2
  - G3
failureAndRecovery:
  potentialFailures:
    - Hardcoded magic numbers in CSS violating design token rules
    - Insufficient color contrast between foreground text and interactive backgrounds
    - Missing focus-visible indicators causing keyboard accessibility failures
  recoveryStrategy: Replace all raw hex/px values with semantic token variables. Adjust token color values using lightness/saturation curves until contrast passes 4.5:1. Automatically inject 2px solid offset outline tokens for focus-visible states.
verificationCriteria:
  - Zero hardcoded color hex values or arbitrary pixel margins in component files
  - All interactive components define hover, focus-visible, active, and disabled styles
  - Contrast ratios between text and background tokens achieve minimum 4.5:1 ratio
  - Design tokens match definitions in contracts/design/contract.json
relevantContractsAndMemory:
  contracts:
    - contracts/design/contract.json
    - contracts/architecture/contract.json
  memoryRecords:
    - durableKnowledge.codingConventions
    - durableKnowledge.domainVocabulary
---

# Design System Engineering (`design-system-engineering`)

## 1. Purpose
The `design-system-engineering` skill translates conceptual visual guidelines and design contracts into production-grade design tokens, component architecture patterns, accessible styling systems, and responsive layouts. It bridges the gap between Gate G2 (Design Approval) and Gate G3/G4 (Architecture and Implementation), preventing ad-hoc CSS, arbitrary "magic number" spacing, and inconsistent UI states.

## 2. When to Use It
Use this skill when:
- Establishing the CSS token architecture (CSS Custom Properties, Tailwind tokens, CSS-in-JS themes).
- Building primitive design system components (Button, Input, Dropdown, Dialog, Toast, Table, Modal).
- Enforcing design token compliance across application user interfaces.
- Ensuring that dark mode, responsive breakpoints, and accessibility states are engineered deterministically.

## 3. Prerequisites
- `contracts/design/contract.json` is available and approved, or currently undergoing G2 formulation.
- Target frontend styling ecosystem identified (`tailwindcss`, `vanilla-css`, `sass`, `styled-components`).
- Target component library primitives identified.

## 4. Inputs
| Input Name | Type | Description |
|---|---|---|
| `designContract` | `object` | The active design contract data defining tokens, palettes, and breakpoints. |
| `stylingFramework` | `string` | The build/CSS framework used by the frontend codebase. |
| `componentInventory` | `array` | The list of primitive UI components required by the system. |

## 5. Procedure (Step-by-Step)
1. **Design Token Codification**:
   - Establish token naming taxonomy following three tiers:
     - **Global/Primitive Tokens**: Raw values (`--color-blue-500: #3b82f6`, `--space-4: 16px`).
     - **Semantic/Alias Tokens**: Purpose-driven values (`--color-primary: var(--color-blue-500)`, `--space-content: var(--space-4)`).
     - **Component Tokens**: Scoped values (`--btn-padding-y: var(--space-2)`).
   - Define typography scale: font families, size hierarchy (xs, sm, base, lg, xl, 2xl, 3xl), line heights, and letter spacing.
   - Define surface elevations and shadow tokens (`elevation-low`, `elevation-mid`, `elevation-high`).

2. **Token File Generation & Build Integration**:
   - Export tokens to standard style definition files (`tokens.css`, `theme.json`, or `tailwind.config.ts`).
   - Validate that tokens support runtime light/dark switching via data attributes (`data-theme="dark"`).

3. **Component Interactive States Specification**:
   - For every component in `componentInventory`, specify distinct visual feedback for 7 core states:
     1. Default / Rest
     2. Hover
     3. Active / Pressed
     4. Focus-visible (mandatory 2px outline with 2px offset)
     5. Disabled (`aria-disabled="true"`, reduced opacity, `pointer-events: none`)
     6. Loading / Busy (`aria-busy="true"`, accessible indicator)
     7. Error / Invalid (`aria-invalid="true"`, semantic red border/text)

4. **Responsive Layouts and Container Queries**:
   - Codify media queries aligning with breakpoints in the design contract:
     - Mobile: 320px - 639px
     - Tablet / Small: 640px - 1023px
     - Desktop: 1024px - 1439px
     - Ultra-wide: 1440px+
   - Implement CSS Grid / Flexbox layouts that prevent horizontal scrollbars and layout shifts.

5. **Accessibility & Reduced Motion Enforcement**:
   - Verify all color tokens pass WCAG 2.1 AA luminance tests (4.5:1 text, 3:1 non-text).
   - Implement `@media (prefers-reduced-motion: reduce)` tokens to zero out long transitions and animations.

## 6. Expected Outputs
- Production-ready design token assets (`tokens.css`, `tailwind.config.js`, or equivalent).
- Component state implementation matrix and props contract.
- Token compliance documentation ready for architectural review.

## 7. Applicable Approval Gates (G0-G6)
- **Gate G2 (Design Approval)**: Delivers token compliance and responsive specifications.
- **Gate G3 (Architecture & Plan)**: Provides interface contracts for frontend component boundaries.

## 8. Failure and Recovery Behavior
- **Hardcoded CSS Values (Magic Numbers)**: Run token linter to detect unmapped hex colors or raw pixel margins; replace immediately with semantic CSS variables.
- **Low Contrast Failures**: Calculate relative luminance using formula `(L1 + 0.05) / (L2 + 0.05)`. If ratio < 4.5, darken or lighten the token until compliance is achieved.
- **Layout Shift (CLS)**: Enforce explicit aspect ratios and reserved dimensions for media assets and dynamic banners.

## 9. Verification Criteria
- Zero instances of raw hex color codes or arbitrary pixel dimensions in feature components.
- Interactive components include visible, high-contrast keyboard focus indicators (`:focus-visible`).
- Responsive layouts adapt smoothly across all defined viewport breakpoints without horizontal scrolling.

## 10. Relevant Contracts and Memory Records
- **Contracts**:
  - `contracts/design/contract.json`
  - `contracts/architecture/contract.json`
- **Memory Records**:
  - `durableKnowledge.codingConventions`
  - `durableKnowledge.domainVocabulary`
