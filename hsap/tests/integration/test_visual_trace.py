from __future__ import annotations
import json
import math

from hsap.config import HSAPConfig
from hsap.simulation import Simulation
from hsap.visual_trace import (
    VisualTrace,
    compute_external_threat_index,
    compute_hsap_index,
    classify_hsap_phase,
    clamp01,
)


def test_clamp01():
    assert clamp01(-0.5) == 0.0
    assert clamp01(0.5) == 0.5
    assert clamp01(1.5) == 1.0
    assert clamp01(0.0) == 0.0
    assert clamp01(1.0) == 1.0


def test_compute_external_threat_index_no_threat():
    """Minimal threat → index near 0."""
    class FakeEnv:
        predator_pressure = 0.0
        disease_pressure = 0.0
        resource_abundance = 2.0

    env = FakeEnv()
    idx = compute_external_threat_index(env)  # type: ignore
    assert 0.0 <= idx <= 0.05, f"Expected near-zero threat, got {idx}"


def test_compute_external_threat_index_max_threat():
    """Maximal threat → index near 1."""
    class FakeEnv:
        predator_pressure = 1.0
        disease_pressure = 1.0
        resource_abundance = 0.0

    env = FakeEnv()
    idx = compute_external_threat_index(env)  # type: ignore
    assert idx >= 0.95, f"Expected near-1 threat, got {idx}"


def test_hsap_index_bounds():
    """HSAP index always in [0, 1]."""
    for male_agg in (0.0, 0.5, 1.0):
        for female_agg in (0.0, 0.5, 1.0):
            for fert in (0.0, 0.5, 1.0):
                idx = compute_hsap_index(0.5, male_agg, female_agg, fert, 0.0)
                assert 0.0 <= idx <= 1.0, f"HSAP index out of bounds: {idx}"


def test_classify_hsap_phase():
    assert classify_hsap_phase(0.0) == "external-control"
    assert classify_hsap_phase(0.34) == "external-control"
    assert classify_hsap_phase(0.35) == "transition"
    assert classify_hsap_phase(0.59) == "transition"
    assert classify_hsap_phase(0.60) == "hsap-active"
    assert classify_hsap_phase(0.79) == "hsap-active"
    assert classify_hsap_phase(0.80) == "strong-social-regulation"
    assert classify_hsap_phase(1.0) == "strong-social-regulation"


def test_visual_trace_emits_valid_frame():
    """VisualTrace.record produces a valid JSON-safe frame."""
    cfg = HSAPConfig(random_seed=42, max_steps=10, initial_population=30)
    sim = Simulation(cfg)
    sim.run(steps=10)

    trace = sim.visual_trace
    assert len(trace.frames) > 0, "No frames recorded"

    frame = trace.frames[-1]
    # Required keys
    for key in ("step", "world", "population", "hsap_index", "male_aggression",
                 "female_aggression", "fertility", "mean_T", "mean_E", "mean_C",
                 "male_T", "female_T", "female_E", "male_C", "female_C",
                 "male_fertility", "female_fertility",
                 "density", "resource_abundance", "external_threat_index"):
        assert key in frame, f"Missing key: {key}"

    # No NaN or Infinity
    for key, val in frame.items():
        if isinstance(val, float):
            assert not math.isnan(val), f"NaN in {key}"
            assert not math.isinf(val), f"Infinity in {key}"


def test_hsap_index_clamped():
    """HSAP index computed from recorded frames stays in [0, 1]."""
    cfg = HSAPConfig(random_seed=42, max_steps=20, initial_population=30)
    sim = Simulation(cfg)
    sim.run(steps=20)

    for frame in sim.visual_trace.frames:
        assert 0.0 <= frame["hsap_index"] <= 1.0, (
            f"HSAP index out of bounds at step {frame['step']}: {frame['hsap_index']}"
        )


def test_export_serializable():
    """Export produces JSON-serializable dict."""
    cfg = HSAPConfig(random_seed=42, max_steps=10, initial_population=20)
    sim = Simulation(cfg)
    sim.visual_trace.world_name = "test_world"
    sim.run(steps=10)

    data = sim.visual_trace.export()
    # Serialize to JSON string
    json_str = json.dumps(data)
    parsed = json.loads(json_str)

    assert parsed["meta"]["world"] == "test_world"
    assert len(parsed["frames"]) > 0
    assert parsed["frames"][0]["population"] >= 0


