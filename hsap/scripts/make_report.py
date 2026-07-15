#!/usr/bin/env python3
"""Generate a comprehensive paper-format report from saved results."""

import json
import subprocess
from pathlib import Path


def load_json(path):
    with open(path) as f:
        return json.load(f)


def fmt_mean_ci(mean, std, n, decimals=2):
    se = std / max((n ** 0.5), 1)
    ci = 1.96 * se
    return f"{mean:.{decimals}f} \u00b1 {ci:.{decimals}f}"


def section(title, level=2):
    return f"\n{'#' * level} {title}\n\n"


def main():
    results_dir = Path("results")
    paper_dir = results_dir / "paper"
    report_path = results_dir / "report.md"

    lines = ["# HSAP Simulation Report\n"]
    lines.append(
        "> Generated for arXiv submission. "
        "Multi-seed aggregate statistics reported throughout. "
        "No single-seed values used as primary evidence.\n"
    )

    # ── Git info ──
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        lines.append(f"- **Git commit**: `{commit}`\n")
    except Exception:
        lines.append("- **Git commit**: unknown\n")
    lines.append(f"- **Report generated**: see file modification time\n")

    # ── Paper manifest ──
    manifest_path = paper_dir / "paper_manifest.json"
    if manifest_path.exists():
        m = load_json(manifest_path)
        lines.append(section("Experiment Manifest"))
        for k, v in m.items():
            lines.append(f"- **{k}**: {v}\n")

    # ── Scenario definitions ──
    scenarios_path = paper_dir / "scenarios.json"
    if scenarios_path.exists():
        sc = load_json(scenarios_path)
        lines.append(section("Scenario Definitions"))
        for name, params in sc.items():
            env = params.get("environment", {})
            parts = [f"**{name}**"]
            for pk, pv in env.items():
                parts.append(f"{pk}={pv}")
            lines.append(f"- {'; '.join(parts)}\n")

    # ── Multi-seed scenario summary ──
    summary_path = paper_dir / "scenario_summary.csv"
    if summary_path.exists():
        import csv
        lines.append(section("Scenario Results (Multi-seed)"))
        with open(summary_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if rows:
            cols = list(rows[0].keys())
            header = "| " + " | ".join(cols) + " |\n"
            sep = "| " + " | ".join("---" for _ in cols) + " |\n"
            lines.append(header)
            lines.append(sep)
            for r in rows:
                lines.append("| " + " | ".join(r.get(c, "") for c in cols) + " |\n")
        lines.append("")

    # ── Per-scenario detail tables ──
    scenarios_dir = paper_dir / "scenarios"
    if scenarios_dir.exists():
        lines.append(section("Per-Scenario Detail"))
        for scenario_dir in sorted(scenarios_dir.iterdir()):
            if not scenario_dir.is_dir():
                continue
            name = scenario_dir.name
            summary_file = scenario_dir / "summary_by_seed.csv"
            if not summary_file.exists():
                continue
            import csv
            with open(summary_file) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if not rows:
                continue
            lines.append(f"### {name}\n")
            lines.append(f"Seeds: {len(rows)}\n")
            cols = list(rows[0].keys())
            header = "| " + " | ".join(cols) + " |\n"
            sep = "| " + " | ".join("---" for _ in cols) + " |\n"
            lines.append(header)
            lines.append(sep)
            for r in rows[:5]:
                lines.append("| " + " | ".join(r.get(c, "") for c in cols) + " |\n")
            if len(rows) > 5:
                lines.append(f"| _({len(rows) - 5} more rows)_ |\n")

    # ── Null model comparisons ──
    null_path = paper_dir / "null_ablation_results.json"
    if null_path.exists():
        null_data = load_json(null_path)
        lines.append(section("Null & Ablation Model Comparisons"))
        for scenario_name, models in null_data.items():
            lines.append(f"### {scenario_name}\n")
            header = "| Model |"
            sep = "|------|"
            # Collect all unique output keys
            all_outputs = set()
            for m_name, m_data in models.items():
                if isinstance(m_data, dict):
                    all_outputs.update(m_data.keys())
            sorted_outputs = sorted(all_outputs)
            for o in sorted_outputs:
                header += f" {o} MSE |"
                sep += "--------|"
            lines.append(header + "\n")
            lines.append(sep + "\n")
            for m_name, m_data in models.items():
                if not isinstance(m_data, dict):
                    continue
                row = f"| {m_name} |"
                for o in sorted_outputs:
                    val = m_data.get(o, {})
                    if isinstance(val, dict):
                        mse = val.get('mse')
                        if mse is not None and isinstance(mse, (int, float)):
                            row += f" {mse:>8.1f} |"
                        else:
                            row += f" {'N/A':>8} |"
                    elif isinstance(val, (int, float)):
                        row += f" {val:>8.1f} |"
                    else:
                        row += f" {str(val):>8} |"
                lines.append(row + "\n")

    # ── GA results ──
    ga_dir = paper_dir / "ga"
    if ga_dir.exists():
        lines.append(section("Genetic Algorithm Results"))
        ga_logs = ["support_log.csv", "falsification_log.csv", "best_individuals.csv"]
        for log_name in ga_logs:
            log_path = ga_dir / log_name
            if not log_path.exists():
                continue
            import csv
            lines.append(f"### {log_name.replace('_', ' ').replace('.csv', '')}\n")
            with open(log_path) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            if not rows:
                continue
            cols = list(rows[0].keys())
            header = "| " + " | ".join(cols) + " |\n"
            sep = "| " + " | ".join("---" for _ in cols) + " |\n"
            lines.append(header)
            lines.append(sep)
            for r in rows[:10]:
                lines.append("| " + " | ".join(r.get(c, "") for c in cols) + " |\n")
            lines.append("")

    # ── Sensitivity analysis ──
    sens_path = paper_dir / "sensitivity" / "sobol_table.csv"
    if sens_path.exists():
        import csv
        lines.append(section("Sensitivity Analysis"))
        with open(sens_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if rows:
            cols = list(rows[0].keys())
            header = "| " + " | ".join(cols) + " |\n"
            sep = "| " + " | ".join("---" for _ in cols) + " |\n"
            lines.append(header)
            lines.append(sep)
            for r in rows:
                lines.append("| " + " | ".join(r.get(c, "") for c in cols) + " |\n")

    # ── Equation reference ──
    eq_path = Path("paper/supplementary/model_equations.md")
    if eq_path.exists():
        lines.append(section("Model Equations"))
        lines.append(
            f"See [`paper/supplementary/model_equations.md`]({eq_path}) "
            f"for the full formal model specification.\n"
        )

    report_path.write_text("".join(lines))
    print(f"Report written to {report_path} ({report_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
