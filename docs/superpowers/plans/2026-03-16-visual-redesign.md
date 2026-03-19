# Visual Redesign — Deep Teal Foundation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the ProblemGenerator frontend with a Deep Teal Foundation color direction — dark teal nav, light teal backgrounds, topic color-coding, self-hosted fonts, and Lucide icons — without changing any code logic.

**Architecture:** CSS-first approach. Update design tokens in `index.css`, then modify each page component's inline `React.CSSProperties` objects. No new components are created — only existing components are restyled. Font files are self-hosted as static assets. Lucide React is added as a dependency for icons.

**Tech Stack:** React 18, TypeScript, CSS Custom Properties, Plus Jakarta Sans (woff2), Lucide React, Vite 6

**Spec:** `PROBLEMGENERATOR/specs/002-visual-redesign/spec.md`

**Baseline:** 157 frontend tests passing (11 test files). All must continue to pass after every task.

---

## File Structure

### New Files
- `frontend/src/assets/fonts/PlusJakartaSans-Regular.woff2` — weight 400
- `frontend/src/assets/fonts/PlusJakartaSans-Medium.woff2` — weight 500
- `frontend/src/assets/fonts/PlusJakartaSans-SemiBold.woff2` — weight 600
- `frontend/src/assets/fonts/PlusJakartaSans-Bold.woff2` — weight 700
- `frontend/src/assets/fonts/PlusJakartaSans-ExtraBold.woff2` — weight 800

### Modified Files
- `frontend/index.html` — remove Google Fonts `<link>` tags (lines 7-9)
- `frontend/package.json` — add `lucide-react` dependency (line 20)
- `frontend/src/index.css` — design token updates, @font-face declarations, card/shadow updates (389 lines, ~30 lines added, ~10 lines modified)
- `frontend/src/components/Layout/Header.tsx` — dark teal nav bar (72 lines, full restyle of inline styles)
- `frontend/src/pages/Landing.tsx` — gradient hero, icon cards, stepper section (94 lines, major restyle + new JSX)
- `frontend/src/pages/Login.tsx` — split layout with branding panel (138 lines, restyle container + add branding panel)
- `frontend/src/pages/Register.tsx` — split layout with branding panel (179 lines, restyle container + add branding panel)
- `frontend/src/pages/Dashboard.tsx` — card structure, welcome banner, stats row (355 lines, restyle inline styles)
- `frontend/src/pages/Generate.tsx` — page title styling update (158 lines, minor style changes)
- `frontend/src/pages/Preview.tsx` — summary bar, controls bar, question card styling (195 lines, restyle inline styles)
- `frontend/src/components/TestConfig/TopicSelector.tsx` — topic color-coded left borders and badges (383 lines, add topic color map + restyle)
- `frontend/src/components/TestConfig/DifficultySelector.tsx` — filled chip active state (72 lines, restyle active/inactive styles)
- `frontend/src/components/TestPreview/QuestionCard.tsx` — numbered badge, colored left border (read file first to determine exact changes)

---

## Chunk 1: Foundation (Fonts, Tokens, Nav Bar)

### Task 1: Download and Self-Host Plus Jakarta Sans Font Files

**Files:**
- Create: `frontend/src/assets/fonts/` directory with 5 woff2 files

- [ ] **Step 1: Create the fonts directory**

```bash
cd PROBLEMGENERATOR/frontend && mkdir -p src/assets/fonts
```

- [ ] **Step 2: Download Plus Jakarta Sans woff2 files from fontsource**

```bash
cd PROBLEMGENERATOR/frontend
npm install --save @fontsource/plus-jakarta-sans 2>&1 | tail -3
```

- [ ] **Step 3: Copy the woff2 files to assets/fonts**

Copy the 5 weight files (400, 500, 600, 700, 800) from `node_modules/@fontsource/plus-jakarta-sans/files/` to `src/assets/fonts/`. The files are named like `plus-jakarta-sans-latin-400-normal.woff2`. Copy only the `latin` subset.

