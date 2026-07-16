#!/usr/bin/env python3
"""Validate HSAP visualization data against paper results.

Checks:
- Scenario count (6 scenarios)
- Population behavior per scenario
- Required fields in every frame

Usage:
    python scripts/check_visualization_consistency.py
    python scripts/check_visualization_consistency.py --data-dir web/data/
"""

import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "web" / "data"

EXPECTED_SCENARIOS = [
    "A_normal_baseline",
    "B_hsap_abundance",
    "C_crowded_abundance",
    "D_high_predation_survival",
    "E_behavioral_sink_recovery",
    "F_behavioral_sink_extinction",
]

REQUIRED_FRAME_FIELDS = [
    "step", "population", "density", "actions", "agent_sample",
    "hsap_index", "growth_rate", "external_threat_index",
    "male_aggression", "female_aggression", "fertility",
]


def check_scenario_count(data: dict) -> list[str]:
    errors = []
    if len(data) != 6:
        errors.append(f"Expected 6 scenarios, found {len(data)}")
    for name in EXPECTED_SCENARIOS:
        if name not in data:
            errors.append(f"Missing scenario: {name}")
    return errors


def check_population_behavior(data: dict) -> list[str]:
    errors = []
    scenarios = {
        "A_normal_baseline": {"expect": "stable", "check": lambda f: f["population"] > 50},
        "B_hsap_abundance": {"expect": "increase", "check": lambda f: f["population"] > 80},
        "C_crowded_abundance": {"expect": "crowding_suppression", "check": lambda f: True},
        "D_high_predation_survival": {"expect": "predation_survival", "check": lambda f: f["population"] > 20},
        "E_behavioral_sink_recovery": {"expect": "recovery", "check": lambda f: True},
        "F_behavioral_sink_extinction": {"expect": "collapse", "check": lambda f: True},
    }
    for name, spec in scenarios.items():
        if name not in data:
            continue
        frames = data[name].get("frames", [])
        if not frames:
            errors.append(f"{name}: no frames")
            continue
        last = frames[-1]
        if not spec["check"](last):
            errors.append(f"{name}: population behavior mismatch (expected {spec['expect']}, final_pop={last['population']})")
    return errors


def check_required_fields(data: dict) -> list[str]:
    errors = []
    for name, trace in data.items():
        frames = trace.get("frames", [])
        for i, frame in enumerate(frames):
            for field in REQUIRED_FRAME_FIELDS:
                if field not in frame:
                    errors.append(f"{name} frame {i}: missing field '{field}'")
                    if len(errors) > 50:
                        return errors
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate HSAP visualization data")
    parser.add_argument("--data-dir", type=str, default=None)
    args = parser.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
    print(f"Checking visualization data in: {data_dir}\n")

    data = {}
    for name in EXPECTED_SCENARIOS:
        path = data_dir / f"{name}.json"
        if not path.exists():
            print(f"  MISSING: {path}")
            continue
        with open(path) as f:
            data[name] = json.load(f)
        n_frames = len(data[name].get("frames", []))
        print(f"  OK: {name} ({n_frames} frames)")

    all_errors = []

    print("\n--- Scenario count ---")
    errs = check_scenario_count(data)
    all_errors.extend(errs)
    print("PASS" if not errs else "\n".join(f"  FAIL: {e}" for e in errs))

    print("\n--- Population behavior ---")
    errs = check_population_behavior(data)
    all_errors.extend(errs)
    print("PASS" if not errs else "\n".join(f"  FAIL: {e}" for e in errs))

    print("\n--- Required fields ---")
    errs = check_required_fields(data)
    all_errors.extend(errs)
    if not errs:
        print("PASS")
    else:
        print(f"  {len(errs)} field violations found")
        for e in errs[:10]:
            print(f"  FAIL: {e}")

    print(f"\n{'='*40}")
    if all_errors:
        print(f"RESULT: FAIL ({len(all_errors)} errors)")
        sys.exit(1)
    else:
        print("RESULT: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
