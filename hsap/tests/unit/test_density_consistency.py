import numpy as np
import pytest
from hsap.config import HSAPConfig
from hsap.simulation import Simulation


def test_recorded_density_matches_population():
    cfg = HSAPConfig(random_seed=1, max_steps=20)
    sim = Simulation(cfg)
    df = sim.run().to_dataframe()
    expected = df["population"] / cfg.environment.carrying_capacity
    assert np.allclose(df["density"], expected, atol=1e-10)


@pytest.mark.parametrize("seed", [10, 42, 99])
def test_density_matches_across_seeds(seed):
    cfg = HSAPConfig(random_seed=seed, max_steps=30)
    sim = Simulation(cfg)
    df = sim.run().to_dataframe()
    expected = df["population"] / cfg.environment.carrying_capacity
    assert np.allclose(df["density"], expected, atol=1e-10)


def test_density_non_negative():
    cfg = HSAPConfig(random_seed=7, max_steps=50)
    sim = Simulation(cfg)
    df = sim.run().to_dataframe()
    assert (df["density"] >= 0).all()


def test_density_reflects_carrying_capacity_change():
    cfg = HSAPConfig(random_seed=3, max_steps=15, initial_population=20)
    cfg.environment.carrying_capacity = 100
    sim = Simulation(cfg)
    df = sim.run().to_dataframe()
    expected = df["population"] / 100.0
    assert np.allclose(df["density"], expected, atol=1e-10)


def test_density_matches_population_with_refugees():
    """Density must match population/CC even when refugees are injected."""
    cfg = HSAPConfig(random_seed=0, max_steps=120, initial_population=50)
    cfg.environment.carrying_capacity = 50
    cfg.environment.resource_abundance = 0.2
    cfg.environment.resource_abundance_max = 0.3
    cfg.environment.behavioral_sink_on_threshold = 0.7
    cfg.environment.behavioral_sink_off_threshold = 0.5
    cfg.environment.behavioral_sink_min_duration = 3
    cfg.environment.behavioral_sink_mortality_bonus = 0.5
    cfg.environment.behavioral_sink_recovery_duration = 30
    cfg.environment.behavioral_sink_recovery_min_population = 45
    cfg.environment.behavioral_sink_recovery_refugee_count = 10
    cfg.mortality.base_mortality = 0.2
    cfg.age_increment = 0.5

    df = Simulation(cfg).run().to_dataframe()

    expected = df["population"] / cfg.environment.carrying_capacity
    assert np.allclose(df["density"], expected, atol=1e-10)
    assert df["refugees"].sum() > 0, "Test must trigger refugee injection"
