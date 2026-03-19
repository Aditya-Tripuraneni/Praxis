# Feature Specification: Core Platform - Math Practice Test Generator

**Feature Branch**: `001-core-platform`
**Created**: 2026-03-11
**Status**: Draft
**Input**: User description: "ProblemGenerator - a web platform that creates customizable practice tests for high school and early university students"

## User Scenarios & Testing

### User Story 1 - Generate and Preview a Practice Test (Priority: P1)

A user selects math topics (e.g., quadratic equations, trigonometric
identities), chooses a difficulty level, picks the number of questions,
and generates a practice test. The user previews the generated questions
on screen with properly rendered math notation. There is no online
answering or scoring — the test is meant to be printed or downloaded.

**Why this priority**: This is the core value proposition and must work
standalone without auth or billing. The developer must be able to test
the generation engine and math rendering end-to-end before adding any
infrastructure layers.

**Independent Test**: Can be tested by selecting topics + difficulty,
generating a test, and confirming the questions are displayed correctly
with proper math notation — no login required.

**Acceptance Scenarios**:

1. **Given** a user on the generate page, **When** they select
   "Algebra > Quadratic Equations" at "Medium" difficulty with 10 questions,
   **Then** a unique test of 10 quadratic equation problems is generated
   and displayed as a preview.
2. **Given** a generated test preview, **When** the user views it,
   **Then** all questions render with correct mathematical notation
   (fractions, exponents, radicals, etc.).
3. **Given** a test generation request, **When** the same user generates
   another test with the same settings, **Then** the problems are different
   from the previous test (randomized parameters).
4. **Given** a user selecting multiple topics, **When** they generate a
   test, **Then** the test contains a mix of problems from all selected
   topics.

---

### User Story 2 - Download Test as PDF (Priority: P1)

A user generates a test and downloads it as a formatted PDF document,
suitable for printing. The PDF includes the test questions on one section
and the answer key (correct final answers) on a separate section. Users
solve problems by hand on paper and check against the answer key.

**Why this priority**: PDF output is the primary delivery mechanism for
the product. Users handwrite solutions and self-check. This must work
alongside generation, without auth or billing.

**Independent Test**: Can be tested by generating a test, clicking
"Download PDF", opening the file, and confirming it contains properly
formatted questions and a separate answer key — no login required.

**Acceptance Scenarios**:

1. **Given** a generated test, **When** the user clicks "Download PDF",
   **Then** a PDF file is downloaded containing all questions formatted
   for printing.
2. **Given** a downloaded PDF, **When** the user opens it, **Then** the
   answer key (correct final answers) is on a separate page from the
   questions.
3. **Given** a test with math expressions, **When** rendered in the PDF,
   **Then** equations are displayed using proper mathematical notation
   (fractions, exponents, radicals, etc.).

---

### User Story 3 - Account Creation and Authentication (Priority: P2)

A student creates an account using email/password or Google OAuth,
verifies their email, and logs in. Authenticated users get a personal
dashboard. This layer wraps around the already-working generation and
PDF features.

**Why this priority**: Auth is needed before billing can be added, but
the core product (generation + PDF) must work first without it.

**Independent Test**: Can be tested by registering a user, verifying
email, logging in, and confirming the dashboard loads with access to
the generation page.

**Acceptance Scenarios**:

1. **Given** a visitor on the landing page, **When** they click "Sign Up"
   and fill in email + password, **Then** an account is created and a
   verification email is sent.
2. **Given** a visitor on the landing page, **When** they click "Sign in
   with Google", **Then** an account is created via OAuth and they are
   logged in.
3. **Given** an authenticated user, **When** they visit the dashboard,
   **Then** they see the test generation page.
4. **Given** an unauthenticated visitor, **When** they try to access
   protected pages, **Then** they are redirected to the login page.

---

### User Story 4 - Subscription and Billing (Priority: P3)

A registered user subscribes to the $5/month plan via Stripe checkout.
After subscribing, the user retains full access. If unsubscribed, the
user sees a dashboard explaining the app and prompting subscription.
This is the last layer added on top of the working product + auth.

**Why this priority**: Billing is the final gate. The entire product
must be functional and tested before adding payment. Stripe should be
the last integration.

**Independent Test**: Can be tested by completing Stripe test-mode
checkout and verifying subscription status changes gate access correctly.

**Acceptance Scenarios**:

1. **Given** a registered but unsubscribed user, **When** they log in,
   **Then** they see a dashboard explaining the app and a subscribe button.
2. **Given** an unsubscribed user, **When** they complete Stripe checkout,
   **Then** their account is marked as active subscriber and they can
   access test generation.
3. **Given** a subscribed user, **When** their subscription lapses or is
   cancelled, **Then** they lose access to test generation but retain
   their account.
4. **Given** a user during Stripe checkout, **When** payment fails,
   **Then** a clear error is shown and they can retry.

---

### Edge Cases

- What happens when a user's subscription expires? (Block new generation,
  retain access to past generated tests.)
- What happens when the generation engine cannot produce enough unique
  questions for the requested count? (Inform the user and generate the
  maximum available.)
- How does the system handle concurrent test generation by the same user?
  (Allow it; each generation is independent.)
- What happens when Stripe webhook delivery is delayed? (Polling fallback
  or graceful degradation with retry.)
- What happens when a topic has very few problem templates? (Show available
  question count to user before generation.)

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow users to create accounts via email/password
  registration with email verification required before activation
