from __future__ import annotations
import numpy as np
from .entities import Agent
from .environment import Environment
from .config import HSAPConfig


class BehaviorEngine:
    def __init__(self, config: HSAPConfig, rng: np.random.Generator):
        self.bp = config.behavior
        self.rng = rng

    def choose_action(self, agent: Agent, env: Environment) -> str:
        density = env.density
        if agent.energy < self.bp.energy_forage_threshold:
            return "forage"
        if agent.sex == "female" and agent.offspring_ids and agent.cortisol > 0.6:
            return "guard_offspring"
        if self.rng.random() < agent.aggression_tendency * 0.3:
            return "dominance_event"
        if density > self.bp.dispersal_density_threshold and agent.age > 15:
            if self.rng.random() < 0.1:
                return "disperse"
        withdraw_prob = 0.3
        if getattr(env, 'sink_factor', 0.0) > 0:
            wd_bonus = getattr(env._full_config.environment, 'behavioral_sink_withdrawal_bonus', 0.0)
            withdraw_prob += env.sink_factor * wd_bonus
        if agent.cortisol > 0.7 and self.rng.random() < withdraw_prob:
            return "withdraw"
        if agent.energy > 0.7 and self.rng.random() < 0.1:
            return "cooperate"
        return "forage"

    def execute(self, agent: Agent, env: Environment) -> str:
        action = self.choose_action(agent, env)
        agent.guarding = False
        density = env.density
        if action == "forage":
            success = self.bp.base_forage_success + self.bp.rank_forage_bonus * agent.rank
            success -= env.resource_scarcity * 0.3
            if self.rng.random() < success:
                gained = 0.2 + self.rng.random() * 0.2
                agent.energy = min(1.0, agent.energy + gained)
            else:
                agent.energy -= 0.05 * (1.0 + density)

        elif action == "dominance_event":
            win_prob = 0.5 + self.bp.fight_win_rank_bonus * (
                agent.rank - 0.5
            ) + self.bp.fight_win_T_bonus * agent.testosterone
            if self.rng.random() < win_prob:
                agent.rank = min(1.0, agent.rank + 0.05)
                agent.energy -= self.bp.fight_energy_cost
            else:
                agent.rank = max(0.0, agent.rank - 0.05)
                agent.energy -= self.bp.fight_energy_cost * 1.5
                if self.rng.random() < self.bp.fight_injury_prob:
                    agent.injury = True
                    agent.injury_timer = 3
                    agent.health -= 0.2

        elif action == "disperse":
            agent.energy -= self.bp.dispersal_energy_cost
            agent.rank = max(0.0, agent.rank - 0.1)
            agent.dispersal_cooldown = 10

        elif action == "withdraw":
            agent.energy = min(1.0, agent.energy + self.bp.withdrawal_energy_save)
            agent.rank = max(0.0, agent.rank - 0.02)

        elif action == "cooperate":
            agent.energy += self.bp.cooperation_energy_bonus
            agent.cooperation_bonus = min(0.3, agent.cooperation_bonus + 0.02)

        elif action == "guard_offspring":
            agent.energy -= 0.1
            agent.guarding = True

        agent.energy = max(0.0, min(1.0, agent.energy))
        return action
