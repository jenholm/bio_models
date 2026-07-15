"""Ablation models for HSAP — systematically removed mechanisms.

Each ablation function takes an HSAPConfig, modifies the relevant
parameters to disable a specific mechanism, and returns the modified config.
"""

from __future__ import annotations
from .config import HSAPConfig


def hsap_full(cfg: HSAPConfig | None = None) -> HSAPConfig:
    """Full HSAP model — no ablation."""
    return (cfg or HSAPConfig()).model_copy(deep=True)


def no_male_T_downshift(cfg: HSAPConfig | None = None) -> HSAPConfig:
    """Remove low-threat testosterone downshift."""
    c = (cfg or HSAPConfig()).model_copy(deep=True)
    c.endocrine.low_threat_T_downshift = 0.0
    return c


def no_female_aggression_channel(cfg: HSAPConfig | None = None) -> HSAPConfig:
    """Remove female aggression as a response channel.

    Female aggression tendency disconnected from T and maternal defense.
    """
    c = (cfg or HSAPConfig()).model_copy(deep=True)
    c.endocrine.offspring_aggression_bonus = 0.0
    c.endocrine.resource_competition_aggression_bonus = 0.0
    c.endocrine.density_aggression_bonus = 0.0
    c.endocrine.endocrine_sensitivity_female = 0.0
    return c


def no_reproductive_restraint(cfg: HSAPConfig | None = None) -> HSAPConfig:
    """Remove density-dependent reproductive restraint."""
    c = (cfg or HSAPConfig()).model_copy(deep=True)
    c.endocrine.reproductive_restraint_max = 0.0
    c.endocrine.reproductive_restraint_density_threshold = 1.0
    c.endocrine.fertility_T_penalty = 0.0
    c.endocrine.fertility_cortisol_penalty = 0.0
    return c


def no_cortisol(cfg: HSAPConfig | None = None) -> HSAPConfig:
    """Remove cortisol stress response.

    Base cortisol set to 0, stress and health amplifiers zeroed.
    """
    c = (cfg or HSAPConfig()).model_copy(deep=True)
    c.endocrine.base_cortisol = 0.0
    c.endocrine.stress_cortisol_rise = 0.0
    c.endocrine.health_stress_amplifier = 0.0
    c.endocrine.rank_stress_buffer = 0.0
    c.endocrine.fertility_cortisol_penalty = 0.0
    c.endocrine.offspring_survival_cortisol_penalty = 0.0
    return c


def no_sink_recovery(cfg: HSAPConfig | None = None) -> HSAPConfig:
    """Disable behavioral sink recovery mechanism.

    Sink can activate but never transitions to recovery.
    """
    c = (cfg or HSAPConfig()).model_copy(deep=True)
    c.environment.behavioral_sink_recovery_duration = 0
    c.environment.behavioral_sink_recovery_fertility_boost = 0.0
    c.environment.behavioral_sink_recovery_mating_boost = 0.0
    c.environment.behavioral_sink_recovery_mortality_relief = 0.0
    c.environment.behavioral_sink_recovery_min_population = 0
    c.environment.behavioral_sink_recovery_refugee_count = 0
    return c


def no_endocrine_responsiveness(cfg: HSAPConfig | None = None) -> HSAPConfig:
    """Remove all endocrine-environment feedback.

    Hormones stay at base levels regardless of external conditions.
    """
    c = (cfg or HSAPConfig()).model_copy(deep=True)
    # Zero all endocrine modifiers
    c.endocrine.dominance_T_bonus = 0.0
    c.endocrine.mating_competition_T_bonus = 0.0
    c.endocrine.crowding_T_penalty = 0.0
    c.endocrine.low_threat_T_downshift = 0.0
    c.endocrine.poor_condition_T_penalty = 0.0
    c.endocrine.offspring_aggression_bonus = 0.0
    c.endocrine.resource_competition_aggression_bonus = 0.0
    c.endocrine.density_aggression_bonus = 0.0
    c.endocrine.endocrine_sensitivity_female = 0.0
    c.endocrine.stress_cortisol_rise = 0.0
    c.endocrine.health_stress_amplifier = 0.0
    c.endocrine.fertility_T_penalty = 0.0
    c.endocrine.fertility_cortisol_penalty = 0.0
    c.endocrine.reproductive_restraint_max = 0.0
    return c


# Registry for convenient access
ABLATION_REGISTRY = {
    "HSAP_full": hsap_full,
    "HSAP_no_male_T_downshift": no_male_T_downshift,
    "HSAP_no_female_aggression_channel": no_female_aggression_channel,
    "HSAP_no_reproductive_restraint": no_reproductive_restraint,
    "HSAP_no_cortisol": no_cortisol,
    "HSAP_no_sink_recovery": no_sink_recovery,
    "HSAP_no_endocrine_responsiveness": no_endocrine_responsiveness,
}