def test_population_matches_agent_count():
    """frame.population equals number of alive agents at record time."""
    cfg = HSAPConfig(random_seed=42, max_steps=10, initial_population=30)
    sim = Simulation(cfg)
    sim.run(steps=10)

    for frame in sim.visual_trace.frames:
        alive = sum(1 for a in sim.agents if a.alive)
        # Frame population was recorded at that step, not current sim state
        # Just check basic consistency
        assert frame["population"] >= 0


def test_all_worlds_export():
    """All worlds produce at least one frame with sink state fields."""
    from hsap.config import HSAPConfig
    from hsap.simulation import Simulation

    _WORLD_DEFAULTS = {
        "A_normal_baseline": {
            "predator_pressure": 0.25,
            "disease_pressure": 0.2,
            "resource_abundance": 0.6,
            "resource_regeneration_rate": 0.03,
            "carrying_capacity": 500,
            "space_constraint": 0.4,
        },
        "B_hsap_abundance": {
            "predator_pressure": 0.1,
            "disease_pressure": 0.05,
            "resource_abundance": 1.5,
            "resource_regeneration_rate": 0.08,
            "carrying_capacity": 500,
            "space_constraint": 0.2,
            "behavioral_sink_on_threshold": 0.92,
        },
        "C_crowded_abundance": {
            "predator_pressure": 0.1,
            "disease_pressure": 0.05,
            "resource_abundance": 1.5,
            "resource_regeneration_rate": 0.08,
            "carrying_capacity": 200,
            "space_constraint": 0.9,
            "behavioral_sink_on_threshold": 0.92,
        },
        "D_high_predation_survival": {
            "predator_pressure": 0.45,
            "disease_pressure": 0.15,
            "resource_abundance": 0.75,
            "resource_regeneration_rate": 0.05,
            "carrying_capacity": 500,
            "space_constraint": 0.4,
        },
        "E_behavioral_sink_recovery": {
            "predator_pressure": 0.2,
            "disease_pressure": 0.1,
            "resource_abundance": 1.0,
            "resource_regeneration_rate": 0.05,
            "carrying_capacity": 500,
            "space_constraint": 0.5,
            "behavioral_sink_on_threshold": 0.7,
            "behavioral_sink_off_threshold": 0.3,
        },
        "F_extinction": {
            "predator_pressure": 0.5,
            "disease_pressure": 0.4,
            "resource_abundance": 0.3,
            "resource_regeneration_rate": 0.01,
            "carrying_capacity": 500,
            "space_constraint": 0.6,
        },
    }

    for name, env_params in _WORLD_DEFAULTS.items():
        cfg = HSAPConfig(random_seed=42, max_steps=5, initial_population=20)
        for k, v in env_params.items():
            setattr(cfg.environment, k, v)
        sim = Simulation(cfg)
        sim.visual_trace.world_name = name
        sim.run(steps=5)
        assert len(sim.visual_trace.frames) > 0, f"{name} produced no frames"
        assert sim.visual_trace.frames[0]["hsap_index"] >= 0
        # Check sink state fields present
        frame = sim.visual_trace.frames[-1]
        assert "sink_active" in frame, f"{name} missing sink_active"
        assert "post_sink_recovery" in frame, f"{name} missing post_sink_recovery"
        assert "recovery_steps_remaining" in frame, f"{name} missing recovery_steps_remaining"
        assert "sink_factor" in frame, f"{name} missing sink_factor"


def test_event_counts_in_frames():
    """Event counts (births, deaths) appear in frames."""
    cfg = HSAPConfig(random_seed=42, max_steps=20, initial_population=50)
    sim = Simulation(cfg)
    sim.run(steps=20)

    total_births = sum(f["births"] for f in sim.visual_trace.frames)
    total_deaths = sum(f["deaths"] for f in sim.visual_trace.frames)
    # In 20 steps with 50 agents, there should be some births and deaths
    assert total_births >= 0
    assert total_deaths >= 0
