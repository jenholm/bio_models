from __future__ import annotations
from typing import Optional
import numpy as np
from .config import HSAPConfig


class Agent:
    __slots__ = (
        "agent_id",
        "sex",
        "age",
        "energy",
        "rank",
        "territory_quality",
        "health",
        "stress",
        "testosterone",
        "estrogen",
        "cortisol",
        "aggression_tendency",
        "maternal_defense_tendency",
        "mating_drive",
        "fertility",
        "offspring_survival_probability",
        "pregnant",
        "gestation_remaining",
        "offspring_ids",
        "alive",
        "injury",
        "injury_timer",
        "dispersal_cooldown",
        "cooperation_bonus",
        "guarding",
        "_rng",
    )

    def __init__(
        self,
        agent_id: int,
        sex: str,
        age: int = 0,
        config: Optional[HSAPConfig] = None,
        rng: Optional[np.random.Generator] = None,
    ):
        self.agent_id = agent_id
        self.sex = sex
        self.age = age
        self.energy = 1.0
        self.rank = 0.5
        self.territory_quality = 0.5
        self.health = 1.0
        self.stress = 0.0
        self.testosterone = 0.0
        self.estrogen = 0.0
        self.cortisol = 0.0
        self.aggression_tendency = 0.0
        self.maternal_defense_tendency = 0.0
        self.mating_drive = 0.0
        self.fertility = 0.0
        self.offspring_survival_probability = 0.0
        self.pregnant = False
        self.gestation_remaining = 0
        self.offspring_ids: list[int] = []
        self.alive = True
        self.injury = False
        self.injury_timer = 0
        self.dispersal_cooldown = 0
        self.cooperation_bonus = 0.0
        self.guarding = False
        self._rng = rng or np.random.default_rng()

    def reset_dynamics(self, config: HSAPConfig):
        ep = config.endocrine
        if self.sex == "male":
            self.testosterone = float(
                self._rng.normal(ep.base_male_testosterone, 0.15)
            )
            self.estrogen = float(self._rng.normal(ep.base_estrogen * 0.3, 0.05))
        else:
            self.testosterone = float(
                self._rng.normal(ep.base_female_testosterone, 0.05)
            )
            self.estrogen = float(self._rng.normal(ep.base_estrogen, 0.15))
        self.cortisol = float(self._rng.normal(ep.base_cortisol, 0.1))
        self._clamp()

    def _clamp(self):
        for attr in (
            "testosterone",
            "estrogen",
            "cortisol",
            "aggression_tendency",
            "maternal_defense_tendency",
            "mating_drive",
            "fertility",
            "offspring_survival_probability",
            "energy",
            "health",
            "stress",
            "rank",
            "territory_quality",
        ):
            v = getattr(self, attr, 0.0)
            setattr(self, attr, max(0.0, min(1.0, v)))

    @property
    def is_adult(self) -> bool:
        return self.age >= 10

    @property
    def is_reproductive_age(self) -> bool:
        return 10 <= self.age <= 60

    def step_age(self, increment: float = 1.0):
        self.age += increment
