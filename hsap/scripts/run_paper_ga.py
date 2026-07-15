#!/usr/bin/env python3
"""Paper-grade GA experiments: three searches with full logging.

GA-1: HSAP-support search across broad parameter space (multi-objective)
GA-2: Constrained falsification inside HSAP-favorable world
GA-3: Parameter identifiability search

Logs:
  results/paper/ga/support_log.csv
  results/paper/ga/falsification_log.csv
  results/paper/ga/best_individuals.csv
  results/paper/ga/pareto_front.csv
"""

import csv
import json
from pathlib import Path

import numpy as np

from hsap.config import HSAPConfig
from hsap.simulation import Simulation
from hsap.ga import (
    BOUNDS, param_keys, dict_from_individual, apply_to_config,
    _make_fitness, run_ga,
)


# ── GA-1: HSAP-support search (multi-objective) ──

def support_fitness_multi(ind, base_config, n_steps=300):
    """Multi-objective fitness: maximize stability, male T decline,
    female aggression increase, fertility decline; minimize extinction."""
    params = dict_from_individual(ind)
    cfg = apply_to_config(base_config, params)
    try:
        sim = Simulation(cfg)
        metrics = sim.run(steps=n_steps)
        s = metrics.summary()
        df = metrics.to_dataframe()
    except Exception:
        return (0.0,)  # single-objective fallback

    pop = df["population"].values
    extinct = 1.0 if pop[-1] <= 0 else 0.0
    stability = min(1.0, s.get("population_crash", 0))
    T_downshift = 1.0 - s.get("mean_T", 0.5)
    female_agg = s.get("mean_female_aggression", 0.3)
    restraint = 1.0 - s.get("mean_fertility", 0.5)

    fitness = (
        0.30 * stability
        + 0.20 * T_downshift
        + 0.20 * female_agg
        + 0.20 * restraint
        - 0.10 * extinct
    )
    return (fitness,)


# ── GA-2: Constrained falsification inside HSAP-favorable world ──

def constrained_falsification_fitness(ind, base_config, n_steps=300):
    """Falsification inside HSAP-favorable bounds:
    predator <= 0.15, disease <= 0.15, resource >= 1.2.

    Can GA still produce high male aggression, low female aggression, high fertility?
    """
    params = dict_from_individual(ind)
    cfg = apply_to_config(base_config, params)

    # Enforce constraints
    if cfg.environment.predator_pressure > 0.15:
        return (-1.0,)
    if cfg.environment.disease_pressure > 0.15:
        return (-1.0,)
    if cfg.environment.resource_abundance < 1.2:
        return (-1.0,)

    try:
        sim = Simulation(cfg)
        metrics = sim.run(steps=n_steps)
        s = metrics.summary()
    except Exception:
        return (0.0,)

    # Anti-HSAP: high male agg, low female agg, high fertility
    high_male_agg = s.get("mean_male_aggression", 0.5)
    low_female_agg = 1.0 - s.get("mean_female_aggression", 0.5)
    high_fertility = s.get("mean_fertility", 0.5)
    stability = min(1.0, s.get("population_crash", 0))

    fitness = (
        0.30 * high_male_agg
        + 0.25 * low_female_agg
        + 0.25 * high_fertility
        + 0.20 * stability
    )
    return (fitness,)


# ── GA-3: Parameter identifiability search ──

def identifiability_fitness(ind, base_config, n_steps=300):
    """Maximize variance explained by each parameter group.

    Fitness = how much each parameter pushes output away from baseline.
    """
    params = dict_from_individual(ind)
    cfg = apply_to_config(base_config, params)
    try:
        sim = Simulation(cfg)
        metrics = sim.run(steps=n_steps)
        s = metrics.summary()
    except Exception:
        return (0.0,)

    # Measure deviation from expected HSAP behavior
    male_agg_dev = abs(s.get("mean_male_aggression", 0.5) - 0.5)
    female_agg_dev = abs(s.get("mean_female_aggression", 0.5) - 0.5)
    fert_dev = abs(s.get("mean_fertility", 0.5) - 0.5)
    T_dev = abs(s.get("mean_T", 0.5) - 0.5)

    param_extremeness = sum(abs(v - 0.5) for v in ind) / len(ind)

    fitness = (
        0.25 * male_agg_dev
        + 0.25 * female_agg_dev
        + 0.25 * fert_dev
        + 0.25 * T_dev
    )
    return (fitness,)


# ── Logging helpers ──

def save_ga_log(pop, results, log_dir, name):
    log_path = log_dir / f"{name}_log.csv"
    best_path = log_dir / "best_individuals.csv"
    pareto_path = log_dir / "pareto_front.csv"

    # Generation log
    log = results.get("log", [])
    if log:
        with open(log_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["gen", "avg", "std", "min", "max"])
            w.writeheader()
            for i, record in enumerate(log):
                w.writerow({
                    "gen": i,
                    "avg": record.get("avg", 0),
                    "std": record.get("std", 0),
                    "min": record.get("min", 0),
                    "max": record.get("max", 0),
                })

    # Best individual
    best_params = results.get("best_params", {})
    best_row = {"search": name, "fitness": results.get("best_fitness", 0)}
    best_row.update(best_params)
    file_exists = best_path.exists()
    with open(best_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(best_row.keys()))
        if not file_exists:
            w.writeheader()
        w.writerow(best_row)

    # Pareto front (top 10% of last population)
    pop_sorted = sorted(pop, key=lambda ind: ind.fitness.values[0], reverse=True)
    n_pareto = max(1, len(pop_sorted) // 10)
    with open(pareto_path, "w", newline="") as f:
        keys = param_keys()
        fieldnames = ["rank", "fitness"] + keys
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rank, ind in enumerate(pop_sorted[:n_pareto]):
            params = dict_from_individual(ind)
            row = {"rank": rank + 1, "fitness": ind.fitness.values[0]}
            row.update(params)
            w.writerow(row)


# ── Main ──

def main():
    base_config = HSAPConfig()
    ga_dir = Path("results/paper/ga")
    ga_dir.mkdir(parents=True, exist_ok=True)

    N_POP = base_config.ga.population_size
    N_GEN = base_config.ga.generations
    N_STEPS = 300

    searches = [
        ("support", support_fitness_multi, "GA-1: HSAP-support search"),
        ("falsification", constrained_falsification_fitness, "GA-2: Constrained falsification"),
        ("identifiability", identifiability_fitness, "GA-3: Parameter identifiability"),
    ]

    for name, fitness_func, description in searches:
        print(f"\n{'=' * 60}")
        print(f"Running {description}")
        print(f"{'=' * 60}")

        pop, results = run_ga(
            base_config,
            fitness_func,
            n_pop=N_POP,
            n_gen=N_GEN,
            cx_prob=base_config.ga.cx_prob,
            mut_prob=base_config.ga.mut_prob,
            n_steps=N_STEPS,
            verbose=True,
        )

        print(f"Best fitness: {results['best_fitness']:.4f}")
        print(f"Best params: {results['best_params']}")

        save_ga_log(pop, results, ga_dir, name)

    print(f"\nGA logs saved to {ga_dir}/")


if __name__ == "__main__":
    main()
