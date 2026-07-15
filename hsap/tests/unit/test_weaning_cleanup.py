import numpy as np
import pytest
from hsap.config import HSAPConfig
from hsap.entities import Agent
from hsap.population import PopulationDynamics


def _make_agent(rng, agent_id, sex="female", age=20):
    cfg = HSAPConfig()
    agent = Agent(agent_id=agent_id, sex=sex, age=age, config=cfg, rng=rng)
    agent.reset_dynamics(cfg)
    return agent


def test_dead_offspring_removed():
    rng = np.random.default_rng(42)
    pop = PopulationDynamics(rng)
    cfg = HSAPConfig()
    weaning_age = cfg.reproduction.weaning_age

    mother = _make_agent(rng, agent_id=0, sex="female", age=20)
    child = _make_agent(rng, agent_id=1, sex="female", age=2)
    child.alive = False

    mother.offspring_ids = [1]
    agents = [mother, child]

    pop.update_offspring_links(agents, weaning_age)
    assert 1 not in mother.offspring_ids, "Dead offspring should be removed from mother"


def test_weaned_offspring_removed():
    rng = np.random.default_rng(42)
    pop = PopulationDynamics(rng)
    cfg = HSAPConfig()
    weaning_age = cfg.reproduction.weaning_age

    mother = _make_agent(rng, agent_id=0, sex="female", age=30)
    child = _make_agent(rng, agent_id=1, sex="male", age=weaning_age + 5)

    mother.offspring_ids = [1]
    agents = [mother, child]

    pop.update_offspring_links(agents, weaning_age)
    assert 1 not in mother.offspring_ids, "Weaned offspring should be removed from mother"


def test_young_alive_offspring_kept():
    rng = np.random.default_rng(42)
    pop = PopulationDynamics(rng)
    cfg = HSAPConfig()
    weaning_age = cfg.reproduction.weaning_age

    mother = _make_agent(rng, agent_id=0, sex="female", age=30)
    child = _make_agent(rng, agent_id=1, sex="male", age=3)

    mother.offspring_ids = [1]
    agents = [mother, child]

    pop.update_offspring_links(agents, weaning_age)
    assert 1 in mother.offspring_ids, "Young alive offspring should remain linked"


def test_mixed_offspring_states():
    rng = np.random.default_rng(42)
    pop = PopulationDynamics(rng)
    cfg = HSAPConfig()
    weaning_age = cfg.reproduction.weaning_age

    mother = _make_agent(rng, agent_id=0, sex="female", age=30)
    baby_alive = _make_agent(rng, agent_id=1, sex="female", age=2)
    dead_child = _make_agent(rng, agent_id=2, sex="male", age=5)
    dead_child.alive = False
    weaned = _make_agent(rng, agent_id=3, sex="female", age=weaning_age + 3)

    mother.offspring_ids = [1, 2, 3]
    agents = [mother, baby_alive, dead_child, weaned]

    pop.update_offspring_links(agents, weaning_age)
    assert mother.offspring_ids == [1], (
        f"Only young alive offspring should remain, got {mother.offspring_ids}"
    )


def test_empty_offspring_ids_unchanged():
    rng = np.random.default_rng(42)
    pop = PopulationDynamics(rng)
    cfg = HSAPConfig()
    weaning_age = cfg.reproduction.weaning_age

    mother = _make_agent(rng, agent_id=0, sex="female", age=30)
    mother.offspring_ids = []
    agents = [mother]

    pop.update_offspring_links(agents, weaning_age)
    assert mother.offspring_ids == []


def test_child_not_in_agents_list_removed():
    rng = np.random.default_rng(42)
    pop = PopulationDynamics(rng)
    cfg = HSAPConfig()
    weaning_age = cfg.reproduction.weaning_age

    mother = _make_agent(rng, agent_id=0, sex="female", age=30)
    mother.offspring_ids = [99]  # ID 99 does not exist in agents

    agents = [mother]
    pop.update_offspring_links(agents, weaning_age)
    assert 99 not in mother.offspring_ids, "Offspring not in agents list should be removed"
