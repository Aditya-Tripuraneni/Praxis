"""Shared helpers for combinatorics & probability templates.

Pure functions returning LaTeX strings, word-problem context pools,
and parameter-range utilities.
"""

from __future__ import annotations

import random

from sympy import Rational, latex

# ---------------------------------------------------------------------------
# LaTeX formatting helpers
# ---------------------------------------------------------------------------


def fmt_perm(n: int, r: int) -> str:
    """Format P(n, r) in LaTeX notation."""
    return f"P({n}, {r})"


def fmt_comb(n: int, r: int) -> str:
    r"""Format C(n, r) in LaTeX binomial notation: \binom{n}{r}."""
    return f"\\binom{{{n}}}{{{r}}}"


def fmt_factorial(n: int) -> str:
    """Format n! in LaTeX."""
    return f"{n}!"


def fmt_fraction(p: int, q: int) -> str:
    r"""Format p/q as a simplified LaTeX fraction via sympy.Rational."""
    return latex(Rational(p, q))


# ---------------------------------------------------------------------------
# Word-problem context pools (25 per subtopic)
# ---------------------------------------------------------------------------

COUNTING_PRINCIPLE_CONTEXTS: list[dict] = [
    {
        "stages": 3,
        "template": "A restaurant offers ${{a}}$ appetizers, ${{b}}$ main courses, and ${{c}}$ desserts. How many different 3-course meals are possible?",
    },
    {
        "stages": 3,
        "template": "An outfit consists of a shirt, pants, and shoes. With ${{a}}$ shirts, ${{b}}$ pairs of pants, and ${{c}}$ pairs of shoes, how many different outfits can be made?",
    },
    {
        "stages": 2,
        "template": "A license plate consists of one letter chosen from ${{a}}$ letters followed by one digit chosen from ${{b}}$ digits. How many different license plates are possible?",
    },
    {
        "stages": 2,
        "template": "A phone password consists of a pattern from ${{a}}$ options followed by a color from ${{b}}$ options. How many different passwords are possible?",
    },
    {
        "stages": 3,
        "template": "An ice cream shop sells ${{a}}$ flavors, ${{b}}$ types of cone, and ${{c}}$ toppings. How many different single-scoop orders are possible?",
    },
    {
        "stages": 2,
        "template": "A travel route goes through $3$ cities. There are ${{a}}$ roads from the first to the second city and ${{b}}$ roads from the second to the third. How many different routes are possible?",
    },
    {
        "stages": 3,
        "template": "A pizza shop offers ${{a}}$ types of crust, ${{b}}$ types of sauce, and ${{c}}$ types of cheese. How many different base pizzas can be made?",
    },
    {
        "stages": 3,
        "template": "A computer password requires one uppercase letter from ${{a}}$ options, one lowercase letter from ${{b}}$ options, and one digit from ${{c}}$ options. How many passwords are possible?",
    },
    {
        "stages": 3,
        "template": "A sandwich shop offers ${{a}}$ types of bread, ${{b}}$ types of meat, and ${{c}}$ condiments. How many different sandwiches can be made?",
    },
    {
        "stages": 3,
        "template": "A gift is wrapped using one of ${{a}}$ types of paper, one of ${{b}}$ ribbon colors, and one of ${{c}}$ bow styles. How many different gift wrappings are possible?",
    },
    {
        "stages": 3,
        "template": "A car can be ordered in ${{a}}$ colors, ${{b}}$ trim levels, and ${{c}}$ engine types. How many different configurations are available?",
    },
    {
        "stages": 3,
        "template": "A breakfast combo consists of one of ${{a}}$ cereals, one of ${{b}}$ juices, and one of ${{c}}$ fruits. How many different breakfast combos are possible?",
    },
    {
        "stages": 3,
        "template": "A student must choose one of ${{a}}$ math sections, one of ${{b}}$ science sections, and one of ${{c}}$ electives. How many different schedules are possible?",
    },
    {
        "stages": 3,
        "template": "A movie night requires choosing one of ${{a}}$ genres, one of ${{b}}$ theaters, and one of ${{c}}$ showtimes. How many different movie plans are possible?",
    },
    {
        "stages": 3,
        "template": "A phone case comes in ${{a}}$ brands, ${{b}}$ colors, and ${{c}}$ materials. How many different phone cases are available?",
    },
    {
        "stages": 3,
        "template": "A smoothie is made with one of ${{a}}$ bases, one of ${{b}}$ fruits, and one of ${{c}}$ protein additions. How many different smoothies can be made?",
    },
    {
        "stages": 3,
        "template": "A hotel room can be chosen from ${{a}}$ floors, ${{b}}$ views, and ${{c}}$ bed types. How many different room selections are possible?",
    },
    {
        "stages": 2,
        "template": "A luggage tag has one of ${{a}}$ first initials and one of ${{b}}$ last initials. How many different tags are possible?",
    },
    {
        "stages": 3,
        "template": "A paint mix uses one of ${{a}}$ base colors, one of ${{b}}$ tints, and one of ${{c}}$ finishes. How many different paints can be mixed?",
    },
    {
        "stages": 3,
        "template": "A birthday party plan requires one of ${{a}}$ themes, one of ${{b}}$ cake flavors, and one of ${{c}}$ activities. How many different party plans are possible?",
    },
    {
        "stages": 2,
        "template": "A concert ticket comes in one of ${{a}}$ seating sections and one of ${{b}}$ price tiers. How many different ticket options are there?",
    },
    {
        "stages": 3,
        "template": "A class project team must choose one of ${{a}}$ topics, one of ${{b}}$ formats, and one of ${{c}}$ presentation dates. How many different project plans are possible?",
    },
    {
        "stages": 3,
        "template": "A pet adoption form asks for one of ${{a}}$ preferred species, one of ${{b}}$ age ranges, and one of ${{c}}$ size preferences. How many different preference combinations exist?",
    },
    {
        "stages": 3,
        "template": "A custom notebook comes in ${{a}}$ cover designs, ${{b}}$ paper types, and ${{c}}$ binding styles. How many different notebooks can be ordered?",
    },
    {
        "stages": 2,
        "template": "A lock has ${{a}}$ options for the first dial and ${{b}}$ options for the second dial. How many different settings are possible?",
    },
]