- **FR-002**: System MUST allow users to create accounts via Google OAuth
  social login (Google only at launch)
- **FR-003**: System MUST integrate with Stripe to manage a single
  subscription plan at $5/month billing cycle
- **FR-004**: System MUST restrict test generation to active subscribers only
  in production (Layer 3); unsubscribed users see a dashboard explaining
  the app and subscription. During Layer 1/2 development, generation is
  unrestricted
- **FR-005**: System MUST allow users to select one or more math topics for
  test generation
- **FR-006**: System MUST allow users to select a difficulty level (Easy,
  Medium, Hard) for test generation
- **FR-007**: System MUST allow users to specify the number of questions
  per test (range: 5 to 50)
- **FR-008**: System MUST generate unique math problems using algorithmic
  templates with randomized parameters
- **FR-009**: System MUST compute and store the correct answer for every
  generated question
- **FR-010**: System MUST provide an online preview of generated questions
  with rendered math notation (desktop web only at launch). No online
  answering or scoring — users solve on paper
- **FR-011**: System MUST include correct final answers in the PDF answer
  key section (no step-by-step solutions, no online scoring)
- **FR-012**: System MUST generate downloadable PDF documents containing
  test questions and a separate answer key
- **FR-013**: System MUST render mathematical notation correctly in both
  the web interface and PDF output
- **FR-014**: [REMOVED — test history not required. Tests are ephemeral;
  users generate fresh tests each time. Statistical uniqueness via
  randomized parameters eliminates need for dedup tracking.]
- **FR-015**: [REMOVED — no test history to browse or review]
- **FR-016**: System MUST support the following math topic categories at
  launch: Algebra (linear, quadratic, polynomial, rational, systems,
  exponents/radicals, logarithms), Functions (evaluation, domain/range,
  composition, inverses, transformations), Trigonometry (unit circle,
  identities, equations, graphing, law of sines/cosines), and Basic
  Calculus (limits, derivatives, integrals). See research.md for ~130+
  specific problem types.
- **FR-017**: System MUST use backward construction (generate answer first,
  then build the problem) to guarantee solvability and answer correctness
- **FR-018**: System MUST render math notation using LaTeX (KaTeX on
  frontend, SymPy latex() for generation)
- **FR-019**: System MUST use Supabase Auth for authentication (email/
  password + Google OAuth), including built-in email verification
- **FR-020**: System MUST use a 2-token strategy (short-lived access token
  ~15 min, long-lived refresh token ~7 days) via Supabase Auth JWTs
- **FR-021**: System MUST enforce password requirements per NIST SP 800-63B:
  minimum 8 characters, check against common/breached password lists,
  allow all printable characters, no forced complexity rules
- **FR-022**: System MUST show a clear error and allow retry when Stripe
  checkout payment fails
- **FR-023**: System MUST delete all user data upon account closure
- **FR-024**: System MUST comply with WCAG 2.1 Level AA accessibility
  standards
- **FR-025**: System MUST define difficulty levels using these criteria:
  Easy (small integers 1-5, 1-2 steps, whole number answers),
  Medium (integers 5-15 or simple fractions, 3-4 steps, fractional answers),
  Hard (large numbers or complex fractions, 5+ steps, irrational/composed answers, word problems)
- **FR-026**: System MUST silently retry failed question generation (up to
  3 attempts per question) before reporting failure to the user
- **FR-027**: System MUST implement rate limiting (100 requests/min per user)
  via FastAPI middleware, CORS protection, CSRF protection, and input
  sanitization on all endpoints. Cloudflare (free tier) MUST be placed
  in front of all endpoints for DDoS protection
- **FR-028**: System MUST handle Stripe webhook events idempotently, relying
  on Stripe's built-in retry mechanism (exponential backoff, up to 3 days)

### Key Entities

- **User**: Represents a registered student. Key attributes: email,
  auth method, subscription status, creation date.
- **Subscription**: Represents a user's billing state. Linked to Stripe
  customer/subscription IDs. Tracks status (active, cancelled, expired).
- **Test**: A generated practice test. Ephemeral (not persisted). Contains
  metadata: selected topics, difficulty, question count, generated questions.
- **Question**: An individual problem within a test. Contains: problem
  text (LaTeX notation), correct final answer, topic, difficulty,
  template ID, generated parameters.
- **ProblemTemplate**: Defines a reusable question structure. Contains:
  topic, difficulty range, parameter schema, generation logic reference,
  solution logic reference.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can complete account creation and subscription in
  under 3 minutes
- **SC-002**: Test generation (selecting topics + generating questions)
  completes in under 3 seconds for a 50-question test
- **SC-003**: Every generated question has a verifiable correct answer
  (100% answer accuracy)
- **SC-004**: Generating the same test configuration twice produces
  different questions at least 95% of the time
- **SC-005**: PDF downloads are available within 10 seconds of request
- **SC-006**: The platform supports at least 100 concurrent subscribed
  users without degradation
- **SC-007**: At least 20 distinct problem types are available at launch
  across all topic categories
- **SC-008**: Mathematical notation renders correctly in both web and PDF
  for all supported problem types
- **SC-009**: Pages load in under 1.5 seconds, API responses return in
  under 200ms (excluding test generation), test generation under 3 seconds
- **SC-010**: Render.com cold start (~30s after 15-min idle) is documented
  and accepted as a known limitation of free-tier deployment
