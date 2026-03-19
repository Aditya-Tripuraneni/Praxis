"""Unit tests for LaTeX-to-image renderer."""

from app.services.latex_renderer import render_latex_to_image


class TestRenderLatexToImage:
    def test_renders_simple_math(self):
        result = render_latex_to_image("$x^2 + 1$")
        assert isinstance(result, bytes)
        assert len(result) > 100
        assert result[:4] == b"\x89PNG"

    def test_renders_mixed_text_and_math(self):
        result = render_latex_to_image("Find $f(x) = x^2$.")
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_renders_pure_text_without_dollars(self):
        """String without $ wraps in $...$ automatically."""
        result = render_latex_to_image("x + 1")
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_fallback_on_invalid_latex(self):
        """Invalid LaTeX falls back to plain text, doesn't crash."""
        result = render_latex_to_image("$\\invalidcommand{broken}$")
        assert isinstance(result, bytes)
        assert len(result) > 50

    def test_caching(self):
        """Same input returns cached result (same object, not just equal)."""
        r1 = render_latex_to_image("$x$", font_size=14, dpi=150)
        r2 = render_latex_to_image("$x$", font_size=14, dpi=150)
        assert r1 is r2

    def test_empty_string(self):
        result = render_latex_to_image("")
        assert isinstance(result, bytes)
