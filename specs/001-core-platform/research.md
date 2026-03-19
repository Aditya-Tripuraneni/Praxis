# Math Problem Generation Research

**Date**: 2026-03-11
**Purpose**: Determine which math topics and problem types can be algorithmically
generated with randomized parameters for the ProblemGenerator platform.

## Key Findings

- **~130+ distinct problem types** across 25 subtopics, all algorithmically feasible
- **SymPy** provides full symbolic math support for generation and verification
- **Backward construction** is the critical pattern: generate the answer first,
  then construct the problem — guarantees solvability and known correct answers
- **KaTeX or MathJax** for frontend LaTeX rendering of generated problems

## Topic Coverage Summary

| Topic Area | Problem Types | SymPy Support | Feasibility |
|---|---|---|---|
| Linear Equations & Inequalities | 5+ | Full | Excellent |
| Quadratic Equations | 7+ | Full | Excellent |
| Polynomials | 8+ | Full | Excellent |
| Rational Expressions | 5+ | Full | Excellent |
| Systems of Equations | 4+ | Full | Excellent |
| Exponents & Radicals | 6+ | Full | Excellent |
| Logarithms | 5+ | Full | Excellent |
| Functions (fundamentals) | 7+ | Full | Excellent |
| Function Operations & Composition | 4+ | Full | Excellent |
| Inverse Functions | 4+ | Full | Excellent |
| Transformations | 3+ | Partial (algebraic) | Good |
| Trig Evaluation (unit circle) | 5+ | Full | Excellent |
| Trig Identities | 4+ | Full (trigsimp) | Good |
| Trig Equations | 3+ | Full | Excellent |
| Trig Graphing | 2+ | Partial | Good |
| Sequences & Series | 6+ | Full | Excellent |
| Conic Sections | 5+ | Full | Excellent |
| Matrices & Determinants | 6+ | Full | Excellent |
| Combinatorics & Probability | 5+ | Full | Excellent |
| Limits | 6+ | Full | Excellent |
| Derivatives | 10+ | Full | Excellent |
| Integrals | 7+ | Full | Excellent |
| Complex Numbers | 3+ | Full | Excellent |
| Vectors (2D/3D) | 5+ | Full | Excellent |
| Descriptive Statistics | 5+ | Partial (NumPy) | Excellent |

## Detailed Problem Types by Category

### 1. Algebra

#### 1.1 Linear Equations and Inequalities
- Solve one-variable linear equation (`ax + b = cx + d`)
- Linear inequality (track sign flip)
- Absolute value equation (`|ax + b| = c`)
- Absolute value inequality
- Literal equation rearrangement

