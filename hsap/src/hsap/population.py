from __future__ import annotations
import numpy as np
from .entities import Agent


class PopulationDynamics:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def age_structure(self, agents: list[Agent]) -> dict:
        age_classes = {"juvenile": 0, "adult": 0, "senior": 0}
        for a in agents:
            if a.age < 10:
                age_classes["juvenile"] += 1
            elif a.age < 50:
                age_classes["adult"] += 1
            else:
                age_classes["senior"] += 1
        return age_classes

    def sex_ratio(self, agents: list[Agent]) -> float:
        males = sum(1 for a in agents if a.sex == "male")
        total = len(agents)
        return males / total if total > 0 else 0.5

    def rank_inequality(self, agents: list[Agent]) -> float:
        if len(agents) < 2:
            return 0.0
        ranks = [a.rank for a in agents]
        return float(np.std(ranks) / max(np.mean(ranks), 0.01))

    def mean_hormones(self, agents: list[Agent]) -> dict:
        if not agents:
            return {"T": 0.0, "E": 0.0, "C": 0.0}
        return {
            "T": float(np.mean([a.testosterone for a in agents])),
            "E": float(np.mean([a.estrogen for a in agents])),
            "C": float(np.mean([a.cortisol for a in agents])),
        }

    def aggression_rates(self, agents: list[Agent]) -> dict:
        males = [a for a in agents if a.sex == "male"]
        females = [a for a in agents if a.sex == "female"]
        return {
            "male_aggression": float(np.mean([a.aggression_tendency for a in males])) if males else 0.0,
            "female_aggression": float(np.mean([a.aggression_tendency for a in females])) if females else 0.0,
            "female_defense": float(np.mean([a.maternal_defense_tendency for a in females])) if females else 0.0,
        }

    def sex_specific_hormones(self, agents: list[Agent]) -> dict:
        males = [a for a in agents if a.sex == "male"]
        females = [a for a in agents if a.sex == "female"]
        return {
            "male_T": float(np.mean([a.testosterone for a in males])) if males else 0.0,
            "female_T": float(np.mean([a.testosterone for a in females])) if females else 0.0,
            "male_E": float(np.mean([a.estrogen for a in males])) if males else 0.0,
            "female_E": float(np.mean([a.estrogen for a in females])) if females else 0.0,
            "male_C": float(np.mean([a.cortisol for a in males])) if males else 0.0,
            "female_C": float(np.mean([a.cortisol for a in females])) if females else 0.0,
        }

    def sex_specific_fertility(self, agents: list[Agent]) -> dict:
        males = [a for a in agents if a.sex == "male" and a.is_reproductive_age]
        females = [a for a in agents if a.sex == "female" and a.is_reproductive_age]
        return {
            "male_fertility": float(np.mean([a.fertility for a in males])) if males else 0.0,
            "female_fertility": float(np.mean([a.fertility for a in females])) if females else 0.0,
        }

    def total_fertility(self, agents: list[Agent]) -> float:
        if not agents:
            return 0.0
        vals = [a.fertility for a in agents if a.is_reproductive_age]
        if not vals:
            return 0.0
        return float(np.mean(vals))

    def update_offspring_links(self, agents: list[Agent], weaning_age: int):
        """Remove dead and weaned offspring IDs from mothers."""
        alive_ids = {a.agent_id for a in agents if a.alive}
        juvenile_ids = {a.agent_id for a in agents if a.alive and a.age < weaning_age}
        for agent in agents:
            agent.offspring_ids = [
                oid for oid in agent.offspring_ids
                if oid in alive_ids and oid in juvenile_ids
            ]
