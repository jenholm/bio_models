from __future__ import annotations
import numpy as np
import pandas as pd
from .entities import Agent
from .environment import Environment
from .population import PopulationDynamics
from .visual_trace import compute_external_threat_index, compute_hsap_index


class MetricsCollector:
    def __init__(self):
        self.records: list[dict] = []

    def record(
        self,
        step: int,
        agents: list[Agent],
        env: Environment,
        pop: PopulationDynamics,
        events: dict | None = None,
    ):
        alive = [a for a in agents if a.alive]
        n = len(alive)
        age_struct = pop.age_structure(alive)
        hormones = pop.mean_hormones(alive)
        aggression = pop.aggression_rates(alive)
        sex_hormones = pop.sex_specific_hormones(alive) if n > 0 else {}
        ev = events or {}
        record = {
            "step": step,
            "population": n,
            "density": env.density,
            "resource_abundance": env.resource_abundance,
            "predator_pressure": env.predator_pressure,
            "disease_pressure": env.disease_pressure,
            "territory_availability": env.territory_availability,
            "sex_ratio": pop.sex_ratio(alive),
            "rank_inequality": pop.rank_inequality(alive),
            "juvenile_count": age_struct["juvenile"],
            "adult_count": age_struct["adult"],
            "senior_count": age_struct["senior"],
            "mean_testosterone": hormones["T"],
            "mean_estrogen": hormones["E"],
            "mean_cortisol": hormones["C"],
            "male_T": sex_hormones.get("male_T", 0.0),
            "female_T": sex_hormones.get("female_T", 0.0),
            "male_aggression": aggression["male_aggression"],
            "female_aggression": aggression["female_aggression"],
            "female_defense": aggression["female_defense"],
            "mean_fertility": pop.total_fertility(alive),
            "births": int(ev.get("births", 0)),
            "deaths": int(ev.get("deaths", 0)),
            "matings": int(ev.get("matings", 0)),
            "pregnancies": int(ev.get("pregnancies", 0)),
            "infanticide": int(ev.get("infanticide", 0)),
            "neglect": int(ev.get("neglect", 0)),
            "refugees": int(ev.get("refugees", 0)),
            "external_threat_index": float(
                max(0.0, min(1.0, 0.4 * env.predator_pressure + 0.3 * env.disease_pressure + 0.3 * max(0.0, 1.0 - env.resource_abundance)))
            ),
            "sink_active": int(env.sink_active),
            "post_sink_recovery": int(env.post_sink_recovery),
            "sink_factor": float(getattr(env, "sink_factor", 0.0)),
        }
        # Compute HSAP index for this step
        threat = compute_external_threat_index(env)
        growth_rate = 0.0
        if len(self.records) > 0:
            prev_pop = self.records[-1]["population"]
            if prev_pop > 0:
                growth_rate = (n - prev_pop) / prev_pop
        record["external_threat_index"] = threat
        record["hsap_index"] = compute_hsap_index(
            threat, aggression["male_aggression"], aggression["female_aggression"],
            record["mean_fertility"], growth_rate, population=n,
        )
        self.records.append(record)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.records)

    def summary(self) -> dict:
        df = self.to_dataframe()
        if df.empty:
            return {}
        return {
            "final_population": int(df["population"].iloc[-1]),
            "max_population": int(df["population"].max()),
            "min_population": int(df["population"].min()),
            "mean_population": float(df["population"].mean()),
            "population_crash": float(
                (df["population"].iloc[-1] / max(df["population"].max(), 1))
            ),
            "time_to_stability": self._time_to_stability(df),
            "mean_male_aggression": float(df["male_aggression"].mean()),
            "mean_female_aggression": float(df["female_aggression"].mean()),
            "mean_fertility": float(df["mean_fertility"].mean()),
            "mean_T": float(df["mean_testosterone"].mean()),
            "mean_C": float(df["mean_cortisol"].mean()),
        }

    def _time_to_stability(self, df: pd.DataFrame, window: int = 20) -> float:
        n = len(df)
        if n < window:
            return float(n)
        pop = df["population"].values
        peak_idx = int(np.argmax(pop))
        start = max(peak_idx, n // 2)
        for i in range(start, n - window):
            segment = pop[i : i + window]
            cv = segment.std() / max(segment.mean(), 1)
            if cv < 0.05:
                return float(i)
        return float(n)