FACTORIAL_CONTEXTS: list[str] = [
    "In how many ways can ${n}$ distinct books be arranged in a row on a shelf?",
    "How many different orders can ${n}$ runners finish a race?",
    "${n}$ students line up for a class photo. How many different arrangements are possible?",
    "A playlist has ${n}$ songs. How many different orderings of all ${n}$ songs are possible?",
    "How many distinct arrangements of all the letters in a ${n}$-letter word (all unique letters) are possible?",
    "${n}$ cards are dealt face up in a row. How many different orderings are possible?",
    "${n}$ speakers will present at an awards ceremony. How many different speaking orders are possible?",
    "${n}$ cars must park in a row of ${n}$ spots. How many different arrangements are possible?",
    "A gallery hangs ${n}$ paintings in a row. How many different arrangements are possible?",
    "A relay team of ${n}$ runners must decide the order they run. How many different orders are possible?",
    "A student has ${n}$ classes in a day. How many different orderings of the classes are possible?",
    "${n}$ movies are watched back-to-back. How many different viewing orders are possible?",
    "A to-do list has ${n}$ tasks. How many different orderings can the tasks be completed in?",
    "${n}$ guests arrive one at a time. How many different arrival orders are possible?",
    "${n}$ files must be arranged in a folder. How many different orderings are possible?",
    "An author arranges ${n}$ chapters in a book. How many different chapter orderings are possible?",
    "A parade has ${n}$ floats. How many different orders can the floats appear in?",
    "${n}$ dancers perform solos in a recital. How many different performance orders are possible?",
    "A tasting menu has ${n}$ dishes. How many different orders can the dishes be served in?",
    "${n}$ candidates speak at a debate. How many different speaking orders are possible?",
    "${n}$ players are assigned to a batting order. How many different lineups are possible?",
    "${n}$ dogs are groomed one at a time. How many different grooming orders are possible?",
    "${n}$ videos are uploaded in sequence. How many different upload orders are possible?",
    "${n}$ athletes march in a ceremony. How many different marching orders are possible?",
    "${n}$ toys are placed in a row on a display. How many different arrangements are possible?",
]