#### 1.2 Quadratic Equations
- Factor quadratic (build from known roots)
- Solve by quadratic formula
- Complete the square
- Vertex form conversion
- Discriminant analysis
- Quadratic word problems (projectile motion)
- Sum and product of roots (Vieta's formulas)

#### 1.3 Polynomials
- Addition/subtraction
- Multiplication
- Long division (build from known quotient + remainder)
- Synthetic division
- Factor by grouping
- Rational root theorem
- Remainder theorem
- Descartes' rule of signs

#### 1.4 Rational Expressions
- Simplify (cancel common factors)
- Add/subtract (LCD computation)
- Multiply/divide
- Solve rational equations (check extraneous solutions)
- Complex fractions

#### 1.5 Systems of Equations
- 2x2 linear system (Cramer's rule)
- 3x3 linear system (Gaussian elimination)
- Linear + quadratic system
- Word problems (mixture, rate, coin)

#### 1.6 Exponents and Radicals
- Simplify with exponent rules
- Negative and fractional exponents
- Simplify radicals
- Rationalize denominator
- Solve radical equations (check extraneous)
- Exponential equations

#### 1.7 Logarithms
- Evaluate logarithms (exact powers)
- Expand/condense using log rules
- Solve logarithmic equations
- Solve exponential equations with logs
- Change of base

### 2. Functions

#### 2.1 Fundamentals
- Evaluate f(a)
- Domain of rational/radical/composite functions
- Range identification
- Piecewise function evaluation
- Odd/even/neither classification

#### 2.2 Operations and Composition
- f+g, f-g, f*g, f/g
- Composition f(g(x))
- Numeric evaluation of composition
- Decompose h(x) into f(g(x))

#### 2.3 Inverse Functions
- Inverse of linear function
- Inverse of simple rational function
- Inverse of quadratic (restricted domain)
- Verify inverse relationship

#### 2.4 Transformations
- Describe transformations from equation
- Write transformed equation from description
- Identify transformation from key points

### 3. Trigonometry

#### 3.1 Unit Circle and Evaluation
- Evaluate trig at standard angles
- Reference angle
- Coterminal angles
- Degree-radian conversion
- Evaluate inverse trig

#### 3.2 Identities
- Simplify using Pythagorean identity
- Double-angle formulas
- Verify identity (SymPy trigsimp)
- Sum/difference formulas

#### 3.3 Equations
- Basic trig equation (sin(x) = a)
- Quadratic in trig function
- Multiple-angle equations

#### 3.4 Graphing and Applications
- Identify amplitude, period, phase shift
- Write equation from graph description
- Law of sines problems
- Law of cosines problems

### 4. Precalculus

#### 4.1 Sequences and Series
- Arithmetic: nth term and sum
- Geometric: nth term, finite/infinite sum
- Sigma notation evaluation
- Recursive sequences

#### 4.2 Conic Sections
- Circle (standard and general form)
- Ellipse properties
- Parabola (vertex, focus, directrix)
- Hyperbola properties and asymptotes

#### 4.3 Matrices
- Addition/subtraction/multiplication
- Determinant (2x2, 3x3)
- Matrix inverse (2x2)
- Solve system via matrices

#### 4.4 Combinatorics and Probability
- Permutations P(n,r)
- Combinations C(n,r)
- Binomial theorem (specific term)
- Basic and compound probability

### 5. Basic Calculus

#### 5.1 Limits
- Direct substitution
- Factorable 0/0 form
- Rationalization
- Limits at infinity (rational functions)
- One-sided limits (piecewise)
- Squeeze theorem

#### 5.2 Derivatives
- Power rule
- Sum/difference of terms
- Product rule
- Quotient rule
- Chain rule
- Trig function derivatives
- Exponential/log derivatives
- Higher-order derivatives
- Implicit differentiation
- Tangent line at a point

#### 5.3 Integrals
- Power rule integration
- Basic trig integrals
- Exponential integrals
- Simple u-substitution
- Definite integrals
- Area under curve
- Area between curves

### 6. Additional Topics

#### 6.1 Complex Numbers
- Arithmetic (add, multiply, divide)
- Modulus and argument
- Powers via De Moivre's theorem

#### 6.2 Vectors (2D/3D)
- Magnitude
- Dot product
- Cross product (3D)
- Angle between vectors
- Projection

#### 6.3 Descriptive Statistics
- Mean, median, mode
- Standard deviation
- Z-score
- Linear regression
- Correlation coefficient

## Backward Construction Pattern

The most important architectural insight: **always generate the answer first,
then construct the problem.** This is used by all major platforms (WeBWorK,
STACK, Numbas).

Examples:
- **Factoring quadratics**: Pick roots r1, r2 first, then expand (x-r1)(x-r2)
- **Systems of equations**: Pick solution (x,y) first, generate equations through it
- **Polynomial division**: Pick quotient and divisor, multiply to get dividend
- **Integrals**: Pick antiderivative, differentiate to get the integrand

## Difficulty Scaling Dimensions

| Dimension | Easy | Medium | Hard |
|---|---|---|---|
| Coefficient size | 1-5 | 5-15 | 10-50 or fractions |
| Number of steps | 1-2 | 3-4 | 5+ |
| Answer type | Integer | Simple fraction | Irrational, complex |
| Function complexity | Single type | Two combined | Nested/composed |
| Problem format | Direct computation | Multi-step | Word problem |
| Number of terms | 2-3 | 3-5 | 5+ |

## Existing Open-Source Projects

| Project | Language | Relevance | Notes |
|---|---|---|---|
| **WeBWorK / OpenProblemLibrary** | Perl | High | 30,000+ templated problems, same randomization model |
| **STACK** | PHP + Maxima CAS | High | Math assessment with CAS verification |
| **Numbas** | JavaScript | High | Excellent template model with JME language |
| **mathgenerator** | Python | Medium | Simple Python lib, limited scope but good starting point |
| **SymPy** | Python | Critical | Core CAS engine for this project |
| **MyOpenMath** | PHP | Medium | Extensive problem libraries |

## Recommended Technology for Problem Engine

| Component | Tool | Purpose |
|---|---|---|
| Symbolic math | SymPy | Generation, solving, simplification, LaTeX output |
| Random params | Python `random` | Coefficient generation within constraints |
| Numerical verify | NumPy | Cross-check symbolic results |
| LaTeX rendering | KaTeX (frontend) | Display math notation in browser |
| Template system | Python dataclasses | Define problem types with parameter specs |

## Answer Verification Approaches

1. **Direct computation**: Evaluate formula (most problems)
2. **Back-substitution**: Solve, then substitute answer back into original
3. **Reverse construction**: Answer known by design (backward construction)
4. **CAS verification**: SymPy `solve()`, `diff()`, `integrate()`, `simplify()`
5. **Numerical cross-check**: Evaluate numerically for transcendental problems
