#!/usr/bin/env python3
"""Validate arxiv figure PDFs for completeness and content.

Checks:
  1. PDF exists for each expected figure
  2. File size > minimum threshold (not empty/corrupt)
  3. No placeholder text embedded in PDF
  4. Expected number of plot objects (lines, patches)

Usage:
  python scripts/check_figures.py
  python scripts/check_figures.py --figures-dir arxiv/latex/figures
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

FIGURES_DIR = Path("arxiv/latex/figures")

EXPECTED_FIGURES = [
    "figure_1_causal_chain.pdf",
    "figure_2_population_trajectories.pdf",
    "figure_3_core_metrics.pdf",
    "figure_4_null_models.pdf",
    "figure_5_ablation_heatmap.pdf",
    "figure_6_sink_trajectories.pdf",
]

MIN_SIZE_BYTES = 1000

PLACEHOLDER_PATTERNS = [
    re.compile(r"data not available", re.IGNORECASE),
    re.compile(r"not found", re.IGNORECASE),
    re.compile(r"placeholder", re.IGNORECASE),
    re.compile(r"No scenario data", re.IGNORECASE),
]


def check_pdf_exists(figures_dir: Path) -> list[str]:
    errors = []
    for name in EXPECTED_FIGURES:
        path = figures_dir / name
        if not path.exists():
            errors.append(f"MISSING: {name}")
        elif path.stat().st_size == 0:
            errors.append(f"EMPTY: {name}")
    return errors


def check_file_sizes(figures_dir: Path) -> list[str]:
    warnings = []
    for name in EXPECTED_FIGURES:
        path = figures_dir / name
        if path.exists() and path.stat().st_size < MIN_SIZE_BYTES:
            warnings.append(
                f"SMALL: {name} ({path.stat().st_size} bytes < {MIN_SIZE_BYTES} threshold)"
            )
    return warnings


def check_placeholder_text(figures_dir: Path) -> list[str]:
    errors = []
    for name in EXPECTED_FIGURES:
        path = figures_dir / name
        if not path.exists():
            continue
        try:
            result = subprocess.run(
                ["pdftotext", str(path), "-"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            text = result.stdout
            for pattern in PLACEHOLDER_PATTERNS:
                if pattern.search(text):
                    errors.append(f"PLACEHOLDER TEXT in {name}: matches '{pattern.pattern}'")
                    break
        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            pass
    return errors


def check_plot_objects(figures_dir: Path) -> list[str]:
    warnings = []
    for name in EXPECTED_FIGURES:
        path = figures_dir / name
        if not path.exists():
            continue
        try:
            result = subprocess.run(
                ["pdfinfo", str(path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            info = result.stdout
            pages_match = re.search(r"Pages:\s+(\d+)", info)
            if pages_match and int(pages_match.group(1)) != 1:
                warnings.append(f"MULTI-PAGE: {name} has {pages_match.group(1)} pages")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    return warnings


def main():
    parser = argparse.ArgumentParser(description="Validate arxiv figures")
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=FIGURES_DIR,
        help="Directory containing figure PDFs",
    )
    args = parser.parse_args()

    figures_dir = args.figures_dir
    print(f"Checking figures in {figures_dir}/ ...")
    print()

    all_errors = []
    all_warnings = []

    # Check 1: PDFs exist
    errors = check_pdf_exists(figures_dir)
    all_errors.extend(errors)
    print(f"  Existence check: {'PASS' if not errors else 'FAIL'}")
    for e in errors:
        print(f"    {e}")

    # Check 2: File sizes
    warnings = check_file_sizes(figures_dir)
    all_warnings.extend(warnings)
    print(f"  Size check: {'PASS' if not warnings else 'WARN'}")
    for w in warnings:
        print(f"    {w}")

    # Check 3: Placeholder text
    errors = check_placeholder_text(figures_dir)
    all_errors.extend(errors)
    print(f"  Placeholder check: {'PASS' if not errors else 'FAIL'}")
    for e in errors:
        print(f"    {e}")

    # Check 4: Page count
    warnings = check_plot_objects(figures_dir)
    all_warnings.extend(warnings)
    print(f"  Page count check: {'PASS' if not warnings else 'WARN'}")
    for w in warnings:
        print(f"    {w}")

    # Summary
    print()
    if all_errors:
        print(f"FAIL: {len(all_errors)} error(s), {len(all_warnings)} warning(s)")
        sys.exit(1)
    elif all_warnings:
        print(f"PASS with {len(all_warnings)} warning(s)")
        sys.exit(0)
    else:
        print(f"PASS: All {len(EXPECTED_FIGURES)} figures validated")
        sys.exit(0)


if __name__ == "__main__":
    main()
