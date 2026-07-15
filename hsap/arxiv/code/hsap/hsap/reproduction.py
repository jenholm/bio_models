from __future__ import annotations
import numpy as np
from .entities import Agent
from .environment import Environment
from .config import HSAPConfig


class ReproductionEngine:
    def __init__(self, config: HSAPConfig, rng: np.random.Generator):
        self.rp = config.reproduction
        self.rng = rng

    def mate(self, male: Agent, female: Agent, env: Environment) -> bool:
        if female.pregnant:
            return False
        if male.energy < self.rp.mating_energy_threshold:
            return False
        if female.energy < self.rp.mating_energy_threshold:
            return False
        if not male.is_reproductive_age or not female.is_reproductive_age:
            return False
        mate_prob = male.fertility * female.fertility * 0.5
        mate_prob *= male.mating_drive
        mate_prob -= env.resource_scarcity * 0.2
        if self.rng.random() < mate_prob:
            female.pregnant = True
            female.gestation_remaining = self.rp.gestation_time
            return True
        return False

    def process_pregnancy(self, female: Agent, env: Environment) -> list[Agent]:
        if not female.pregnant:
            return []
        female.gestation_remaining -= 1
        if female.gestation_remaining > 0:
            return []
        female.pregnant = False
        litter_size = int(
            round(
                self.rng.normal(
                    self.rp.litter_size_mean * female.fertility,
                    self.rp.litter_size_std,
                )
            )
        )
        litter_size = max(1, litter_size)
        female.energy -= self.rp.post_partum_energy_cost
        offspring = []
        for _ in range(litter_size):
            # Offspring survival filtered by maternal survival probability
            if self.rng.random() > female.offspring_survival_probability:
                continue
            sex = "male" if self.rng.random() < 0.5 else "female"
            child = Agent(
                agent_id=-1,
                sex=sex,
                age=0,
                rng=self.rng,
            )
            child.energy = 0.5
            child.health = self.rng.uniform(0.7, 1.0)
            offspring.append(child)
        return offspring

    def check_infanticide(self, agent: Agent, env: Environment) -> bool:
        density = env.density
        if density > self.rp.infanticide_density_threshold:
            prob = self.rp.infanticide_rate * (density - self.rp.infanticide_density_threshold) / (
                1.0 - self.rp.infanticide_density_threshold
            )
            prob *= agent.aggression_tendency
            return self.rng.random() < prob
        return False

    def check_offspring_neglect(self, agent: Agent, env: Environment) -> bool:
        density = env.density
        if density > self.rp.offspring_neglect_density_threshold or agent.cortisol > self.rp.offspring_neglect_cortisol_threshold:
            prob = 0.05 + 0.1 * density + 0.1 * (agent.cortisol > self.rp.offspring_neglect_cortisol_threshold)
            return self.rng.random() < prob
        return False
