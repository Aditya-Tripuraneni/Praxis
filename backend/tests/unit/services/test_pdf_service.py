"""Unit tests for PDF service — _latex_escape, _get helper, and fallback renderer."""

from unittest.mock import patch

from app.services.pdf_service import PdfService, _get, _latex_escape


class TestLatexEscape:
    def test_escapes_underscore(self):
        assert _latex_escape("domain_rational") == r"domain\_rational"

    def test_escapes_ampersand(self):
        assert _latex_escape("A & B") == r"A \& B"

    def test_escapes_percent(self):
        assert _latex_escape("100%") == r"100\%"

    def test_escapes_hash(self):
        assert _latex_escape("#1") == r"\#1"

    def test_escapes_dollar(self):
        assert _latex_escape("$5") == r"\$5"

    def test_escapes_braces(self):
        assert _latex_escape("{x}") == r"\{x\}"

    def test_escapes_tilde(self):
        assert "textasciitilde" in _latex_escape("~")

    def test_escapes_caret(self):
        assert "textasciicircum" in _latex_escape("^")

    def test_passthrough_normal_text(self):
        assert _latex_escape("Hello World 123") == "Hello World 123"

    def test_compound_escaping(self):
        result = _latex_escape("domain_rational & 100%")
        assert r"\_" in result
        assert r"\&" in result
        assert r"\%" in result

    def test_empty_string(self):
        assert _latex_escape("") == ""


class TestGetHelper:
    def test_dict_access(self):
        assert _get({"a": 1}, "a") == 1

    def test_dict_default(self):
        assert _get({}, "missing", "default") == "default"

    def test_object_access(self):
        class Obj:
            x = 42

        assert _get(Obj(), "x") == 42

    def test_object_default(self):
        class Obj:
            pass

        assert _get(Obj(), "missing", "fallback") == "fallback"


class TestPdfFallback:
    @patch("app.services.pdf_service._tectonic_available", return_value=False)
    def test_fallback_produces_valid_pdf(self, _mock):
        service = PdfService()
        questions = [
            {"question_latex": "Solve $x + 1 = 2$.", "answer_latex": "$x = 1$"},
        ]
        config = {"topics": ["algebra"], "difficulty": "easy", "count": 1}
        buf = service.generate(questions, config, "test123", include_answers=True)
        content = buf.read()
        assert content[:4] == b"%PDF", "Fallback did not produce valid PDF"
        assert len(content) > 100

    @patch("app.services.pdf_service._tectonic_available", return_value=False)
    def test_fallback_without_answers(self, _mock):
        service = PdfService()
        questions = [
            {"question_latex": "Solve $2x = 4$.", "answer_latex": "$x = 2$"},
        ]
        config = {"topics": ["algebra"], "difficulty": "easy", "count": 1}
        buf = service.generate(questions, config, "test456", include_answers=False)
        content = buf.read()
        assert content[:4] == b"%PDF"
