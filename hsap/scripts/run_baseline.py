#!/usr/bin/env python3
"""Run a single baseline simulation and save results."""

import sys
from pathlib import Path

from hsap.config import load_config
from hsap.simulation import Simulation
from hsap.io import save_metrics_csv, save_summary_json
from hsap.null_models import NullModelSuite, compare_to_null
import numpy as np


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/baseline.yaml"
    out_dir = Path("results/runs/baseline")
    out_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(config_path)
    sim = Simulation(config)
    metrics = sim.run()

    df = metrics.to_dataframe()
    save_metrics_csv(df, str(out_dir / "metrics.csv"))

    summary = metrics.summary()
    save_summary_json(summary, str(out_dir / "summary.json"))

    null_runner = NullModelSuite(
        config.environment, config.initial_population, sim.rng
    )
    null_results = null_runner.run_all(steps=config.max_steps)
    null_summaries = {k: v.summary() for k, v in null_results.items()}
    save_summary_json(null_summaries, str(out_dir / "null_summaries.json"))

    comparisons = compare_to_null(
        df["population"].tolist(), config, null_results
    )
    save_summary_json(comparisons, str(out_dir / "null_comparisons.json"))

    print(f"Results saved to {out_dir}/")
    print(f"Final population: {summary['final_population']}")
    print(f"Mean male aggression: {summary['mean_male_aggression']:.3f}")
    print(f"Mean female aggression: {summary['mean_female_aggression']:.3f}")


if __name__ == "__main__":
    main()
