"""Combinatorics & Probability topic templates.

Every template uses backward construction: generate the answer first,
then build the problem from it.  This guarantees solvability for all
difficulty levels.
"""

from __future__ import annotations

import math
import random

from sympy import Rational, latex

from app.engine.registry import register_template
from app.engine.topics.combinatorics._helpers import (
    BASIC_PROB_BAG_2COLOR,
    BASIC_PROB_BAG_3COLOR,
    COMBINATION_CONTEXTS,
    COUNTING_PRINCIPLE_CONTEXTS,
    FACTORIAL_CONTEXTS,
    PERMUTATION_CONTEXTS,
    comb_params,
    counting_principle_choices,
    factorial_n,
    fmt_comb,
    fmt_factorial,
    fmt_perm,
    perm_params,
)
from app.engine.types import (
    ALL_DIFFICULTIES,
    Difficulty,
    GeneratedProblem,
    Topic,
    TrustedLatex,
)

# ---------------------------------------------------------------------------
# CountingPrincipleTemplate — subtopic "counting_principle"
# ---------------------------------------------------------------------------


@register_template
class CountingPrincipleTemplate:
    topic = Topic.COMBINATORICS
    subtopic = "counting_principle"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        ctx = rng.choice(COUNTING_PRINCIPLE_CONTEXTS)
        stages = ctx["stages"]
        choices = counting_principle_choices(rng, stages, difficulty.value)
        answer = math.prod(choices)

        # Build question text from template
        subs = {}
        labels = ["a", "b", "c", "d"]
        for i, c in enumerate(choices):
            subs[labels[i]] = str(c)
        question_text = ctx["template"]
        for key, val in subs.items():
            question_text = question_text.replace("{{" + key + "}}", val)

        # Solution steps
        choices_str = " \\times ".join(str(c) for c in choices)
        steps = [
            TrustedLatex(
                "$\\text{Apply the Fundamental Counting Principle: "
                "multiply the number of options at each stage.}$"
            ),
            TrustedLatex(f"$\\text{{Total}} = {choices_str}$"),
            TrustedLatex(f"$\\text{{Total}} = {latex(answer)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(answer)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"choices": choices, "answer": answer, "stages": stages},
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# FactorialBasicsTemplate — subtopic "factorial_basics"
# ---------------------------------------------------------------------------


@register_template
class FactorialBasicsTemplate:
    topic = Topic.COMBINATORICS
    subtopic = "factorial_basics"
    supported_difficulties = [Difficulty.EASY, Difficulty.MEDIUM]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        return self._medium(rng)

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        """Compute n! directly, wrapped in a word problem."""
        n = factorial_n(rng, "easy")
        answer = math.factorial(n)

        # Pick a word-problem context or pure computation
        if rng.random() < 0.15:
            # Pure computation: "Evaluate: 5!"
            question_text = f"Evaluate: ${fmt_factorial(n)}$"
        else:
            ctx = rng.choice(FACTORIAL_CONTEXTS)
            question_text = ctx.format(n=n)

        # Solution steps
        expansion = " \\times ".join(str(i) for i in range(n, 0, -1))
        steps = [
            TrustedLatex(f"${fmt_factorial(n)} = {expansion}$"),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(answer)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            metadata={"n": n, "answer": answer, "type": "factorial"},
            solution_steps=tuple(steps),
        )

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        """Simplify n!/k! where k < n."""
        n = factorial_n(rng, "medium")
        gap = rng.randint(2, 4)
        k = n - gap  # so n!/k! = n * (n-1) * ... * (k+1)
        if k < 1:
            k = 1
        answer = math.factorial(n) // math.factorial(k)

        # Pure computation or word problem variant
        if rng.random() < 0.2:
            question_text = f"Simplify: $\\frac{{{fmt_factorial(n)}}}{{{fmt_factorial(k)}}}$"
        else:
            ctx = rng.choice(PERMUTATION_CONTEXTS)
            question_text = ctx.format(n=n, r=n - k)

        # Solution steps
        factors = " \\times ".join(str(i) for i in range(n, k, -1))
        steps = [
            TrustedLatex(f"$\\frac{{{fmt_factorial(n)}}}{{{fmt_factorial(k)}}} = {factors}$"),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(answer)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            metadata={"n": n, "k": k, "answer": answer, "type": "factorial_ratio"},
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# PermutationsTemplate — subtopic "permutations"
# ---------------------------------------------------------------------------


@register_template
class PermutationsTemplate:
    topic = Topic.COMBINATORICS
    subtopic = "permutations"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        n, r = perm_params(rng, difficulty.value)
        answer = math.perm(n, r)

        ctx = rng.choice(PERMUTATION_CONTEXTS)
        question_text = ctx.format(n=n, r=r)

        # Solution steps
        factors = " \\times ".join(str(i) for i in range(n, n - r, -1))
        steps = [
            TrustedLatex("$\\text{This is a permutation: order matters.}$"),
            TrustedLatex(
                f"${fmt_perm(n, r)} = \\frac{{{fmt_factorial(n)}}}{{{fmt_factorial(n - r)}}}$"
            ),
            TrustedLatex(f"$= {factors}$"),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(answer)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"n": n, "r": r, "answer": answer},
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# CombinationsTemplate — subtopic "combinations"
# ---------------------------------------------------------------------------


@register_template
class CombinationsTemplate:
    topic = Topic.COMBINATORICS
    subtopic = "combinations"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.HARD:
            return self._hard(rng)
        return self._standard(difficulty, rng)

    def _standard(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        n, r = comb_params(rng, difficulty.value)
        answer = math.comb(n, r)

        ctx = rng.choice(COMBINATION_CONTEXTS)
        question_text = ctx.format(n=n, r=r)

        steps = [
            TrustedLatex("$\\text{This is a combination: order does not matter.}$"),
            TrustedLatex(
                f"${fmt_comb(n, r)} = \\frac{{{fmt_factorial(n)}}}{{{fmt_factorial(r)} \\cdot {fmt_factorial(n - r)}}}$"
            ),
            TrustedLatex(f"$= {latex(answer)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(answer)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=difficulty,
            subtopic=self.subtopic,
            metadata={"n": n, "r": r, "answer": answer, "type": "simple"},
            solution_steps=tuple(steps),
        )

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        """'At least k' combination: sum of C(n, k) for k >= threshold."""
        n = rng.randint(8, 14)
        r = rng.randint(4, min(6, n - 1))
        threshold = rng.randint(2, r - 1)

        # "At least threshold from group A" pattern:
        # Total ways to pick r from n, but at least `threshold` from group_a_size
        group_a_size = rng.randint(threshold + 1, min(n - 2, threshold + 4))
        group_b_size = n - group_a_size

        # Ensure we can actually form the committee
        if group_a_size < threshold or group_b_size < 0:
            # Fallback to simple combination
            return self._standard(Difficulty.HARD, rng)

        answer = 0
        terms = []
        for a_count in range(threshold, min(group_a_size, r) + 1):
            b_count = r - a_count
            if b_count < 0 or b_count > group_b_size:
                continue
            term = math.comb(group_a_size, a_count) * math.comb(group_b_size, b_count)
            terms.append((a_count, b_count, term))
            answer += term

        if answer <= 1 or not terms:
            return self._standard(Difficulty.HARD, rng)

        # Build question
        group_a_label = rng.choice(["women", "seniors", "science students", "experienced members"])
        group_b_label = rng.choice(["men", "juniors", "arts students", "new members"])
        question_text = (
            f"A committee of ${r}$ is formed from ${group_a_size}$ {group_a_label} and "
            f"${group_b_size}$ {group_b_label}. How many committees have at least "
            f"${threshold}$ {group_a_label}?"
        )

        # Solution steps
        steps = [
            TrustedLatex(
                f"$\\text{{We need at least {threshold} {group_a_label} out of {r} total.}}$"
            ),
        ]
        term_strs = []
        for a_count, b_count, term in terms:
            expr = f"{fmt_comb(group_a_size, a_count)} \\cdot {fmt_comb(group_b_size, b_count)} = {latex(term)}"
            term_strs.append(str(term))
            steps.append(TrustedLatex(f"${a_count} \\text{{ {group_a_label}}}: {expr}$"))
        steps.append(
            TrustedLatex(f"$\\text{{Total}} = {' + '.join(term_strs)} = {latex(answer)}$")
        )

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(answer)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            metadata={
                "n": n,
                "r": r,
                "answer": answer,
                "type": "at_least",
                "group_a": group_a_size,
                "group_b": group_b_size,
                "threshold": threshold,
            },
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# BasicProbabilityTemplate — subtopic "basic_probability"
# ---------------------------------------------------------------------------


@register_template
class BasicProbabilityTemplate:
    topic = Topic.COMBINATORICS
    subtopic = "basic_probability"
    supported_difficulties = ALL_DIFFICULTIES

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.EASY:
            return self._easy(rng)
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    def _easy(self, rng: random.Random) -> GeneratedProblem:
        """Bag with 2 colors, draw one."""
        ctx = rng.choice(BASIC_PROB_BAG_2COLOR)
        color1, color2 = ctx["items"]
        container = ctx["container"]
        objects = ctx["objects"]

        a = rng.randint(2, 8)
        b = rng.randint(2, 8)
        total = a + b
        # Pick which color to ask about
        target_color, favorable = rng.choice([(color1, a), (color2, b)])

        prob = Rational(favorable, total)
        # Ensure non-trivial
        if prob == 0 or prob == 1:
            a, b = 3, 5
            total = 8
            target_color, favorable = color1, a
            prob = Rational(favorable, total)

        singular = objects[:-1] if objects.endswith("s") else objects
        question_text = (
            f"A {container} contains ${a}$ {color1} and ${b}$ {color2} {objects}. "
            f"One {singular} is drawn at random. "
            f"What is the probability it is {target_color}?"
        )

        steps = [
            TrustedLatex(f"$\\text{{Favorable outcomes}} = {favorable}$"),
            TrustedLatex(f"$\\text{{Total outcomes}} = {total}$"),
            TrustedLatex(f"$P = \\frac{{{favorable}}}{{{total}}} = {latex(prob)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.EASY,
            subtopic=self.subtopic,
            metadata={
                "favorable": favorable,
                "total": total,
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
            },
            solution_steps=tuple(steps),
        )

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        """Bag with 3 colors, draw one."""
        ctx = rng.choice(BASIC_PROB_BAG_3COLOR)
        color1, color2, color3 = ctx["items"]
        container = ctx["container"]
        objects = ctx["objects"]

        a = rng.randint(2, 7)
        b = rng.randint(2, 7)
        c = rng.randint(2, 7)
        total = a + b + c
        counts = {color1: a, color2: b, color3: c}
        target_color = rng.choice([color1, color2, color3])
        favorable = counts[target_color]

        prob = Rational(favorable, total)
        if prob == 0 or prob == 1:
            a, b, c = 3, 4, 5
            total = 12
            target_color, favorable = color1, a
            prob = Rational(favorable, total)

        question_text = (
            f"A {container} contains ${a}$ {color1}, ${b}$ {color2}, and ${c}$ {color3} {objects}. "
            f"One is drawn at random. What is the probability it is {target_color}?"
        )

        steps = [
            TrustedLatex(f"$\\text{{Favorable outcomes}} = {favorable}$"),
            TrustedLatex(f"$\\text{{Total outcomes}} = {a} + {b} + {c} = {total}$"),
            TrustedLatex(f"$P = \\frac{{{favorable}}}{{{total}}} = {latex(prob)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            metadata={
                "favorable": favorable,
                "total": total,
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
            },
            solution_steps=tuple(steps),
        )

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        """Two dice sum or number from range with condition."""
        variant = rng.choice(["two_dice", "number_range"])

        if variant == "two_dice":
            return self._hard_two_dice(rng)
        return self._hard_number_range(rng)

    def _hard_two_dice(self, rng: random.Random) -> GeneratedProblem:
        """Two dice are rolled. P(sum > threshold) or P(sum == target)."""
        threshold = rng.randint(7, 10)
        # Count outcomes where sum > threshold
        favorable = sum(1 for d1 in range(1, 7) for d2 in range(1, 7) if d1 + d2 > threshold)
        total = 36
        prob = Rational(favorable, total)

        if prob == 0 or prob == 1:
            threshold = 9
            favorable = sum(1 for d1 in range(1, 7) for d2 in range(1, 7) if d1 + d2 > threshold)
            prob = Rational(favorable, total)

        question_text = (
            f"Two fair dice are rolled. What is the probability that the sum "
            f"is greater than ${threshold}$?"
        )

        steps = [
            TrustedLatex("$\\text{Total outcomes} = 6 \\times 6 = 36$"),
            TrustedLatex(
                f"$\\text{{Favorable outcomes (sum}} > {threshold}\\text{{)}} = {favorable}$"
            ),
            TrustedLatex(f"$P = \\frac{{{favorable}}}{{36}} = {latex(prob)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            metadata={
                "favorable": favorable,
                "total": total,
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
                "variant": "two_dice",
            },
            solution_steps=tuple(steps),
        )

    def _hard_number_range(self, rng: random.Random) -> GeneratedProblem:
        """A number is chosen from 1 to n. P(divisible by d)."""
        n = rng.randint(15, 40)
        d = rng.choice([3, 4, 5, 6, 7])
        favorable = n // d
        total = n

        prob = Rational(favorable, total)
        if prob == 0 or prob == 1:
            n, d = 30, 7
            favorable = n // d
            total = n
            prob = Rational(favorable, total)

        question_text = (
            f"A number is chosen at random from $1$ to ${n}$. "
            f"What is the probability it is divisible by ${d}$?"
        )

        steps = [
            TrustedLatex(f"$\\text{{Total outcomes}} = {n}$"),
            TrustedLatex(
                f"$\\text{{Multiples of {d} from 1 to {n}}}: {d}, {2 * d}, \\ldots, {favorable * d}$"
            ),
            TrustedLatex(f"$\\text{{Count}} = \\lfloor {n} \\div {d} \\rfloor = {favorable}$"),
            TrustedLatex(f"$P = \\frac{{{favorable}}}{{{n}}} = {latex(prob)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            metadata={
                "favorable": favorable,
                "total": total,
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
                "variant": "number_range",
            },
            solution_steps=tuple(steps),
        )


# ---------------------------------------------------------------------------
# CompoundProbabilityTemplate — subtopic "compound_probability"
# ---------------------------------------------------------------------------


@register_template
class CompoundProbabilityTemplate:
    topic = Topic.COMBINATORICS
    subtopic = "compound_probability"
    supported_difficulties = [Difficulty.MEDIUM, Difficulty.HARD]

    def generate(self, difficulty: Difficulty, rng: random.Random) -> GeneratedProblem:
        if difficulty == Difficulty.MEDIUM:
            return self._medium(rng)
        return self._hard(rng)

    def _medium(self, rng: random.Random) -> GeneratedProblem:
        """Independent events."""
        variant = rng.choice(["coins", "coin_die", "spinner", "repeated"])

        if variant == "coins":
            return self._two_coins(rng)
        if variant == "coin_die":
            return self._coin_and_die(rng)
        if variant == "spinner":
            return self._spinner_twice(rng)
        return self._repeated_independent(rng)

    def _hard(self, rng: random.Random) -> GeneratedProblem:
        """Dependent events (without replacement)."""
        variant = rng.choice(["bag_2color", "bag_3color", "cards"])

        if variant == "bag_2color":
            return self._bag_without_replacement_2(rng)
        if variant == "bag_3color":
            return self._bag_without_replacement_3(rng)
        return self._cards_without_replacement(rng)

    # -- Independent event helpers --

    def _two_coins(self, rng: random.Random) -> GeneratedProblem:
        prob = Rational(1, 4)
        question_text = (
            "Two fair coins are flipped. What is the probability of getting heads on both?"
        )
        steps = [
            TrustedLatex("$P(\\text{heads}) = \\frac{1}{2}$ for each coin."),
            TrustedLatex(
                f"$P(\\text{{both heads}}) = \\frac{{1}}{{2}} \\times \\frac{{1}}{{2}} = {latex(prob)}$"
            ),
        ]
        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            metadata={"answer_num": 1, "answer_den": 4, "type": "independent", "variant": "coins"},
            solution_steps=tuple(steps),
        )

    def _coin_and_die(self, rng: random.Random) -> GeneratedProblem:
        k = rng.randint(2, 5)
        favorable_die = 6 - k  # numbers > k
        prob = Rational(1, 2) * Rational(favorable_die, 6)

        question_text = (
            f"A coin is flipped and a fair die is rolled. What is the probability "
            f"of getting heads and rolling a number greater than ${k}$?"
        )
        steps = [
            TrustedLatex("$P(\\text{heads}) = \\frac{1}{2}$"),
            TrustedLatex(f"$P(\\text{{die}} > {k}) = \\frac{{{favorable_die}}}{{6}}$"),
            TrustedLatex(
                f"$P = \\frac{{1}}{{2}} \\times \\frac{{{favorable_die}}}{{6}} = {latex(prob)}$"
            ),
        ]
        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            metadata={
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
                "type": "independent",
                "variant": "coin_die",
            },
            solution_steps=tuple(steps),
        )

    def _spinner_twice(self, rng: random.Random) -> GeneratedProblem:
        a = rng.randint(2, 6)
        b = rng.randint(2, 6)
        total = a + b
        prob = Rational(a, total) * Rational(a, total)

        question_text = (
            f"A spinner with ${a}$ red and ${b}$ blue equal sections is spun twice. "
            f"What is the probability of landing on red both times?"
        )
        p1 = Rational(a, total)
        steps = [
            TrustedLatex(f"$P(\\text{{red}}) = \\frac{{{a}}}{{{total}}} = {latex(p1)}$"),
            TrustedLatex(
                f"$P(\\text{{red both}}) = {latex(p1)} \\times {latex(p1)} = {latex(prob)}$"
            ),
        ]
        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            metadata={
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
                "type": "independent",
                "variant": "spinner",
            },
            solution_steps=tuple(steps),
        )

    def _repeated_independent(self, rng: random.Random) -> GeneratedProblem:
        """Repeated independent trials: e.g., free throws, guessing quiz answers."""
        p_num = rng.randint(1, 4)
        p_den = rng.choice([5, 6, 8, 10])
        while p_num >= p_den:
            p_den = rng.choice([5, 6, 8, 10])
        k = rng.randint(2, 3)
        p_single = Rational(p_num, p_den)
        prob = p_single**k

        contexts = [
            f"A basketball player makes free throws with probability ${latex(p_single)}$. What is the probability of making ${k}$ consecutive free throws?",
            f"The probability of rain on any given day is ${latex(p_single)}$. Assuming independence, what is the probability it rains on all ${k}$ days of a long weekend?",
            f"An archer hits the target with probability ${latex(p_single)}$ per shot. What is the probability of hitting the target on ${k}$ consecutive independent shots?",
        ]
        question_text = rng.choice(contexts)

        steps = [
            TrustedLatex(f"$P(\\text{{single event}}) = {latex(p_single)}$"),
            TrustedLatex("$\\text{Events are independent, so multiply:}$"),
            TrustedLatex(f"$P = \\left({latex(p_single)}\\right)^{{{k}}} = {latex(prob)}$"),
        ]
        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.MEDIUM,
            subtopic=self.subtopic,
            metadata={
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
                "type": "independent",
                "variant": "repeated",
            },
            solution_steps=tuple(steps),
        )

    # -- Dependent event helpers (without replacement) --

    def _bag_without_replacement_2(self, rng: random.Random) -> GeneratedProblem:
        """Two draws without replacement from 2-color bag."""
        a = rng.randint(3, 10)
        b = rng.randint(3, 10)
        total = a + b

        # Ask about both being color1 or color2
        target = rng.choice(["first", "second"])
        if target == "first":
            fav = a
        else:
            fav = b

        ctx = rng.choice(BASIC_PROB_BAG_2COLOR)
        color1, color2 = ctx["items"]
        container = ctx["container"]
        objects = ctx["objects"]

        if target == "first":
            chosen_color = color1
            fav = a
        else:
            chosen_color = color2
            fav = b

        p1 = Rational(fav, total)
        p2 = Rational(fav - 1, total - 1)
        prob = p1 * p2

        if prob == 0 or prob == 1:
            a, b, fav = 5, 7, 5
            total = 12
            chosen_color = color1
            p1 = Rational(5, 12)
            p2 = Rational(4, 11)
            prob = p1 * p2

        question_text = (
            f"A {container} has ${a}$ {color1} and ${b}$ {color2} {objects}. "
            f"Two are drawn without replacement. What is the probability both are {chosen_color}?"
        )

        steps = [
            TrustedLatex(
                f"$P(\\text{{1st {chosen_color}}}) = \\frac{{{fav}}}{{{total}}} = {latex(p1)}$"
            ),
            TrustedLatex(
                f"$P(\\text{{2nd {chosen_color} | 1st {chosen_color}}}) = \\frac{{{fav - 1}}}{{{total - 1}}} = {latex(p2)}$"
            ),
            TrustedLatex(f"$P(\\text{{both}}) = {latex(p1)} \\times {latex(p2)} = {latex(prob)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            metadata={
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
                "type": "dependent",
                "variant": "bag_2color",
            },
            solution_steps=tuple(steps),
        )

    def _bag_without_replacement_3(self, rng: random.Random) -> GeneratedProblem:
        """Two draws without replacement from 3-color bag."""
        ctx = rng.choice(BASIC_PROB_BAG_3COLOR)
        color1, color2, color3 = ctx["items"]
        container = ctx["container"]
        objects = ctx["objects"]

        a = rng.randint(3, 8)
        b = rng.randint(3, 8)
        c = rng.randint(3, 8)
        total = a + b + c

        counts = {color1: a, color2: b, color3: c}
        chosen_color = rng.choice([color1, color2, color3])
        fav = counts[chosen_color]

        p1 = Rational(fav, total)
        p2 = Rational(fav - 1, total - 1)
        prob = p1 * p2

        if prob == 0 or prob == 1:
            a, b, c = 4, 5, 3
            total = 12
            fav = a
            chosen_color = color1
            p1 = Rational(4, 12)
            p2 = Rational(3, 11)
            prob = p1 * p2

        question_text = (
            f"A {container} has ${a}$ {color1}, ${b}$ {color2}, and ${c}$ {color3} {objects}. "
            f"Two are drawn without replacement. What is the probability both are {chosen_color}?"
        )

        steps = [
            TrustedLatex(f"$\\text{{Total}} = {a} + {b} + {c} = {total}$"),
            TrustedLatex(
                f"$P(\\text{{1st {chosen_color}}}) = \\frac{{{fav}}}{{{total}}} = {latex(p1)}$"
            ),
            TrustedLatex(
                f"$P(\\text{{2nd {chosen_color} | 1st}}) = \\frac{{{fav - 1}}}{{{total - 1}}} = {latex(p2)}$"
            ),
            TrustedLatex(f"$P(\\text{{both}}) = {latex(p1)} \\times {latex(p2)} = {latex(prob)}$"),
        ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            metadata={
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
                "type": "dependent",
                "variant": "bag_3color",
            },
            solution_steps=tuple(steps),
        )

    def _cards_without_replacement(self, rng: random.Random) -> GeneratedProblem:
        """Two cards drawn without replacement from standard deck."""
        variant = rng.choice(["suit", "face"])

        if variant == "suit":
            suit = rng.choice(["hearts", "spades", "diamonds", "clubs"])
            p1 = Rational(13, 52)
            p2 = Rational(12, 51)
            prob = p1 * p2
            question_text = (
                f"Two cards are drawn without replacement from a standard $52$-card deck. "
                f"What is the probability both are {suit}?"
            )
            steps = [
                TrustedLatex(f"$P(\\text{{1st {suit}}}) = \\frac{{13}}{{52}} = {latex(p1)}$"),
                TrustedLatex(
                    f"$P(\\text{{2nd {suit} | 1st}}) = \\frac{{12}}{{51}} = {latex(p2)}$"
                ),
                TrustedLatex(
                    f"$P(\\text{{both}}) = {latex(p1)} \\times {latex(p2)} = {latex(prob)}$"
                ),
            ]
        else:
            # Face cards: 12 in deck (J, Q, K × 4 suits)
            p1 = Rational(12, 52)
            p2 = Rational(11, 51)
            prob = p1 * p2
            question_text = (
                "Two cards are drawn without replacement from a standard $52$-card deck. "
                "What is the probability both are face cards?"
            )
            steps = [
                TrustedLatex("$\\text{Face cards in deck} = 12$"),
                TrustedLatex(f"$P(\\text{{1st face}}) = \\frac{{12}}{{52}} = {latex(p1)}$"),
                TrustedLatex(f"$P(\\text{{2nd face | 1st}}) = \\frac{{11}}{{51}} = {latex(p2)}$"),
                TrustedLatex(
                    f"$P(\\text{{both}}) = {latex(p1)} \\times {latex(p2)} = {latex(prob)}$"
                ),
            ]

        return GeneratedProblem(
            question_latex=TrustedLatex(question_text),
            answer_latex=TrustedLatex(f"${latex(prob)}$"),
            topic=Topic.COMBINATORICS,
            difficulty=Difficulty.HARD,
            subtopic=self.subtopic,
            metadata={
                "answer_num": int(prob.p),
                "answer_den": int(prob.q),
                "type": "dependent",
                "variant": f"cards_{variant}",
            },
            solution_steps=tuple(steps),
        )
