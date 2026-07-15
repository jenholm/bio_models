import numpy as np
import pytest
from hsap.config import HSAPConfig
from hsap.entities import Agent
from hsap.environment import Environment
from hsap.mortality import MortalityEngine


@pytest.fixture
def setup():
    cfg = HSAPConfig(random_seed=42)
    rng = np.random.default_rng(42)
    env = Environment(cfg, rng)
    engine = MortalityEngine(cfg, rng)
    return cfg, rng, env, engine


def _make_agent(cfg, rng, **kwargs):
    agent = Agent(0, "male", age=20, config=cfg, rng=rng)
    agent.reset_dynamics(cfg)
    for k, v in kwargs.items():
        setattr(agent, k, v)
    return agent


def test_predation_risk_non_negative(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng)
    risk = engine._predation_risk(agent, env)
    assert risk >= 0.0


def test_disease_risk_non_negative(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng)
    risk = engine._disease_risk(agent, env)
    assert risk >= 0.0


def test_starvation_risk_non_negative(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng, energy=0.01)
    risk = engine._starvation_risk(agent, env)
    assert risk >= 0.0


def test_starvation_risk_zero_when_energy_high(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng, energy=0.9)
    risk = engine._starvation_risk(agent, env)
    assert risk == 0.0


def test_injury_risk_non_negative(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng, injury=True)
    risk = engine._injury_risk(agent)
    assert risk >= 0.0


def test_injury_risk_zero_when_no_injury(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng, injury=False)
    risk = engine._injury_risk(agent)
    assert risk == 0.0


def test_old_age_risk_non_negative(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng, age=80)
    risk = engine._old_age_risk(agent)
    assert risk >= 0.0


def test_old_age_risk_zero_when_young(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng, age=10)
    risk = engine._old_age_risk(agent)
    assert risk == 0.0


def test_crowding_risk_non_negative(setup):
    cfg, rng, env, engine = setup
    risk = engine._crowding_risk(env)
    assert risk >= 0.0


def test_all_risks_non_negative_varied_agents(setup):
    cfg, rng, env, engine = setup
    ages = [0, 5, 20, 50, 80]
    energy_levels = [0.01, 0.3, 0.5, 0.9]
    injuries = [True, False]

    for age in ages:
        for energy in energy_levels:
            for inj in injuries:
                agent = _make_agent(cfg, rng, age=age, energy=energy, injury=inj)
                for risk_fn, label in [
                    (lambda: engine._predation_risk(agent, env), "predation"),
                    (lambda: engine._disease_risk(agent, env), "disease"),
                    (lambda: engine._starvation_risk(agent, env), "starvation"),
                    (lambda: engine._injury_risk(agent), "injury"),
                    (lambda: engine._old_age_risk(agent), "old_age"),
                    (lambda: engine._crowding_risk(env), "crowding"),
                ]:
                    val = risk_fn()
                    assert val >= 0.0, (
                        f"{label} risk negative: {val} for age={age}, energy={energy}, injury={inj}"
                    )


def test_total_death_probability_in_unit_interval(setup):
    cfg, rng, env, engine = setup
    ages = [0, 5, 20, 50, 70, 90]
    energy_levels = [0.01, 0.3, 0.6, 0.9]
    injuries = [True, False]

    for age in ages:
        for energy in energy_levels:
            for inj in injuries:
                agent = _make_agent(cfg, rng, age=age, energy=energy, injury=inj)
                prob = (
                    cfg.mortality.base_mortality
                    + engine._predation_risk(agent, env)
                    + engine._disease_risk(agent, env)
                    + engine._starvation_risk(agent, env)
                    + engine._injury_risk(agent)
                    + engine._old_age_risk(agent)
                    + engine._crowding_risk(env)
                )
                prob *= engine.time_scale
                prob *= env.mortality_multiplier
                assert 0.0 <= prob <= 1.0, (
                    f"Total prob {prob} out of [0,1] for age={age}, "
                    f"energy={energy}, injury={inj}"
                )


def test_check_death_returns_bool(setup):
    cfg, rng, env, engine = setup
    agent = _make_agent(cfg, rng)
    result = engine.check_death(agent, env)
    assert isinstance(result, bool)
