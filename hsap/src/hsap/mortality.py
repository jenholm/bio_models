from __future__ import annotations
import numpy as np
from .entities import Agent
from .environment import Environment
from .config import HSAPConfig


class MortalityEngine:
    def __init__(self, config: HSAPConfig, rng: np.random.Generator):
        self.mp = config.mortality
        self.time_scale = config.age_increment
        self.rng = rng

    def check_death(self, agent: Agent, env: Environment, mortality_multiplier: float = 1.0) -> bool:
        if not agent.alive:
            return True
        prob = self.mp.base_mortality
        prob += self._predation_risk(agent, env)
        prob += self._disease_risk(agent, env)
        prob += self._starvation_risk(agent, env)
        prob += self._injury_risk(agent)
        prob += self._old_age_risk(agent)
        prob += self._crowding_risk(env)
        prob *= self.time_scale
        prob *= mortality_multiplier
        return self.rng.random() < min(1.0, prob)

    def _predation_risk(self, agent: Agent, env: Environment) -> float:
        risk = self.mp.predation_mortality_base * env.predator_pressure
        risk -= 0.02 * (1.0 - env.resource_scarcity)
        if agent.injury:
            risk *= 1.5
        if agent.age < 5:
            risk *= 2.0
        return max(0.0, risk)

    def _disease_risk(self, agent: Agent, env: Environment) -> float:
        risk = self.mp.disease_mortality_base * env.disease_pressure
        risk *= 1.0 + 0.5 * (1.0 - agent.health)
        risk *= 1.0 + env.density * 0.5
        return max(0.0, risk)

    def _starvation_risk(self, agent: Agent, env: Environment) -> float:
        if agent.energy < self.mp.starvation_mortality_threshold:
            scarcity = env.resource_scarcity
            return self.mp.starvation_mortality_max * scarcity * (
                1.0 - agent.energy / self.mp.starvation_mortality_threshold
            )
        return 0.0

    def _injury_risk(self, agent: Agent) -> float:
        return self.mp.injury_mortality_bonus if agent.injury else 0.0

    def _old_age_risk(self, agent: Agent) -> float:
        if agent.age > self.mp.old_age_mortality_start:
            return self.mp.old_age_mortality_rise * (
                agent.age - self.mp.old_age_mortality_start
            )
        return 0.0

    def _crowding_risk(self, env: Environment) -> float:
        risk = self.mp.crowding_mortality_bonus * max(0.0, env.density - 0.8)
        if env.sink_active and env.sink_factor > 0:
            sink_mort = env._full_config.environment.behavioral_sink_mortality_bonus
            risk += env.sink_factor * sink_mort
        return risk
