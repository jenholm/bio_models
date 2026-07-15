from __future__ import annotations
import random
import numpy as np
from deap import base, creator, tools, algorithms
from typing import Callable
from .config import HSAPConfig
from .simulation import Simulation
from .metrics import MetricsCollector


BOUNDS = {
    "endocrine__base_male_testosterone": (0.2, 2.0),
    "endocrine__base_female_testosterone": (0.05, 1.0),
    "endocrine__base_estrogen": (0.2, 2.0),
    "endocrine__low_threat_T_downshift": (0.0, 0.8),
    "endocrine__offspring_aggression_bonus": (0.0, 1.0),
    "endocrine__reproductive_restraint_max": (0.0, 0.8),
    "endocrine__fertility_cortisol_penalty": (0.0, 0.6),
    "environment__predator_pressure": (0.0, 1.0),
    "environment__disease_pressure": (0.0, 1.0),
    "environment__resource_abundance": (0.3, 1.5),
}


def param_keys() -> list[str]:
    return list(BOUNDS.keys())


def individual_from_dict(d: dict) -> list[float]:
    scaled = []
    for k in param_keys():
        lo, hi = BOUNDS[k]
        v = d.get(k, (lo + hi) / 2)
        scaled.append((v - lo) / (hi - lo) if hi != lo else 0.5)
    return scaled


def dict_from_individual(ind: list[float]) -> dict:
    raw = dict(zip(param_keys(), ind))
    scaled = {}
    for k, v in raw.items():
        lo, hi = BOUNDS[k]
        scaled[k] = lo + v * (hi - lo)
    return scaled


def apply_to_config(config: HSAPConfig, params: dict) -> HSAPConfig:
    cfg = config.model_copy(deep=True)
    for key, value in params.items():
        section, attr = key.split("__", 1)
        section_obj = getattr(cfg, section, None)
        if section_obj is not None and hasattr(section_obj, attr):
            setattr(section_obj, attr, value)
    return cfg


def _make_fitness(
    minimize: bool = False,
) -> tuple[Callable, Callable]:
    weight = -1.0 if minimize else 1.0
    if hasattr(creator, "FitnessMulti"):
        del creator.FitnessMulti
    if hasattr(creator, "Individual"):
        del creator.Individual
    creator.create("FitnessMulti", base.Fitness, weights=(weight,))
    creator.create("Individual", list, fitness=creator.FitnessMulti)
    return creator.FitnessMulti, creator.Individual


def hsap_support_fitness(
    ind: list[float],
    base_config: HSAPConfig,
    n_steps: int = 300,
) -> tuple[float]:
    params = dict_from_individual(ind)
    cfg = apply_to_config(base_config, params)
    try:
        sim = Simulation(cfg)
        metrics = sim.run(steps=n_steps)
        s = metrics.summary()
    except Exception:
        return (0.0,)
    stability = min(1.0, s.get("population_crash", 0))
    resource_score = min(1.0, cfg.environment.resource_abundance / 1.5)
    T_downshift = 1.0 - s.get("mean_T", 0.5)
    female_agg = s.get("mean_female_aggression", 0.3)
    restraint = 1.0 - s.get("mean_fertility", 0.5)
    crash_pen = 0.0
    if s.get("population_crash", 1) < 0.2:
        crash_pen = 0.5
    fitness = (
        0.25 * stability
        + 0.15 * resource_score
        + 0.2 * T_downshift
        + 0.15 * female_agg
        + 0.15 * restraint
        - 0.1 * crash_pen
    )
    return (fitness,)


def hsap_falsification_fitness(
    ind: list[float],
    base_config: HSAPConfig,
    n_steps: int = 300,
) -> tuple[float]:
    params = dict_from_individual(ind)
    cfg = apply_to_config(base_config, params)
    try:
        sim = Simulation(cfg)
        metrics = sim.run(steps=n_steps)
        s = metrics.summary()
    except Exception:
        return (0.0,)
    crash_penalty = max(0, 1.0 - s.get("population_crash", 0))
    instability = 1.0 - min(
        1.0, s.get("time_to_stability", n_steps) / n_steps
    )
    null_like = 1.0 - abs(s.get("mean_T", 0.5) - 0.5) * 2
    contrarian = 1.0 - s.get("mean_male_aggression", 0.5)
    tuning = 0.0
    for v in ind:
        if v < 0.1 or v > 0.9:
            tuning += 0.1
    fitness = (
        0.3 * crash_penalty
        + 0.2 * instability
        + 0.2 * null_like
        + 0.15 * contrarian
        - 0.15 * tuning
    )
    return (fitness,)


def run_ga(
    base_config: HSAPConfig,
    fitness_func: Callable,
    n_pop: int = 50,
    n_gen: int = 30,
    cx_prob: float = 0.7,
    mut_prob: float = 0.2,
    n_steps: int = 300,
    verbose: bool = True,
) -> tuple[list, dict]:
    random.seed(base_config.random_seed)
    np.random.seed(base_config.random_seed)
    keys = param_keys()
    bounds = [BOUNDS[k] for k in keys]
    n_vars = len(keys)

    FitnessMulti, Individual = _make_fitness(minimize=False)

    toolbox = base.Toolbox()
    toolbox.register(
        "attr_float",
        random.uniform,
        0,
        1,
    )
    toolbox.register("individual", tools.initRepeat, Individual, toolbox.attr_float, n_vars)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(ind):
        return fitness_func(ind, base_config, n_steps)

    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxSimulatedBinaryBounded, low=0, up=1, eta=20.0)
    toolbox.register(
        "mutate",
        tools.mutPolynomialBounded,
        low=0,
        up=1,
        eta=20.0,
        indpb=1.0 / n_vars,
    )
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=n_pop)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, logbook = algorithms.eaSimple(
        pop,
        toolbox,
        cxpb=cx_prob,
        mutpb=mut_prob,
        ngen=n_gen,
        stats=stats,
        halloffame=hof,
        verbose=verbose,
    )

    best_ind = hof[0]
    best_params = dict_from_individual(best_ind)

    results = {
        "best_fitness": float(best_ind.fitness.values[0]),
        "best_params": best_params,
        "log": logbook,
    }
    return pop, results
