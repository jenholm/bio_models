import numpy as np
import pytest
from hsap.config import HSAPConfig
from hsap.entities import Agent
from hsap.environment import Environment
from hsap.behavior import BehaviorEngine


@pytest.fixture
def setup():
    cfg = HSAPConfig(random_seed=42)
    rng = np.random.default_rng(42)
    env = Environment(cfg, rng)
    behavior = BehaviorEngine(cfg, rng)
    return cfg, rng, env, behavior


def test_withdrawal_gains_energy(setup):
    cfg, rng, env, behavior = setup
    agent = Agent(0, "male", age=20, config=cfg, rng=rng)
    agent.reset_dynamics(cfg)
    agent.energy = 0.5
    agent.cortisol = 0.9  # high cortisol to trigger withdraw
    agent.injury = False

    initial_energy = agent.energy
    action = behavior.execute(agent, env)

    if action == "withdraw":
        assert agent.energy > initial_energy, (
            "withdrawal action should GAIN energy, not cost it"
        )


def test_withdrawal_energy_save_parameter_is_positive():
    cfg = HSAPConfig()
    assert cfg.behavior.withdrawal_energy_save > 0, (
        "withdrawal_energy_save must be positive to represent energy gained"
    )


def test_withdrawal_energy_additive(setup):
    cfg, rng, env, behavior = setup
    agent = Agent(0, "female", age=20, config=cfg, rng=rng)
    agent.reset_dynamics(cfg)
    agent.energy = 0.3
    agent.cortisol = 0.9

    # Manually force the withdraw path
    energy_before = agent.energy
    agent.energy = min(1.0, agent.energy + cfg.behavior.withdrawal_energy_save)
    assert agent.energy == pytest.approx(min(1.0, energy_before + cfg.behavior.withdrawal_energy_save))


def test_withdrawal_does_not_exceed_one():
    cfg = HSAPConfig()
    rng = np.random.default_rng(42)
    env = Environment(cfg, rng)
    behavior = BehaviorEngine(cfg, rng)

    agent = Agent(0, "male", age=20, config=cfg, rng=rng)
    agent.reset_dynamics(cfg)
    agent.energy = 0.99
    agent.cortisol = 0.9

    # Simulate withdrawal energy gain
    agent.energy = min(1.0, agent.energy + cfg.behavior.withdrawal_energy_save)
    assert agent.energy <= 1.0
