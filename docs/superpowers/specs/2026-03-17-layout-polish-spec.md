# Spec: Layout Polish, Animations, and Punctuation Fix

**Date**: 2026-03-17
**Status**: Implemented

---

## Overview

Visual polish pass addressing floating banner/hero layouts, auth page viewport fill, stray punctuation in geometry questions, and micro-animations across the site.

---

## Layout Fixes

### Full-bleed breakout system (index.css)
Three new CSS utility classes that break elements out of Layout.tsx's 960px max-width container:
- `.full-bleed` — spans full viewport width (banners, heroes)
- `.full-bleed-padded` — spans full width with centered content padding (toolbars)
- `.auth-full` — escapes container width + padding, fills viewport height minus header

### Pages updated
- **Dashboard.tsx**: Banner gets `.full-bleed` — spans edge to edge
- **Landing.tsx**: Hero gets `.full-bleed` — spans edge to edge
- **Preview.tsx**: Summary bar + controls bar get `.full-bleed-padded`
- **Login.tsx**: Split layout gets `.auth-full` — both panels fill full viewport height
- **Register.tsx**: Same as Login

### Auth page feature bullets (Login + Register)
Updated to: Unlimited math questions, Daily streak tracker, Questions tracker, 34 question templates, Instant PDF download, Unlimited test banks

---

## Geometry Punctuation Fix

### Problem
Question strings like `"Find the slope of the line passing through ${p1}$ and ${p2}$."` rendered commas and periods on separate lines because MathRenderer treats each `$...$` block as display math.

### Fix (backend)
Merged multiple `$...$` point blocks into single blocks:
- **"P1 and P2" patterns**: `${p1} \text{ and } {p2}$` (one math block with `\text{}` connector)
- **"A, B, C" vertex patterns**: `$A = {a_pt}, \; B = {b_pt}, \; C = {c_pt}$` (one block)
- Trailing periods removed from all geometry question strings

### Files modified
- `backend/app/engine/topics/geometry/lines.py` — 6 question_latex strings
- `backend/app/engine/topics/geometry/shapes.py` — 13 question_latex strings

---

## Micro-Animations (index.css)

All wrapped in `@media (prefers-reduced-motion: reduce)` fallback.

| Class | Effect | Duration |
|---|---|---|
| `.page-enter` | fadeIn on page mount | 300ms |
| `.card-hover` | translateY(-2px) + shadow on hover | 150ms |
| `.stagger-1/2/3` | animation-delay 0/100/200ms | — |
| `.stat-pop` | fadeIn for stat numbers | 200ms |
| `.reveal-enter` | slideDown for answer/solution reveals | 200ms |
| `.btn-primary:active` | scale(0.98) press feedback | — |

### Applied to
- Dashboard: page-enter, stat-pop on stat cards
- Landing: page-enter, stagger + card-hover on feature cards, stagger on how-it-works steps
- Preview: page-enter
- QuestionCard: reveal-enter on solution/answer sections

---

## Test Fixes

### Root cause: MSW handler leakage between parallel test files
- `Dashboard.test.tsx`: Added explicit `beforeEach` handler for subscription-status (self-contained, not reliant on default handler that parallel tests can override)
- `billing.test.tsx`: Removed `StatsProvider` from generic `renderWithProviders` helper (only Dashboard-specific helpers need it; SubscriptionConsumer tests don't render Dashboard)
