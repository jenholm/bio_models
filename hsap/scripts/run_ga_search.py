#!/usr/bin/env python3
"""Run GA search for HSAP-supporting and HSAP-falsifying parameter sets."""

import sys
from pathlib import Path

from hsap.config import load_config
from hsap.ga import run_ga, hsap_support_fitness, hsap_falsification_fitness
from hsap.io import save_ga_results


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/ga_search.yaml"
    out_dir = Path("results/runs/ga_search")
    out_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(config_path)

    print("=== GA: HSAP-supporting search ===")
    pop_support, results_support = run_ga(
        config,
        hsap_support_fitness,
        n_pop=config.ga.population_size,
        n_gen=config.ga.generations,
        cx_prob=config.ga.cx_prob,
        verbose=True,
    )
    save_ga_results(results_support, str(out_dir / "support_results.json"))
    print(f"Best support fitness: {results_support['best_fitness']:.4f}")
    print(f"Best params: {results_support['best_params']}")

    print("\n=== GA: HSAP-falsifying search ===")
    pop_falsify, results_falsify = run_ga(
        config,
        hsap_falsification_fitness,
        n_pop=config.ga.population_size,
        n_gen=config.ga.generations,
        cx_prob=config.ga.cx_prob,
        verbose=True,
    )
    save_ga_results(results_falsify, str(out_dir / "falsify_results.json"))
    print(f"Best falsification fitness: {results_falsify['best_fitness']:.4f}")
    print(f"Best params: {results_falsify['best_params']}")


if __name__ == "__main__":
    main()