```bash
cd PROBLEMGENERATOR/frontend
for weight in 400 500 600 700 800; do
  cp node_modules/@fontsource/plus-jakarta-sans/files/plus-jakarta-sans-latin-${weight}-normal.woff2 src/assets/fonts/ 2>/dev/null || echo "weight ${weight} not found, checking alternate naming..."
done
ls src/assets/fonts/
```

If the file naming differs, list `node_modules/@fontsource/plus-jakarta-sans/files/` and find the correct woff2 files for latin subset, weights 400-800.

- [ ] **Step 4: Uninstall the fontsource package (we only needed the files)**

```bash
cd PROBLEMGENERATOR/frontend && npm uninstall @fontsource/plus-jakarta-sans 2>&1 | tail -3
```

- [ ] **Step 5: Verify font files exist**

```bash
ls -la PROBLEMGENERATOR/frontend/src/assets/fonts/*.woff2
```

Expected: 5 woff2 files present.

---

### Task 2: Update index.html — Remove Google Fonts CDN

**Files:**
- Modify: `frontend/index.html:7-9`

- [ ] **Step 1: Remove the three Google Fonts link tags**

In `frontend/index.html`, remove these three lines (7-9):

```html
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&display=swap" rel="stylesheet">
```

The file should become:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ProblemGenerator</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 2: Run tests to verify nothing breaks**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

---

### Task 3: Update index.css — Font-Face Declarations and Design Token Updates

**Files:**
- Modify: `frontend/src/index.css:1-118` (add @font-face before :root, update tokens inside :root)

- [ ] **Step 1: Add @font-face declarations at the top of index.css**

Insert these declarations BEFORE the `:root {` block (before the current line 8). Adjust file names to match the actual files downloaded in Task 1:

```css
/* --------------------------------------------------------------------------
   0. Self-Hosted Fonts
   -------------------------------------------------------------------------- */
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('./assets/fonts/plus-jakarta-sans-latin-400-normal.woff2') format('woff2');
}
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('./assets/fonts/plus-jakarta-sans-latin-500-normal.woff2') format('woff2');
}
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('./assets/fonts/plus-jakarta-sans-latin-600-normal.woff2') format('woff2');
}
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('./assets/fonts/plus-jakarta-sans-latin-700-normal.woff2') format('woff2');
}
@font-face {
  font-family: 'Plus Jakarta Sans';
  font-style: normal;
  font-weight: 800;
  font-display: swap;
  src: url('./assets/fonts/plus-jakarta-sans-latin-800-normal.woff2') format('woff2');
}
```

- [ ] **Step 2: Update design tokens inside :root**

Make these specific changes inside the `:root` block:

**Note: All line references below are to the ORIGINAL file before @font-face insertion. After Step 1, lines shift by ~35. Locate tokens by name, not line number.**

**Change `--bg-page` (find `--bg-page:`):**
```css
  --bg-page: #f0fdfa;
```

**Change `--text-muted` (find `--text-muted:`) to pass WCAG AA on #f0fdfa (FR-VR-015):**
```css
  --text-muted: #78716c;
```

**Update `--shadow-sm` and `--shadow-md` to neutral tint (find `--shadow-sm:`):**
```css
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.08);
```

**Add nav tokens after the Backgrounds section (find `--bg-elevated:`):**
```css
  /* Navigation */
  --nav-bg: #0f2b2e;
  --nav-text: #5eead4;
  --nav-link: #99f6e4;
  --nav-link-active-border: #5eead4;
```

