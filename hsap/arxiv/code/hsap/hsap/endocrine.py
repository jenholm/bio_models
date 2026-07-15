from __future__ import annotations
from .entities import Agent
from .environment import Environment
from .config import HSAPConfig


class EndocrineSystem:
    def __init__(self, config: HSAPConfig):
        self.ep = config.endocrine

    def update(self, agent: Agent, env: Environment, density: float):
        if agent.sex == "male":
            self._update_male(agent, env, density)
        else:
            self._update_female(agent, env, density)
        self._update_cortisol(agent, env, density)
        self._update_aggression(agent, env, density)
        self._update_fertility(agent, env, density)
        self._update_offspring_survival(agent, env, density)
        agent._clamp()

    def _update_male(self, agent: Agent, env: Environment, density: float):
        t = self.ep.base_male_testosterone
        t += self.ep.dominance_T_bonus * agent.rank
        t += self.ep.mating_competition_T_bonus * agent.mating_drive
        t -= self.ep.crowding_T_penalty * density
        low_threat = 1.0 - env.predator_pressure
        t -= self.ep.low_threat_T_downshift * low_threat
        t -= self.ep.poor_condition_T_penalty * (1.0 - agent.health)
        agent.testosterone = max(0.0, t)

    def _update_female(self, agent: Agent, env: Environment, density: float):
        t = self.ep.base_female_testosterone
        t += self.ep.dominance_T_bonus * agent.rank * 0.5
        t += self.ep.resource_competition_aggression_bonus * env.resource_scarcity
        t += self.ep.density_aggression_bonus * density
        agent.testosterone = max(0.0, t)

        e = self.ep.base_estrogen
        e -= self.ep.fertility_cortisol_penalty * agent.cortisol
        agent.estrogen = max(0.0, e)

    def _update_cortisol(self, agent: Agent, env: Environment, density: float):
        c = self.ep.base_cortisol
        c += self.ep.stress_cortisol_rise * density * 2.0
        c -= self.ep.rank_stress_buffer * agent.rank
        c += self.ep.health_stress_amplifier * (1.0 - agent.health)
        c += env.predator_pressure * 0.2
        c += env.resource_scarcity * 0.3
        agent.cortisol = max(0.0, min(1.0, c))

    def _update_aggression(self, agent: Agent, env: Environment, density: float):
        aggression = agent.testosterone * 0.5 + agent.cortisol * 0.2
        if agent.sex == "female":
            aggression += (
                self.ep.offspring_aggression_bonus * len(agent.offspring_ids) * 0.2
            )
            aggression += (
                self.ep.resource_competition_aggression_bonus * env.resource_scarcity
            )
            aggression += self.ep.density_aggression_bonus * density
            aggression += self.ep.endocrine_sensitivity_female * agent.testosterone
        else:
            aggression += self.ep.dominance_T_bonus * agent.rank
        agent.aggression_tendency = max(0.0, min(1.0, aggression))

        if agent.sex == "female":
            defense = self.ep.offspring_aggression_bonus * len(
                agent.offspring_ids
            ) * 0.3 + agent.testosterone * 0.3
            agent.maternal_defense_tendency = max(0.0, min(1.0, defense))

    def _update_fertility(self, agent: Agent, env: Environment, density: float):
        fert = 0.5
        if agent.sex == "male":
            fert += agent.testosterone * 0.3
        else:
            fert += agent.estrogen * 0.3
            fert -= self.ep.fertility_T_penalty * agent.testosterone
        fert -= self.ep.fertility_cortisol_penalty * agent.cortisol
        fert -= self.ep.fertility_age_decline * max(0, agent.age - 40)

        if density > self.ep.reproductive_restraint_density_threshold:
            restraint = self.ep.reproductive_restraint_max * (
                density - self.ep.reproductive_restraint_density_threshold
            ) / (1.0 - self.ep.reproductive_restraint_density_threshold)
            fert -= restraint
        fert *= max(0.2, env.territory_availability)
        agent.fertility = max(0.0, min(1.0, fert))

    def _update_offspring_survival(self, agent: Agent, env: Environment, density: float):
        prob = 0.5
        prob += self.ep.offspring_survival_T_effect * agent.testosterone
        prob -= self.ep.offspring_survival_cortisol_penalty * agent.cortisol
        prob -= density * 0.3
        prob -= env.resource_scarcity * 0.2
        agent.offspring_survival_probability = max(0.0, min(1.0, prob))
