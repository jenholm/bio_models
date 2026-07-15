from __future__ import annotations
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class EndocrineParams(BaseModel):
    base_male_testosterone: float = 1.0
    base_female_testosterone: float = 0.3
    base_estrogen: float = 1.0
    base_cortisol: float = 0.5

    dominance_T_bonus: float = 0.3
    mating_competition_T_bonus: float = 0.4
    crowding_T_penalty: float = 0.3
    low_threat_T_downshift: float = 0.4
    poor_condition_T_penalty: float = 0.2

    offspring_aggression_bonus: float = 0.5
    resource_competition_aggression_bonus: float = 0.4
    density_aggression_bonus: float = 0.3
    endocrine_sensitivity_female: float = 0.5

    stress_cortisol_rise: float = 0.05
    rank_stress_buffer: float = 0.3
    health_stress_amplifier: float = 0.5

    fertility_T_penalty: float = 0.2
    fertility_cortisol_penalty: float = 0.3
    fertility_age_decline: float = 0.02
    reproductive_restraint_density_threshold: float = 0.7
    reproductive_restraint_max: float = 0.5

    offspring_survival_T_effect: float = 0.1
    offspring_survival_cortisol_penalty: float = 0.2


class BehaviorParams(BaseModel):
    base_forage_success: float = 0.7
    rank_forage_bonus: float = 0.15
    energy_forage_threshold: float = 0.3
    fight_win_rank_bonus: float = 0.2
    fight_win_T_bonus: float = 0.15
    fight_energy_cost: float = 0.15
    fight_injury_prob: float = 0.1
    dispersal_energy_cost: float = 0.3
    dispersal_density_threshold: float = 0.6
    cooperation_energy_bonus: float = 0.05
    withdrawal_energy_save: float = 0.05


class ReproductionParams(BaseModel):
    gestation_time: int = 5
    litter_size_mean: float = 4.0
    litter_size_std: float = 1.0
    mating_energy_threshold: float = 0.4
    post_partum_energy_cost: float = 0.3
    weaning_age: int = 10
    infanticide_density_threshold: float = 0.8
    infanticide_rate: float = 0.05
    offspring_neglect_density_threshold: float = 0.7
    offspring_neglect_cortisol_threshold: float = 0.7


class MortalityParams(BaseModel):
    base_mortality: float = 0.02
    predation_mortality_base: float = 0.05
    disease_mortality_base: float = 0.03
    starvation_mortality_threshold: float = 0.2
    starvation_mortality_max: float = 0.3
    injury_mortality_bonus: float = 0.1
    old_age_mortality_start: int = 50
    old_age_mortality_rise: float = 0.01
    infanticide_mortality: float = 0.1
    crowding_mortality_bonus: float = 0.05


class EnvironmentParams(BaseModel):
    resource_abundance: float = 1.0
    resource_abundance_max: float = 2.0
    resource_regeneration_rate: float = 0.05
    predator_pressure: float = 0.5
    disease_pressure: float = 0.3
    carrying_capacity: int = 500
    space_constraint: float = 0.5
    seasonality: float = 0.0
    territory_availability: float = 1.0
    # Sink hysteresis — on/off thresholds with time-based auto-recovery
    behavioral_sink_on_threshold: float = 0.75
    behavioral_sink_off_threshold: float = 0.50
    behavioral_sink_min_duration: int = 30
    behavioral_sink_auto_recovery_duration: int | None = None
    behavioral_sink_fertility_penalty: float = 0.85
    behavioral_sink_neglect_bonus: float = 0.25
    behavioral_sink_withdrawal_bonus: float = 0.25
    behavioral_sink_mating_penalty: float = 0.4
    behavioral_sink_mortality_bonus: float = 0.0
    # Post-sink recovery
    behavioral_sink_recovery_duration: int = 100
    behavioral_sink_recovery_fertility_boost: float = 0.3
    behavioral_sink_recovery_mating_boost: float = 0.3
    behavioral_sink_recovery_female_fertility_gate: float = 0.15
    behavioral_sink_recovery_mortality_relief: float = 0.4
    behavioral_sink_recovery_min_population: int = 30
    behavioral_sink_recovery_refugee_count: int = 10


class GAParams(BaseModel):
    population_size: int = 50
    generations: int = 30
    cx_prob: float = 0.7
    mut_prob: float = 0.2
    mut_eta: float = 20.0
    cx_eta: float = 20.0
    tournament_size: int = 3


class HSAPConfig(BaseModel):
    random_seed: Optional[int] = None
    max_steps: int = 500
    initial_population: int = 50
    age_increment: float = 0.1

    endocrine: EndocrineParams = Field(default_factory=EndocrineParams)
    behavior: BehaviorParams = Field(default_factory=BehaviorParams)
    reproduction: ReproductionParams = Field(default_factory=ReproductionParams)
    mortality: MortalityParams = Field(default_factory=MortalityParams)
    environment: EnvironmentParams = Field(default_factory=EnvironmentParams)
    ga: GAParams = Field(default_factory=GAParams)


def load_config(path: str) -> HSAPConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return HSAPConfig.model_validate(raw)


def config_from_dict(d: dict) -> HSAPConfig:
    return HSAPConfig.model_validate(d)
