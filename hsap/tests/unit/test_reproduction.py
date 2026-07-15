import pytest
import numpy as np
from hsap.config import HSAPConfig
from hsap.entities import Agent
from hsap.environment import Environment
from hsap.reproduction import ReproductionEngine


@pytest.fixture
def config():
    return HSAPConfig()


@pytest.fixture
def rng():
    return np.random.default_rng(42)


def test_mating_success(config, rng):
    env = Environment(config, rng)
    repro = ReproductionEngine(config, rng)
    male = Agent(0, "male", age=20, rng=rng)
    male.reset_dynamics(config)
    male.fertility = 0.8
    male.mating_drive = 0.7
    male.energy = 0.8
    female = Agent(1, "female", age=20, rng=rng)
    female.reset_dynamics(config)
    female.fertility = 0.8
    female.energy = 0.8
    result = repro.mate(male, female, env)
    assert isinstance(result, bool)


def test_pregnancy_and_birth(config, rng):
    env = Environment(config, rng)
    repro = ReproductionEngine(config, rng)
    female = Agent(0, "female", rng=rng)
    female.reset_dynamics(config)
    female.pregnant = True
    female.gestation_remaining = 1
    female.fertility = 0.8
    offspring = repro.process_pregnancy(female, env)
    assert isinstance(offspring, list)
    assert not female.pregnant


def test_infanticide_check(config, rng):
    env = Environment(config, rng)
    repro = ReproductionEngine(config, rng)
    agent = Agent(0, "male", rng=rng)
    agent.reset_dynamics(config)
    agent.aggression_tendency = 0.9
    env.carrying_capacity = 100
    env.current_population = 95
    result = repro.check_infanticide(agent, env)
    assert isinstance(result, bool)