PERMUTATION_CONTEXTS: list[str] = [
    "${n}$ students are running a race. In how many ways can the top ${r}$ positions be filled?",
    "How many different ${r}$-letter arrangements can be formed from ${n}$ distinct letters without repetition?",
    "In how many ways can ${r}$ books be arranged on a shelf chosen from a collection of ${n}$ books?",
    "A club has ${n}$ members. In how many ways can ${r}$ different officer positions be filled?",
    "How many different ${r}$-digit codes can be formed using digits from $1$ to ${n}$ without repetition?",
    "From ${n}$ contestants, how many ways can a first, second, and third prize be awarded?",
    "${n}$ students are in a class. In how many ways can ${r}$ specific seats in the front row be assigned?",
    "A coach selects ${r}$ players from a roster of ${n}$ for the starting batting order. How many different lineups are possible?",
    "From ${n}$ dancers, how many ways can ${r}$ be chosen and ordered for a performance?",
    "A DJ creates a playlist of ${r}$ songs chosen in order from ${n}$ available songs. How many playlists are possible?",
    "${n}$ volunteers are available. How many ways can ${r}$ be chosen to present in a specific order?",
    "A store window displays ${r}$ products in a row chosen from ${n}$ available items. How many arrangements are possible?",
    "How many ${r}$-character passwords can be created from ${n}$ distinct characters without repeating any?",
    "A manager assigns ${r}$ different tasks to ${r}$ people chosen from ${n}$ employees. How many assignments are possible?",
    "A relay team needs ${r}$ runners in a specific order chosen from ${n}$ athletes. How many different teams are possible?",
    "A traveler visits ${r}$ cities in order from a list of ${n}$ cities. How many different itineraries are possible?",
    "A chef adds ${r}$ ingredients one at a time from ${n}$ available. How many different orders of addition are possible?",
    "${n}$ cars compete and ${r}$ numbered parking spots are assigned to the top finishers. How many outcomes are possible?",
    "From ${n}$ candidates, how many ways can ${r}$ be selected to speak in a specific debate order?",
    "A fashion show features ${r}$ models walking in order, selected from ${n}$ models. How many lineups are possible?",
    "A coach assigns ${r}$ specific field positions from a team of ${n}$ players. How many different assignments are possible?",
    "An art show selects ${r}$ paintings to display in numbered positions from ${n}$ submissions. How many arrangements are possible?",
    "A phone number is formed by choosing ${r}$ digits in order from ${n}$ available digits, no repetition. How many phone numbers are possible?",
    "A choreographer arranges ${r}$ dance moves in sequence from ${n}$ possible moves. How many routines are possible?",
    "From ${n}$ movies, ${r}$ are selected and scheduled in order for a film marathon. How many different schedules are possible?",
]

COMBINATION_CONTEXTS: list[str] = [
    "From a group of ${n}$ students, how many ways can a committee of ${r}$ be formed?",
    "A pizza shop offers ${n}$ toppings. How many different ${r}$-topping pizzas can be made?",
    "How many ways can ${r}$ books be chosen from a shelf of ${n}$?",
    "A team of ${r}$ players is selected from ${n}$ applicants. How many possible teams are there?",
    "In how many ways can ${r}$ songs be chosen from a playlist of ${n}$?",
    "A student must answer ${r}$ questions from a test with ${n}$ questions. How many different selections are possible?",
    "A fruit basket contains ${r}$ fruits chosen from ${n}$ types. How many different baskets are possible?",
    "${r}$ identical scholarships are awarded to ${r}$ students chosen from ${n}$ applicants. How many selections are possible?",
    "A hand of ${r}$ cards is dealt from a deck of ${n}$ cards. How many different hands are possible?",
    "${r}$ chaperones are needed from ${n}$ parent volunteers. How many different groups can be chosen?",
    "A student selects ${r}$ elective courses from ${n}$ available. How many different course selections are possible?",
    "You can invite ${r}$ friends to a party from a group of ${n}$. How many different guest lists are possible?",
    "A quality inspector selects ${r}$ items from a batch of ${n}$ to test. How many different samples are possible?",
    "${r}$ cookie flavors are chosen from ${n}$ available for a variety box. How many different boxes are possible?",
    "From ${n}$ movies, ${r}$ are selected for a film festival. How many different selections are possible?",
    "${r}$ vacation destinations are chosen from ${n}$ options for a travel package. How many packages are possible?",
    "${r}$ raffle winners are drawn from ${n}$ entries. How many different sets of winners are possible?",
    "A lab group of ${r}$ students is formed from a class of ${n}$. How many different lab groups are possible?",
    "A recipe calls for ${r}$ spices chosen from ${n}$ available. How many different spice combinations are possible?",
    "A book club selects ${r}$ books from ${n}$ nominations. How many different reading lists are possible?",
    "In a lottery, ${r}$ numbers are chosen from $1$ to ${n}$. How many different tickets are possible?",
    "${r}$ gifts are selected from ${n}$ options for a gift basket. How many different baskets are possible?",
    "A student attends ${r}$ workshop sessions from ${n}$ available. How many different schedules are possible?",
    "An appetizer sampler includes ${r}$ items chosen from ${n}$ on the menu. How many different samplers are possible?",
    "A hiker picks ${r}$ trails to explore from ${n}$ available trails. How many different selections are possible?",
]

