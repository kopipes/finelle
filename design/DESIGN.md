---
name: Precision Ledger
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#444653'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#757684'
  outline-variant: '#c4c5d5'
  surface-tint: '#3755c3'
  primary: '#00288e'
  on-primary: '#ffffff'
  primary-container: '#1e40af'
  on-primary-container: '#a8b8ff'
  inverse-primary: '#b8c4ff'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d0e1fb'
  on-secondary-container: '#54647a'
  tertiary: '#003d27'
  on-tertiary: '#ffffff'
  tertiary-container: '#00563a'
  on-tertiary-container: '#3fd298'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde1ff'
  primary-fixed-dim: '#b8c4ff'
  on-primary-fixed: '#001453'
  on-primary-fixed-variant: '#173bab'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.03em
  mono-data:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 0.25rem
  sm: 0.5rem
  md: 1rem
  lg: 1.5rem
  xl: 2rem
  gutter: 1rem
  margin-mobile: 1rem
  margin-desktop: 2rem
---

## Brand & Style
The brand personality is authoritative, transparent, and meticulous. It is designed for financial controllers, HR administrators, and payroll specialists who require a tool that minimizes cognitive load while maximizing data accuracy. 

The design system adopts a **Modern Corporate** style with a focus on **Information Density**. It avoids unnecessary ornamentation, favoring high-clarity typography and a structured grid. The emotional response should be one of confidence and reliability—users must feel that their data is secure and their workflows are logical. Visual hierarchy is established through purposeful color application and strict alignment rather than decorative elements.

## Colors
The palette is rooted in stability and utility. 

- **Primary (#1E40AF):** Used for primary actions, active navigation states, and branding. It represents institutional trust.
- **Secondary (#64748B):** Reserved for supporting information, labels, and iconography. It provides enough contrast for legibility without competing with primary data.
- **Accent/Positive (#10B981):** Specifically for growth indicators, completed payments, and "success" status badges.
- **Neutral/Background (#F8FAFC):** A cool-toned off-white that reduces eye strain during long periods of data entry and review.
- **Semantic Red (#EF4444):** (Implicit) Reserved for payroll errors, overdrawn accounts, or critical warnings.

## Typography
**Inter** is utilized for its exceptional legibility and tabular numeric features. 

For all financial tables and currency displays, the `font-feature-settings: 'tnum' (tabular figures)` must be enabled to ensure that columns of numbers align perfectly, facilitating easy scanning of vertical data. Headlines use a tighter letter-spacing for a professional, "tucked" appearance. Body text is set primarily at 14px to balance density with readability.

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. Navigation and sidebars are fixed, while the primary workspace (containing tables and reports) is fluid to maximize real estate on large monitors used by financial professionals.

A **4px base grid** governs all spacing.
- **Data Tables:** Use `sm` (8px) vertical cell padding for high-density views, and `md` (16px) for standard views.
- **Breakpoints:** 
  - Mobile (< 640px): 4-column grid, 16px margins.
  - Tablet (640px - 1024px): 8-column grid, 24px margins.
  - Desktop (> 1024px): 12-column grid, 32px margins.
- **Hierarchical Depth:** Indentation in report views should follow increments of 1.5rem (`lg`) to clearly signify parent-child relationships in line items.

## Elevation & Depth
This design system uses **Tonal Layers** and **Low-Contrast Outlines** rather than heavy shadows to maintain a "flat" professional aesthetic.

- **Level 0 (Background):** #F8FAFC.
- **Level 1 (Cards/Containers):** Pure white background with a 1px solid border in #E2E8F0. No shadow.
- **Level 2 (Dropdowns/Modals):** Pure white background with a subtle, tight shadow (0 4px 6px -1px rgb(0,0,0,0.1)) to indicate focus.
- **Active State:** A 2px primary-colored border-left is used on active list items or navigation links to indicate focus without adding bulk.

## Shapes
A **Soft (0.25rem)** roundedness is applied consistently across the system. This provides a modern touch while maintaining the structural rigidity expected of a financial tool. 

- **Inputs & Buttons:** 4px (0.25rem) radius.
- **Large Containers/Cards:** 8px (0.5rem) radius.
- **Badges:** 2px or fully pill-shaped (16px) for role-based labels to distinguish them from interactive buttons.

## Components
- **Data Tables:** Headers must have a subtle gray background (#F1F5F9) and sticky positioning. Cell text is `body-md`, while headers use `label-sm`.
- **Form Inputs (Currency):** Must include a fixed leading currency symbol ($) and right-aligned text to mimic financial ledger entry.
- **Role-based Badges:** Small, high-contrast labels (e.g., "Admin," "Employee"). Use `secondary` for standard roles and `primary` for elevated permissions.
- **Status Indicators:** Use a combination of a colored dot and text. Never rely on color alone (accessibility). Emerald green for "Paid," Slate gray for "Draft," and Amber for "Pending."
- **Hierarchical Reports:** Use chevron-toggle icons for row expansion. Expanded rows should have a very light blue tint (#EFF6FF) to group child elements visually.
- **Buttons:** 
  - *Primary:* Solid #1E40AF with white text.
  - *Secondary:* Ghost style with #1E40AF border and text.
  - *Tertiary:* Text-only with secondary gray for utility actions (e.g., "Cancel," "Export").