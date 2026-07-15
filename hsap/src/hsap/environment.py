from __future__ import annotations
import numpy as np
from .config import HSAPConfig


class Environment:
    def __init__(self, config: HSAPConfig, rng: np.random.Generator):
        self._full_config = config
        self.cfg = config.environment
        self.rng = rng
        self.resource_abundance = float(self.cfg.resource_abundance)
        self.resource_abundance_max = float(self.cfg.resource_abundance_max)
        self.resource_regeneration_rate = float(self.cfg.resource_regeneration_rate)
        self.predator_pressure = float(self.cfg.predator_pressure)
        self.disease_pressure = float(self.cfg.disease_pressure)
        self.carrying_capacity = int(self.cfg.carrying_capacity)
        self.space_constraint = float(self.cfg.space_constraint)
        self.seasonality = float(self.cfg.seasonality)
        self.territory_availability = float(self.cfg.territory_availability)
        self.current_population: int = 0
        self.time: int = 0
        # Sink hysteresis state
        self.sink_active: bool = False
        self.sink_active_steps: int = 0
        self.post_sink_recovery: bool = False
        self.recovery_steps_remaining: int = 0
        self.sink_factor: float = 0.0

    def step(self, population_size: int):
        self.time += 1
        self.current_population = population_size
        density = population_size / max(self.carrying_capacity, 1)
        seasonal_factor = 1.0 + self.seasonality * np.sin(
            2 * np.pi * self.time / 365
        )
        self.resource_abundance = max(
            0.0,
            self.resource_abundance
            + self.resource_regeneration_rate * (1.0 - density)
            - 0.01 * density * (not self._is_regenerating()),
        )
        self.resource_abundance *= seasonal_factor
        self.resource_abundance = min(self.resource_abundance_max, self.resource_abundance)
        self.territory_availability = max(0.0, 1.0 - density * self.space_constraint)
        self._update_sink_state(density)

    def _update_sink_state(self, density: float):
        ep = self._full_config.environment

        # Post-sink recovery: count down and then exit
        if self.post_sink_recovery:
            self.sink_factor = 0.0
            self.recovery_steps_remaining -= 1
            if self.recovery_steps_remaining <= 0:
                self.post_sink_recovery = False
            return

        # Currently in sink
        if self.sink_active:
            self.sink_active_steps += 1
            # Minimum duration must be satisfied before any exit
            minimum_satisfied = self.sink_active_steps >= ep.behavioral_sink_min_duration
            density_exit = minimum_satisfied and density < ep.behavioral_sink_off_threshold
            auto_recovery = (
                ep.behavioral_sink_auto_recovery_duration is not None
                and self.sink_active_steps >= ep.behavioral_sink_auto_recovery_duration
            )
            if density_exit or auto_recovery:
                self.sink_active = False
                self.sink_active_steps = 0
                if ep.behavioral_sink_recovery_duration > 0:
                    self.post_sink_recovery = True
                    self.recovery_steps_remaining = ep.behavioral_sink_recovery_duration
                self.sink_factor = 0.0
            else:
                # Still in sink — compute factor
                thresh = ep.behavioral_sink_on_threshold
                if density > thresh:
                    self.sink_factor = min(1.0, (density - thresh) / (1.0 - thresh))
                else:
                    self.sink_factor = 0.0
        else:
            # Normal — check entry condition
            if density > ep.behavioral_sink_on_threshold:
                self.sink_active = True
                self.sink_active_steps = 0
                thresh = ep.behavioral_sink_on_threshold
                self.sink_factor = min(1.0, (density - thresh) / (1.0 - thresh))
            else:
                self.sink_factor = 0.0

    @property
    def recovery_active(self) -> bool:
        return self.post_sink_recovery

    @property
    def mortality_multiplier(self) -> float:
        ep = self._full_config.environment
        if self.post_sink_recovery:
            return ep.behavioral_sink_recovery_mortality_relief
        return 1.0

    def _is_regenerating(self) -> bool:
        return self.rng.random() < self.resource_regeneration_rate

    def sync_population(self, population_size: int) -> None:
        """Update population and derived quantities after all population changes."""
        self.current_population = population_size
        density = self.density
        self.territory_availability = max(
            0.0,
            1.0 - density * self.space_constraint,
        )

    @property
    def density(self) -> float:
        return self.current_population / max(self.carrying_capacity, 1)

    @property
    def predation_risk(self) -> float:
        return self.predator_pressure * (1.0 + 0.5 * self.density)

    @property
    def disease_risk(self) -> float:
        return self.disease_pressure * (1.0 + 0.5 * self.density)

    @property
    def resource_scarcity(self) -> float:
        return max(0.0, 1.0 - self.resource_abundance)