# Basic probability contexts return (question_template, color_key) tuples.
# The template uses {a}, {b}, {c} for counts and {color} for the target.
BASIC_PROB_BAG_2COLOR: list[dict] = [
    {"items": ("red", "blue"), "container": "bag", "objects": "marbles"},
    {"items": ("red", "blue"), "container": "bag", "objects": "balls"},
    {"items": ("black", "white"), "container": "drawer", "objects": "socks"},
    {"items": ("strawberry", "lemon"), "container": "bag", "objects": "candies"},
    {"items": ("red", "white"), "container": "box", "objects": "tickets"},
    {"items": ("plain", "flavored"), "container": "bag", "objects": "chips"},
]

BASIC_PROB_BAG_3COLOR: list[dict] = [
    {"items": ("red", "blue", "green"), "container": "bag", "objects": "balls"},
    {"items": ("red", "blue", "yellow"), "container": "spinner", "objects": "sections"},
    {"items": ("pennies", "nickels", "dimes"), "container": "jar", "objects": "coins"},
    {"items": ("apples", "oranges", "bananas"), "container": "basket", "objects": "fruits"},
    {"items": ("red", "blue", "white"), "container": "jar", "objects": "beads"},
    {"items": ("cars", "dolls", "blocks"), "container": "bin", "objects": "toys"},
    {"items": ("red", "yellow", "white"), "container": "garden", "objects": "flowers"},
]

BASIC_PROB_NUMBER_CONDITIONS: list[dict] = [
    {"label": "even", "test": lambda x: x % 2 == 0},
    {"label": "odd", "test": lambda x: x % 2 == 1},
    {"label": "greater than {threshold}", "test": None},  # threshold set at runtime
    {"label": "less than {threshold}", "test": None},
    {"label": "divisible by {d}", "test": None},
    {
        "label": "a prime number",
        "test": lambda x: x > 1 and all(x % i != 0 for i in range(2, int(x**0.5) + 1)),
    },
]

BASIC_PROB_WORD_CONTEXTS: list[str] = [
    'A letter is chosen at random from the word "{word}". What is the probability it is a vowel?',
    "A class has {a} boys and {b} girls. One student is chosen at random. What is the probability the student is a boy?",
    "A day of the week is chosen at random. What is the probability it is a weekday?",
    "A card is drawn from a standard 52-card deck. What is the probability it is a heart?",
    "A card is drawn from a standard 52-card deck. What is the probability it is a face card?",
    "A fair die is rolled. What is the probability of rolling a number greater than {threshold}?",
    "A number is chosen at random from 1 to {n}. What is the probability it is even?",
]

