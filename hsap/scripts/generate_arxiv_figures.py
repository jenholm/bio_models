#!/usr/bin/env python3
"""Generate arxiv-quality figures from actual simulation data.

Produces figures for arxiv/latex/figures/:
  figure_1_causal_chain.pdf    - conceptual diagram (unchanged)
  figure_2_population_trajectories.pdf - shrunk, no embedded title
  figure_3_core_metrics.pdf    - no embedded title
  figure_4_null_models.pdf     - no embedded title
  figure_5_ablation_heatmap.pdf - no embedded title
  figure_6_sink_trajectories.pdf - no embedded title (only if sink data available)
  figure_8_sensitivity.pdf     - REMOVED from paper (no Sobol data)
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

DPI = 300

RESULTS_DIR = Path("results/paper")
FIGS_DIR = Path("arxiv/latex/figures")
ABLATION_CSV = Path("arxiv/data/generated_results/ablation_summary.csv")
NULL_ABLATION_JSON = RESULTS_DIR / "null_ablation_results.json"

SCENARIO_COLORS = {
    "A_normal_baseline": "#6a7090",
    "B_hsap_abundance": "#66bb6a",
    "C_crowded_abundance": "#ffb74d",
    "C_crowded_stable": "#4fc3f7",
    "D_high_predation_survival": "#ef5350",
    "E_behavioral_sink_recovery": "#ab47bc",
    "F_behavioral_sink_partial_collapse": "#d32f2f",
}

CORE_SCENARIOS = [
    "A_normal_baseline",
    "B_hsap_abundance",
    "C_crowded_abundance",
    "D_high_predation_survival",
]


plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7,
    "figure.dpi": DPI,
    "savefig.dpi": DPI,
    "savefig.bbox": "tight",
})


def fig1_causal_chain(out_path):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    nodes = {
        "Low Threat":                (1.5, 4.5),
        "Density \u2191":             (1.5, 1.5),
        "Male T \u2193":              (4,   4.5),
        "Male Agg \u2193":            (4,   2),
        "Cortisol \u2191":            (4,   0.5),
        "Female Agg \u2191":          (5.5, 3),
        "Fertility \u2193":           (7,   2.5),
        "Population\nstabilization":  (9,   3),
    }

    for label, (x, y) in nodes.items():
        ax.text(x, y, label, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#141827",
                          edgecolor="#2a3045", linewidth=1),
                fontsize=8, color="#ccd2e6")

    edges = [
        ("Low Threat", "Male T \u2193", 0),
        ("Low Threat", "Female Agg \u2191", -0.1),
        ("Male T \u2193", "Male Agg \u2193", 0.12),
        ("Male Agg \u2193", "Population\nstabilization", 0),
        ("Female Agg \u2191", "Fertility \u2193", 0),
        ("Fertility \u2193", "Population\nstabilization", 0),
        ("Density \u2191", "Cortisol \u2191", 0),
        ("Cortisol \u2191", "Fertility \u2193", 0),
        ("Density \u2191", "Male Agg \u2193", 0.1),
    ]

    for src, dst, rad in edges:
        x1, y1 = nodes[src]
        x2, y2 = nodes[dst]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#4a4d5e",
                                    lw=1.5, connectionstyle=f"arc3,rad={rad}"))

    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 1 saved to {out_path}")


def fig2_population_trajectories(out_path):
    """Shrunk figure with no embedded title."""
    fig, ax = plt.subplots(figsize=(6, 4))

    found = False
    for name in CORE_SCENARIOS:
        sc_dir = RESULTS_DIR / "scenarios" / name
        if not sc_dir.exists():
            continue
        seed_files = sorted(sc_dir.glob("seed_*.csv"))
        if not seed_files:
            continue
        found = True
        trajectories = []
        for sf in seed_files[:20]:
            try:
                df = pd.read_csv(sf)
                trajectories.append(df["population"].values)
            except Exception:
                continue
        if not trajectories:
            continue
        min_len = min(len(t) for t in trajectories)
        traj_arr = np.array([t[:min_len] for t in trajectories])
        mean = traj_arr.mean(axis=0)
        ci = 1.96 * traj_arr.std(axis=0) / np.sqrt(traj_arr.shape[0])
        x = np.arange(min_len)
        color = SCENARIO_COLORS.get(name, "#6a7090")
        label = name.replace("_", " ")
        ax.plot(x, mean, color=color, label=label, linewidth=1.5)
        ax.fill_between(x, mean - ci, mean + ci, color=color, alpha=0.2)

    if not found:
        raise FileNotFoundError(
            f"No scenario data found in {RESULTS_DIR / 'scenarios'} "
            f"for core scenarios {CORE_SCENARIOS}"
        )

    ax.set_xlabel("Time Step")
    ax.set_ylabel("Population")
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.15)
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 2 saved to {out_path}")


def fig3_core_metrics(out_path):
    summary_path = RESULTS_DIR / "scenario_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {summary_path}"
        )

    df = pd.read_csv(summary_path)
    if df.empty:
        return
    df = df[df["scenario"].isin(CORE_SCENARIOS)].copy()

    metrics = ["mean_male_aggression", "mean_female_aggression", "mean_fertility"]
    labels = ["Male Aggression", "Female Aggression", "Fertility"]
    fig, axes = plt.subplots(1, 3, figsize=(10, 4))

    for ax, metric, label in zip(axes, metrics, labels):
        mean_col = f"{metric}_mean" if f"{metric}_mean" in df.columns else metric
        ci_col = f"{metric}_ci95" if f"{metric}_ci95" in df.columns else None
        names = df["scenario"].values
        vals = df[mean_col].values
        colors = [SCENARIO_COLORS.get(n, "#6a7090") for n in names]
        x = np.arange(len(names))
        ax.bar(x, vals, color=colors, width=0.6, edgecolor="none")
        if ci_col and ci_col in df.columns:
            cis = df[ci_col].values
            ax.errorbar(x, vals, yerr=cis, fmt="none", ecolor="#ffffff",
                        capsize=2, capthick=1, elinewidth=1)
        ax.set_xticks(x)
        short_names = []
        for n in names:
            parts = n.split("_", 1)
            prefix = parts[0] if parts[0] in ("A", "B", "C", "D", "E", "F") else ""
            rest = parts[1] if len(parts) > 1 else n
            short_map = {
                "normal_baseline": "baseline",
                "hsap_abundance": "abundance",
                "crowded_abundance": "crowded",
                "high_predation_survival": "predation",
                "sink_recovery": "S2 recovery",
                "sink_partial_collapse": "S3 collapse",
            }
            short = short_map.get(rest, rest.replace("_", " "))
            short_names.append(f"{prefix} {short}" if prefix else short)

        ax.set_xticklabels(short_names, rotation=15, ha="right", fontsize=8)
        ax.set_title(label, fontsize=9)
        ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 3 saved to {out_path}")


def fig4_null_models(out_path):
    """Null model comparison from ablation_summary.csv."""
    if not ABLATION_CSV.exists():
        raise FileNotFoundError(
            f"Required data file not found: {ABLATION_CSV}"
        )

    df = pd.read_csv(ABLATION_CSV)
    if df.empty:
        return

    # Use the ablation data as a heatmap
    scenarios = [c for c in df.columns if c != "ablation"]
    ablations = df["ablation"].values
    data = df[scenarios].values

    fig, ax = plt.subplots(figsize=(8, max(4, len(ablations) * 0.5)))
    cmap = plt.cm.YlOrRd.copy()
    cmap.set_bad("#e0e0e0")
    vmax = data.max() if data.max() > 0 else 1
    im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0, vmax=vmax)

    ax.set_xticks(range(len(scenarios)))
    short_scenarios = []
    for s in scenarios:
        parts = s.split("_", 1)
        prefix = parts[0] if parts[0] in ("A", "B", "C", "D", "E", "F") else ""
        rest = parts[1] if len(parts) > 1 else s
        short_map = {
            "normal_baseline": "baseline",
            "hsap_abundance": "abundance",
            "crowded_abundance": "crowded",
            "high_predation_survival": "predation",
            "sink_recovery": "recovery",
            "sink_partial_collapse": "collapse",
        }
        short = short_map.get(rest, rest.replace("_", " "))
        short_scenarios.append(f"{prefix} {short}" if prefix else short)
    ax.set_xticklabels(short_scenarios, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(ablations)))
    ax.set_yticklabels([a.replace("HSAP_no_", "No ").replace("_", " ")
                        for a in ablations], fontsize=8)

    for i in range(len(ablations)):
        for j in range(len(scenarios)):
            val = data[i, j]
            if val > 0:
                ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                        fontsize=7, color="white" if val > vmax * 0.5 else "black")

    plt.colorbar(im, ax=ax, label="MSE (trajectory fit)", shrink=0.8)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 4 saved to {out_path}")


def fig5_ablation_heatmap(out_path):
    """Ablation heatmap from ablation_summary.csv."""
    if not ABLATION_CSV.exists():
        raise FileNotFoundError(
            f"Required data file not found: {ABLATION_CSV}"
        )

    df = pd.read_csv(ABLATION_CSV)
    if df.empty:
        return

    scenarios = [c for c in df.columns if c != "ablation"]
    ablations = df["ablation"].values
    data = df[scenarios].values

    # Normalize per column
    data_norm = np.zeros_like(data, dtype=float)
    for j in range(data.shape[1]):
        col = data[:, j].astype(float)
        mx = col.max() if col.max() > 0 else 1
        data_norm[:, j] = col / mx

    fig, ax = plt.subplots(figsize=(8, max(4, len(ablations) * 0.5)))
    cmap = plt.cm.YlOrRd.copy()
    cmap.set_bad("#e0e0e0")
    data_plot = np.ma.masked_where(data_norm <= 0, data_norm)
    im = ax.imshow(data_plot, cmap=cmap, aspect="auto",
                   norm=mcolors.LogNorm(vmin=0.01, vmax=1))

    ax.set_xticks(range(len(scenarios)))
    short_scenarios = []
    for s in scenarios:
        parts = s.split("_", 1)
        prefix = parts[0] if parts[0] in ("A", "B", "C", "D", "E", "F") else ""
        rest = parts[1] if len(parts) > 1 else s
        short_map = {
            "normal_baseline": "baseline",
            "hsap_abundance": "abundance",
            "crowded_abundance": "crowded",
            "high_predation_survival": "predation",
            "sink_recovery": "recovery",
            "sink_partial_collapse": "collapse",
        }
        short = short_map.get(rest, rest.replace("_", " "))
        short_scenarios.append(f"{prefix} {short}" if prefix else short)
    ax.set_xticklabels(short_scenarios, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(ablations)))
    ax.set_yticklabels([a.replace("HSAP_no_", "No ").replace("_", " ")
                        for a in ablations], fontsize=8)
    ax.set_xlabel("Scenario", fontsize=9)
    ax.set_ylabel("Ablation", fontsize=9)

    for i in range(len(ablations)):
        for j in range(len(scenarios)):
            val = data_norm[i, j]
            if val > 0:
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=7, color="white" if val > 0.5 else "black")

    plt.colorbar(im, ax=ax, label="Normalized MSE", shrink=0.8)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 5 saved to {out_path}")


def fig6_sink_trajectories(out_path):
    """Sink trajectories - only if sink data exists."""
    fig, ax = plt.subplots(figsize=(6, 4))
    sink_scenarios = ["C_crowded_stable", "E_behavioral_sink_recovery",
                      "F_behavioral_sink_partial_collapse"]
    has_data = False

    for name in sink_scenarios:
        sc_dir = RESULTS_DIR / "scenarios" / name
        if not sc_dir.exists():
            continue
        seed_files = sorted(sc_dir.glob("seed_*.csv"))
        if not seed_files:
            continue
        trajectories = []
        for sf in seed_files[:50]:
            try:
                df = pd.read_csv(sf)
                trajectories.append(df["population"].values)
            except Exception:
                continue
        if not trajectories:
            continue
        has_data = True
        min_len = min(len(t) for t in trajectories)
        pops = np.array([t[:min_len] for t in trajectories])
        mean = pops.mean(axis=0)
        ci = 1.96 * pops.std(axis=0) / np.sqrt(pops.shape[0])
        x = np.arange(min_len)
        color = SCENARIO_COLORS.get(name, "#6a7090")
        sink_label_map = {
            "C_crowded_stable": "S1 crowded-stable",
            "E_behavioral_sink_recovery": "S2 recovery",
            "F_behavioral_sink_partial_collapse": "S3 partial collapse",
        }
        label = sink_label_map.get(name, name.replace("_", " "))
        ax.plot(x, mean, color=color, label=label, linewidth=1.5)
        ax.fill_between(x, mean - ci, mean + ci, color=color, alpha=0.2)

    if not has_data:
        raise FileNotFoundError(
            f"No sink scenario data found in {RESULTS_DIR / 'scenarios'}. "
            f"Expected scenarios: {sink_scenarios}"
        )

    ax.set_xlabel("Time Step")
    ax.set_ylabel("Population")
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.15)
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 6 saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate arxiv paper figures")
    parser.add_argument("--dpi", type=int, default=300, help="Figure DPI")
    args = parser.parse_args()

    global DPI
    DPI = args.dpi

    FIGS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating arxiv figures in {FIGS_DIR}/ ...")

    fig1_causal_chain(FIGS_DIR / "figure_1_causal_chain.pdf")
    fig2_population_trajectories(FIGS_DIR / "figure_2_population_trajectories.pdf")
    fig3_core_metrics(FIGS_DIR / "figure_3_core_metrics.pdf")
    fig4_null_models(FIGS_DIR / "figure_4_null_models.pdf")
    fig5_ablation_heatmap(FIGS_DIR / "figure_5_ablation_heatmap.pdf")
    fig6_sink_trajectories(FIGS_DIR / "figure_6_sink_trajectories.pdf")

    print("All arxiv figures generated.")
    print("NOTE: figure_7 removed from manuscript.")


if __name__ == "__main__":
    main()
