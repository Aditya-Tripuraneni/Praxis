# Spec: Step-by-Step Solutions

**Date**: 2026-03-17
**Status**: Implemented

---

## Overview

Every generated math question includes an optional list of symbolic solution steps showing the work from the original equation through each algebraic manipulation to the final answer. Steps are purely symbolic (LaTeX equations, no narrative text), fully deterministic (derived from backward construction), and backward-compatible (templates without steps return empty arrays).

---

## Data Model

### Backend — `GeneratedProblem` (frozen dataclass)
- `solution_steps: tuple[TrustedLatex, ...] = ()` — immutable, default empty

### Backend — `QuestionResponse` (Pydantic)
- `solution_steps: list[str] = Field(default_factory=list)` — always present in JSON

### Frontend — `QuestionResponse` (TypeScript)
- `solution_steps: string[]` — always present, may be empty

---

## Templates Implemented (All 6 Topics)

### Algebra (9 templates)
LinearEquation, TwoStepLinear, QuadraticFactoring, QuadraticFormula, PolynomialAddSub, PolynomialMultiply, SystemOf2Linear, ExponentSimplify, RadicalSimplify

### Calculus (4 templates)
Limit (3-4 steps: factor/cancel/conjugate/substitute), DerivativeBasic (2-3 steps: term-by-term), ChainRule (3 steps: outer/inner decomposition with unevaluated Derivative notation), BasicIntegral (2-4 steps: split sum / u-substitution)

### Functions (3 templates)
FunctionEval (2 steps), FunctionComposition (3 steps: inner then outer), InverseFunction (3-4 steps: y=f(x), solve for x, swap)

### Geometry (8 templates across lines.py + shapes.py)
SlopeFromPoints, SlopeIntercept, ParallelPerpSlope, LineEquation, DistanceFormula, MidpointFormula, TriangleAreaCoords, PerpendicularBisector

### Trigonometry (6+ template classes, 150+ variants)
TrigEval, InverseTrig, TrigSimplify (via _build() method covering all variants), TrigEquationBasic, TrigQuadratic, TrigEvalExpanded, InverseTrigExpanded

### Domain (5 templates across basic.py + advanced.py)
RationalDomain, RadicalDomain, LogDomain, CompositeDomain, TrigDomain

---

## Frontend UI

### QuestionCard behavior
- `solution_steps.length === 0`: only "Show Answer" / "Hide Answer" (unchanged)
- `solution_steps.length > 0 && !showSolution`: both "Show Solution" and "Show Answer"
- `solution_steps.length > 0 && showSolution`: only "Hide Solution" (answer is last step)
- Steps rendered as ordered list via MathRenderer

### Preview page
- "Include solutions" checkbox (visible when any question has steps)
- Passed to `downloadPdf(testId, includeAnswers, includeSolutions)`

### PDF
- `GET /api/tests/{id}/pdf?include_solutions=true` adds "Worked Solutions" section
- Tectonic template: nested enumerate with "Step N:" labels
- Fallback renderer: steps rendered via render_latex_to_image()

---

## Step Contract
- Step 0 (first): the original equation/expression from the question
- Step N (last): the final answer value
- Each intermediate step shows one algebraic manipulation
- All steps are `$...$` delimited LaTeX (parsed by MathRenderer/KaTeX)
- Steps are deterministic: same seed produces same steps

---

## Files Modified

### Infrastructure (Batch 1 — ships once)
- `backend/app/engine/types.py` — GeneratedProblem field
- `backend/app/models/test.py` — QuestionResponse field
- `backend/app/services/generation_service.py` — extraction line
- `backend/app/api/pdf.py` — include_solutions query param
- `backend/app/services/pdf_service.py` — forwarding to templates
- `backend/app/services/templates/test.tex.j2` — Worked Solutions section
- `frontend/src/types/index.ts` — TypeScript interface
- `frontend/src/services/api.ts` — downloadPdf param + validator
- `frontend/src/components/TestPreview/QuestionCard.tsx` — UI toggle + steps section
- `frontend/src/pages/Preview.tsx` — checkbox + download handler

### Template files (one per batch)
- `backend/app/engine/topics/algebra/templates.py`
- `backend/app/engine/topics/calculus/templates.py`
- `backend/app/engine/topics/functions/templates.py`
- `backend/app/engine/topics/geometry/lines.py`
- `backend/app/engine/topics/geometry/shapes.py`
- `backend/app/engine/topics/trigonometry/templates.py`
- `backend/app/engine/topics/trigonometry/identities.py`
- `backend/app/engine/topics/trigonometry/equations.py`
- `backend/app/engine/topics/trigonometry/evaluation.py`
- `backend/app/engine/topics/domain/basic.py`
- `backend/app/engine/topics/domain/advanced.py`

### Tests
- `backend/tests/unit/engine/test_solution_steps.py` — per-topic test classes
- `backend/tests/integration/test_api.py` — API response + PDF tests
- `frontend/src/__tests__/QuestionCard.test.tsx` — UI toggle tests
- `frontend/src/__tests__/Preview.test.tsx` — checkbox tests

---

## Performance
- Test generation threshold bumped from 3.0s to 5.0s to accommodate step computation
- Steps built from existing local variables — no additional SymPy calls for most templates
