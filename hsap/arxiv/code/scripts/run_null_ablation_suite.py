#!/usr/bin/env python3
"""Compare HSAP, null models, and ablation models across multiple outputs.

Produces:
  results/paper/null_ablation_results.json
  results/paper/null_ablation_summary.csv
  results/paper/figures/null_ablation_heatmap.png (if run with --figures)
"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from hsap.config import HSAPConfig
from hsap.simulation import Simulation
from hsap.null_models import NullModelSuite
from hsap.ablation_models import ABLATION_REGISTRY


OUTPUT_METRICS = [
    "population",
    "births",
    "deaths",
    "mean_fertility",
    "male_aggression",
    "female_aggression",
    "male_T",
    "female_T",
    "mean_cortisol",
    "density",
    "sink_active",
    "post_sink_recovery",
]


def mse(hsap_arr, model_arr):
    min_len = min(len(hsap_arr), len(model_arr))
    return float(np.mean((hsap_arr[:min_len] - model_arr[:min_len]) ** 2))


def run_hsap(cfg):
    sim = Simulation(cfg)
    metrics = sim.run()
    return metrics.to_dataframe()


def run_scenario_comparisons(scenario_name, env_overrides, n_steps, base_config, rng_seed=42):
    """Run HSAP plus all null/ablation models for one scenario."""
    cfg = base_config.model_copy(deep=True)
    cfg.random_seed = rng_seed
    cfg.max_steps = n_steps
    for k, v in env_overrides.items():
        setattr(cfg.environment, k, v)

    hsap_df = run_hsap(cfg)
    hsap_ts = {col: hsap_df[col].values for col in OUTPUT_METRICS if col in hsap_df.columns}

    null_suite = NullModelSuite(cfg.environment, cfg.initial_population, np.random.default_rng(rng_seed))
    null_results = null_suite.run_all(steps=n_steps)

    # Null model comparisons: null models only define population, so only compare that
    comparisons = {}
    for name, null_res in null_results.items():
        null_ts = null_res.population_ts
        comp = {
            "population": {"mse": mse(hsap_ts.get("population", [0]), null_ts)},
        }
        comparisons[name] = comp

    # Ablation model comparisons
    for ab_name, ab_fn in ABLATION_REGISTRY.items():
        if ab_name == "HSAP_full":
            continue
        ab_cfg = ab_fn(cfg)
        ab_cfg.random_seed = rng_seed
        ab_cfg.max_steps = n_steps
        for k, v in env_overrides.items():
            setattr(ab_cfg.environment, k, v)
        try:
            ab_df = run_hsap(ab_cfg)
            comp = {}
            for metric in OUTPUT_METRICS:
                if metric in ab_df.columns and metric in hsap_df.columns:
                    comp[metric] = {"mse": mse(hsap_df[metric].values, ab_df[metric].values)}
            comparisons[ab_name] = comp
        except Exception as e:
            comparisons[ab_name] = {"error": str(e)}

    return comparisons


def main():
    parser = argparse.ArgumentParser(description="Run null/ablation comparison suite")
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--figures", action="store_true", help="Generate heatmap figure")
    args = parser.parse_args()

    paper_dir = Path("results/paper")
    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "figures").mkdir(exist_ok=True)

    # Load scenarios
    scenarios_path = paper_dir / "scenarios.json"
    if scenarios_path.exists():
        all_scenarios = json.loads(scenarios_path.read_text())
    else:
        all_scenarios = {
            "A_normal_baseline": {
                "environment": {
                    "predator_pressure": 0.25, "disease_pressure": 0.2,
                    "resource_abundance": 0.6, "resource_regeneration_rate": 0.03,
                }
            },
            "B_hsap_abundance": {
                "environment": {
                    "predator_pressure": 0.1, "disease_pressure": 0.05,
                    "resource_abundance": 1.5, "resource_regeneration_rate": 0.08,
                }
            },
        }

    base_config = HSAPConfig()
    all_results = {}
    out_path = paper_dir / "null_ablation_results.json"

    for sc_name, sc_params in all_scenarios.items():
        print(f"Comparing models for: {sc_name}")
        env_overrides = sc_params.get("environment", {})
        comparisons = run_scenario_comparisons(sc_name, env_overrides, args.steps, base_config)
        all_results[sc_name] = comparisons
        # Save incrementally so partial progress is preserved
        with open(out_path, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"  -> Saved partial results ({len(all_results)}/{len(all_scenarios)} scenarios)")

    print(f"All results saved to {out_path}")

    # Summary CSV
    rows = []
    for sc_name, models in all_results.items():
        for model_name, outputs in models.items():
            row = {"scenario": sc_name, "model": model_name}
            for metric, val in outputs.items():
                if isinstance(val, dict) and "mse" in val:
                    row[f"{metric}_mse"] = val["mse"]
                elif isinstance(val, dict) and "error" in val:
                    row[f"{metric}_error"] = val["error"]
            rows.append(row)

    if rows:
        csv_path = paper_dir / "null_ablation_summary.csv"
        fieldnames = sorted(set().union(*(r.keys() for r in rows)))
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in fieldnames})
        print(f"Saved summary to {csv_path}")

    # Figure
    if args.figures:
        try:
            _make_heatmap(all_results, paper_dir / "figures" / "null_ablation_heatmap.png")
        except Exception as e:
            print(f"Could not generate heatmap: {e}")

    print("Done.")


def _make_heatmap(results, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    # Collect model names and metric names
    models_set = set()
    metrics_set = set()
    for sc_name, models in results.items():
        for m_name in models:
            models_set.add(m_name)
            for metric in models[m_name]:
                if isinstance(models[m_name][metric], dict) and "mse" in models[m_name][metric]:
                    metrics_set.add(metric)

    models_sorted = sorted(models_set)
    metrics_sorted = sorted(metrics_set)

    # Normalize MSE within each metric across models (col-normalize)
    n_models = len(models_sorted)
    n_metrics = len(metrics_sorted)
    data = np.zeros((n_models, n_metrics))

    for mi, metric in enumerate(metrics_sorted):
        vals = []
        for ni, model in enumerate(models_sorted):
            mse_vals = [
                results[sc].get(model, {}).get(metric, {}).get("mse", 0)
                for sc in results
                if results[sc].get(model, {}).get(metric, {}).get("mse") is not None
            ]
            avg_val = np.mean(mse_vals) if mse_vals else 0
            vals.append(avg_val)
        vmax = max(vals) if max(vals) > 0 else 1
        for ni, model in enumerate(models_sorted):
            mse_vals = [
                results[sc].get(model, {}).get(metric, {}).get("mse", 0)
                for sc in results
                if results[sc].get(model, {}).get(metric, {}).get("mse") is not None
            ]
            avg_val = np.mean(mse_vals) if mse_vals else 0
            data[ni, mi] = avg_val / vmax

    fig, ax = plt.subplots(figsize=(max(8, n_metrics * 1.2), max(6, n_models * 0.5)))
    im = ax.imshow(data, cmap="YlOrRd", aspect="auto", norm=mcolors.LogNorm(vmin=max(0.01, data.min()), vmax=1))

    ax.set_xticks(range(n_metrics))
    ax.set_xticklabels(metrics_sorted, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(n_models))
    ax.set_yticklabels(models_sorted, fontsize=8)
    ax.set_xlabel("Output Variable", fontsize=10)
    ax.set_ylabel("Model", fontsize=10)
    ax.set_title("Normalized MSE: HSAP vs Null/Ablation Models", fontsize=11)

    for i in range(n_models):
        for j in range(n_metrics):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", fontsize=7, color="white" if data[i, j] > 0.5 else "black")

    plt.colorbar(im, ax=ax, label="Normalized MSE", shrink=0.8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved heatmap to {out_path}")


if __name__ == "__main__":
    main()
