#!/usr/bin/env python3
"""Generate all static paper figures from saved results.

Figures:
  Figure 1: Model architecture / causal chain diagram
  Figure 2: Scenario population trajectories, mean +/- CI
  Figure 3: Male aggression, female aggression, fertility across scenarios
  Figure 4a: Null models — population MSE bar chart
  Figure 4b: Ablation models — multi-output heatmap
  Figure 5: Behavioral sink recovery vs extinction trajectories
  Figure 6: Sensitivity analysis
  Figure 7: GA parameter distribution / Pareto front
  Figure 8: State-space phase map

Usage:
  python scripts/make_paper_figures.py [--dpi 300]
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

DPI = 300
FIGSIZE_FULL = (7.5, 5)
FIGSIZE_WIDE = (10, 4)
FIGSIZE_SQUARE = (6, 6)

RESULTS_DIR = Path("results/paper")
FIGS_DIR = RESULTS_DIR / "figures"
SCENARIOS_DIR = RESULTS_DIR / "scenarios"

# ── Global style ──
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": DPI,
    "savefig.dpi": DPI,
    "savefig.bbox": "tight",
})

SCENARIO_COLORS = {
    "A_normal_baseline": "#6a7090",
    "B_hsap_abundance": "#66bb6a",
    "C_crowded_abundance": "#ffb74d",
    "C_crowded_stable": "#4fc3f7",
    "D_high_predation_survival": "#ef5350",
    "E_behavioral_sink_recovery": "#ab47bc",
    "F_behavioral_sink_partial_collapse": "#d32f2f",
}

HSAP_COLORS = {
    "external-control": "#ef5350",
    "transition": "#ffb74d",
    "hsap-active": "#66bb6a",
    "strong-social-regulation": "#4fc3f7",
}


# ── Figure 1: Causal chain diagram ──

def fig1_causal_chain(out_path):
    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    # Left-to-right layered layout — no arrow passes through any label
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

    ax.set_title("Figure 1: HSAP Causal Architecture", fontsize=11, fontweight="bold", pad=10)
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 1 saved to {out_path}")


# ── Figure 2: Population trajectories ──

CORE_SCENARIOS = [
    "A_normal_baseline",
    "B_hsap_abundance",
    "C_crowded_abundance",
    "D_high_predation_survival",
]

ALL_SCENARIOS = [
    "A_normal_baseline",
    "B_hsap_abundance",
    "C_crowded_abundance",
    "C_crowded_stable",
    "D_high_predation_survival",
    "E_behavioral_sink_recovery",
    "F_behavioral_sink_partial_collapse",
]


def fig2_population_trajectories(out_path):
    fig, ax = plt.subplots(figsize=FIGSIZE_FULL)

    found = False
    for name in ALL_SCENARIOS:
        sc_dir = SCENARIOS_DIR / name
        if not sc_dir.exists():
            continue
        seed_files = sorted(sc_dir.glob("seed_*.csv"))
        if not seed_files:
            continue
        found = True
        trajectories = []
        for sf in seed_files[:20]:
            import pandas as pd
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
        ax.plot(x, mean, color=color, label=name.replace("_", " "), linewidth=1.5)
        ax.fill_between(x, mean - ci, mean + ci, color=color, alpha=0.2)

    if not found:
        raise FileNotFoundError(
            f"No scenario data found in {SCENARIOS_DIR} for core scenarios"
        )

    ax.set_xlabel("Time Step")
    ax.set_ylabel("Population")
    ax.set_title("Figure 2: Population Trajectories (Mean \u00b1 95% CI)")
    ax.legend(fontsize=8, loc="best")
    ax.grid(True, alpha=0.15)
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 2 saved to {out_path}")


# ── Figure 3: Key metrics comparison ──

def fig3_metrics_comparison(out_path):
    summary_path = RESULTS_DIR / "scenario_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {summary_path}"
        )

    import pandas as pd
    df = pd.read_csv(summary_path)
    if df.empty:
        return
    df = df[df["scenario"].isin(CORE_SCENARIOS)].copy()

    metrics = ["mean_male_aggression", "mean_female_aggression", "mean_fertility"]
    labels = ["Male Aggression", "Female Aggression", "Fertility"]
    fig, axes = plt.subplots(1, 3, figsize=FIGSIZE_WIDE)

    for ax, metric, label in zip(axes, metrics, labels):
        mean_col = f"{metric}_mean" if f"{metric}_mean" in df.columns else metric
        ci_col = f"{metric}_ci95" if f"{metric}_ci95" in df.columns else None
        names = df["scenario"].values
        vals = df[mean_col].values
        colors = [SCENARIO_COLORS.get(n, "#6a7090") for n in names]
        x = np.arange(len(names))
        bars = ax.bar(x, vals, color=colors, width=0.6, edgecolor="none")
        if ci_col and ci_col in df.columns:
            cis = df[ci_col].values
            ax.errorbar(x, vals, yerr=cis, fmt="none", ecolor="#ffffff", capsize=2, capthick=1, elinewidth=1)
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
                "crowded_stable": "S1 crowded-stable",
                "high_predation_survival": "predation",
                "behavioral_sink_recovery": "S2 recovery",
                "behavioral_sink_partial_collapse": "S3 collapse",
            }
            short = short_map.get(rest, rest.replace("_", " "))
            short_names.append(f"{prefix} {short}" if prefix else short)

        ax.set_xticklabels(short_names, rotation=15, ha="right", fontsize=8)
        ax.set_title(label, fontsize=9)
        ax.set_ylim(0, 1)

    fig.suptitle("Figure 3: Key Metrics Across HSAP Scenarios", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 3 saved to {out_path}")


# ── Figure 4a: Null-model comparison heatmap (population only) ──

def _load_null_ablation_results():
    path = RESULTS_DIR / "null_ablation_results.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def _is_null_model(name):
    return name.startswith("N") or name == "null"


def _is_ablation_model(name):
    return name.startswith("HSAP_") or name.startswith("ablation_")


def fig4a_null_population(out_path):
    """Null models only produce population — single-column heatmap."""
    results = _load_null_ablation_results()
    if not results:
        raise FileNotFoundError(
            "Required data file not found: null_ablation_results.json"
        )

    null_models = sorted(m for m in next(iter(results.values())) if _is_null_model(m))
    if not null_models:
        raise FileNotFoundError(
            "No null models found in null_ablation_results.json"
        )

    # Compute population MSE for each null model
    model_mse = []
    for model in null_models:
        vals = [
            results[sc].get(model, {}).get("population", {}).get("mse", np.nan)
            for sc in results
            if results[sc].get(model, {}).get("population", {}).get("mse") is not None
        ]
        model_mse.append((model, np.mean(vals) if vals else np.nan))

    # Sort by MSE ascending
    model_mse.sort(key=lambda x: (0 if not np.isnan(x[1]) else 1, x[1] if not np.isnan(x[1]) else 0))

    sorted_models = [m for m, _ in model_mse]
    vals = np.array([v for _, v in model_mse])
    valid = ~np.isnan(vals)
    vmax = vals[valid].max() if valid.any() else 1

    short_labels = []
    for m in sorted_models:
        short = m.replace("_", " ")
        for prefix, repl in [("N0 ", "Logistic "), ("N1 ", "Pred-Prey "), ("N2 ", "Density-Fert "),
                              ("N3 ", "Disease "), ("N4 ", "Hierarchy "), ("N5 ", "Rand Horm "),
                              ("N6 ", "Resource "), ("N7 ", "Density+Rec "), ("N8 ", "Rand Behav "),
                              ("N9 ", "Social "), ("N10 ", "Endo-NoBehav ")]:
            if short.startswith(prefix):
                short = repl.strip()
                break
        short_labels.append(short)

    fig, ax = plt.subplots(figsize=(5, len(sorted_models) * 0.45))
    colors = ["#e0e0e0"] * len(sorted_models)
    for i in range(len(sorted_models)):
        if valid[i]:
            norm_val = vals[i] / vmax
            colors[i] = matplotlib.colors.to_hex(plt.cm.YlOrRd(norm_val))

    bars = ax.barh(range(len(sorted_models)), vals, color=colors, edgecolor="none", height=0.6)
    ax.set_yticks(range(len(sorted_models)))
    ax.set_yticklabels(short_labels, fontsize=8)
    ax.set_xlabel("Population MSE (lower = closer to HSAP)", fontsize=9)
    ax.set_title("Figure 4a: Null Models — Population Only", fontsize=10)
    ax.axvline(0, color="#6a7090", linewidth=0.5)
    ax.grid(True, axis="x", alpha=0.15)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 4a saved to {out_path}")


# ── Figure 4b: Ablation-model multi-output heatmap ──

def _norm_per_column(data_2d):
    """Column-normalize a (n_models, n_metrics) array; returns normalized copy."""
    out = np.zeros_like(data_2d)
    for j in range(data_2d.shape[1]):
        col = data_2d[:, j]
        mx = col.max() if col.max() > 0 else 1
        out[:, j] = col / mx
    return out


def fig4b_ablation_heatmap(out_path):
    """Ablation models have all metrics — full heatmap."""
    results = _load_null_ablation_results()
    if not results:
        raise FileNotFoundError(
            "Required data file not found: null_ablation_results.json"
        )

    all_models = set()
    for sc_name, models in results.items():
        all_models.update(models.keys())
    ablation_models = sorted(m for m in all_models if _is_ablation_model(m))

    if not ablation_models:
        raise FileNotFoundError(
            "No ablation models found in null_ablation_results.json"
        )

    metrics_set = set()
    for sc_name, models in results.items():
        for m_name in ablation_models:
            if m_name in models:
                for metric, val in models[m_name].items():
                    if isinstance(val, dict) and "mse" in val:
                        metrics_set.add(metric)
    metrics_sorted = sorted(metrics_set)

    n_models = len(ablation_models)
    n_metrics = len(metrics_sorted)
    data = np.zeros((n_models, n_metrics))

    for mi, metric in enumerate(metrics_sorted):
        for ni, model in enumerate(ablation_models):
            mse_vals = [
                results[sc].get(model, {}).get(metric, {}).get("mse", 0)
                for sc in results
                if results[sc].get(model, {}).get(metric, {}).get("mse") is not None
            ]
            data[ni, mi] = np.mean(mse_vals) if mse_vals else 0

    data_norm = _norm_per_column(data)

    fig, ax = plt.subplots(figsize=(max(8, n_metrics * 1.2), max(5, n_models * 0.5)))
    data_plot = np.ma.masked_where(data_norm <= 0, data_norm)
    cmap = plt.cm.YlOrRd.copy()
    cmap.set_bad("#e0e0e0")
    im = ax.imshow(data_plot, cmap=cmap, aspect="auto", norm=matplotlib.colors.LogNorm(vmin=0.01, vmax=1))

    ax.set_xticks(range(n_metrics))
    ax.set_xticklabels(metrics_sorted, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(n_models))
    ax.set_yticklabels(ablation_models, fontsize=8)
    ax.set_xlabel("Output Variable", fontsize=10)
    ax.set_ylabel("Model", fontsize=10)
    ax.set_title("Figure 4b: Ablation Models — Multi-Output MSE (col-normalized)", fontsize=10)

    for i in range(n_models):
        for j in range(n_metrics):
            val = data_norm[i, j]
            if val > 0:
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=7, color="white" if val > 0.5 else "black")

    plt.colorbar(im, ax=ax, label="Normalized MSE", shrink=0.8)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 4b saved to {out_path}")


# ── Figure 5: Sink recovery vs extinction ──

def fig5_sink_trajectories(out_path):
    import pandas as pd
    fig, ax = plt.subplots(figsize=FIGSIZE_FULL)

    sink_scenarios = ["C_crowded_stable", "E_behavioral_sink_recovery", "F_behavioral_sink_partial_collapse"]
    has_data = False
    trajectory_data = {}

    for name in sink_scenarios:
        sc_dir = SCENARIOS_DIR / name
        if not sc_dir.exists():
            continue
        seed_files = sorted(sc_dir.glob("seed_*.csv"))
        if not seed_files:
            continue
        trajectories = []
        sink_fractions = []
        recovery_fractions = []
        for sf in seed_files[:50]:
            try:
                df = pd.read_csv(sf)
                trajectories.append(df["population"].values)
                sink_active = df["sink_active"].values if "sink_active" in df.columns else np.zeros(len(df), dtype=bool)
                post_recovery = df["post_sink_recovery"].values if "post_sink_recovery" in df.columns else np.zeros(len(df), dtype=bool)
                sink_fractions.append(sink_active.astype(float))
                recovery_fractions.append(post_recovery.astype(float))
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

        # Sink-active fraction across seeds
        sink_arr = np.array([s[:min_len] for s in sink_fractions])
        mean_sink = sink_arr.mean(axis=0)

        # Recovery fraction across seeds
        rec_arr = np.array([r[:min_len] for r in recovery_fractions])
        mean_rec = rec_arr.mean(axis=0)

        trajectory_data[name] = {
            "x": x, "mean": mean, "ci": ci,
            "mean_sink": mean_sink, "mean_rec": mean_rec,
        }

        color = SCENARIO_COLORS.get(name, "#6a7090")
        ax.plot(x, mean, color=color, label=name.replace("_", " "), linewidth=1.5)
        ax.fill_between(x, mean - ci, mean + ci, color=color, alpha=0.2)

    if not has_data:
        raise FileNotFoundError(
            f"No sink scenario data found in {SCENARIOS_DIR}. "
            f"Expected scenarios: {sink_scenarios}"
        )

    # Sink-active shading (E only — only scenario that triggers sink)
    if "E_behavioral_sink_recovery" in trajectory_data:
        d = trajectory_data["E_behavioral_sink_recovery"]
        # Shade regions where ≥10% of seeds have sink active (green)
        sink_active_mask = d["mean_sink"] >= 0.1
        if sink_active_mask.any():
            # Contiguous sink-active bands
            transitions = np.diff(sink_active_mask.astype(int), prepend=0, append=0)
            starts = np.where(transitions == 1)[0]
            ends = np.where(transitions == -1)[0]
            for s, e in zip(starts, ends):
                ax.axvspan(d["x"][s], d["x"][e - 1], alpha=0.06, color="#66bb6a")

        # Recovery-phase shading (blue)
        rec_active_mask = d["mean_rec"] >= 0.1
        if rec_active_mask.any():
            transitions = np.diff(rec_active_mask.astype(int), prepend=0, append=0)
            starts = np.where(transitions == 1)[0]
            ends = np.where(transitions == -1)[0]
            for s, e in zip(starts, ends):
                ax.axvspan(d["x"][s], d["x"][e - 1], alpha=0.04, color="#4fc3f7")

        # Vertical markers for mean sink onset and recovery onset
        sink_onsets = []
        rec_onsets = []
        sc_dir = SCENARIOS_DIR / "E_behavioral_sink_recovery"
        for sf in sorted(sc_dir.glob("seed_*.csv")):
            try:
                df = pd.read_csv(sf)
                if "sink_active" in df.columns:
                    sink_on = df[df["sink_active"] == True]
                    if not sink_on.empty:
                        sink_onsets.append(int(sink_on["step"].iloc[0]))
                if "post_sink_recovery" in df.columns:
                    rec_on = df[df["post_sink_recovery"] == True]
                    if not rec_on.empty:
                        rec_onsets.append(int(rec_on["step"].iloc[0]))
            except Exception:
                continue

        if sink_onsets:
            mean_onset = np.mean(sink_onsets)
            ax.axvline(mean_onset, color="#66bb6a", linestyle="--", linewidth=1.2, alpha=0.8)
            ax.text(mean_onset, ax.get_ylim()[1] * 0.95, "  Sink onset\n  (mean)",
                    fontsize=7, color="#66bb6a", va="top")

        if rec_onsets:
            mean_rec = np.mean(rec_onsets)
            ax.axvline(mean_rec, color="#4fc3f7", linestyle="--", linewidth=1.2, alpha=0.8)
            ax.text(mean_rec, ax.get_ylim()[1] * 0.85, "  Recovery\n  (mean)",
                    fontsize=7, color="#4fc3f7", va="top")

    # Legend entries for shading
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#66bb6a", alpha=0.12, label="Sink-active period"),
        Patch(facecolor="#4fc3f7", alpha=0.06, label="Recovery phase"),
    ]
    # Merge handles; avoid duplicate labels
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles + legend_elements, fontsize=7, loc="best")

    ax.axhline(30, color="#6a7090", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.text(ax.get_xlim()[1] * 0.98, 32, "Recovery threshold", fontsize=7, color="#6a7090", alpha=0.6, ha="right")
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Population")
    ax.set_title("Figure 5: Behavioral Sink Trajectories")
    ax.grid(True, alpha=0.15)
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 5 saved to {out_path}")
    print(f"    Caption: Green shading = sink-active period; blue shading = recovery from sink suppression")


# ── Figure 6: Sensitivity tornado ──

def fig6_sensitivity_tornado(out_path):
    sobol_path = RESULTS_DIR / "sensitivity" / "sobol_results.json"
    if not sobol_path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {sobol_path}"
        )

    results = json.loads(sobol_path.read_text())
    output = "final_population"
    if output not in results:
        output = list(results.keys())[0]
    st = results[output].get("ST", {})
    sorted_params = sorted(st.items(), key=lambda x: x[1], reverse=True)
    params, vals = zip(*sorted_params)

    fig, ax = plt.subplots(figsize=(8, max(4, len(params) * 0.35)))
    colors = ["#ef5350" if v > 0.1 else "#66bb6a" for v in vals]
    ax.barh(range(len(params)), vals, color=colors, edgecolor="none")
    ax.set_yticks(range(len(params)))
    ax.set_yticklabels(params, fontsize=8)
    ax.set_xlabel("Sobol Total-order Index (ST)", fontsize=9)
    ax.set_title(f"Figure 6: Sensitivity Analysis — Target: {output.replace('_', ' ')}", fontsize=10)
    ax.axvline(0.1, color="#6a7090", linestyle="--", linewidth=0.8, label="Threshold")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 6 saved to {out_path}")


# ── Figure 7: GA Pareto front ──

def fig7_ga_convergence(out_path):
    """GA convergence (single-objective weighted-sum fitness) and best-params bar chart."""
    ga_dir = RESULTS_DIR / "ga"

    log_path = ga_dir / "support_log.csv"
    if not log_path.exists():
        raise FileNotFoundError(
            f"Required data file not found: {log_path}"
        )

    import pandas as pd
    log_df = pd.read_csv(log_path)
    if log_df.empty:
        return

    best_path = ga_dir / "best_individuals.csv"
    best_df = pd.read_csv(best_path) if best_path.exists() else None

    n_cols = 2 if best_df is not None and not best_df.empty else 1
    fig, axes = plt.subplots(1, n_cols, figsize=(10, 4) if n_cols == 2 else (5, 4))
    if n_cols == 1:
        axes = [axes]

    ax = axes[0]
    ax.plot(log_df["gen"], log_df["max"], color="#66bb6a", label="Best", linewidth=1.5)
    ax.plot(log_df["gen"], log_df["avg"], color="#4fc3f7", label="Mean", linewidth=1, alpha=0.7)
    ax.fill_between(log_df["gen"], log_df["min"], log_df["max"], alpha=0.1, color="#66bb6a")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Weighted-sum Fitness")
    ax.set_title("GA Convergence (Support Search)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.15)

    if n_cols == 2 and best_df is not None and not best_df.empty:
        ax = axes[1]
        best_row = best_df.iloc[0] if len(best_df) > 0 else best_df.iloc[0]
        param_cols = [c for c in best_df.columns if c not in ("fitness", "rank", "gen", "search")]
        if param_cols:
            vals = [float(best_row[c]) if c in best_row else 0 for c in param_cols]
            colors = ["#66bb6a" if v > 0.5 else "#ef5350" for v in vals]
            y = np.arange(len(param_cols))
            ax.barh(y, vals, color=colors, edgecolor="none")
            ax.set_yticks(y)
            ax.set_yticklabels([c.replace("_", " ") for c in param_cols], fontsize=7)
            ax.set_xlabel("Parameter Value (0–1)")
            ax.set_title("Best Individual Parameters")
            ax.set_xlim(0, 1)

    fig.suptitle("Figure 7: Genetic Algorithm — Single-Objective Support Search", fontsize=10, fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 7 saved to {out_path}")


# ── Figure 8: Phase map ──

def fig8_phase_map(out_path):
    """Overlay trajectory paths across all core scenarios in density × external_threat space."""
    fig, ax = plt.subplots(figsize=FIGSIZE_SQUARE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Density")
    ax.set_ylabel("External Threat Index")
    ax.set_title("Figure 8: State-Space Phase Map")

    # Region shading
    regions = [
        (0, 0.5, 0.5, 1, "Predator/Disease\nDominated", "#ef5350"),
        (0.5, 0.5, 1, 1, "Crowding\nSink", "#ffb74d"),
        (0, 0, 0.5, 0.5, "Low Density\nAbundance", "#66bb6a"),
        (0.5, 0, 1, 0.5, "HSAP\nCandidate", "#4fc3f7"),
    ]
    for x1, y1, x2, y2, label, color in regions:
        ax.fill_between([x1, x2], y1, y2, alpha=0.08, color=color)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, label,
                ha="center", va="center", fontsize=8, color="#4a5070")

    # Overlay trajectories from all scenarios
    import pandas as pd
    has_data = False
    for name in ALL_SCENARIOS:
        sc_dir = SCENARIOS_DIR / name
        if not sc_dir.exists():
            continue
        seed_files = sorted(sc_dir.glob("seed_*.csv"))
        if not seed_files:
            continue
        has_data = True
        color = SCENARIO_COLORS.get(name, "#6a7090")
        # Plot first 5 seeds with low alpha, plus mean trajectory
        trajectories = []
        for sf in seed_files[:10]:
            try:
                df = pd.read_csv(sf)
                density = df["density"].values
                threat = df["external_threat_index"].values if "external_threat_index" in df.columns else np.full_like(density, 0.5)
                trajectories.append((density, threat))
                ax.plot(density, threat, color=color, linewidth=0.3, alpha=0.15)
            except Exception:
                continue
        if trajectories:
            # Mean trajectory
            min_len = min(len(t[0]) for t in trajectories)
            mean_d = np.mean([t[0][:min_len] for t in trajectories], axis=0)
            mean_t = np.mean([t[1][:min_len] for t in trajectories], axis=0)
            ax.plot(mean_d, mean_t, color=color, linewidth=1.5, label=name.replace("_", " "))
            # Terminal point
            ax.scatter(mean_d[-1], mean_t[-1], color=color, s=50, zorder=5,
                       edgecolor="white", linewidth=0.5)

    if not has_data:
        ax.text(0.5, 0.5, "No trajectory data found", ha="center", va="center", transform=ax.transAxes)

    ax.legend(fontsize=7, loc="upper right")
    ax.grid(True, alpha=0.1, linestyle="--")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"  Figure 8 saved to {out_path}")
    print(f"    Caption: Right-angle turns reflect threat index equilibrating faster than density (real dynamics)")


# ── Main ──

def main():
    parser = argparse.ArgumentParser(description="Generate paper figures")
    parser.add_argument("--dpi", type=int, default=300, help="Figure DPI")
    args = parser.parse_args()

    global DPI
    DPI = args.dpi

    FIGS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating paper figures in {FIGS_DIR}/ ...")

    fig1_causal_chain(FIGS_DIR / "fig1_causal_chain.png")
    fig2_population_trajectories(FIGS_DIR / "fig2_population_trajectories.png")
    fig3_metrics_comparison(FIGS_DIR / "fig3_metrics_comparison.png")
    fig4a_null_population(FIGS_DIR / "fig4a_null_population.png")
    fig4b_ablation_heatmap(FIGS_DIR / "fig4b_ablation_heatmap.png")
    fig5_sink_trajectories(FIGS_DIR / "fig5_sink_trajectories.png")
    fig6_sensitivity_tornado(FIGS_DIR / "fig6_sensitivity_tornado.png")
    fig7_ga_convergence(FIGS_DIR / "fig7_ga_convergence.png")
    fig8_phase_map(FIGS_DIR / "fig8_phase_map.png")

    # Also save all figures as PDF
    for png_path in sorted(FIGS_DIR.glob("fig*.png")):
        pdf_path = png_path.with_suffix(".pdf")
        try:
            import matplotlib.image as mpimg
            img = mpimg.imread(str(png_path))
            h, w = img.shape[:2]
            dpi = 100
            fig, ax = plt.subplots(figsize=(w / dpi, h / dpi))
            ax.imshow(img)
            ax.axis("off")
            fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
            fig.savefig(pdf_path, dpi=dpi, bbox_inches="tight", pad_inches=0)
            plt.close()
        except Exception:
            pass

    print("All figures generated.")


if __name__ == "__main__":
    main()
