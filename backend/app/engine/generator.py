from __future__ import annotations

import logging
import random

from app.engine.registry import TemplateRegistry
from app.engine.types import GeneratedProblem, GenerationConfig, GenerationError

logger = logging.getLogger(__name__)

MAX_RETRIES_PER_TEMPLATE = 3
MAX_RETRIES_PER_SLOT = 20  # try different templates before giving up on a slot


def generate_test(config: GenerationConfig, registry: TemplateRegistry) -> list[GeneratedProblem]:
    rng = random.Random(config.seed)

    # Collect eligible templates, filtered by subtopic if specified
    topic_templates: dict = {}
    for topic in config.topics:
        if config.subtopics and topic in config.subtopics:
            templates = []
            for sub in config.subtopics[topic]:
                found = registry.get_templates_for_subtopic(topic, sub, config.difficulty)
                templates.extend(found)
        else:
            templates = registry.get_templates(topic, config.difficulty)
        if templates:
            topic_templates[topic] = templates

    if not topic_templates:
        raise GenerationError(
            f"No templates available for topics={config.topics}, difficulty={config.difficulty}"
        )

    # Distribute questions across topics (round-robin)
    topics_cycle = list(topic_templates.keys())
    assignments = [topics_cycle[i % len(topics_cycle)] for i in range(config.count)]
    rng.shuffle(assignments)

    seen: set[str] = set()  # Track unique question_latex strings

    problems: list[GeneratedProblem] = []
    for topic in assignments:
        problem = _generate_for_slot(topic_templates[topic], config.difficulty, rng, seen)
        if problem:
            seen.add(str(problem.question_latex))
            problems.append(problem)
        else:
            logger.warning(
                "Could not generate problem for topic=%s after %d attempts",
                topic,
                MAX_RETRIES_PER_SLOT,
            )

    if len(problems) < config.count:
        logger.warning(
            "Generated %d of %d requested problems (some slots failed)",
            len(problems),
            config.count,
        )

    if not problems:
        raise GenerationError("Failed to generate any problems")

    rng.shuffle(problems)
    return problems


def _generate_for_slot(
    templates: list,
    difficulty,
    rng: random.Random,
    seen: set[str],
) -> GeneratedProblem | None:
    """Try multiple templates to fill one question slot with a unique question.

    Picks random templates and retries when a duplicate is detected.
    The RNG advances on each ``_try_template`` call, so retries naturally
    produce different parameters.  After exhausting random attempts the
    function does a deterministic sweep of every template before giving up.
    """
    for _ in range(MAX_RETRIES_PER_SLOT):
        template = rng.choice(templates)
        result = _try_template(template, difficulty, rng)

        if result and str(result.question_latex) not in seen:
            return result  # Unique question found

        # Either failed (exception) or duplicate — RNG already advanced, retry

    return None


def _try_template(template, difficulty, rng: random.Random) -> GeneratedProblem | None:
    """Try a single template once. Log failure at WARNING on exception."""
    try:
        problem = template.generate(difficulty, rng)
        if problem.question_latex and problem.answer_latex:
            return problem
        logger.debug("Empty output from %s", template.subtopic)
    except Exception:
        logger.warning(
            "Template %s failed at %s difficulty",
            template.subtopic,
            difficulty,
            exc_info=True,
        )
    return None