COMPOUND_PROB_CONTEXTS: list[dict] = [
    # Independent events
    {
        "type": "independent",
        "template": "Two fair coins are flipped. What is the probability of getting heads on both?",
    },
    {
        "type": "independent",
        "template": "A coin is flipped and a fair die is rolled. What is the probability of getting heads and rolling a number greater than {k}?",
    },
    {
        "type": "independent",
        "template": "A spinner with {a} red and {b} blue sections is spun twice. What is the probability of landing on red both times?",
    },
    {
        "type": "independent",
        "template": "A basketball player makes free throws with probability $\\frac{{{p}}}{{{q}}}$. What is the probability of making {k} consecutive free throws?",
    },
    {
        "type": "independent",
        "template": "The probability of rain on any given day is $\\frac{{{p}}}{{{q}}}$. What is the probability it rains on both Saturday and Sunday?",
    },
    {
        "type": "independent",
        "template": "A multiple-choice question has {choices} options. If a student guesses randomly on {k} questions, what is the probability of getting all {k} correct?",
    },
    {
        "type": "independent",
        "template": "Two fair dice are rolled. What is the probability both show an even number?",
    },
    {
        "type": "independent",
        "template": "A fair die is rolled twice. What is the probability of getting a {first} on the first roll and a {second} on the second roll?",
    },
    {
        "type": "independent",
        "template": "An archer hits the target with probability $\\frac{{{p}}}{{{q}}}$ per shot. What is the probability of hitting the target on {k} consecutive shots?",
    },
    # Dependent (without replacement)
    {
        "type": "dependent",
        "template": "A bag has {a} red and {b} blue marbles. Two are drawn without replacement. What is the probability both are red?",
    },
    {
        "type": "dependent",
        "template": "A bag has {a} red and {b} blue marbles. Two are drawn without replacement. What is the probability both are blue?",
    },
    {
        "type": "dependent",
        "template": "A class has {a} boys and {b} girls. Two students are chosen at random. What is the probability both are boys?",
    },
    {
        "type": "dependent",
        "template": "A class has {a} boys and {b} girls. Two students are chosen at random. What is the probability both are girls?",
    },
    {
        "type": "dependent",
        "template": "A box has {a} red and {b} green balls. Two are drawn without replacement. What is the probability both are red?",
    },
    {
        "type": "dependent",
        "template": "A jar has {a} strawberry and {b} lemon candies. Two are chosen without replacement. What is the probability both are strawberry?",
    },
    {
        "type": "dependent",
        "template": "A jar has {a} strawberry and {b} lemon candies. Two are chosen without replacement. What is the probability both are lemon?",
    },
    {
        "type": "dependent",
        "template": "A jar has {a} pennies and {b} dimes. Two coins are drawn without replacement. What is the probability both are pennies?",
    },
    {
        "type": "dependent",
        "template": "A drawer has {a} black and {b} white socks. Two are drawn without replacement. What is the probability both are black?",
    },
    {
        "type": "dependent",
        "template": "A batch of {total} items has {a} defective ones. Two are selected without replacement. What is the probability both are defective?",
    },
    {
        "type": "dependent",
        "template": "A basket has {a} apples and {b} oranges. Two fruits are picked without replacement. What is the probability both are apples?",
    },
    {
        "type": "dependent",
        "template": "A bag has {a} red, {b} blue, and {c} green marbles. Two are drawn without replacement. What is the probability both are red?",
    },
    {
        "type": "dependent",
        "template": "Two tickets are drawn from a raffle with {a} winning and {b} losing tickets. What is the probability both are winning tickets?",
    },
    {
        "type": "dependent",
        "template": "Two cards are drawn without replacement from a standard 52-card deck. What is the probability both are hearts?",
    },
    {
        "type": "dependent",
        "template": "A box has {a} red and {b} yellow beads. Two beads are drawn without replacement. What is the probability both are red?",
    },
    {
        "type": "dependent",
        "template": "Two cards are drawn without replacement from a standard 52-card deck. What is the probability both are face cards?",
    },
]


# ---------------------------------------------------------------------------
# Parameter range helpers
# ---------------------------------------------------------------------------


def counting_principle_choices(
    rng: random.Random,
    stages: int,
    difficulty: str,
) -> list[int]:
    """Return a list of choices-per-stage for the counting principle."""
    if difficulty == "easy":
        return [rng.randint(3, 8) for _ in range(stages)]
    # medium
    return [rng.randint(3, 9) for _ in range(stages)]


def factorial_n(rng: random.Random, difficulty: str) -> int:
    """Return n for factorial computation."""
    if difficulty == "easy":
        return rng.randint(3, 7)
    # medium: used for n!/k! simplification
    return rng.randint(6, 12)


def perm_params(
    rng: random.Random,
    difficulty: str,
) -> tuple[int, int]:
    """Return (n, r) for permutation problems."""
    if difficulty == "easy":
        n = rng.randint(4, 7)
        r = rng.randint(2, min(3, n - 1))
    elif difficulty == "medium":
        n = rng.randint(7, 12)
        r = rng.randint(3, min(5, n - 1))
    else:  # hard
        n = rng.randint(8, 15)
        r = rng.randint(4, min(6, n - 1))
    return n, r


def comb_params(
    rng: random.Random,
    difficulty: str,
) -> tuple[int, int]:
    """Return (n, r) for combination problems."""
    if difficulty == "easy":
        n = rng.randint(4, 8)
        r = rng.randint(2, min(3, n - 1))
    elif difficulty == "medium":
        n = rng.randint(8, 15)
        r = rng.randint(3, min(5, n - 1))
    else:  # hard
        n = rng.randint(10, 20)
        r = rng.randint(4, min(7, n - 1))
    return n, r
