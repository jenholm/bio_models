from __future__ import annotations
import math
from typing import Any
import numpy as np
from .entities import Agent
from .environment import Environment
from .population import PopulationDynamics


MAX_AGENT_SAMPLE = 100


def _to_python(obj: Any) -> Any:
    """Recursively convert numpy types to Python native types for JSON-safe output."""
    if isinstance(obj, dict):
        return {k: _to_python(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_python(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        v = float(obj)
        return 0.0 if (v != v or v == float('inf') or v == float('-inf')) else v
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, float):
        return 0.0 if (obj != obj or obj == float('inf') or obj == float('-inf')) else obj
    return obj


def clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def compute_external_threat_index(env: Environment) -> float:
    scarcity = max(0.0, 1.0 - env.resource_abundance)
    return clamp01(0.4 * env.predator_pressure + 0.3 * env.disease_pressure + 0.3 * scarcity)


def compute_hsap_index(
    threat: float,
    male_aggression: float,
    female_aggression: float,
    fertility: float,
    growth_rate: float,
    population: int = -1,
) -> float:
    if population == 0:
        return 0.0
    low_threat = 1.0 - threat
    pop_stable = clamp01(1.0 - abs(growth_rate) * 5.0)
    hsap = clamp01(
        0.25 * low_threat
        + 0.20 * (1.0 - male_aggression)
        + 0.20 * female_aggression
        + 0.20 * (1.0 - fertility)
        + 0.15 * pop_stable
    )
    # Viability multiplier: small remnant populations cannot score as HSAP-active
    if population > 0 and population < 50:
        viability = population / 50.0
        hsap *= viability
    return clamp01(hsap)


def classify_hsap_phase(hsap_index: float, population: int = -1) -> str:
    if population == 0:
        return "extinct"
    if hsap_index < 0.35:
        return "external-control"
    if hsap_index < 0.60:
        return "transition"
    if hsap_index < 0.80:
        return "hsap-active"
    return "strong-social-regulation"


def compute_scenario_label(
    hsap_index: float,
    population: int,
    density: float,
    threat: float,
    growth_rate: float,
    sink_factor: float | None = None,
    sink_active: bool = False,
    post_sink_recovery: bool = False,
) -> str:
    if population <= 0:
        return "Extinct"
    if post_sink_recovery and population > 0:
        return "Post-sink recovery"
    if sink_active and sink_factor and sink_factor > 0.1:
        return "Behavioral sink"
    if threat > 0.5:
        return "External-control"
    if hsap_index > 0.6 and population >= 20:
        return "HSAP-active"
    if density > 0.5 and abs(growth_rate) < 0.03 and population >= 20:
        return "Crowded stable"
    if hsap_index < 0.35:
        return "External-control"
    return "Transition"


def _age_group(age: int) -> str:
    if age < 10:
        return "juvenile"
    elif age < 50:
        return "adult"
    return "senior"


def sample_agents(agents: list[Agent], step: int) -> list[dict[str, Any]]:
    alive = [a for a in agents if a.alive]
    if not alive:
        return []

    # Stratify by age group x sex
    buckets: dict[str, list[Agent]] = {}
    for a in alive:
        key = f"{a.sex}_{_age_group(a.age)}"
        buckets.setdefault(key, []).append(a)

    n = min(len(alive), MAX_AGENT_SAMPLE)
    sample: list[Agent] = []
    # Round-robin across buckets
    bucket_list = [b for b in buckets.values() if b]
    bucket_iterators = [iter(b) for b in bucket_list]
    while len(sample) < n:
        exhausted = True
        for it in bucket_iterators:
            try:
                sample.append(next(it))
                exhausted = False
                if len(sample) >= n:
                    break
            except StopIteration:
                continue
        if exhausted:
            break

    return [
        {
            "id": a.agent_id,
            "sex": a.sex,
            "age": a.age,
            "health": round(a.health, 4),
            "energy": round(a.energy, 4),
            "rank": round(a.rank, 4),
            "T": round(a.testosterone, 4),
            "E": round(a.estrogen, 4),
            "C": round(a.cortisol, 4),
            "aggression": round(a.aggression_tendency, 4),
            "fertility": round(a.fertility, 4),
            "pregnant": a.pregnant,
            "offspring_count": len(a.offspring_ids),
            "injury": a.injury,
        }
        for a in sample
    ]


class VisualTrace:
    def __init__(self, world_name: str = "unknown"):
        self.world_name = world_name
        self.frames: list[dict[str, Any]] = []
        self._prev_population: int | None = None

    def record(
        self,
        step: int,
        agents: list[Agent],
        env: Environment,
        pop: PopulationDynamics,
        events: dict[str, Any] | None = None,
    ):
        alive = [a for a in agents if a.alive]
        n = len(alive)
        age_struct = pop.age_structure(alive)
        hormones = pop.mean_hormones(alive)
        sex_hormones = pop.sex_specific_hormones(alive)
        aggression = pop.aggression_rates(alive)
        sex_fert = pop.sex_specific_fertility(alive)
        fertility = pop.total_fertility(alive)
        growth_rate = 0.0
        if self._prev_population is not None and self._prev_population > 0:
            growth_rate = (n - self._prev_population) / self._prev_population
        self._prev_population = n

        threat = compute_external_threat_index(env)
        hsap = compute_hsap_index(
            threat, aggression["male_aggression"], aggression["female_aggression"], fertility, growth_rate, population=n
        )

        ev = events or {}
        action_counts = ev.get("actions", {})
        if isinstance(action_counts, dict):
            action_counts = {k: int(v) for k, v in action_counts.items()}

        frame: dict[str, Any] = {
            "step": step,
            "world": self.world_name,
            "population": n,
            "growth_rate": round(growth_rate, 6),
            "births": int(ev.get("births", 0)),
            "deaths": int(ev.get("deaths", 0)),
            "matings": int(ev.get("matings", 0)),
            "pregnancies": int(ev.get("pregnancies", 0)),
            "infanticide": int(ev.get("infanticide", 0)),
            "neglect": int(ev.get("neglect", 0)),
            "refugees": int(ev.get("refugees", 0)),
            "density": round(env.density, 4),
            "resource_abundance": round(env.resource_abundance, 4),
            "resource_scarcity": round(env.resource_scarcity, 4),
            "territory_availability": round(env.territory_availability, 4),
            "predator_pressure": round(env.predator_pressure, 4),
            "disease_pressure": round(env.disease_pressure, 4),
            "external_threat_index": round(threat, 4),
            "hsap_index": round(hsap, 4),
            "hsap_phase": classify_hsap_phase(hsap, population=n),
            "sink_active": env.sink_active,
            "post_sink_recovery": env.post_sink_recovery,
            "recovery_steps_remaining": env.recovery_steps_remaining,
            "sink_factor": round(env.sink_factor, 4),
            "scenario_label": compute_scenario_label(
                hsap, n, env.density, threat, growth_rate,
                sink_factor=env.sink_factor,
                sink_active=env.sink_active,
                post_sink_recovery=env.post_sink_recovery,
            ),
            "mean_T": round(hormones["T"], 4),
            "mean_E": round(hormones["E"], 4),
            "mean_C": round(hormones["C"], 4),
            "male_T": round(sex_hormones["male_T"], 4),
            "female_T": round(sex_hormones["female_T"], 4),
            "male_E": round(sex_hormones["male_E"], 4),
            "female_E": round(sex_hormones["female_E"], 4),
            "male_C": round(sex_hormones["male_C"], 4),
            "female_C": round(sex_hormones["female_C"], 4),
            "male_fertility": round(sex_fert["male_fertility"], 4),
            "female_fertility": round(sex_fert["female_fertility"], 4),
            "male_aggression": round(aggression["male_aggression"], 4),
            "female_aggression": round(aggression["female_aggression"], 4),
            "female_defense": round(aggression["female_defense"], 4),
            "fertility": round(fertility, 4),
            "sex_ratio": round(pop.sex_ratio(alive), 4),
            "rank_inequality": round(pop.rank_inequality(alive), 4),
            "age_juvenile": age_struct["juvenile"],
            "age_adult": age_struct["adult"],
            "age_senior": age_struct["senior"],
            "actions": action_counts,
            "agent_sample": sample_agents(agents, step),
        }
        for key in ("step", "population", "births", "deaths", "matings", "pregnancies", "infanticide", "neglect"):
            val = frame[key]
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                frame[key] = 0

        self.frames.append(frame)

    def export(self) -> dict[str, Any]:
        return _to_python({
            "meta": {
                "world": self.world_name,
                "total_steps": len(self.frames),
                "hsap_version": "1.0",
            },
            "frames": self.frames,
        })

    def reset(self, world_name: str | None = None):
        self.frames.clear()
        self._prev_population = None
        if world_name:
            self.world_name = world_name