**Add topic color tokens after the Focus section (after line 62):**
```css
  /* Topic Colors */
  --color-topic-algebra: #14b8a6;
  --color-topic-algebra-text: #0d6d63;
  --color-topic-algebra-light: #ccfbf1;
  --color-topic-functions: #8b5cf6;
  --color-topic-functions-text: #6d28d9;
  --color-topic-functions-light: #ede9fe;
  --color-topic-geometry: #3b82f6;
  --color-topic-geometry-text: #1d4ed8;
  --color-topic-geometry-light: #dbeafe;
  --color-topic-trigonometry: #f97316;
  --color-topic-trigonometry-text: #c2410c;
  --color-topic-trigonometry-light: #fff7ed;
  --color-topic-calculus: #10b981;
  --color-topic-calculus-text: #047857;
  --color-topic-calculus-light: #d1fae5;
```

**Add card shadow tokens after the existing Shadows section (after line 112):**
```css
  --shadow-card: 0 1px 4px rgba(0, 0, 0, 0.06);
  --shadow-card-hover: 0 2px 8px rgba(0, 0, 0, 0.1);
  --shadow-cta-glow: 0 2px 8px rgba(249, 115, 22, 0.3);
```

- [ ] **Step 3: Update the .card utility class to use box-shadow instead of border**

Change the `.card` class (currently lines 327-337):

```css
.card {
  background: var(--bg-card);
  border: none;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition-normal);
}

.card:hover {
  box-shadow: var(--shadow-card-hover);
}
```

- [ ] **Step 4: Add CTA glow to .btn-primary**

Add after the existing `.btn-primary:hover:not(:disabled)` rule (after line 219):

```css
.btn-primary:not(:disabled) {
  box-shadow: var(--shadow-cta-glow);
}
```

- [ ] **Step 5: Run tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 6: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/assets/fonts/ frontend/index.html frontend/src/index.css
git commit -m "feat(ui): self-host Plus Jakarta Sans, update design tokens and card styles

