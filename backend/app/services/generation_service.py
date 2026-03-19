"""Service layer for math test generation.

Orchestrates the engine, manages caching, and formats data for the API.
Display-name mapping lives here (not in the engine) — the engine returns
raw identifiers, this service adds presentation details.
"""

from __future__ import annotations

import random as _random
import threading
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from cachetools import TTLCache

import app.engine.topics  # noqa: F401 — triggers template registration
from app.engine import Difficulty, GenerationConfig, Topic, generate_test, registry
from app.engine.constants import SUBTOPIC_DISPLAY_NAMES
from app.models.test import (
    GenerateRequest,
    QuestionResponse,
    SubtopicInfo,
    TestResponse,
    TopicInfo,
)

# Tests expire after 30 minutes, max 100 cached
_CACHE_MAX = 100
_CACHE_TTL = 1800  # seconds

# Track test ownership: test_id -> user_id (same TTL as test cache)
_test_owners: TTLCache[str, str] = TTLCache(maxsize=_CACHE_MAX, ttl=_CACHE_TTL)


def _parse_topic_selections(
    raw_topics: list[str],
) -> tuple[list[Topic], dict[Topic, list[str]] | None]:
    """Parse dot-notation topic selections into topics list + subtopic filter.

    "algebra" → all algebra subtopics
    "algebra.linear_equations" → only linear_equations from algebra

    Returns (topics, subtopics_filter) where subtopics_filter is None
    if all entries are bare topic names (backward compatible).
    """
    topics_set: set[Topic] = set()
    subtopic_map: dict[Topic, list[str]] = defaultdict(list)
    has_specific = False

    for entry in raw_topics:
        if "." in entry:
            topic_str, subtopic = entry.split(".", 1)
            topic = Topic(topic_str)
            topics_set.add(topic)
            subtopic_map[topic].append(subtopic)
            has_specific = True
        else:
            topic = Topic(entry)
            topics_set.add(topic)

    topics = sorted(topics_set, key=lambda t: t.value)

    if not has_specific:
        return topics, None

    result: dict[Topic, list[str]] = {}
    for topic in topics:
        if topic in subtopic_map:
            result[topic] = subtopic_map[topic]

    return topics, result if result else None


def _display_name(subtopic_id: str) -> str:
    """Map a subtopic ID to its display name. Fallback: title-case the ID."""
    return SUBTOPIC_DISPLAY_NAMES.get(subtopic_id, subtopic_id.replace("_", " ").title())


class GenerationService:
    def __init__(self):
        self._cache: TTLCache[str, TestResponse] = TTLCache(maxsize=_CACHE_MAX, ttl=_CACHE_TTL)
        self._lock = threading.Lock()

    def generate(self, request: GenerateRequest, user_id: str = "") -> TestResponse:
        # Always assign a concrete seed for reproducibility (needed for saved tests)
        actual_seed = request.seed if request.seed is not None else _random.randint(0, 2**31 - 1)

        topics, subtopics = _parse_topic_selections(request.topics)
        difficulty = Difficulty(request.difficulty)

        config = GenerationConfig(
            topics=topics,
            difficulty=difficulty,
            count=request.count,
            seed=actual_seed,
            subtopics=subtopics,
        )

        problems = generate_test(config, registry)

        questions = [
            QuestionResponse(
                id=i + 1,
                question_latex=p.question_latex.value,
                answer_latex=p.answer_latex.value,
                topic=p.topic.value,
                difficulty=p.difficulty.value,
                subtopic=p.subtopic,
                solution_steps=[s.value for s in p.solution_steps],
            )
            for i, p in enumerate(problems)
        ]

        test_id = uuid.uuid4().hex[:12]
        response = TestResponse(
            test_id=test_id,
            questions=questions,
            created_at=datetime.now(timezone.utc),
            config=GenerateRequest(
                topics=request.topics,
                difficulty=request.difficulty,
                count=request.count,
                seed=actual_seed,
            ),
        )

        self._store(test_id, response)
        if user_id:
            _test_owners[test_id] = user_id
        return response

    def get_test(self, test_id: str) -> TestResponse | None:
        with self._lock:
            return self._cache.get(test_id)

    def get_test_for_user(self, test_id: str, user_id: str) -> TestResponse | None:
        """Get a test by ID, verifying ownership.

        Returns None (not 403) if the test is not found or not owned by
        the requesting user, preventing existence-leakage.
        """
        result = self.get_test(test_id)
        if result is None:
            return None
        owner = _test_owners.get(test_id)
        if owner and owner != user_id:
            return None
        return result

    def get_topics(self) -> list[TopicInfo]:
        """Build topic info with display names. Registry provides raw data,
        this method adds the presentation layer."""
        result = []
        for topic in registry.get_all_topics():
            data = registry.get_topic_data(topic)
            subtopics = [
                SubtopicInfo(id=sid, name=_display_name(sid)) for sid in data["subtopic_ids"]
            ]
            result.append(
                TopicInfo(
                    id=data["topic"],
                    name=data["topic"].title(),
                    subtopics=subtopics,
                    difficulties=data["difficulties"],
                    template_count=data["template_count"],
                )
            )
        return result

    def _store(self, test_id: str, response: TestResponse) -> None:
        with self._lock:
            self._cache[test_id] = response


generation_service = GenerationService()
