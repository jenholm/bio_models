import pytest
import numpy as np
from hsap.config import HSAPConfig, EnvironmentParams
from hsap.null_models import (
    NullModelSuite,
    NullModelResult,
    compare_to_null,
)


@pytest.fixture
def env_params():
    return EnvironmentParams(
        carrying_capacity=500,
        predator_pressure=0.5,
        disease_pressure=0.3,
        resource_abundance=1.0,
    )


@pytest.fixture
def config():
    return HSAPConfig()


def test_null_model_suite_runs(env_params):
    rng = np.random.default_rng(42)
    suite = NullModelSuite(env_params, 50, rng)
    results = suite.run_all(steps=50)
    assert len(results) == 11
    for name, result in results.items():
        assert isinstance(result, NullModelResult)
        assert len(result.population_ts) == 51


def test_logistic_growth(env_params):
    rng = np.random.default_rng(42)
    suite = NullModelSuite(env_params, 50, rng)
    result = suite._logistic_growth(50)
    assert result.final_population >= 0
    assert result.max_population >= 0


def test_compare_to_null(config):
    rng = np.random.default_rng(42)
    suite = NullModelSuite(config.environment, config.initial_population, rng)
    null_results = suite.run_all(steps=30)
    hsap_ts = list(range(31))
    comparisons = compare_to_null(hsap_ts, config, null_results)
    assert len(comparisons) == 11
    for model_name, metrics in comparisons.items():
        assert "mse" in metrics
        assert "final_diff" in metrics
