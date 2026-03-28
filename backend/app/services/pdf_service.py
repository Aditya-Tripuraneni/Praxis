"""Generate practice test PDFs.

Primary: Tectonic (LaTeX compiler) for textbook-quality output.
Fallback: matplotlib + ReportLab if Tectonic is not installed.
"""

from __future__ import annotations

import io
import logging
import os
import shutil
import subprocess
import tempfile
import time
from datetime import date
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_MM_TO_PT = 72.0 / 25.4
_QUESTION_WRITE_SPACE_MM = 16.0
_QUESTION_WRITE_SPACE_PT = int(round(_QUESTION_WRITE_SPACE_MM * _MM_TO_PT))
_QUESTION_BLOCK_NEEDSPACE_LINES = 8

# Characters that must be escaped in LaTeX text mode
_LATEX_SPECIAL = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _latex_escape(text: str) -> str:
    """Escape LaTeX special characters in plain text strings."""
    for char, replacement in _LATEX_SPECIAL.items():
        text = text.replace(char, replacement)
    return text


_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    block_start_string="<%",
    block_end_string="%>",
    variable_start_string="<<",
    variable_end_string=">>",
    comment_start_string="<#",
    comment_end_string="#>",
)
_jinja_env.filters["latex_escape"] = _latex_escape


def _tectonic_available() -> bool:
    return shutil.which("tectonic") is not None


def _get(obj, attr: str, default=""):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