- Add @font-face declarations for weights 400-800 (woff2)
- Remove Google Fonts CDN dependency from index.html
- Update --bg-page to light teal (#f0fdfa)
- Add nav, topic color, and card shadow tokens
- Update .card to use box-shadow instead of border
- Add CTA glow shadow to .btn-primary"
```

---

### Task 4: Install Lucide React

**Files:**
- Modify: `frontend/package.json` (add dependency)

- [ ] **Step 1: Install lucide-react**

```bash
cd PROBLEMGENERATOR/frontend && npm install lucide-react 2>&1 | tail -5
```

- [ ] **Step 2: Verify it installed correctly**

```bash
cd PROBLEMGENERATOR/frontend && node -e "require('lucide-react')" 2>&1 || echo "ESM module, checking differently..."
ls node_modules/lucide-react/dist/ | head -5
```

- [ ] **Step 3: Run tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 4: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/package.json frontend/package-lock.json
git commit -m "feat(ui): add lucide-react icon library"
```

---

### Task 5: Restyle Header Component — Dark Teal Nav Bar

**Files:**
- Modify: `frontend/src/components/Layout/Header.tsx` (lines 4-43, inline style objects)

- [ ] **Step 1: Update the inline style objects in Header.tsx**

Replace the style objects (lines 4-43) with:

```typescript
const headerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: 'var(--space-4) var(--space-7)',
  backgroundColor: 'var(--nav-bg)',
  position: 'sticky',
  top: 0,
  zIndex: 50,
};

const brandStyle: React.CSSProperties = {
  fontSize: 'var(--font-size-xl)',
  fontWeight: 700,
  color: 'var(--nav-text)',
  textDecoration: 'none',
  fontFamily: 'var(--font-family)',
};

const navStyle: React.CSSProperties = {
  display: 'flex',
  gap: 'var(--space-6)',
};

const linkBase: React.CSSProperties = {
  textDecoration: 'none',
  fontSize: 'var(--font-size-sm)',
  fontWeight: 500,
  color: 'var(--nav-link)',
  padding: 'var(--space-1) 0',
  borderBottom: '2px solid transparent',
  transition: 'color var(--transition-fast), border-color var(--transition-fast)',
};

const linkActive: React.CSSProperties = {
  ...linkBase,
  color: 'var(--nav-text)',
  borderBottomColor: 'var(--nav-link-active-border)',
};
```

Key changes:
- `headerStyle.backgroundColor`: `var(--bg-elevated)` becomes `var(--nav-bg)`
- `headerStyle.borderBottom`: removed (no border on dark nav)
- `brandStyle.color`: `var(--color-primary-800)` becomes `var(--nav-text)`
- `linkBase.color`: `var(--text-secondary)` becomes `var(--nav-link)`
- `linkActive.color`: `var(--text-primary)` becomes `var(--nav-text)`
- `linkActive.borderBottomColor`: `var(--color-primary-500)` becomes `var(--nav-link-active-border)`

- [ ] **Step 2: Run tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing. The Header tests check for text content and links, not colors, so they should pass.

- [ ] **Step 3: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/components/Layout/Header.tsx
git commit -m "feat(ui): restyle Header with dark teal nav bar"
```

---

## Chunk 2: Landing Page

### Task 6: Restyle Landing Page — Gradient Hero, Icon Cards, Stepper

**Files:**
- Modify: `frontend/src/pages/Landing.tsx` (full restyle — nearly all inline styles change, new JSX sections added)

- [ ] **Step 1: Read the existing Landing.tsx test file to understand what assertions are made**

```bash
cd PROBLEMGENERATOR/frontend && cat src/__tests__/Landing.test.tsx
```

Note which text strings and roles are asserted so we do not break them. Key assertions to preserve:
- The title text "ProblemGenerator" (or whatever the h1 contains)
- The "Get Started" button
- Feature section headings

- [ ] **Step 2: Rewrite Landing.tsx with the new design**

Replace the entire file. Preserve ALL existing text content, semantic HTML roles, and the `useNavigate` + button onClick logic. Only change the visual presentation.

The new Landing.tsx must include:
1. **Import Lucide icons** at the top: `import { BookOpen, Target, FileDown, ChevronRight } from 'lucide-react';`
2. **Gradient hero section**: background `linear-gradient(135deg, #134e4a 0%, #0f766e 50%, #0d9488 100%)`, white heading (large text only over lighter area), light teal tagline, orange CTA with glow shadow
3. **Feature cards**: 3 cards with Lucide icons (BookOpen for Topics, Target for Difficulty, FileDown for PDF), box shadows, specific content ("5 Topics", "3 Levels", "Instant PDF")
4. **How it works stepper**: 3 numbered teal circles with descriptions, connected by ChevronRight icons. Centered, white card with teal border.

**Critical text to preserve (for tests):**
- h1 must contain "ProblemGenerator"
- "Get Started" button text must be exact
- Feature h2 headings must remain EXACTLY: "Topics", "Difficulty Levels", "Instant PDF" (these are asserted by Landing.test.tsx)
- The spec content "5 Topics", "3 Levels" goes in a PARAGRAPH below the h2 heading, NOT in the h2 itself. This satisfies spec FR-VR-006 while preserving test assertions.

**Note on Lucide icons as SVG:** Lucide React renders all icons as SVG elements. Using `<ChevronRight />` for stepper connectors satisfies spec FR-VR-007's "SVG connector arrows" requirement.

- [ ] **Step 3: Run tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run src/__tests__/Landing.test.tsx 2>&1 | tail -10
```

If tests fail, check which assertions broke and adjust text content or element roles to match. The design changes are visual only — all text content and interaction behavior must remain identical.

- [ ] **Step 4: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 5: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/pages/Landing.tsx
git commit -m "feat(ui): redesign Landing page with gradient hero, icon cards, stepper"
```

---

## Chunk 3: Auth Pages (Login + Register)

### Task 7: Restyle Login Page — Split Layout with Branding Panel

**Files:**
- Modify: `frontend/src/pages/Login.tsx` (restyle container, add branding panel JSX)

- [ ] **Step 1: Read the Login test file**

```bash
cd PROBLEMGENERATOR/frontend && cat src/__tests__/Login.test.tsx
```

Note all asserted text, roles, and form interactions.

- [ ] **Step 2: Update Login.tsx with split layout**

Replace the `containerStyle` with a split layout wrapper. The existing form JSX and all logic remain unchanged. Add a branding panel on the left.

Key structural change:
- Outer wrapper: `display: flex`, `minHeight: 'calc(100vh - 60px)'`, **add `className="auth-split"`** (used by Task 14 responsive CSS)
- Left panel (~38%): teal gradient background, "Welcome back" heading, feature bullets with Check icons from Lucide, **add `className="auth-branding"`**
- Right panel (~62%): white background, contains the existing form card content (remove the `.card` className from the `<section>`, move form into right panel)
- Responsive: handled by CSS media query in Task 14 via the `auth-split` and `auth-branding` classNames

**Critical: preserve ALL form fields, validation, submit logic, error display, footer links, and ARIA attributes exactly as-is.**

- [ ] **Step 3: Run Login tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run src/__tests__/Login.test.tsx 2>&1 | tail -10
```

- [ ] **Step 4: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 5: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/pages/Login.tsx
git commit -m "feat(ui): redesign Login page with split layout and branding panel"
```

---

### Task 8: Restyle Register Page — Split Layout with Branding Panel

**Files:**
- Modify: `frontend/src/pages/Register.tsx`

- [ ] **Step 1: Read the Register test file**

```bash
cd PROBLEMGENERATOR/frontend && cat src/__tests__/Register.test.tsx
```

- [ ] **Step 2: Update Register.tsx with split layout**

Same structural pattern as Login (Task 7). Outer wrapper gets `className="auth-split"`, left panel gets `className="auth-branding"`. Left panel shows "Start practicing" heading and $5/month price card. Right panel contains the existing form.

**Important:** The Register page has a success state (lines 92-111) that shows "Check Your Email" with a verification button. This success state must also be restyled to match the new design, but its content and behavior must remain identical.

- [ ] **Step 3: Run Register tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run src/__tests__/Register.test.tsx 2>&1 | tail -10
```

- [ ] **Step 4: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 5: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/pages/Register.tsx
git commit -m "feat(ui): redesign Register page with split layout and pricing panel"
```

---

## Chunk 4: Dashboard

### Task 9: Restyle Dashboard — Welcome Banner, Cards, Stats Row

**Files:**
- Modify: `frontend/src/pages/Dashboard.tsx` (restyle all inline style objects, restructure JSX card layout)

- [ ] **Step 1: Read the Dashboard test file**

```bash
cd PROBLEMGENERATOR/frontend && cat src/__tests__/Dashboard.test.tsx
```

Note exact assertions. Key things to preserve:
- "Welcome back" heading text
- User email display
- "Generate New Test" button
- "Sign Out" button
- "Delete Account" button
- Subscription status badge text
- Cancel subscription flow

- [ ] **Step 2: Update Dashboard.tsx with new card structure**

Import Lucide icons at the top: `import { ChevronRight } from 'lucide-react';`

Replace inline style objects and restructure the JSX:

1. **Welcome banner**: Replace the plain h1 + email with a full-width teal gradient banner div wrapping them. h1 text becomes white, email becomes light teal.
2. **Quick action card**: Wrap the "Generate New Test" button in a card with "Ready to practice?" text above it.
3. **Subscription card**: Restyle the subscription card to be compact with a green dot, "Active" text, renewal date, and a "Manage" button that triggers the existing cancel flow.
4. **Stats row**: Add 3 small stat cards (these are static display — template count "34", topic count "5", level count "3").
5. **Account section**: Group "Sign Out" and "Delete Account" into a single card as list items with ChevronRight icons.

**Critical: ALL state logic, callbacks, conditional rendering, and ARIA attributes must remain exactly as-is. Only change the visual wrapper elements and styles.**

- [ ] **Step 3: Run Dashboard tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run src/__tests__/Dashboard.test.tsx 2>&1 | tail -10
```

- [ ] **Step 4: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 5: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/pages/Dashboard.tsx
git commit -m "feat(ui): redesign Dashboard with welcome banner, cards, stats row"
```

---

## Chunk 5: Generate Page (Topic Colors + Difficulty)

### Task 10: Add Topic Color Map to TopicSelector

**Files:**
- Modify: `frontend/src/components/TestConfig/TopicSelector.tsx`

- [ ] **Step 1: Read the TopicSelector test file**

```bash
cd PROBLEMGENERATOR/frontend && cat src/__tests__/TopicSelector.test.tsx
```

- [ ] **Step 2: Read the current TopicSelector.tsx fully**

```bash
cd PROBLEMGENERATOR/frontend && cat src/components/TestConfig/TopicSelector.tsx
```

Understand all inline styles, the group/subtopic rendering logic, and the expand/collapse mechanism.

- [ ] **Step 3: Add a topic color map constant**

Add at the top of the file (after imports):

```typescript
const TOPIC_COLORS: Record<string, { decorative: string; text: string; light: string }> = {
  algebra: { decorative: 'var(--color-topic-algebra)', text: 'var(--color-topic-algebra-text)', light: 'var(--color-topic-algebra-light)' },
  functions: { decorative: 'var(--color-topic-functions)', text: 'var(--color-topic-functions-text)', light: 'var(--color-topic-functions-light)' },
  geometry: { decorative: 'var(--color-topic-geometry)', text: 'var(--color-topic-geometry-text)', light: 'var(--color-topic-geometry-light)' },
  trigonometry: { decorative: 'var(--color-topic-trigonometry)', text: 'var(--color-topic-trigonometry-text)', light: 'var(--color-topic-trigonometry-light)' },
  calculus: { decorative: 'var(--color-topic-calculus)', text: 'var(--color-topic-calculus-text)', light: 'var(--color-topic-calculus-light)' },
};

const DEFAULT_TOPIC_COLOR = { decorative: 'var(--color-primary-500)', text: 'var(--color-primary-700)', light: 'var(--color-primary-50)' };
```

- [ ] **Step 4: Update the group fieldset styles to use topic colors**

For each topic group row, look up `TOPIC_COLORS[topicName.toLowerCase()]` and apply:
- `borderLeft: 3px solid ${colors.decorative}` on the fieldset
- Template count badge: `color: colors.text`, `backgroundColor: colors.light`, pill-shaped
- Checkbox accent: `accentColor: colors.decorative`
- Arrow: `color: colors.decorative`

Replace `box-shadow: var(--shadow-sm)` with `box-shadow: var(--shadow-card)` on group fieldsets.

- [ ] **Step 5: Run TopicSelector tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run src/__tests__/TopicSelector.test.tsx 2>&1 | tail -10
```

- [ ] **Step 6: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 7: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/components/TestConfig/TopicSelector.tsx
git commit -m "feat(ui): add topic color-coding to TopicSelector"
```

---

### Task 11: Restyle DifficultySelector — Filled Chip Active State

**Files:**
- Modify: `frontend/src/components/TestConfig/DifficultySelector.tsx`

- [ ] **Step 1: Check if a DifficultySelector-specific test file exists, then read the component**

```bash
cd PROBLEMGENERATOR/frontend && ls src/__tests__/Difficulty* 2>/dev/null || echo "No dedicated test file — DifficultySelector is tested via Generate.test.tsx"
cd PROBLEMGENERATOR/frontend && cat src/components/TestConfig/DifficultySelector.tsx
```

- [ ] **Step 2: Update active/inactive chip styles**

Change the active state style to: `backgroundColor: '#134e4a'`, `color: '#ffffff'`, `fontWeight: 600`, `borderColor: '#134e4a'`, `boxShadow: '0 2px 4px rgba(19, 78, 74, 0.2)'`.

Change inactive state style to: `backgroundColor: '#ffffff'`, `color: 'var(--text-secondary)'`, `border: '1.5px solid var(--color-stone-200)'`, `boxShadow: '0 1px 2px rgba(0, 0, 0, 0.04)'`.

- [ ] **Step 3: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 4: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/components/TestConfig/DifficultySelector.tsx
git commit -m "feat(ui): restyle DifficultySelector with filled teal active chip"
```

---

### Task 12: Update Generate Page Title Styling

**Files:**
- Modify: `frontend/src/pages/Generate.tsx` (lines 7-12, pageTitle style + add subtitle)

- [ ] **Step 1: Update pageTitle color and add subtitle**

Change `pageTitle` color from `var(--text-primary)` to `var(--color-primary-900)`.

Add a subtitle element below the h1:
```tsx
<p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--text-secondary)', marginBottom: 'var(--space-5)' }}>
  Select topics, difficulty, and question count
</p>
```

- [ ] **Step 2: Run Generate tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run src/__tests__/Generate.test.tsx 2>&1 | tail -10
```

- [ ] **Step 3: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 4: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/pages/Generate.tsx
git commit -m "feat(ui): update Generate page title and add subtitle"
```

---

## Chunk 6: Preview Page

### Task 13: Restyle Preview Page — Summary Bar and Question Cards

**Files:**
- Modify: `frontend/src/pages/Preview.tsx`
- Modify: `frontend/src/components/TestPreview/QuestionCard.tsx`

- [ ] **Step 1: Read QuestionCard.tsx and Preview test file**

```bash
cd PROBLEMGENERATOR/frontend && cat src/components/TestPreview/QuestionCard.tsx
cd PROBLEMGENERATOR/frontend && cat src/__tests__/Preview.test.tsx
```

- [ ] **Step 2: Restyle Preview.tsx**

Replace the existing `pageTitle`, `metaRow`, `tagStyle`, `actionsStyle` with the new summary bar design:

1. **Summary bar**: dark teal (#134e4a) full-width bar below the nav. Contains: "Test Preview" heading (white), metadata pills (semi-transparent white backgrounds), and Download PDF button (orange, positioned right).
2. **Controls bar**: white background strip below summary bar. Contains: "Include answers" checkbox and a "Generate New Test" secondary button (preserve EXACT existing button text — do NOT change to "+ New Test" as tests may assert this text).
3. The `<QuestionList>` section below stays the same structurally.

**Critical: preserve ALL state logic, download handler, error display, loading state, button text, and ARIA attributes.**

- [ ] **Step 3: Restyle QuestionCard.tsx**

Update the card styling:
- Add a teal left border (`borderLeft: '3px solid var(--color-primary-500)'`)
- Use `boxShadow: 'var(--shadow-card)'` instead of border
- Question number: render as a teal circle badge (`backgroundColor: 'var(--color-primary-100)'`, `color: 'var(--color-primary-900)'`, `borderRadius: '8px'`, `width: '32px'`, `height: '32px'`, centered)
- Subtopic: render as a colored pill badge. Use primary teal as the default color for all subtopic pills (do NOT import the topic color map from TopicSelector — keep QuestionCard self-contained). If topic-specific colors are desired later, extract the color map to a shared `frontend/src/constants/topicColors.ts` file in a future task.

- [ ] **Step 4: Run Preview tests**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run src/__tests__/Preview.test.tsx 2>&1 | tail -10
```

- [ ] **Step 5: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 6: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/pages/Preview.tsx frontend/src/components/TestPreview/QuestionCard.tsx
git commit -m "feat(ui): redesign Preview page with summary bar and styled question cards"
```

---

## Chunk 7: Responsive Auth + Final Verification

### Task 14: Add Responsive CSS for Auth Split Layout

**Files:**
- Modify: `frontend/src/index.css` (add media query at the end)

- [ ] **Step 1: Add responsive media query for auth split layout**

Add at the end of index.css:

```css
/* --------------------------------------------------------------------------
   8. Responsive: Auth Split Layout
   -------------------------------------------------------------------------- */
@media (max-width: 768px) {
  .auth-split {
    flex-direction: column !important;
  }
  .auth-branding {
    min-height: 200px !important;
    flex: none !important;
  }
}
```

Then ensure Login.tsx and Register.tsx use `className="auth-split"` on the outer flex container and `className="auth-branding"` on the left panel. (These classes should be added in Tasks 7 and 8.)

- [ ] **Step 2: Run full test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run 2>&1 | tail -5
```

Expected: 157 tests passing.

- [ ] **Step 3: Commit**

```bash
cd PROBLEMGENERATOR
git add frontend/src/index.css
git commit -m "feat(ui): add responsive CSS for auth split layout"
```

---

### Task 15: Final Verification — Run All Tests and Build

- [ ] **Step 1: Run full frontend test suite**

```bash
cd PROBLEMGENERATOR/frontend && npx vitest run --reporter=verbose 2>&1 | tail -30
```

Expected: 157 tests passing (or more if any visual tests were added).

- [ ] **Step 2: Run TypeScript check**

```bash
cd PROBLEMGENERATOR/frontend && npx tsc --noEmit 2>&1
```

Expected: No errors.

- [ ] **Step 3: Run ESLint**

```bash
cd PROBLEMGENERATOR/frontend && npx eslint src/ 2>&1 | tail -20
```

Expected: No errors (warnings are acceptable).

- [ ] **Step 4: Run production build**

```bash
cd PROBLEMGENERATOR/frontend && npm run build 2>&1 | tail -10
```

Expected: Build succeeds.

- [ ] **Step 5: Visual verification with Playwright**

Navigate to each page with Playwright MCP and take screenshots to verify the redesign:

```
http://localhost:5173/          — Landing (gradient hero, icon cards, stepper)
http://localhost:5173/login     — Login (split layout, branding panel)
http://localhost:5173/register  — Register (split layout, price panel)
http://localhost:5173/dashboard — Dashboard (welcome banner, cards, stats)
http://localhost:5173/generate  — Generate (topic colors, filled difficulty chip)
http://localhost:5173/preview/* — Preview (summary bar, styled question cards)
```

Save screenshots to `screenshots/redesign/` for comparison.

- [ ] **Step 6: Final commit (use explicit paths, NOT git add -A)**

```bash
cd PROBLEMGENERATOR
git add frontend/src/ frontend/index.html frontend/package.json frontend/package-lock.json
git commit -m "feat(ui): complete visual redesign — Deep Teal Foundation

Implements spec 002-visual-redesign:
- Dark teal nav bar with bright teal branding
- Light teal page backgrounds
- Self-hosted Plus Jakarta Sans fonts
- Lucide React icons
- Gradient hero + icon feature cards + how-it-works stepper on Landing
- Split layout with branding panels on Login/Register
- Welcome banner, card structure, stats row on Dashboard
- Topic color-coding on Generate page
- Summary bar and styled question cards on Preview
- WCAG 2.1 AA contrast compliance maintained
- All 157 existing tests passing"
```

---

## Post-Implementation Notes

- **Backend tests**: No backend changes were made, so backend tests are unaffected.
- **Docker**: The frontend Docker build will automatically include the self-hosted fonts since they are in `src/assets/`. No Dockerfile changes needed.
- **CI/CD**: GitHub Actions runs `npm test` and `npm run build` — both should pass without changes.
- **Lighthouse**: Run a Lighthouse audit after deployment to verify SC-VR-006 (performance score does not drop by more than 5 points).
