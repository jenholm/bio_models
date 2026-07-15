#!/usr/bin/env python3
"""Paper-grade sensitivity analysis: Morris screening + Sobol main effects.

Produces:
  results/paper/sensitivity/sobol_results.json
  results/paper/sensitivity/sobol_table.csv
  results/paper/figures/sensitivity_tornado.png
  results/paper/figures/sobol_heatmap.png
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

from hsap.config import HSAPConfig
from hsap.simulation import Simulation


# Extended problem definition for paper-grade analysis
PROBLEM = {
    "num_vars": 12,
    "names": [
        "predator_pressure",
        "disease_pressure",
        "resource_abundance",
        "resource_regeneration_rate",
        "base_male_testosterone",
        "base_female_testosterone",
        "low_threat_T_downshift",
        "offspring_aggression_bonus",
        "reproductive_restraint_max",
        "fertility_cortisol_penalty",
        "space_constraint",
        "carrying_capacity",
    ],
    "bounds": [
        [0.0, 1.0],
        [0.0, 1.0],
        [0.3, 1.5],
        [0.01, 0.2],
        [0.2, 2.0],
        [0.05, 0.8],
        [0.0, 0.8],
        [0.0, 1.0],
        [0.0, 0.8],
        [0.0, 0.6],
        [0.0, 1.0],
        [100, 1000],
    ],
}


def map_problem_to_config(base_config, values):
    cfg = base_config.model_copy(deep=True)
    cfg.environment.predator_pressure = float(values[0])
    cfg.environment.disease_pressure = float(values[1])
    cfg.environment.resource_abundance = float(values[2])
    cfg.environment.resource_regeneration_rate = float(values[3])
    cfg.endocrine.base_male_testosterone = float(values[4])
    cfg.endocrine.base_female_testosterone = float(values[5])
    cfg.endocrine.low_threat_T_downshift = float(values[6])
    cfg.endocrine.offspring_aggression_bonus = float(values[7])
    cfg.endocrine.reproductive_restraint_max = float(values[8])
    cfg.endocrine.fertility_cortisol_penalty = float(values[9])
    cfg.environment.space_constraint = float(values[10])
    cfg.environment.carrying_capacity = int(values[11])
    return cfg


OUTPUT_NAMES = [
    "final_population",
    "crash_probability",
    "recovery_probability",
    "mean_male_aggression",
    "mean_female_aggression",
    "mean_fertility",
    "mean_HSAP_index",
    "time_to_sink",
    "time_to_recovery",
]


def compute_outputs(df):
    pop = df["population"].values
    n = len(pop)
    if n == 0:
        return [0.0] * len(OUTPUT_NAMES)

    final_pop = float(pop[-1]) / 500.0  # normalize
    crash_prob = 1.0 if pop[-1] <= 0 else 0.0
    recovery_prob = float(df["post_sink_recovery"].max() > 0) if "post_sink_recovery" in df.columns else 0.0
    male_agg = float(df["male_aggression"].mean())
    female_agg = float(df["female_aggression"].mean())
    fertility = float(df["mean_fertility"].mean())

    # HSAP index
    threat = df["external_threat_index"] if "external_threat_index" in df.columns else df.get("predator_pressure", pd.Series([0.5]))
    hsap = 0.25 * (1 - threat.mean()) + 0.20 * (1 - male_agg) + 0.20 * female_agg + 0.20 * (1 - fertility) + 0.15 * (1 - crash_prob)

    sink_times = np.where(df["sink_active"] > 0)[0] if "sink_active" in df.columns else []
    time_to_sink = float(sink_times[0]) if len(sink_times) > 0 else float(n)
    recovery_times = np.where(df["post_sink_recovery"] > 0)[0] if "post_sink_recovery" in df.columns else []
    time_to_recovery = float(recovery_times[0]) if len(recovery_times) > 0 else float(n)

    return [
        final_pop, crash_prob, recovery_prob, male_agg, female_agg,
        fertility, float(hsap), time_to_sink / n, time_to_recovery / n,
    ]


def run_morris_screening(n_trajectories=20, n_steps=300):
    """Morris screening for broad parameter sensitivity."""
    from SALib.sample import morris as morris_sample
    from SALib.analyze import morris as morris_analyze

    param_values = morris_sample.sample(PROBLEM, N=n_trajectories, num_levels=4)
    n_cases = param_values.shape[0]
    n_outputs = len(OUTPUT_NAMES)
    outputs = np.zeros((n_cases, n_outputs))
    base_config = HSAPConfig()

    import pandas as pd

    for i in range(n_cases):
        cfg = map_problem_to_config(base_config, param_values[i])
        cfg.random_seed = i
        cfg.max_steps = n_steps
        try:
            sim = Simulation(cfg)
            metrics = sim.run(steps=n_steps)
            df = metrics.to_dataframe()
            outputs[i] = compute_outputs(df)
        except Exception:
            outputs[i] = 0.5

    results = {}
    for j, name in enumerate(OUTPUT_NAMES):
        Si = morris_analyze.analyze(PROBLEM, param_values, outputs[:, j], num_levels=4)
        results[name] = {
            "mu": dict(zip(PROBLEM["names"], Si["mu"].tolist())),
            "mu_star": dict(zip(PROBLEM["names"], Si["mu_star"].tolist())),
            "sigma": dict(zip(PROBLEM["names"], Si["sigma"].tolist())),
        }
    return results


def run_sobol_analysis(n_samples=256, n_steps=300):
    """Sobol sensitivity analysis."""
    from SALib.sample import saltelli
    from SALib.analyze import sobol

    param_values = saltelli.sample(PROBLEM, n_samples, calc_second_order=False)
    n_cases = param_values.shape[0]
    n_outputs = len(OUTPUT_NAMES)
    outputs = np.zeros((n_cases, n_outputs))
    base_config = HSAPConfig()

    import pandas as pd

    for i in range(n_cases):
        cfg = map_problem_to_config(base_config, param_values[i])
        cfg.random_seed = i
        cfg.max_steps = n_steps
        try:
            sim = Simulation(cfg)
            metrics = sim.run(steps=n_steps)
            df = metrics.to_dataframe()
            outputs[i] = compute_outputs(df)
        except Exception:
            outputs[i] = 0.5

        if (i + 1) % 50 == 0:
            print(f"  Sobol: {i + 1}/{n_cases} cases done")

    results = {}
    for j, name in enumerate(OUTPUT_NAMES):
        Si = sobol.analyze(PROBLEM, outputs[:, j], calc_second_order=False)
        results[name] = {
            "S1": dict(zip(PROBLEM["names"], Si["S1"].tolist())),
            "ST": dict(zip(PROBLEM["names"], Si["ST"].tolist())),
        }
    # Incremental save of partial results
    if n_cases > 500:
        import json as _json
        _savepath = Path("results/paper/sensitivity/sobol_results_partial.json")
        _savepath.parent.mkdir(parents=True, exist_ok=True)
        with open(_savepath, "w") as _f:
            _json.dump(results, _f, indent=2, default=str)
    return results


def save_results(results, out_dir):
    with open(out_dir / "sobol_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    # CSV table
    rows = []
    for output_name, metrics in results.items():
        for param in PROBLEM["names"]:
            rows.append({
                "output": output_name,
                "parameter": param,
                "S1": metrics.get("S1", {}).get(param, ""),
                "ST": metrics.get("ST", {}).get(param, ""),
            })
    if rows:
        with open(out_dir / "sobol_table.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["output", "parameter", "S1", "ST"])
            w.writeheader()
            w.writerows(rows)


def make_tornado_plot(results, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output = list(results.keys())[0]
    st = results[output].get("ST", {})
    sorted_params = sorted(st.items(), key=lambda x: x[1], reverse=True)
    params, vals = zip(*sorted_params)

    fig, ax = plt.subplots(figsize=(8, max(4, len(params) * 0.4)))
    colors = ["#ef5350" if v > 0.1 else "#66bb6a" for v in vals]
    ax.barh(range(len(params)), vals, color=colors)
    ax.set_yticks(range(len(params)))
    ax.set_yticklabels(params, fontsize=9)
    ax.set_xlabel("Sobol Total-order Index (ST)", fontsize=10)
    ax.set_title(f"Sensitivity: {output}", fontsize=11)
    ax.axvline(0.1, color="#6a7090", linestyle="--", linewidth=0.8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved tornado plot to {out_path}")


def make_heatmap(results, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import numpy as np

    outputs = list(results.keys())
    params = PROBLEM["names"]
    data = np.zeros((len(params), len(outputs)))
    for j, out in enumerate(outputs):
        st = results[out].get("ST", {})
        for i, p in enumerate(params):
            data[i, j] = st.get(p, 0)

    fig, ax = plt.subplots(figsize=(max(8, len(outputs) * 1.2), max(5, len(params) * 0.4)))
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto", vmin=0, vmax=max(0.01, data.max()))

    ax.set_xticks(range(len(outputs)))
    ax.set_xticklabels(outputs, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(params)))
    ax.set_yticklabels(params, fontsize=9)
    ax.set_xlabel("Output", fontsize=10)
    ax.set_ylabel("Parameter", fontsize=10)
    ax.set_title("Sobol Total-order Indices (ST)", fontsize=11)

    for i in range(len(params)):
        for j in range(len(outputs)):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", fontsize=7,
                    color="white" if data[i, j] > 0.5 else "black")

    plt.colorbar(im, ax=ax, label="ST", shrink=0.8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved Sobol heatmap to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Paper-grade sensitivity analysis")
    parser.add_argument("--sobol-samples", type=int, default=128, help="Sobol samples (total cases = N*(2D+2))")
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--morris-only", action="store_true")
    parser.add_argument("--skip-morris", action="store_true")
    args = parser.parse_args()

    sens_dir = Path("results/paper/sensitivity")
    figs_dir = Path("results/paper/figures")
    sens_dir.mkdir(parents=True, exist_ok=True)
    figs_dir.mkdir(parents=True, exist_ok=True)

    base_config = HSAPConfig()

    # Morris screening
    if not args.skip_morris:
        print("Running Morris screening...")
        morris_results = run_morris_screening(n_trajectories=20, n_steps=args.steps)
        with open(sens_dir / "morris_results.json", "w") as f:
            json.dump(morris_results, f, indent=2, default=str)
        print("Morris screening done.")

    # Sobol analysis
    if not args.morris_only:
        print(f"Running Sobol analysis with {args.sobol_samples} samples...")
        sobol_results = run_sobol_analysis(n_samples=args.sobol_samples, n_steps=args.steps)
        save_results(sobol_results, sens_dir)

        # Figures
        if sobol_results:
            output_list = list(sobol_results.keys())
            make_tornado_plot({output_list[0]: sobol_results[output_list[0]]},
                              figs_dir / "sensitivity_tornado.png")
            make_heatmap(sobol_results, figs_dir / "sobol_heatmap.png")

    print("Sensitivity analysis complete.")


if __name__ == "__main__":
    main()