class PdfService:
    def generate(
        self,
        questions: list[dict[str, Any]],
        config: dict[str, Any],
        test_id: str,
        include_answers: bool = True,
        include_solutions: bool = False,
        include_topics: bool = False,
    ) -> io.BytesIO:
        if _tectonic_available():
            return self._generate_tectonic(
                questions,
                config,
                test_id,
                include_answers,
                include_solutions,
                include_topics,
            )
        logger.warning("Tectonic not found, using matplotlib fallback")
        return self._generate_fallback(
            questions,
            config,
            test_id,
            include_answers,
            include_solutions,
            include_topics,
        )

    def _generate_tectonic(
        self,
        questions: list[dict[str, Any]],
        config: dict[str, Any],
        test_id: str,
        include_answers: bool,
        include_solutions: bool,
        include_topics: bool,
    ) -> io.BytesIO:
        t0 = time.perf_counter()

        template = _jinja_env.get_template("test.tex.j2")
        tex_source = template.render(
            date=date.today().isoformat(),
            test_id=test_id,
            topics=", ".join(t.replace("_", " ").title() for t in config.get("topics", [])),
            difficulty=str(config.get("difficulty", "")),
            count=config.get("count", len(questions)),
            question_write_space_pt=_QUESTION_WRITE_SPACE_PT,
            question_block_needspace_lines=_QUESTION_BLOCK_NEEDSPACE_LINES,
            questions=[
                {
                    "question_latex": _get(q, "question_latex", ""),
                    "answer_latex": _get(q, "answer_latex", ""),
                    "solution_steps": _get(q, "solution_steps", []),
                }
                for q in questions
            ],
            include_answers=include_answers,
            include_solutions=include_solutions,
            include_topics=include_topics,
        )
        t1 = time.perf_counter()

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "test.tex"
            pdf_path = Path(tmpdir) / "test.pdf"
            tex_path.write_text(tex_source, encoding="utf-8")

            # Shell escape disabled as defense-in-depth against LaTeX injection.
            # Even if malicious LaTeX reaches Tectonic, \write18 cannot execute.
            safe_env = {**os.environ, "TECTONIC_SHELL_ESCAPE": "0"}
            result = subprocess.run(
                ["tectonic", str(tex_path)],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=30,
                env=safe_env,
            )
            t2 = time.perf_counter()

            if result.returncode != 0:
                logger.error("Tectonic failed: %s", result.stderr)
                raise RuntimeError(f"LaTeX compilation failed: {result.stderr[:500]}")

            buf = io.BytesIO(pdf_path.read_bytes())
            buf.seek(0)

        logger.info(
            "pdf test_id=%s template=%.0fms tectonic=%.0fms total=%.0fms",
            test_id,
            (t1 - t0) * 1000,
            (t2 - t1) * 1000,
            (t2 - t0) * 1000,
        )
        return buf

    def _generate_fallback(
        self,
        questions: list[dict[str, Any]],
        config: dict[str, Any],
        test_id: str,
        include_answers: bool,
        include_solutions: bool,
        include_topics: bool,
    ) -> io.BytesIO:
        """matplotlib + ReportLab fallback when Tectonic is unavailable."""
        from PIL import Image as PILImage
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Image,
            KeepTogether,
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        )

        from app.services.latex_renderer import render_latex_to_image

        def _latex_image(latex_str: str) -> Image:
            png_bytes = render_latex_to_image(latex_str, font_size=14, dpi=150)
            img = PILImage.open(io.BytesIO(png_bytes))
            w_px, h_px = img.size
            w_pt = w_px * 72.0 / 150
            h_pt = h_px * 72.0 / 150
            max_w = 6.0 * inch
            if w_pt > max_w:
                scale = max_w / w_pt
                w_pt *= scale
                h_pt *= scale
            return Image(io.BytesIO(png_bytes), width=w_pt, height=h_pt)

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch
        )
        styles = getSampleStyleSheet()
        story: list = []

        story.append(Paragraph("Math Practice Test", styles["Title"]))
        story.append(Spacer(1, 6))
        info = ParagraphStyle("Info", parent=styles["Normal"], fontSize=10, textColor="#555")
        topics_str = ", ".join(str(t) for t in config.get("topics", []))
        diff = config.get("difficulty", "")
        cnt = config.get("count", len(questions))
        story.append(Paragraph(f"Date: {date.today().isoformat()} | Test ID: {test_id}", info))
        story.append(
            Paragraph(f"Topics: {topics_str} | Difficulty: {diff} | Questions: {cnt}", info)
        )
        story.append(Spacer(1, 18))
        story.append(Paragraph("Questions", styles["Heading2"]))
        story.append(Spacer(1, 8))

        qlabel = ParagraphStyle("QL", parent=styles["Normal"], fontSize=11, spaceAfter=2)
        for idx, q in enumerate(questions, 1):
            story.append(
                KeepTogether(
                    [
                        Paragraph(f"<b>Q{idx}.</b>", qlabel),
                        _latex_image(_get(q, "question_latex", "")),
                        Spacer(1, _QUESTION_WRITE_SPACE_PT),
                    ]
                )
            )

        if include_answers:
            story.append(PageBreak())
            story.append(Paragraph("Answer Key", styles["Title"]))
            story.append(Spacer(1, 12))
            for idx, q in enumerate(questions, 1):
                story.append(Paragraph(f"<b>A{idx}.</b>", qlabel))
                story.append(_latex_image(_get(q, "answer_latex", "")))
                story.append(Spacer(1, 10))

        if include_solutions:
            story.append(PageBreak())
            story.append(Paragraph("Worked Solutions", styles["Title"]))
            story.append(Spacer(1, 12))
            for idx, q in enumerate(questions, 1):
                story.append(Paragraph(f"<b>S{idx}.</b>", qlabel))
                steps = _get(q, "solution_steps", [])
                if steps:
                    for step_num, step in enumerate(steps, 1):
                        story.append(Paragraph(f"<b>Step {step_num}:</b>", qlabel))
                        story.append(_latex_image(step))
                        story.append(Spacer(1, 4))
                else:
                    story.append(_latex_image(_get(q, "answer_latex", "")))
                story.append(Spacer(1, 10))

        if include_topics:
            story.append(Spacer(1, 18))
            story.append(Paragraph("Topics", styles["Heading3"]))
            story.append(Spacer(1, 4))
            story.append(Paragraph(topics_str, info))

        def _page_num(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 9)
            canvas.drawCentredString(doc.pagesize[0] / 2, 0.5 * inch, f"Page {doc.page}")
            canvas.restoreState()

        doc.build(story, onFirstPage=_page_num, onLaterPages=_page_num)
        buf.seek(0)
        return buf
