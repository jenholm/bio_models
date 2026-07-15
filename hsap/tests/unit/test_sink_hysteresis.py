import numpy as np
import pytest
from hsap.config import HSAPConfig
from hsap.environment import Environment


def _make_env_with_sink(min_duration=30, off_threshold=0.50, on_threshold=0.75,
                        auto_recovery=None, recovery_duration=0):
    cfg = HSAPConfig()
    cfg.environment.behavioral_sink_on_threshold = on_threshold
    cfg.environment.behavioral_sink_off_threshold = off_threshold
    cfg.environment.behavioral_sink_min_duration = min_duration
    cfg.environment.behavioral_sink_auto_recovery_duration = auto_recovery
    cfg.environment.behavioral_sink_recovery_duration = recovery_duration
    rng = np.random.default_rng(0)
    env = Environment(cfg, rng)
    return env


def test_sink_does_not_exit_before_min_duration():
    env = _make_env_with_sink(min_duration=20, off_threshold=0.50, on_threshold=0.75)
    population = 400
    env.carrying_capacity = 500

    for step in range(15):
        env.step(population)

    assert env.sink_active
    assert env.sink_active_steps < 20

    env.step(100)
    assert env.sink_active, "Sink should persist because min_duration not yet met"


def test_sink_exits_after_min_duration_when_density_low():
    env = _make_env_with_sink(min_duration=5, off_threshold=0.60, on_threshold=0.75,
                              recovery_duration=0)
    env.carrying_capacity = 500
    for _ in range(6):
        env.step(400)

    assert env.sink_active, "Sink should be active after exceeding on_threshold"

    for _ in range(10):
        env.step(100)

    assert not env.sink_active, "Sink should exit when density < off_threshold after min_duration"


def test_sink_stays_active_above_off_threshold():
    env = _make_env_with_sink(min_duration=5, off_threshold=0.60, on_threshold=0.75,
                              recovery_duration=0)
    env.carrying_capacity = 500
    for _ in range(6):
        env.step(400)

    assert env.sink_active

    for _ in range(20):
        env.step(350)

    assert env.sink_active, "Sink should remain active while density > off_threshold"


def test_auto_recovery_causes_sink_exits():
    env_auto = _make_env_with_sink(min_duration=3, off_threshold=0.50,
                                    on_threshold=0.75, auto_recovery=10,
                                    recovery_duration=0)
    env_auto.carrying_capacity = 500

    # Activate and keep density high — auto_recovery should cause periodic exits
    for _ in range(4):
        env_auto.step(400)
    assert env_auto.sink_active

    sink_exit_count = 0
    for _ in range(50):
        was_active = env_auto.sink_active
        env_auto.step(400)
        if was_active and not env_auto.sink_active:
            sink_exit_count += 1

    assert sink_exit_count > 0, "Auto recovery should have caused at least one sink exit"


def test_no_auto_recovery_persists_at_high_density():
    env_no_auto = _make_env_with_sink(min_duration=3, off_threshold=0.50,
                                       on_threshold=0.75, auto_recovery=None,
                                       recovery_duration=0)
    env_no_auto.carrying_capacity = 500

    for _ in range(4):
        env_no_auto.step(400)
    assert env_no_auto.sink_active

    sink_exit_count = 0
    for _ in range(50):
        was_active = env_no_auto.sink_active
        env_no_auto.step(400)
        if was_active and not env_no_auto.sink_active:
            sink_exit_count += 1

    assert sink_exit_count == 0, (
        "Without auto_recovery, sink should never exit at high density"
    )


def test_sink_factor_zero_when_no_sink():
    env = _make_env_with_sink()
    env.step(100)
    assert env.sink_factor == 0.0


def test_sink_factor_increases_with_density():
    env = _make_env_with_sink(min_duration=3, off_threshold=0.50, on_threshold=0.75,
                              recovery_duration=0)
    env.carrying_capacity = 500
    env.step(400)
    assert env.sink_active
    assert env.sink_factor > 0.0
