# Feature Specification: Visual Redesign — Deep Teal Foundation

**Feature Branch**: `002-visual-redesign`
**Created**: 2026-03-16
**Status**: Draft
**Input**: User description: "Visual redesign of ProblemGenerator frontend to address color theory gaps, empty white space, weak brand presence, broken typography, and missing visual hierarchy. No code logic changes."

## Constraints

- **Zero code logic changes.** Only CSS custom properties, JSX structure (element ordering/wrapping), static assets (fonts, icons), and markup.
- **No changes to:** state management, API calls, routing, auth flows, billing flows, Supabase integration, Stripe integration, or any business logic.
- **All existing tests must continue to pass** without modification. If a test references a specific CSS class or text content, that class/text must remain unchanged.
- **Constitution compliance:** Respects Principle VI (Simplicity First / YAGNI). No design system framework, no CSS-in-JS migration, no Tailwind adoption.

## Design Direction

**Personality:** Modern and Energetic (Brilliant meets Notion)
**Color direction:** Deep Teal Foundation — dark teal navigation, light teal page backgrounds, topic color-coding, orange CTAs
**Typography:** Plus Jakarta Sans (self-hosted, woff2)
**Icon library:** Lucide React (tree-shakeable, MIT license)

## User Scenarios & Testing

### User Story 1 — Consistent Brand Experience Across All Pages (Priority: P1)

A user navigates any page of the app and immediately recognizes the ProblemGenerator brand through a consistent dark teal navigation bar, light teal page background, and properly loaded Plus Jakarta Sans typography.

**Why this priority**: The nav bar, page background, and font affect every single page. Implementing these first gives a baseline visual improvement across the entire app with minimal effort.

**Independent Test**: Can be tested by navigating to any page (landing, login, dashboard, generate, preview, 404) and confirming the dark teal nav, light teal background, and Plus Jakarta Sans font render correctly.

**Acceptance Scenarios**:

1. **Given** any page of the app, **When** it loads, **Then** the navigation bar has a dark teal background (#0f2b2e) with bright teal logo (#5eead4) and light teal nav links (#99f6e4).
2. **Given** any page of the app, **When** it loads, **Then** the page background is light teal (#f0fdfa) instead of warm cream.
3. **Given** any page, **When** it loads, **Then** Plus Jakarta Sans renders from self-hosted font files (no Google Fonts CDN request).
4. **Given** the active nav link, **When** the user is on that page, **Then** it displays a 2px solid #5eead4 bottom border indicator.

---

### User Story 2 — Landing Page with Visual Hierarchy and Filled Space (Priority: P1)

A visitor lands on the homepage and sees a teal gradient hero section, feature cards with icons, and a "How it works" stepper. The page feels complete with no large empty white space gaps.

**Why this priority**: The landing page is the first impression. Currently it has excessive empty space, no icons, and a flat visual hierarchy.

**Independent Test**: Can be tested by loading the landing page and verifying the gradient hero, icon feature cards, and stepper section all render without large empty gaps.

**Acceptance Scenarios**:

1. **Given** the landing page, **When** it loads, **Then** the hero section has a teal gradient background (linear-gradient from #134e4a to #0d9488) with white heading text and an orange CTA button with a glow shadow.
2. **Given** the landing page, **When** it loads, **Then** three feature cards display with Lucide icons, specific content ("5 Topics", "3 Levels", "Instant PDF"), and box shadows instead of borders.
3. **Given** the landing page, **When** it loads, **Then** a "How it works" section shows a 3-step horizontal flow (Pick topics, Preview test, Download PDF) with numbered teal circles and proper SVG connector elements.
4. **Given** the landing page hero, **When** a user reads the tagline, **Then** it does not contain the word "algorithmic", does not use dashes, and the CTA button has no trailing arrow.

---

### User Story 3 — Color-Coded Topic Selector on Generate Page (Priority: P2)

A user on the Generate page sees each math topic with a distinct color (teal for Algebra, purple for Functions, blue for Geometry, orange for Trigonometry, emerald for Calculus), making topics instantly distinguishable.

**Why this priority**: The Generate page is the core interaction. Color-coding aids recognition, memory, and visual engagement.

**Independent Test**: Can be tested by loading the Generate page and confirming each topic row has its assigned color on the left border, checkbox fill, and template count badge.

**Acceptance Scenarios**:

1. **Given** the Generate page, **When** topics load, **Then** each topic row displays a colored left border matching its assigned color (Algebra: #14b8a6, Functions: #8b5cf6, Geometry: #3b82f6, Trigonometry: #f97316, Calculus: #10b981).
2. **Given** a topic row, **When** the user checks it, **Then** the checkbox fills with the topic's assigned color.
3. **Given** a topic row, **When** it displays template count, **Then** the count appears as a colored pill badge (topic color text on light topic color background).
4. **Given** the difficulty selector, **When** a level is active, **Then** it renders as a filled dark teal chip (#134e4a background, white text) instead of a border-only highlight.

---

### User Story 4 — Dashboard with Structured Cards and Filled Layout (Priority: P2)

An authenticated user sees a dashboard with a teal gradient welcome banner, a quick-action card, a compact subscription status card, a stats row, and grouped account actions. No empty space gaps.

**Why this priority**: The dashboard is the logged-in home screen. Currently it's flat with lots of wasted vertical space.

**Independent Test**: Can be tested by logging in and confirming the welcome banner, quick action card, subscription card, stats row, and account section all render in order.

**Acceptance Scenarios**:

1. **Given** the dashboard, **When** it loads, **Then** a teal gradient banner (linear-gradient from #134e4a to #0d9488) shows "Welcome back" in white and the user's email in light teal.
2. **Given** the dashboard, **When** it loads, **Then** a quick-action card with "Ready to practice?" text and a "Generate New Test" orange CTA button appears below the banner.
3. **Given** a subscribed user, **When** the dashboard loads, **Then** a compact subscription card shows a green dot status indicator, "Active" label, renewal date, and a "Manage" button.
4. **Given** the dashboard, **When** it loads, **Then** a stats row displays three small cards showing template count, topic count, and level count with teal numbers.
5. **Given** the dashboard, **When** it loads, **Then** account actions (Sign Out, Delete Account) are grouped in a single card as a list with chevron indicators.

---

### User Story 5 — Split-Layout Auth Pages (Priority: P2)

A visitor on the Login or Register page sees a split layout: a teal gradient branding panel on the left with value propositions, and the form on the right. The page feels complete without wasted space around a small centered card.

**Why this priority**: Auth pages currently show a small form card floating in empty cream space. The split layout fills the viewport and reinforces the brand during sign-in/sign-up.

**Independent Test**: Can be tested by loading /login and /register and confirming the split layout renders with branding panel and form panel side by side.

**Acceptance Scenarios**:

1. **Given** the login page on desktop, **When** it loads, **Then** a left panel (~38% width) with teal gradient shows "Welcome back" heading and feature bullet points (34 templates, PDF download, 5 topics).
2. **Given** the register page on desktop, **When** it loads, **Then** a left panel shows "Start practicing" heading and a $5/month price display.
3. **Given** either auth page on screens narrower than 768px, **When** it loads, **Then** the layout stacks vertically with the branding panel above the form.
4. **Given** the form panel, **When** it renders, **Then** all existing form fields, validation, and submit behavior work identically to the current implementation.

---

### User Story 6 — Preview Page with Summary Bar and Styled Question Cards (Priority: P2)

A user previewing a generated test sees a dark teal summary bar with test metadata and the Download PDF button, followed by styled question cards with numbered badges and colored left borders.

**Why this priority**: The Preview page is the core output page. Styled cards improve readability and the summary bar keeps controls accessible.

**Independent Test**: Can be tested by generating a test, navigating to the preview page, and confirming the summary bar, controls bar, and question cards render with the new styling.

**Acceptance Scenarios**:

1. **Given** the preview page, **When** it loads, **Then** a dark teal (#134e4a) summary bar shows the test title, metadata pills (topic, difficulty, question count), and a Download PDF button.
2. **Given** the preview page, **When** it loads, **Then** a white controls bar shows the "Include answers" checkbox and a "+ New Test" link.
3. **Given** a question card, **When** it renders, **Then** it has a teal left border, a numbered badge (teal circle with white number), and a subtopic pill badge.
4. **Given** a question card, **When** "Show Answer" is clicked, **Then** the answer section renders identically to the current implementation (teal left-bordered box).

---

### Edge Cases

- What happens on screens between 768px and 960px where the split auth layout may feel cramped? (Branding panel collapses to a compact banner.)
- What happens when a topic color is added for a new topic in the future? (Topic color map in CSS custom properties makes adding a new color a single-line change.)
- What happens if Lucide React fails to install or tree-shake correctly? (Emoji fallback: feature cards use emoji icons as in the mockups.)
- What happens with the existing `prefers-reduced-motion` media query? (All new animations respect it. The gradient hero and card hover shadows are not animations and do not need motion gating.)
- What about 404, Verify Email, Verify Success, Checkout Success/Cancel pages? (These inherit global styles from the Layout component — dark teal nav bar and light teal background apply automatically. No page-specific changes are needed.)
- What about Geometry, which is not listed in spec 001's FR-016? (Geometry was added post-001 and exists in the backend's Topic enum. The backend's `types.py` Topic enum is the source of truth for the topic list.)

## Requirements

### Functional Requirements

- **FR-VR-001**: System MUST render a dark teal (#0f2b2e) navigation bar with bright teal (#5eead4) logo text and light teal (#99f6e4) nav links on all pages.
- **FR-VR-002**: System MUST use a light teal (#f0fdfa) page background on all pages.
- **FR-VR-003**: System MUST self-host Plus Jakarta Sans font files (woff2 format, weights 400, 500, 600, 700, 800) and load them via @font-face declarations. No Google Fonts CDN dependency. Note: the existing CSS font-family variable already references 'Plus Jakarta Sans' — this change migrates from broken CDN delivery to self-hosted delivery, not a font change.
- **FR-VR-004**: System MUST install Lucide React as a dependency and use its icons for feature cards, stepper connectors, account list chevrons, and other visual elements.
- **FR-VR-005**: System MUST render the landing page hero section with a CSS gradient background (linear-gradient from #134e4a through #0f766e to #0d9488). Only large text (>= 24px or >= 18.66px bold) may appear over the lighter gradient region; body-size text must appear only over the #134e4a end where white achieves 11.1:1 contrast.
- **FR-VR-006**: System MUST render three feature cards on the landing page with Lucide icons, box shadows, and specific content ("5 Topics", "3 Levels", "Instant PDF").
- **FR-VR-007**: System MUST render a "How it works" stepper section on the landing page with 3 numbered steps, teal circles, and SVG connector arrows.
- **FR-VR-008**: System MUST assign a distinct color to each math topic. Each topic has three color variants: a decorative color (for borders, checkbox fills, and non-text accents), a dark text color (for text labels on white/light backgrounds, must pass 4.5:1), and a light background color (for pill badge backgrounds):
  - Algebra: decorative #14b8a6, text #0d6d63, light #ccfbf1
  - Functions: decorative #8b5cf6, text #6d28d9, light #ede9fe
  - Geometry: decorative #3b82f6, text #1d4ed8, light #dbeafe
  - Trigonometry: decorative #f97316, text #c2410c, light #fff7ed
  - Calculus: decorative #10b981, text #047857, light #d1fae5
  Topic left borders and checkbox fills use the decorative color. Template count badge text and topic labels use the dark text color. The decorative colors are used for thick (3px+) borders which are decorative accents, not UI component boundaries in the WCAG 1.4.11 sense.
- **FR-VR-009**: System MUST render the active difficulty level as a filled dark teal chip (#134e4a background, white text) and inactive levels as white chips with light borders.
- **FR-VR-010**: System MUST render Login and Register pages in a split layout: teal gradient branding panel (left, ~38%) and white form panel (right, ~62%). On screens < 768px, panels MUST stack vertically.
- **FR-VR-011**: System MUST render the Dashboard with: teal gradient welcome banner, quick-action card, subscription status card with green dot indicator, stats row (3 cards), and grouped account actions list.
- **FR-VR-012**: System MUST render the Preview page with: dark teal summary bar (metadata + Download PDF), white controls bar (answers checkbox + new test link), and question cards with numbered teal badges and colored left borders.
- **FR-VR-013**: System MUST use box-shadow instead of borders for non-interactive container card components (`.card` class and equivalent inline-styled cards). Form inputs, badges, semantic borders, and interactive component boundaries are excluded from this change.
- **FR-VR-014**: System MUST render the orange (#f97316) CTA button with a glow shadow (box-shadow with orange tint) for primary actions only. Secondary buttons and destructive actions MUST NOT use orange.
- **FR-VR-015**: System MUST maintain WCAG 2.1 Level AA compliance:
  - All text: minimum 4.5:1 contrast ratio against background
  - Large text (>= 24px or >= 18.66px bold): minimum 3:1
  - UI component boundaries: minimum 3:1 against adjacent colors
  - Muted text color MUST be #78716c or darker (not #a8a29e) on #f0fdfa backgrounds
  - All topic text colors (dark variants) MUST pass 4.5:1 for text-on-white usage. Decorative topic colors (used only for borders and checkbox fills) are exempt from text contrast requirements
- **FR-VR-016**: System MUST NOT change any existing routing, state management, API calls, auth flows, billing flows, or business logic.
- **FR-VR-017**: System MUST preserve all existing ARIA labels, roles, focus management, skip link, and keyboard navigation behavior.

### Key Entities

No new data entities. This spec affects only visual presentation of existing entities.

### Design Tokens (New/Modified)

**New CSS custom properties:**

```
--nav-bg: #0f2b2e
--nav-text: #5eead4
--nav-link: #99f6e4
--nav-link-active-border: #5eead4
--bg-page: #f0fdfa (modified from #fafaf9)
--color-topic-algebra: #14b8a6 (decorative)
--color-topic-algebra-text: #0d6d63 (4.5:1+ on white)
--color-topic-algebra-light: #ccfbf1
--color-topic-functions: #8b5cf6 (decorative)
--color-topic-functions-text: #6d28d9 (4.5:1+ on white)
--color-topic-functions-light: #ede9fe
--color-topic-geometry: #3b82f6 (decorative)
--color-topic-geometry-text: #1d4ed8 (4.5:1+ on white)
--color-topic-geometry-light: #dbeafe
--color-topic-trigonometry: #f97316 (decorative)
--color-topic-trigonometry-text: #c2410c (4.5:1+ on white)
--color-topic-trigonometry-light: #fff7ed
--color-topic-calculus: #10b981 (decorative)
--color-topic-calculus-text: #047857 (4.5:1+ on white)
--color-topic-calculus-light: #d1fae5
--shadow-card: 0 1px 4px rgba(0,0,0,0.06)
--shadow-card-hover: 0 2px 8px rgba(0,0,0,0.1)
--shadow-cta-glow: 0 2px 8px rgba(249,115,22,0.3)
```

**Modified CSS custom properties:**

```
--bg-page: #fafaf9 → #f0fdfa
--shadow-sm: warm stone tint → neutral tint
--shadow-md: warm stone tint → neutral tint
```

**Unchanged:**
- All accent/CTA colors (orange scale)
- All semantic colors (success, error, warning)
- Focus ring (amber #fbbf24)
- All primary teal scale values
- All stone neutral scale values
- All spacing, typography size, and radius tokens

## Success Criteria

### Measurable Outcomes

- **SC-VR-001**: Plus Jakarta Sans font loads successfully on all pages. Verified by (a) checking the browser's computed font-family for body text is 'Plus Jakarta Sans' via Playwright's page.evaluate(), and (b) confirming no network request is made to fonts.googleapis.com.
- **SC-VR-002**: All pages pass WCAG 2.1 Level AA automated accessibility audit (axe-core or similar, zero critical/serious violations).
- **SC-VR-003**: No page has a visible gap of unpopulated background exceeding 96px between distinct content sections, as verified by visual inspection of Playwright full-page screenshots.
- **SC-VR-004**: All 5 math topics display with their assigned distinct colors on the Generate page (verified by Playwright snapshot).
- **SC-VR-005**: All existing 489 tests (332 backend + 157 frontend) continue to pass without modification.
- **SC-VR-006**: Lighthouse performance score does not decrease by more than 5 points after the redesign (font files and icon library add minimal bundle size).
- **SC-VR-007**: The dark teal navigation bar renders consistently across Chrome, Firefox, and Safari (verified by Playwright cross-browser screenshots).

## Files Affected

### Modified
- `frontend/src/index.css` — design token updates, @font-face declarations, nav/card/button style updates
- `frontend/index.html` — remove Google Fonts `<link>` tag (file is at frontend root, not in src/)
- `frontend/src/components/Layout/Header.tsx` — dark teal nav bar styling
- `frontend/src/pages/Landing.tsx` — gradient hero, icon feature cards, how-it-works stepper
- `frontend/src/pages/Login.tsx` — split layout with branding panel
- `frontend/src/pages/Register.tsx` — split layout with branding panel
- `frontend/src/pages/Dashboard.tsx` — card structure, welcome banner, stats row
- `frontend/src/pages/Generate.tsx` — topic color styling updates
- `frontend/src/pages/Preview.tsx` — summary bar, question card styling
- `frontend/src/components/TestConfig/TopicSelector.tsx` — topic color-coded left borders and badges
- `frontend/src/components/TestConfig/DifficultySelector.tsx` — filled chip active state
- `frontend/src/components/TestPreview/QuestionCard.tsx` — numbered badge, colored left border

### New
- `frontend/src/assets/fonts/PlusJakartaSans-*.woff2` — self-hosted font files (5 weights)
- `frontend/package.json` — add `lucide-react` dependency

### Unchanged
- All backend files
- All test files
- All routing, state, context, and service files
- `frontend/src/App.tsx`
- All auth and billing components (ProtectedRoute, SubscriptionContext, etc.)

## References

- Mockups: `.superpowers/brainstorm/75594-1773691372/` (landing, dashboard, generate, auth, preview before/after comparisons)
- Screenshots of current state: `screenshots/` directory
- Color theory research: Figma "100 Color Combinations", WCAG 2.1, 60-30-10 rule analysis
- Design direction: "Deep Teal Foundation" (Option A from brainstorming)
- Typography: Plus Jakarta Sans (Option B, self-hosted)
- Icon library: Lucide React (tree-shakeable, MIT)
