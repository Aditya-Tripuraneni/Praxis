"""Render LaTeX math strings to PNG images using matplotlib's mathtext.

Matplotlib natively handles mixed text and $...$ inline math. We pass
the string as-is and let matplotlib render both text and math together.
"""

from __future__ import annotations

import functools
import io
import logging

import matplotlib
import matplotlib.figure

matplotlib.use("Agg")

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=512)
def render_latex_to_image(
    latex_str: str,
    font_size: int = 14,
    dpi: int = 150,
) -> bytes:
    """Render a string (possibly containing $...$ math) to PNG bytes.

    Matplotlib's text renderer handles inline $...$ math natively.
    If the string has no $ delimiters, we wrap it in $...$ assuming pure math.
    """
    text = latex_str.strip()

    # If the string has $ delimiters, pass as-is (mixed text + math)
    # If not, assume it's pure math and wrap in $...$
    if "$" not in text:
        text = f"${text}$"

    try:
        return _render(text, font_size, dpi)
    except Exception:
        logger.debug("Render failed for %r, trying plain text", text[:80], exc_info=True)
        # Strip all $ and render as plain text
        plain = text.replace("$", "")
        return _render_plain(plain, font_size, dpi)


def _render(text: str, font_size: int, dpi: int) -> bytes:
    fig = matplotlib.figure.Figure()
    fig.patch.set_alpha(0.0)
    fig.text(
        0.0,
        0.5,
        text,
        fontsize=font_size,
        verticalalignment="center",
        horizontalalignment="left",
    )
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.05, transparent=True)
    buf.seek(0)
    return buf.read()


def _render_plain(text: str, font_size: int, dpi: int) -> bytes:
    fig = matplotlib.figure.Figure()
    fig.patch.set_alpha(0.0)
    fig.text(
        0.0,
        0.5,
        text,
        fontsize=font_size,
        verticalalignment="center",
        horizontalalignment="left",
        family="monospace",
    )
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.05, transparent=True)
    buf.seek(0)
    return buf.read()
