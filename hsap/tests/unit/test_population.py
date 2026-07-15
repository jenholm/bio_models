import pytest
import numpy as np
from hsap.config import HSAPConfig
from hsap.entities import Agent
from hsap.environment import Environment
from hsap.population import PopulationDynamics
from hsap.simulation import Simulation


@pytest.fixture
def config():
    return HSAPConfig()


def test_age_structure(config):
    rng = np.random.default_rng(42)
    pop = PopulationDynamics(rng)
    agents = [
        Agent(0, "male", age=5, config=config, rng=rng),
        Agent(1, "female", age=20, config=config, rng=rng),
        Agent(2, "male", age=55, config=config, rng=rng),
    ]
    struct = pop.age_structure(agents)
    assert struct["juvenile"] == 1
    assert struct["adult"] == 1
    assert struct["senior"] == 1


def test_sex_ratio(config):
    rng = np.random.default_rng(42)
    pop = PopulationDynamics(rng)
    agents = [
        Agent(0, "male", config=config, rng=rng),
        Agent(1, "female", config=config, rng=rng),
        Agent(2, "male", config=config, rng=rng),
    ]
    ratio = pop.sex_ratio(agents)
    assert ratio == pytest.approx(2 / 3)


def test_simulation_runs(config):
    config.max_steps = 20
    config.initial_population = 20
    sim = Simulation(config)
    metrics = sim.run()
    df = metrics.to_dataframe()
    assert len(df) > 0
    assert "population" in df.columns


def test_population_does_not_go_negative(config):
    config.max_steps = 30
    config.initial_population = 10
    sim = Simulation(config)
    metrics = sim.run()
    df = metrics.to_dataframe()
    assert (df["population"] >= 0).all()


def test_run_rejects_preinitialized_simulation(config):
    config.max_steps = 1
    config.initial_population = 10
    sim = Simulation(config)
    sim.initialize()
    with pytest.raises(RuntimeError, match=".*agents already initialized.*"):
        sim.run(steps=1)
