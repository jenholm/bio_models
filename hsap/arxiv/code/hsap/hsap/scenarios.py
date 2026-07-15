"""
Scenario definitions for HSAP paper experiments.

Centralized here so scripts don't depend on each other as libraries.
"""
from __future__ import annotations


SCENARIO_SETS: dict = {
    "Set1_HSAP_comparison": {
        "description": "Core HSAP comparison — low external threat vs baseline vs crowding vs high threat",
        "scenarios": {
            "A_normal_baseline": {
                "environment": {
                    "predator_pressure": 0.25,
                    "disease_pressure": 0.2,
                    "resource_abundance": 0.6,
                    "resource_regeneration_rate": 0.03,
                    "carrying_capacity": 500,
                    "space_constraint": 0.4,
                }
            },
            "B_hsap_abundance": {
                "environment": {
                    "predator_pressure": 0.1,
                    "disease_pressure": 0.05,
                    "resource_abundance": 1.5,
                    "resource_regeneration_rate": 0.08,
                    "carrying_capacity": 500,
                    "space_constraint": 0.2,
                }
            },
            "C_crowded_abundance": {
                "environment": {
                    "predator_pressure": 0.1,
                    "disease_pressure": 0.05,
                    "resource_abundance": 1.5,
                    "resource_regeneration_rate": 0.08,
                    "carrying_capacity": 200,
                    "space_constraint": 0.9,
                }
            },
            "D_high_predation_survival": {
                "environment": {
                    "predator_pressure": 0.45,
                    "disease_pressure": 0.15,
                    "resource_abundance": 0.75,
                    "resource_abundance_max": 1.2,
                    "resource_regeneration_rate": 0.05,
                    "carrying_capacity": 500,
                    "space_constraint": 0.4,
                }
            },
        },
    },
    "Set2_behavioral_sink": {
        "description": "Behavioral sink comparison — stable crowding vs recoverable sink vs partial collapse",
        "scenarios": {
            "C_crowded_stable": {
                "environment": {
                    "predator_pressure": 0.1,
                    "disease_pressure": 0.05,
                    "resource_abundance": 1.5,
                    "resource_regeneration_rate": 0.08,
                    "carrying_capacity": 200,
                    "space_constraint": 0.9,
                    "behavioral_sink_on_threshold": 0.92,
                }
            },
            "E_behavioral_sink_recovery": {
                "environment": {
                    "predator_pressure": 0.2,
                    "disease_pressure": 0.1,
                    "resource_abundance": 1.0,
                    "resource_abundance_max": 1.5,
                    "resource_regeneration_rate": 0.06,
                    "carrying_capacity": 200,
                    "space_constraint": 0.8,
                    "behavioral_sink_on_threshold": 0.25,
                    "behavioral_sink_off_threshold": 0.12,
                    "behavioral_sink_min_duration": 30,
                    "behavioral_sink_auto_recovery_duration": 100,
                    "behavioral_sink_fertility_penalty": 0.8,
                    "behavioral_sink_neglect_bonus": 0.25,
                    "behavioral_sink_withdrawal_bonus": 0.25,
                    "behavioral_sink_mating_penalty": 0.5,
                    "behavioral_sink_mortality_bonus": 0.02,
                    "behavioral_sink_recovery_duration": 60,
                    "behavioral_sink_recovery_fertility_boost": 0.6,
                    "behavioral_sink_recovery_mating_boost": 0.4,
                    "behavioral_sink_recovery_female_fertility_gate": 0.15,
                    "behavioral_sink_recovery_mortality_relief": 0.4,
                    "behavioral_sink_recovery_min_population": 30,
                    "behavioral_sink_recovery_refugee_count": 10,
                }
            },
            "F_behavioral_sink_partial_collapse": {
                "environment": {
                    "predator_pressure": 0.1,
                    "disease_pressure": 0.05,
                    "resource_abundance": 0.4,
                    "resource_abundance_max": 0.6,
                    "resource_regeneration_rate": 0.03,
                    "carrying_capacity": 200,
                    "space_constraint": 0.8,
                    "behavioral_sink_on_threshold": 0.15,
                    "behavioral_sink_off_threshold": 0.08,
                    "behavioral_sink_min_duration": 10,
                    "behavioral_sink_fertility_penalty": 0.95,
                    "behavioral_sink_mortality_bonus": 0.08,
                    "behavioral_sink_recovery_duration": 0,
                    "behavioral_sink_recovery_min_population": 0,
                    "behavioral_sink_recovery_refugee_count": 0,
                }
            },
        },
    },
    "Set3_factorial": {
        "description": "Full factorial parameter grid: predator x disease x resource x space (3x3x3x2 = 54)",
        "scenarios": {},
    },
}

# Generate factorial scenarios
_PP = [("low", 0.1), ("med", 0.4), ("high", 0.8)]
_DP = [("low", 0.05), ("med", 0.3), ("high", 0.7)]
_RA = [("low", 0.4), ("med", 1.0), ("high", 1.5)]
_SC = [("low", 0.2), ("high", 0.8)]

for pp_lbl, pp_val in _PP:
    for dp_lbl, dp_val in _DP:
        for ra_lbl, ra_val in _RA:
            for sc_lbl, sc_val in _SC:
                name = f"F_{pp_lbl}_pred_{dp_lbl}_dis_{ra_lbl}_res_{sc_lbl}_space"
                SCENARIO_SETS["Set3_factorial"]["scenarios"][name] = {
                    "environment": {
                        "predator_pressure": pp_val,
                        "disease_pressure": dp_val,
                        "resource_abundance": ra_val,
                        "resource_regeneration_rate": 0.05,
                        "carrying_capacity": 500,
                        "space_constraint": sc_val,
                    }
                }


def get_all_scenarios() -> dict:
    """Return flat dict of all scenarios across all sets."""
    result = {}
    for set_name, set_data in SCENARIO_SETS.items():
        for scenario_name, scenario_def in set_data["scenarios"].items():
            result[scenario_name] = scenario_def
    return result


def get_scenario_sets() -> dict:
    """Return the full SCENARIO_SETS structure."""
    return SCENARIO_SETS
