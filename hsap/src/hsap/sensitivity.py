from __future__ import annotations
import numpy as np
from SALib.sample import saltelli
from SALib.analyze import sobol
from .config import HSAPConfig
from .simulation import Simulation


PROBLEM = {
    "num_vars": 10,
    "names": [
        "predator_pressure",
        "disease_pressure",
        "resource_abundance",
        "resource_regeneration_rate",
        "base_male_testosterone",
        "low_threat_T_downshift",
        "offspring_aggression_bonus",
        "reproductive_restraint_max",
        "fertility_cortisol_penalty",
        "space_constraint",
    ],
    "bounds": [
        [0.0, 1.0],
        [0.0, 1.0],
        [0.3, 1.5],
        [0.01, 0.2],
        [0.2, 2.0],
        [0.0, 0.8],
        [0.0, 1.0],
        [0.0, 0.8],
        [0.0, 0.6],
        [0.0, 1.0],
    ],
}


def map_problem_to_config(
    base_config: HSAPConfig,
    values: np.ndarray,
) -> HSAPConfig:
    cfg = base_config.model_copy(deep=True)
    cfg.environment.predator_pressure = float(values[0])
    cfg.environment.disease_pressure = float(values[1])
    cfg.environment.resource_abundance = float(values[2])
    cfg.environment.resource_regeneration_rate = float(values[3])
    cfg.endocrine.base_male_testosterone = float(values[4])
    cfg.endocrine.low_threat_T_downshift = float(values[5])
    cfg.endocrine.offspring_aggression_bonus = float(values[6])
    cfg.endocrine.reproductive_restraint_max = float(values[7])
    cfg.endocrine.fertility_cortisol_penalty = float(values[8])
    cfg.environment.space_constraint = float(values[9])
    return cfg


class SensitivityAnalyzer:
    def __init__(self, base_config: HSAPConfig):
        self.base_config = base_config

    def run_sobol(
        self,
        n_samples: int = 256,
        n_steps: int = 300,
    ) -> dict:
        param_values = saltelli.sample(PROBLEM, n_samples)
        n_cases = param_values.shape[0]
        outputs = np.zeros((n_cases, 3))

        for i in range(n_cases):
            cfg = map_problem_to_config(self.base_config, param_values[i])
            try:
                sim = Simulation(cfg)
                metrics = sim.run(steps=n_steps)
                s = metrics.summary()
                outputs[i, 0] = s.get("mean_male_aggression", 0.5)
                outputs[i, 1] = s.get("mean_female_aggression", 0.3)
                outputs[i, 2] = s.get("population_crash", 0.5)
            except Exception:
                outputs[i, :] = 0.5

        results = {}
        for j, name in enumerate(
            ["male_aggression", "female_aggression", "population_crash"]
        ):
            Si = sobol.analyze(PROBLEM, outputs[:, j], calc_second_order=False)
            results[name] = {
                "S1": dict(zip(PROBLEM["names"], Si["S1"])),
                "ST": dict(zip(PROBLEM["names"], Si["ST"])),
            }
        return results
