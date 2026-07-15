import pytest

deap = pytest.importorskip("deap")

import numpy as np
from hsap.config import HSAPConfig
from hsap.ga import (
    param_keys,
    individual_from_dict,
    dict_from_individual,
    apply_to_config,
    hsap_support_fitness,
    hsap_falsification_fitness,
)


@pytest.fixture
def config():
    return HSAPConfig(random_seed=42)


def test_param_keys_consistent():
    keys = param_keys()
    assert len(keys) > 0
    assert all("__" in k for k in keys)


def test_round_trip_individual(config):
    keys = param_keys()
    d = {k: 0.5 for k in keys}
    ind = individual_from_dict(d)
    d2 = dict_from_individual(ind)
    for k in keys:
        assert abs(d2[k] - d[k]) < 1e-6, f"Mismatch for {k}: {d2[k]} vs {d[k]}"


def test_apply_to_config(config):
    cfg = apply_to_config(config, {"endocrine__base_male_testosterone": 2.0})
    assert cfg.endocrine.base_male_testosterone == pytest.approx(2.0)


def test_support_fitness_runs(config):
    keys = param_keys()
    ind = [0.5] * len(keys)
    fitness = hsap_support_fitness(ind, config, n_steps=10)
    assert isinstance(fitness, tuple)
    assert len(fitness) == 1
    assert isinstance(fitness[0], float)


def test_falsification_fitness_runs(config):
    keys = param_keys()
    ind = [0.5] * len(keys)
    fitness = hsap_falsification_fitness(ind, config, n_steps=10)
    assert isinstance(fitness, tuple)
    assert len(fitness) == 1
    assert isinstance(fitness[0], float)
