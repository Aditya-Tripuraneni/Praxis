#!/usr/bin/env python3
"""Benchmark PDF generation pipeline — temporary script for performance analysis.

Run from the backend directory with the backend venv activated:
    export PATH="$HOME/.local/bin:$PATH"
    .venv/bin/python benchmark_pdf.py

Measures:
  1. Question generation (engine)
  2. Jinja2 LaTeX template rendering
  3. Tectonic compilation (subprocess)
  4. Total end-to-end
"""

from __future__ import annotations

import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

# ── Bootstrap imports ────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))

import app.engine.topics  # noqa: F401,E402 — triggers template registration
from app.engine import Difficulty, GenerationConfig, Topic, generate_test, registry  # noqa: E402
from app.services.pdf_service import _jinja_env  # noqa: E402

ITERATIONS = 3
QUESTION_COUNT = 10
TOPICS = [Topic.ALGEBRA]
DIFFICULTY = Difficulty.MEDIUM
SEED = 42


def _get(obj, attr: str, default=""):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def benchmark_once(iteration: int) -> dict[str, float]:
    """Run one full pipeline and return step timings in seconds."""
    timings: dict[str, float] = {}

    config = GenerationConfig(
        topics=TOPICS,
        difficulty=DIFFICULTY,
        count=QUESTION_COUNT,
        seed=SEED + iteration,  # vary seed to avoid any weird caching artifacts
    )

    # ── Step 1: Question generation ──────────────────────────────────
    t0 = time.perf_counter()
    problems = generate_test(config, registry)
    t1 = time.perf_counter()
    timings["question_generation"] = t1 - t0

    questions = [
        {
            "question_latex": p.question_latex,
            "answer_latex": p.answer_latex,
        }
        for p in problems
    ]

    # ── Step 2: Jinja2 template rendering ────────────────────────────
    t2 = time.perf_counter()
    template = _jinja_env.get_template("test.tex.j2")
    tex_source = template.render(
        date=date.today().isoformat(),
        test_id="bench00001",
        topics=", ".join(t.value for t in TOPICS),
        difficulty=DIFFICULTY.value,
        count=QUESTION_COUNT,
        questions=questions,
        include_answers=True,
    )
    t3 = time.perf_counter()
    timings["template_rendering"] = t3 - t2

    # ── Step 3: Tectonic compilation ─────────────────────────────────
    if not shutil.which("tectonic"):
        print(
            "ERROR: tectonic not found on PATH. Did you 'export PATH=\"$HOME/.local/bin:$PATH\"'?"
        )
        sys.exit(1)

    t4 = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "test.tex"
        pdf_path = Path(tmpdir) / "test.pdf"
        tex_path.write_text(tex_source, encoding="utf-8")

        result = subprocess.run(
            ["tectonic", str(tex_path)],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        t5 = time.perf_counter()

        if result.returncode != 0:
            print(f"Tectonic failed (iteration {iteration}):")
            print(result.stderr[:1000])
            sys.exit(1)

        pdf_size = pdf_path.stat().st_size

    timings["tectonic_compilation"] = t5 - t4

    # ── Total ────────────────────────────────────────────────────────
    timings["total"] = (
        timings["question_generation"]
        + timings["template_rendering"]
        + timings["tectonic_compilation"]
    )
    timings["pdf_size_kb"] = pdf_size / 1024

    return timings


def main() -> None:
    print("=" * 70)
    print("ProblemGenerator PDF Pipeline Benchmark")
    print(f"  Questions: {QUESTION_COUNT}  |  Topics: {[t.value for t in TOPICS]}")
    print(f"  Difficulty: {DIFFICULTY.value}  |  Iterations: {ITERATIONS}")
    print("=" * 70)
    print()

    # ── Pre-warm: first invocation may download Tectonic packages ────
    print("Pre-warm run (not counted)...")
    pw_start = time.perf_counter()
    prewarm = benchmark_once(-1)
    pw_end = time.perf_counter()
    print(
        f"  Pre-warm total: {pw_end - pw_start:.3f}s  "
        f"(tectonic: {prewarm['tectonic_compilation']:.3f}s)"
    )
    print()

    # ── Measured runs ────────────────────────────────────────────────
    all_timings: list[dict[str, float]] = []
    for i in range(ITERATIONS):
        print(f"Run {i + 1}/{ITERATIONS}...", end=" ", flush=True)
        t = benchmark_once(i)
        all_timings.append(t)
        print(
            f"total={t['total']:.3f}s  (gen={t['question_generation']:.3f}s  "
            f"tmpl={t['template_rendering']:.3f}s  tectonic={t['tectonic_compilation']:.3f}s)"
        )

    # ── Averages ─────────────────────────────────────────────────────
    print()
    print("-" * 70)
    print("AVERAGES (over {0} runs):".format(ITERATIONS))
    print("-" * 70)

    steps = ["question_generation", "template_rendering", "tectonic_compilation", "total"]
    avgs: dict[str, float] = {}
    stds: dict[str, float] = {}
    for step in steps:
        vals = [t[step] for t in all_timings]
        avgs[step] = statistics.mean(vals)
        stds[step] = statistics.stdev(vals) if len(vals) > 1 else 0.0

    total_avg = avgs["total"]
    for step in steps:
        pct = (avgs[step] / total_avg * 100) if total_avg > 0 else 0
        marker = " <-- BOTTLENECK" if step != "total" and pct > 50 else ""
        print(f"  {step:25s}  {avgs[step]:8.4f}s  (+/- {stds[step]:.4f}s)  {pct:5.1f}%{marker}")

    avg_pdf_kb = statistics.mean(t["pdf_size_kb"] for t in all_timings)
    print(f"\n  PDF size: {avg_pdf_kb:.1f} KB")

    # ── Cold vs. warm comparison ─────────────────────────────────────
    print()
    print("-" * 70)
    print("COLD vs. WARM Tectonic comparison:")
    print("-" * 70)
    print(f"  Pre-warm (cold or cached): {prewarm['tectonic_compilation']:.3f}s")
    print(f"  Average warm:              {avgs['tectonic_compilation']:.3f}s")
    diff = prewarm["tectonic_compilation"] - avgs["tectonic_compilation"]
    if diff > 0.5:
        print(f"  --> First run is {diff:.2f}s slower (likely package download/caching)")
    else:
        print(f"  --> Difference is {diff:.2f}s (packages already cached)")

    print()
    print("=" * 70)
    print("Done. Delete this file when finished: benchmark_pdf.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
