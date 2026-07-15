#!/usr/bin/env python3
"""DEPRECATED: Use run_paper_experiments.py for the canonical six-world set.

This script uses the older six-scenario naming convention (high_predation_low_resource,
etc.) which does not match the final paper scenarios (A_normal_baseline, B_hsap_abundance,
etc.). Kept for reference but results are not used in the paper."""

from pathlib import Path

from hsap.config import HSAPConfig
from hsap.simulation import Simulation
from hsap.io import save_metrics_csv, save_summary_json
import numpy as np


SCENARIOS = {
    "high_predation_low_resource": {
        "environment": {
            "predator_pressure": 0.9,
            "disease_pressure": 0.5,
            "resource_abundance": 0.4,
            "resource_regeneration_rate": 0.02,
        }
    },
    "high_predation_high_resource": {
        "environment": {
            "predator_pressure": 0.9,
            "disease_pressure": 0.5,
            "resource_abundance": 1.2,
            "resource_regeneration_rate": 0.08,
        }
    },
    "low_predation_low_resource": {
        "environment": {
            "predator_pressure": 0.1,
            "disease_pressure": 0.3,
            "resource_abundance": 0.4,
            "resource_regeneration_rate": 0.02,
        }
    },
    "low_predation_high_resource": {
        "environment": {
            "predator_pressure": 0.1,
            "disease_pressure": 0.1,
            "resource_abundance": 1.3,
            "resource_regeneration_rate": 0.1,
        }
    },
    "low_predation_high_resource_crowded": {
        "environment": {
            "predator_pressure": 0.1,
            "disease_pressure": 0.1,
            "resource_abundance": 1.3,
            "resource_regeneration_rate": 0.1,
            "carrying_capacity": 200,
            "space_constraint": 0.9,
        }
    },
    "high_disease": {
        "environment": {
            "predator_pressure": 0.5,
            "disease_pressure": 0.9,
            "resource_abundance": 1.0,
            "resource_regeneration_rate": 0.05,
        }
    },
}


def main():
    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    base_config = HSAPConfig()
    summaries = {}

    for name, overrides in SCENARIOS.items():
        print(f"Running scenario: {name}")
        cfg = base_config.model_copy(deep=True)
        for section, params in overrides.items():
            section_obj = getattr(cfg, section)
            for k, v in params.items():
                setattr(section_obj, k, v)

        sim = Simulation(cfg)
        metrics = sim.run()
        s = metrics.summary()
        summaries[name] = s

        scenario_dir = Path(f"results/runs/{name}")
        scenario_dir.mkdir(parents=True, exist_ok=True)
        save_metrics_csv(
            metrics.to_dataframe(), str(scenario_dir / "metrics.csv")
        )

    save_summary_json(summaries, str(out_dir / "scenario_grid.json"))

    print("\n=== Scenario Grid Results ===")
    for name, s in summaries.items():
        print(
            f"{name:40s} | final={s['final_population']:4d} | "
            f"male_agg={s['mean_male_aggression']:.3f} | "
            f"female_agg={s['mean_female_aggression']:.3f} | "
            f"fert={s['mean_fertility']:.3f}"
        )


if __name__ == "__main__":
    main()
