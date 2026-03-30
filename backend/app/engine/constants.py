"""Display names and other constants for the math engine.

Open for extension (add new entries when new templates are created).
Closed for modification (existing entries should not change).
"""

SUBTOPIC_DISPLAY_NAMES: dict[str, str] = {
    # Algebra
    "linear_equations": "Linear Equations",
    "two_step_linear": "Two-Step Linear Equations",
    "quadratic_factoring": "Quadratic Factoring",
    "quadratic_formula": "Quadratic Formula",
    "quadratic_form_conversion": "Quadratic Form Conversion",
    "polynomial_add_sub": "Polynomial Addition & Subtraction",
    "polynomial_multiply": "Polynomial Multiplication",
    "systems_of_equations": "Systems of Equations",
    "exponent_rules": "Exponent Rules",
    "radical_simplify": "Simplifying Radicals",
    "rational_simplify": "Simplifying Rational Expressions",
    "rational_add_sub": "Adding & Subtracting Rationals",
    "rational_multiply_divide": "Multiplying & Dividing Rationals",
    "rational_equations": "Solving Rational Equations",
    "rational_extraneous": "Rational Equations (Extraneous)",
    "complex_fractions": "Simplifying Complex Fractions",
    # Functions
    "function_evaluation": "Function Evaluation",
    "function_composition": "Function Composition",
    "inverse_function": "Inverse Functions",
    # Domain (specialized subtopics)
    "domain_rational": "Domain: Rational Functions",
    "domain_radical": "Domain: Radical Functions",
    "domain_logarithmic": "Domain: Logarithmic Functions",
    "domain_composite": "Domain: Composite Functions",
    "domain_trigonometric": "Domain: Trigonometric Functions",
    # Geometry
    "slope_from_points": "Slope from Two Points",
    "slope_intercept": "Slope-Intercept Form",
    "parallel_perp_slopes": "Parallel & Perpendicular Slopes",
    "distance_formula": "Distance Formula",
    "midpoint_formula": "Midpoint Formula",
    "triangle_area_coords": "Triangle Area from Coordinates",
    "perpendicular_bisector": "Perpendicular Bisectors",
    "line_equation": "Line Equations",
    # Trigonometry
    "trig_evaluation": "Trig Evaluation",
    "inverse_trig": "Inverse Trig Functions",
    "trig_simplify": "Trig Simplification",
    "trig_equation": "Trig Equations",
    "trig_quadratic": "Quadratic Trig Equations",
    # Calculus
    "limits": "Limits",
    "derivative_basic": "Basic Derivatives",
    "chain_rule": "Chain Rule",
    "basic_integral": "Basic Integrals",
    # Combinatorics & Probability
    "counting_principle": "Fundamental Counting Principle",
    "factorial_basics": "Factorial Basics",
    "permutations": "Permutations",
    "combinations": "Combinations",
    "basic_probability": "Basic Probability",
    "compound_probability": "Compound Probability",
}
