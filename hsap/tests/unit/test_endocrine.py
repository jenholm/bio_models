import pytest
import numpy as np
from hsap.config import HSAPConfig
from hsap.entities import Agent
from hsap.environment import Environment
from hsap.endocrine import EndocrineSystem


@pytest.fixture
def config():
    return HSAPConfig()


@pytest.fixture
def rng():
    return np.random.default_rng(42)


def test_male_testosterone_downshift(config, rng):
    env = Environment(config, rng)
    endocrine = EndocrineSystem(config)
    agent = Agent(0, "male", rng=rng)
    agent.reset_dynamics(config)

    env.predator_pressure = 0.9
    endocrine.update(agent, env, env.density)
    high_T = agent.testosterone

    agent2 = Agent(1, "male", rng=rng)
    agent2.reset_dynamics(config)
    env.predator_pressure = 0.1
    endocrine.update(agent2, env, env.density)
    low_T = agent2.testosterone

    assert low_T <= high_T + 1e-6, (
        f"Expected lower T under low predation, got {low_T} vs {high_T}"
    )


def test_female_aggression_rises_with_offspring(config, rng):
    env = Environment(config, rng)
    endocrine = EndocrineSystem(config)
    agent = Agent(0, "female", rng=rng)
    agent.reset_dynamics(config)
    endocrine.update(agent, env, env.density)
    base_agg = agent.aggression_tendency

    agent.offspring_ids = [1, 2, 3]
    endocrine.update(agent, env, env.density)
    offspring_agg = agent.aggression_tendency

    assert offspring_agg >= base_agg - 1e-6


def test_cortisol_rises_with_density(config, rng):
    env = Environment(config, rng)
    endocrine = EndocrineSystem(config)
    agent = Agent(0, "male", rng=rng)
    agent.reset_dynamics(config)
    env.current_population = 10
    env.carrying_capacity = 100
    endocrine.update(agent, env, 0.1)
    low_C = agent.cortisol

    env.current_population = 90
    env.carrying_capacity = 100
    endocrine.update(agent, env, 0.9)
    high_C = agent.cortisol

    assert high_C >= low_C - 1e-6
