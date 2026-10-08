---
skillId: baseline-ui
name: Baseline UI Craftsmanship & Anti-Slop Layout Standards
purpose: Enforce world-class visual craftsmanship, 4px/8px geometric spacing cadence, strict design token discipline, WCAG 2.1 AA mathematical contrast, and motion bounds to eliminate sloppy UI.
whenToUse:
  - Building or refactoring user interfaces, web components, dashboards, and layouts
  - Auditing CSS, Tailwind classes, or styling code during Gate G2 and Gate G5
  - Eliminating arbitrary pixel values, ungrounded shadows, and decorative slop
  - Verifying keyboard navigation, visible focus rings, and color contrast ratios
prerequisites:
  - Target web interface or UI components rendered in browser or codebase
  - Design tokens or theme definitions established in CSS/Tailwind
  - Access to WCAG 2.1 AA contrast requirements
inputs:
  - name: uiSourceFiles
    type: array
    description: Paths to CSS, HTML, TSX/JSX, or template files under evaluation
  - name: designTokens
    type: object
    description: Declared semantic color tokens, typography scales, and spacing units
procedure:
  - stepNumber: 1
    title: Geometric Spacing Cadence Audit
    action: Audit all margins, paddings, gaps, and widths. Enforce 4px/8px grid scale (4, 8, 12, 16, 20, 24, 32, 48, 64px). Flag and eliminate all arbitrary pixel nudges (e.g., 7px, 11px, 13px, 19px).
  - stepNumber: 2
    title: Design Token Adherence & Palette Economy
    action: Scan for hardcoded hex or RGB colors outside root token definitions. Mandate semantic tokens (e.g., var(--bg-surface), var(--text-primary)) across all components.
  - stepNumber: 3
    title: Mathematical Contrast & Typography Hierarchy
    action: Calculate color contrast ratios. Enforce >= 4.5:1 for body copy and >= 3:1 for large text and interactive components. Constrain font sizes to modular scales and limit active weights.
  - stepNumber: 4
    title: Interaction, Focus & Motion Discipline
    action: Verify interactive states (:hover, :active, :focus-visible). Require explicit 2px focus-visible offset ring. Cap transition durations at <= 200ms with snappy easing curves.
  - stepNumber: 5
    title: Visual Surface Deslopping
    action: Strip meaningless gradient borders, ungrounded floating cards, blurry multi-colored glow effects, and non-functional decorative widgets.
expectedOutputs:
  - Baseline UI Craftsmanship Audit Report detailing spacing adherence, contrast ratios, and token usage
  - Remediated CSS/styling code adhering strictly to the 4px/8px geometric scale
  - Zero accessibility contrast defects
applicableApprovalGates:
  - G2
  - G5
failureAndRecovery:
  potentialFailures:
    - Arbitrary pixel spacing values detected in component styling
    - Hardcoded hex colors bypassing semantic token system
    - Text contrast ratio below WCAG 2.1 AA 4.5:1 threshold
    - Focus outlines suppressed with outline: none without replacement
  recoveryStrategy: Reject Gate G2/G5. Output exact line references and mathematical token replacements. Map arbitrary values to the nearest 4px/8px step.
verificationCriteria:
  - 100% of spacing declarations adhere to 4px/8px scale
  - Zero raw hex colors in component declaration blocks
  - WCAG 2.1 AA contrast passed across all text elements
  - Explicit focus-visible indicator present on all interactive controls
  - Motion transitions capped at <= 200ms with prefers-reduced-motion fallback
relevantContractsAndMemory:
  contracts:
    - contracts/design/contract.json
    - contracts/quality/contract.json
  memoryRecords:
    - executionState.activeTasks
    - durableKnowledge.architecturalDecisions
---

# Baseline UI Craftsmanship & Anti-Slop Layout Standards (`baseline-ui`)

## 1. Principles of Baseline UI Craftsmanship
Derived from the `ibelick/baseline-ui` standard in the `ui-skills` ecosystem, this skill establishes non-negotiable craftsmanship standards for user interfaces. 

A sloppy UI is characterized by:
- Arbitrary spacing nudges (`margin-top: 13px; padding-left: 7px;`)
- Random hex colors scattered through component classes
- Low-contrast light gray text on white or dark gray text on black
- Float-y, sluggish animations (500ms ease) that make the UI feel unresponsive
- Stripped focus rings (`outline: none`) that render the UI unusable for keyboard users
- "AI slop" visuals: gratuitous gradient text, glowing neon borders, and cards inside cards with zero margin

Baseline UI replaces arbitrary choices with **mathematical, principled systems**.

---

## 2. The Baseline UI Standard Specification

### Rule 1: The 4px / 8px Geometric Spacing Cadence
All spatial dimensions (margins, paddings, layout grid gaps, min-heights) must adhere to multiples of 4px (with 8px as the primary rhythmic interval):
- `4px`: Micro padding, badge offsets, inline icon gaps
- `8px`: Compact padding, button inline padding, small gaps
- `12px`: Medium padding, tight card gutters
- `16px`: Standard card padding, component margins, content flow gaps
- `24px`: Section spacing, large card padding, dialog gutters
- `32px`: Page section gutters, column gaps
- `48px`: Hero padding, major landmark spacing
- `64px`: Page container top/bottom bounds

**Forbidden**: Any odd or arbitrary number like `3px`, `7px`, `9px`, `11px`, `13px`, `17px`, `19px`.

### Rule 2: Strict Design Token Palette Economy
Never hardcode raw `#hex` or `rgb()` color values in component classes.
All color values must reference semantic variables defined at `:root`:
```css
/* COMPLIANT */
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
}

/* REJECTED (SLOPPY) */
.card {
  background: #1e1e24;
  border: 1px solid #333;
  color: #efefef;
}
```

### Rule 3: Typography & Modular Scale
- Maximum 3 font weights per application (e.g. Regular 400, Medium 500, Semibold 600).
- Explicit line-height matched inversely to font size:
  - Body (14px): line-height 1.5 to 1.6
  - Small (12px): line-height 1.4 to 1.5
  - Large Heading (24px - 32px): line-height 1.15 to 1.25 with subtle negative tracking (`letter-spacing: -0.02em`).

### Rule 4: Mathematical Contrast (WCAG 2.1 AA)
- Normal text (<18pt / 24px regular, <14pt / 19px bold): **Minimum 4.5:1** contrast against background.
- Large text (>=18pt or >=14pt bold): **Minimum 3.0:1** contrast.
- Interactive component boundaries, icons, and focus indicators: **Minimum 3.0:1** contrast.

### Rule 5: Visible Keyboard Navigation & Focus Rings
Never suppress outlines without providing a high-contrast replacement.
All focusable elements must support `:focus-visible`:
```css
:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}
```

### Rule 6: High-Performance Snappy Motion
- Micro-interactions (hover, active, toggle): `<= 150ms ease-out`.
- Transitions (modal enter, drawer slide): `<= 200ms cubic-bezier(0.16, 1, 0.3, 1)`.
- Never exceed 250ms for functional UI transitions.
- Always include:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```
