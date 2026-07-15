import numpy as np
import pytest
from hsap.config import HSAPConfig
from hsap.entities import Agent
from hsap.environment import Environment
from hsap.reproduction import ReproductionEngine


def _make_pregnant_female(cfg, rng, survival_prob):
    female = Agent(0, "female", age=20, config=cfg, rng=rng)
    female.reset_dynamics(cfg)
    female.pregnant = True
    female.gestation_remaining = 1
    female.fertility = 0.9
    female.offspring_survival_probability = survival_prob
    return female


def test_high_survival_produces_offspring():
    cfg = HSAPConfig(random_seed=42)
    rng = np.random.default_rng(42)
    env = Environment(cfg, rng)
    repro = ReproductionEngine(cfg, rng)

    female = _make_pregnant_female(cfg, rng, survival_prob=1.0)
    total = 0
    for _ in range(50):
        female.pregnant = True
        female.gestation_remaining = 1
        female.fertility = 0.9
        female.offspring_survival_probability = 1.0
        offspring = repro.process_pregnancy(female, env)
        total += len(offspring)
    assert total > 0, "With survival_prob=1.0, there should be offspring"


def test_low_survival_produces_fewer_offspring():
    cfg = HSAPConfig(random_seed=42)
    rng_high = np.random.default_rng(42)
    rng_low = np.random.default_rng(42)
    env = Environment(cfg, rng_high)
    repro_high = ReproductionEngine(cfg, rng_high)
    repro_low = ReproductionEngine(cfg, rng_low)

    high_count = 0
    low_count = 0
    for _ in range(50):
        f_high = _make_pregnant_female(cfg, rng_high, survival_prob=1.0)
        offspring_high = repro_high.process_pregnancy(f_high, env)
        high_count += len(offspring_high)

        f_low = _make_pregnant_female(cfg, rng_low, survival_prob=0.1)
        offspring_low = repro_low.process_pregnancy(f_low, env)
        low_count += len(offspring_low)

    assert low_count < high_count, (
        f"Low survival ({low_count}) should produce fewer offspring than high ({high_count})"
    )


def test_zero_survival_produces_no_offspring():
    cfg = HSAPConfig(random_seed=42)
    rng = np.random.default_rng(42)
    env = Environment(cfg, rng)
    repro = ReproductionEngine(cfg, rng)

    for _ in range(30):
        female = _make_pregnant_female(cfg, rng, survival_prob=0.0)
        offspring = repro.process_pregnancy(female, env)
        assert len(offspring) == 0, "With survival_prob=0.0, no offspring should survive"


def test_offspring_survival_probability_clamped():
    cfg = HSAPConfig(random_seed=42)
    rng = np.random.default_rng(42)
    female = Agent(0, "female", age=20, config=cfg, rng=rng)
    female.reset_dynamics(cfg)
    assert 0.0 <= female.offspring_survival_probability <= 1.0
