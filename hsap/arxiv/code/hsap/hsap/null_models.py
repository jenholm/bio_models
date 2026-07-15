from __future__ import annotations
import numpy as np
from typing import Callable
from .config import HSAPConfig, EnvironmentParams
from .metrics import MetricsCollector


class NullModelResult:
    def __init__(self, name: str, population_ts: list[float]):
        self.name = name
        self.population_ts = np.array(population_ts)

    @property
    def final_population(self) -> float:
        return float(self.population_ts[-1]) if len(self.population_ts) > 0 else 0.0

    @property
    def max_population(self) -> float:
        return float(self.population_ts.max()) if len(self.population_ts) > 0 else 0.0

    def summary(self) -> dict:
        return {
            "model": self.name,
            "final": self.final_population,
            "max": self.max_population,
            "mean": float(self.population_ts.mean()),
            "std": float(self.population_ts.std()),
        }


class NullModelSuite:
    def __init__(self, env_params: EnvironmentParams, initial_population: int, rng: np.random.Generator):
        self.env = env_params
        self.n0 = initial_population
        self.rng = rng

    def run_all(self, steps: int = 500) -> dict[str, NullModelResult]:
        return {
            "N0_logistic": self._logistic_growth(steps),
            "N1_predator_prey": self._predator_prey(steps),
            "N2_density_fertility": self._density_fertility(steps),
            "N3_disease_pressure": self._disease_pressure(steps),
            "N4_dominance_hierarchy": self._dominance_hierarchy(steps),
            "N5_random_hormone": self._random_hormone_drift(steps),
            "N6_resource_only": self._resource_only(steps),
            "N7_density_with_recovery": self._density_with_recovery(steps),
            "N8_random_behavior": self._random_behavior_no_endocrine(steps),
            "N9_social_behavior": self._social_behavior_no_hormones(steps),
            "N10_endocrine_no_behavior": self._endocrine_no_behavior_feedback(steps),
        }

    def _logistic_growth(self, steps: int) -> NullModelResult:
        K = self.env.carrying_capacity
        r = 0.08
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            pop += r * pop * (1 - pop / K)
            noise = self.rng.normal(0, max(1, pop * 0.02))
            pop = max(0, pop + noise)
            ts.append(pop)
        return NullModelResult("N0_logistic", ts)

    def _predator_prey(self, steps: int) -> NullModelResult:
        K = self.env.carrying_capacity
        r = 0.08
        a = self.env.predator_pressure * 0.02
        b = 0.005
        d = 0.06
        prey = float(self.n0)
        pred = float(self.n0 * 0.1)
        ts = [prey]
        for _ in range(steps):
            dprey = r * prey * (1 - prey / K) - a * prey * pred
            dpred = b * a * prey * pred - d * pred
            prey = max(0, prey + dprey + self.rng.normal(0, max(0.1, prey * 0.01)))
            pred = max(0, pred + dpred + self.rng.normal(0, max(0.1, pred * 0.01)))
            ts.append(prey)
        return NullModelResult("N1_predator_prey", ts)

    def _density_fertility(self, steps: int) -> NullModelResult:
        K = self.env.carrying_capacity
        base_fertility = 0.3
        base_mortality = 0.05
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            density = pop / K
            fertility = base_fertility * (1 - density * 0.5)
            mortality = base_mortality * (1 + density * 0.5)
            births = fertility * pop * 0.5
            deaths = mortality * pop
            pop = max(0, pop + births - deaths + self.rng.normal(0, max(0.1, pop * 0.01)))
            ts.append(pop)
        return NullModelResult("N2_density_fertility", ts)

    def _disease_pressure(self, steps: int) -> NullModelResult:
        K = self.env.carrying_capacity
        r = 0.08
        disease = self.env.disease_pressure
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            density = pop / K
            disease_mortality = disease * 0.1 * (1 + density)
            growth = r * pop * (1 - pop / K) - disease_mortality * pop
            pop = max(0, pop + growth + self.rng.normal(0, max(0.1, pop * 0.01)))
            ts.append(pop)
        return NullModelResult("N3_disease_pressure", ts)

    def _dominance_hierarchy(self, steps: int) -> NullModelResult:
        K = self.env.carrying_capacity
        r = 0.08
        n_ranks = 10
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            density = pop / K
            rank_suppression = 1.0 - 0.3 * density
            growth = r * pop * (1 - pop / K) * rank_suppression
            pop = max(0, pop + growth + self.rng.normal(0, max(0.1, pop * 0.01)))
            ts.append(pop)
        return NullModelResult("N4_dominance_hierarchy", ts)

    def _random_hormone_drift(self, steps: int) -> NullModelResult:
        K = self.env.carrying_capacity
        r = 0.08
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            hormone_noise = self.rng.normal(0, 0.1)
            modifier = 1.0 + hormone_noise * 0.1
            growth = r * pop * (1 - pop / K) * modifier
            pop = max(0, pop + growth + self.rng.normal(0, max(0.1, pop * 0.01)))
            ts.append(pop)
        return NullModelResult("N5_random_hormone", ts)


    def _resource_only(self, steps: int) -> NullModelResult:
        """N6: Resource-only — no density, predation, or disease.

        Population grows to resource carrying capacity and stabilizes.
        """
        K = self.env.carrying_capacity
        r = 0.06
        resource = self.env.resource_abundance
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            carrying = K * min(1.0, resource)
            growth = r * pop * (1 - pop / carrying) if carrying > 0 else -0.1 * pop
            pop = max(0, pop + growth + self.rng.normal(0, max(0.1, pop * 0.01)))
            ts.append(pop)
        return NullModelResult("N6_resource_only", ts)

    def _density_with_recovery(self, steps: int) -> NullModelResult:
        """N7: Density-only with demographic recovery.

        When population drops below threshold, a recovery bonus
        mimics refuge/recolonization.
        """
        K = self.env.carrying_capacity
        r = 0.08
        recovery_threshold = 30
        recovery_bonus = 0.15
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            growth = r * pop * (1 - pop / K)
            if pop < recovery_threshold:
                growth += recovery_bonus * recovery_threshold * (1 - pop / recovery_threshold)
            pop = max(0, pop + growth + self.rng.normal(0, max(0.1, pop * 0.01)))
            ts.append(pop)
        return NullModelResult("N7_density_with_recovery", ts)

    def _random_behavior_no_endocrine(self, steps: int) -> NullModelResult:
        """N8: Random behavior — no endocrine system.

        Behavioral parameters vary randomly; no hormonal state.
        """
        K = self.env.carrying_capacity
        r = 0.07
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            behavior_noise = self.rng.uniform(0.8, 1.2)
            growth = r * pop * (1 - pop / K) * behavior_noise
            pop = max(0, pop + growth + self.rng.normal(0, max(0.1, pop * 0.02)))
            ts.append(pop)
        return NullModelResult("N8_random_behavior", ts)

    def _social_behavior_no_hormones(self, steps: int) -> NullModelResult:
        """N9: Social behavior only — rank/dominance without hormone mediation.

        Hierarchical suppression affects reproduction directly.
        """
        K = self.env.carrying_capacity
        r = 0.08
        n_ranks = 10
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            density = pop / K if K > 0 else 1.0
            rank_suppression = 1.0 - 0.4 * density * (1 - 1.0 / max(n_ranks, 1))
            social_stress = 0.1 * density * (1 - rank_suppression)
            growth = r * pop * (1 - pop / K) * rank_suppression - social_stress * pop
            pop = max(0, pop + growth + self.rng.normal(0, max(0.1, pop * 0.01)))
            ts.append(pop)
        return NullModelResult("N9_social_behavior", ts)

    def _endocrine_no_behavior_feedback(self, steps: int) -> NullModelResult:
        """N10: Endocrine dynamics — no behavioral feedback loop.

        Hormones respond to environment but do not affect behavior,
        reproduction, or mortality beyond baseline.
        """
        K = self.env.carrying_capacity
        r = 0.08
        pop = float(self.n0)
        ts = [pop]
        for _ in range(steps):
            density = pop / K if K > 0 else 1.0
            pred = self.env.predator_pressure * 0.02 * pop
            disease = self.env.disease_pressure * 0.03 * (1 + density) * pop
            growth = r * pop * (1 - pop / K) - pred - disease
            pop = max(0, pop + growth + self.rng.normal(0, max(0.1, pop * 0.01)))
            ts.append(pop)
        return NullModelResult("N10_endocrine_no_behavior", ts)


def compare_to_null(
    hsap_ts: list[float],
    hsap_config: HSAPConfig,
    null_results: dict[str, NullModelResult],
) -> dict:
    comparisons = {}
    hsap_arr = np.array(hsap_ts)
    for name, result in null_results.items():
        null_arr = result.population_ts
        min_len = min(len(hsap_arr), len(null_arr))
        mse = float(np.mean((hsap_arr[:min_len] - null_arr[:min_len]) ** 2))
        final_diff = float(hsap_arr[-1] - null_arr[-1])
        comparisons[name] = {
            "mse": mse,
            "final_diff": final_diff,
            "hsap_final": float(hsap_arr[-1]),
            "null_final": float(null_arr[-1]),
        }
    return comparisons
