"""Topic template modules.

Importing this package triggers template registration via @register_template decorators.
"""

import app.engine.topics.algebra as algebra  # noqa: F401 — auto-registers templates
import app.engine.topics.calculus as calculus  # noqa: F401
import app.engine.topics.combinatorics as combinatorics  # noqa: F401
import app.engine.topics.domain as domain  # noqa: F401
import app.engine.topics.functions as functions  # noqa: F401
import app.engine.topics.geometry as geometry  # noqa: F401
import app.engine.topics.trigonometry as trigonometry  # noqa: F401
