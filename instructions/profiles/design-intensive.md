# Quality Profile: Design-Intensive Product (`DESIGN_INTENSIVE`)

## 1. Overview and Intent
The **Design-Intensive Product** profile is tailored for customer-facing web applications, mobile apps, smart TV, or smartwatch user interfaces where visual polish, pixel perfection, smooth responsive transitions, design token compliance, and accessibility ergonomics are paramount. It prevents UI regressions, arbitrary styling overrides, visual glitches, and Cumulative Layout Shift (CLS).

---

## 2. Threshold Matrix and Requirements

| Quality Dimension | Requirement | Threshold / Policy |
|---|---|---|
| **Code Coverage** | Mandatory | **>= 75%** coverage on UI components and hooks |
| **Design Token Adherence** | Mandatory | 100% token usage; zero raw hex colors or magic px |
| **Responsive Verification** | Mandatory | Verified across Mobile (375px), Tablet (768px), Desktop (1440px) |
| **Accessibility (a11y)** | Mandatory | WCAG 2.1 Level AA compliance; contrast ratio >= 4.5:1 |
| **Component States** | Mandatory | All 7 interactive states defined for interactive primitives |
| **Independent Review (G5)** | Mandatory | Visual audit and component token verification |
| **Mandatory Baseline Rules** | Non-Negotiable | BL-001 through BL-007 enforced without exception |

---

## 3. Engineering Guidelines for Design-Intensive Products

### 3.1 Strict Design Token Adherence
- **Zero Raw Hex / Pixel Magic Numbers**:
  - Never write inline styles or CSS rules with raw hex codes (e.g., `color: #3b82f6`) or arbitrary pixel margins (e.g., `margin-top: 13px`).
  - All spacing, colors, radii, shadows, and fonts must consume semantic design tokens defined in `contracts/design/contract.json` (e.g., `var(--space-4)`, `var(--color-primary)`).
- **Design Token Linter**: Automated checks must scan JSX/TSX/CSS for undeclared style values and fail builds containing hardcoded magic numbers.

### 3.2 7-State Component Specification
Every interactive UI primitive (Button, Input, Checkbox, Select, Modal, Tab) must implement explicit visual styling for all seven canonical states:
1. **Rest / Default**: Balanced contrast and clear visual affordance.
2. **Hover**: Smooth elevation or color shift (150ms-250ms duration).
3. **Active / Pressed**: Tactile feedback (e.g., 1px translate or inset shadow).
4. **Focus-Visible**: High-contrast outline ring (minimum 2px thickness with 2px offset) strictly compliant with keyboard navigation.
5. **Disabled**: Visual deemphasis (`opacity: 0.5`, `cursor: not-allowed`), `aria-disabled="true"`, zero click events.
6. **Loading / Busy**: Non-shifting spinner or skeleton loader with `aria-busy="true"`.
7. **Error / Invalid**: High-contrast error border, accessible alert message, `aria-invalid="true"`.

### 3.3 Responsive Breakpoints & Container Layouts
- Visual layouts must adapt gracefully across viewports without horizontal scrollbars:
  - Mobile: `375px` to `639px`
  - Tablet: `640px` to `1023px`
  - Desktop: `1024px` to `1439px`
  - Ultra-Wide: `1440px+`
- Prefer CSS Grid and Flexbox with `min()`, `max()`, and `clamp()` fluid typography.
- Enforce Zero Cumulative Layout Shift (CLS < 0.1) by specifying explicit aspect-ratios and dimensions for images and containers.

### 3.4 Theme Consistency & Dark Mode
- Support seamless light and dark themes using CSS Custom Properties.
- Theme switching must occur dynamically via data attributes (`data-theme="dark"`) without re-rendering component trees or causing layout jitter.
- Both themes must independently satisfy WCAG 2.1 AA color contrast standards.
