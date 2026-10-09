# Design System Specification (`DESIGN.md`)

> **The Core Brand Contract**: This document defines the immutable visual rules, token scales, interactive behaviors, and accessibility invariants for all user interfaces in this project. All coding agents, developers, and tools MUST read and follow these rules.

---

## 1. Principles & Visual Voice

1. **Restraint over Clutter**: Every element must earn its visual weight. Avoid decorative flourishes that do not convey information.
2. **Mathematical Harmony**: All spacing, sizing, and type scales adhere to predictable geometric ratios (4px baseline and minor-third type scale).
3. **Accessibility by Construction**: Contrast ratios MUST meet WCAG 2.1 AA (>= 4.5:1 for body text, >= 3.0:1 for large text and key UI borders) in both Light and Dark themes.
4. **Motion with Intent**: Animations exist only to guide spatial orientation and state feedback. All transitions respect `prefers-reduced-motion`.

---

## 2. Design Tokens

### 2.1 Color Palette (OKLCH Color Space)

```css
:root {
  /* Surface & Background */
  --color-bg: oklch(98% 0.005 240);
  --color-surface: oklch(100% 0 0);
  --color-surface-hover: oklch(96% 0.008 240);
  --color-border: oklch(88% 0.012 240);
  --color-border-subtle: oklch(93% 0.008 240);

  /* Typography */
  --color-text: oklch(20% 0.02 240);
  --color-text-soft: oklch(40% 0.02 240);
  --color-text-muted: oklch(55% 0.015 240);

  /* Primary Accent (Blue) */
  --color-accent: oklch(55% 0.20 250);
  --color-accent-hover: oklch(48% 0.22 250);
  --color-accent-active: oklch(42% 0.24 250);
  --color-accent-subtle: oklch(94% 0.04 250);

  /* Semantic Feedback */
  --color-success: oklch(62% 0.18 145);
  --color-warning: oklch(72% 0.16 85);
  --color-error: oklch(58% 0.22 28);
  --color-info: oklch(60% 0.15 220);
}

:root[data-theme="dark"] {
  /* Surface & Background */
  --color-bg: oklch(14% 0.01 240);
  --color-surface: oklch(18% 0.012 240);
  --color-surface-hover: oklch(22% 0.015 240);
  --color-border: oklch(28% 0.015 240);
  --color-border-subtle: oklch(22% 0.012 240);

  /* Typography */
  --color-text: oklch(96% 0.005 240);
  --color-text-soft: oklch(82% 0.01 240);
  --color-text-muted: oklch(65% 0.012 240);

  /* Primary Accent */
  --color-accent: oklch(65% 0.20 250);
  --color-accent-hover: oklch(72% 0.18 250);
  --color-accent-active: oklch(78% 0.16 250);
  --color-accent-subtle: oklch(24% 0.06 250);

  /* Semantic Feedback */
  --color-success: oklch(70% 0.16 145);
  --color-warning: oklch(78% 0.14 85);
  --color-error: oklch(66% 0.20 28);
  --color-info: oklch(68% 0.14 220);
}
```

### 2.2 Typography Scale

```css
:root {
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  --font-mono: ui-monospace, "SF Mono", Monaco, "Cascadia Code", "Courier New", monospace;

  --text-xs: 0.75rem;     /* 12px - Line height: 1.00rem */
  --text-sm: 0.875rem;    /* 14px - Line height: 1.25rem */
  --text-base: 1.000rem;  /* 16px - Line height: 1.50rem */
  --text-lg: 1.125rem;    /* 18px - Line height: 1.75rem */
  --text-xl: 1.250rem;    /* 20px - Line height: 1.75rem */
  --text-2xl: 1.500rem;   /* 24px - Line height: 2.00rem */
  --text-3xl: 1.875rem;   /* 30px - Line height: 2.25rem */
  --text-4xl: 2.250rem;   /* 36px - Line height: 2.50rem */
}
```

### 2.3 Spacing Grid (4px Baseline)

```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.50rem;   /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1.00rem;   /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.50rem;   /* 24px */
  --space-8: 2.00rem;   /* 32px */
  --space-10: 2.50rem;  /* 40px */
  --space-12: 3.00rem;  /* 48px */
  --space-16: 4.00rem;  /* 64px */
}
```

### 2.4 Elevation & Radii

```css
:root {
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;

  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
```

### 2.5 Motion & Transitions

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --duration-fast: 0ms;
    --duration-normal: 0ms;
    --duration-slow: 0ms;
  }
}
```

---

## 3. Core Component Blueprints

### Primary Button
- **Height**: 40px (desktop) / 44px (touch)
- **Padding**: `var(--space-2) var(--space-4)`
- **Background**: `var(--color-accent)`
- **Text Color**: `#ffffff` (meets 4.5:1 on both themes)
- **Border Radius**: `var(--radius-md)`
- **States**: Hover (`--color-accent-hover`), Active (`--color-accent-active`), Focus (`outline: 2px solid var(--color-accent)`, `outline-offset: 2px`).

### Surface Card
- **Background**: `var(--color-surface)`
- **Border**: `1px solid var(--color-border)`
- **Border Radius**: `var(--radius-lg)`
- **Padding**: `var(--space-6)`
- **Shadow**: `var(--shadow-sm)`

---

## 4. Strict Prohibitions

1. **NO arbitrary hex codes** in component files (e.g. `color: #4f46e5`). Always use `var(--color-...)`.
2. **NO ungrounded spacing** (e.g. `margin: 17px`). Always snap to the 4px spacing scale.
3. **NO missing interactive states**. Every clickable element must define `:hover`, `:active`, and `:focus-visible`.
4. **NO inaccessible contrast**. Text under 18px MUST have a minimum contrast ratio of 4.5:1 against its background.
