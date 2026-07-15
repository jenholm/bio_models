import numpy as np
import pytest
from hsap.config import HSAPConfig
from hsap.simulation import Simulation


def _cfg_with_recovery(refugee_count=10, min_population=30, recovery_duration=60):
    cfg = HSAPConfig(random_seed=42, max_steps=200, initial_population=10)
    cfg.environment.behavioral_sink_on_threshold = 0.3
    cfg.environment.behavioral_sink_off_threshold = 0.2
    cfg.environment.behavioral_sink_min_duration = 5
    cfg.environment.behavioral_sink_fertility_penalty = 0.95
    cfg.environment.behavioral_sink_mortality_bonus = 0.1
    cfg.environment.behavioral_sink_recovery_duration = recovery_duration
    cfg.environment.behavioral_sink_recovery_fertility_boost = 0.6
    cfg.environment.behavioral_sink_recovery_mating_boost = 0.4
    cfg.environment.behavioral_sink_recovery_female_fertility_gate = 0.1
    cfg.environment.behavioral_sink_recovery_mortality_relief = 0.3
    cfg.environment.behavioral_sink_recovery_min_population = min_population
    cfg.environment.behavioral_sink_recovery_refugee_count = refugee_count
    return cfg


def test_refugee_count_bounded_by_min_population():
    cfg = _cfg_with_recovery(refugee_count=20, min_population=30)
    sim = Simulation(cfg)
    metrics = sim.run()
    df = metrics.to_dataframe()

    total_refugees = df["refugees"].sum()
    if total_refugees > 0:
        refugee_steps = df[df["refugees"] > 0]
        for _, row in refugee_steps.iterrows():
            assert row["refugees"] <= cfg.environment.behavioral_sink_recovery_refugee_count


def test_refugees_do_not_overshoot_min_population():
    cfg = _cfg_with_recovery(refugee_count=15, min_population=30)
    sim = Simulation(cfg)
    metrics = sim.run()
    df = metrics.to_dataframe()

    # After any refugee injection step, population should not exceed
    # min_population + refugee_count (one batch overshoot at most)
    refugee_steps = df[df["refugees"] > 0]
    for _, row in refugee_steps.iterrows():
        pop_after = row["population"]
        assert pop_after <= cfg.environment.behavioral_sink_recovery_min_population + cfg.environment.behavioral_sink_recovery_refugee_count, (
            f"Population {pop_after} exceeds min_pop + refugee_count by more than expected"
        )


def test_no_refugees_without_recovery():
    cfg = HSAPConfig(random_seed=42, max_steps=50, initial_population=50)
    cfg.environment.behavioral_sink_recovery_duration = 0
    cfg.environment.behavioral_sink_recovery_min_population = 0
    cfg.environment.behavioral_sink_recovery_refugee_count = 0
    sim = Simulation(cfg)
    df = sim.run().to_dataframe()
    assert df["refugees"].sum() == 0


def test_refugee_injection_never_exceeds_min_by_one_batch():
    cfg = _cfg_with_recovery(refugee_count=5, min_population=25)
    sim = Simulation(cfg)
    metrics = sim.run()
    df = metrics.to_dataframe()

    max_refugees_in_step = df["refugees"].max()
    assert max_refugees_in_step <= cfg.environment.behavioral_sink_recovery_refugee_count
