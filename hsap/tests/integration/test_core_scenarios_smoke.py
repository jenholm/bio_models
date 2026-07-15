import pytest
import numpy as np
from hsap.config import HSAPConfig
from hsap.simulation import Simulation
from hsap.scenarios import SCENARIO_SETS


SET1 = SCENARIO_SETS["Set1_HSAP_comparison"]["scenarios"]
SEEDS = [10, 42, 99]
STEPS = 100


@pytest.mark.integration
@pytest.mark.parametrize("scenario_name", list(SET1.keys()))
@pytest.mark.parametrize("seed", SEEDS)
def test_set1_scenario_runs_without_crash(scenario_name, seed):
    env_params = SET1[scenario_name]["environment"]
    cfg = HSAPConfig(random_seed=seed, max_steps=STEPS, initial_population=50)
    for k, v in env_params.items():
        setattr(cfg.environment, k, v)

    sim = Simulation(cfg)
    metrics = sim.run()
    df = metrics.to_dataframe()

    assert len(df) > 0, f"No records produced for {scenario_name} seed={seed}"
    assert "population" in df.columns


@pytest.mark.integration
@pytest.mark.parametrize("scenario_name", list(SET1.keys()))
@pytest.mark.parametrize("seed", SEEDS)
def test_set1_population_non_negative(scenario_name, seed):
    env_params = SET1[scenario_name]["environment"]
    cfg = HSAPConfig(random_seed=seed, max_steps=STEPS, initial_population=50)
    for k, v in env_params.items():
        setattr(cfg.environment, k, v)

    sim = Simulation(cfg)
    df = sim.run().to_dataframe()
    assert (df["population"] >= 0).all(), f"Negative population in {scenario_name} seed={seed}"


@pytest.mark.integration
@pytest.mark.parametrize("scenario_name", list(SET1.keys()))
@pytest.mark.parametrize("seed", SEEDS)
def test_set1_density_column_present(scenario_name, seed):
    env_params = SET1[scenario_name]["environment"]
    cfg = HSAPConfig(random_seed=seed, max_steps=STEPS, initial_population=50)
    for k, v in env_params.items():
        setattr(cfg.environment, k, v)

    sim = Simulation(cfg)
    df = sim.run().to_dataframe()
    assert "density" in df.columns
    assert (df["density"] >= 0).all()


@pytest.mark.integration
@pytest.mark.parametrize("scenario_name", list(SET1.keys()))
@pytest.mark.parametrize("seed", SEEDS)
def test_set1_metrics_valid(scenario_name, seed):
    env_params = SET1[scenario_name]["environment"]
    cfg = HSAPConfig(random_seed=seed, max_steps=STEPS, initial_population=50)
    for k, v in env_params.items():
        setattr(cfg.environment, k, v)

    sim = Simulation(cfg)
    df = sim.run().to_dataframe()

    assert "male_aggression" in df.columns
    assert "female_aggression" in df.columns
    assert "mean_fertility" in df.columns
    assert (df["male_aggression"] >= 0).all()
    assert (df["female_aggression"] >= 0).all()
    assert (df["mean_fertility"] >= 0).all()


@pytest.mark.integration
def test_set1_all_scenarios_produce_results():
    for scenario_name, scenario_def in SET1.items():
        env_params = scenario_def["environment"]
        cfg = HSAPConfig(random_seed=42, max_steps=STEPS, initial_population=50)
        for k, v in env_params.items():
            setattr(cfg.environment, k, v)

        sim = Simulation(cfg)
        df = sim.run().to_dataframe()
        assert len(df) > 0, f"{scenario_name} produced no records"
        assert df["population"].iloc[-1] >= 0
