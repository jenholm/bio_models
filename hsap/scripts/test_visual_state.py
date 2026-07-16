#!/usr/bin/env python3
"""Test that visualization metrics change across frames.

Verifies that the metrics are not static by checking that key fields
differ between frame 0 and frame 250.

Usage:
    python scripts/test_visual_state.py
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "web" / "data"

SCENARIOS = [
    "A_normal_baseline",
    "B_hsap_abundance",
    "C_crowded_abundance",
    "D_high_predation_survival",
    "E_behavioral_sink_recovery",
    "F_behavioral_sink_extinction",
]

FIELDS_TO_CHECK = [
    "population",
    "density",
    "hsap_index",
    "male_aggression",
    "female_aggression",
    "fertility",
]


def main():
    print("Testing visualization metric dynamics...\n")
    errors = []

    for name in SCENARIOS:
        path = DATA_DIR / f"{name}.json"
        if not path.exists():
            print(f"  SKIP {name}: file not found")
            continue

        with open(path) as f:
            data = json.load(f)

        frames = data.get("frames", [])
        if len(frames) < 260:
            print(f"  SKIP {name}: only {len(frames)} frames (need 260+)")
            continue

        f0 = frames[0]
        f250 = frames[250]

        changed_fields = []
        unchanged_fields = []

        for field in FIELDS_TO_CHECK:
            v0 = f0.get(field)
            v250 = f250.get(field)
            if v0 != v250:
                changed_fields.append(field)
            else:
                unchanged_fields.append(field)

        if unchanged_fields:
            errors.append(f"{name}: fields unchanged between frame 0 and 250: {unchanged_fields}")
            print(f"  FAIL {name}: {len(changed_fields)}/{len(FIELDS_TO_CHECK)} fields changed")
            for f in unchanged_fields:
                print(f"    - {f}: {f0.get(f)} == {f250.get(f)}")
        else:
            print(f"  PASS {name}: all {len(FIELDS_TO_CHECK)} fields changed between frame 0 and 250")

    print(f"\n{'='*40}")
    if errors:
        print(f"RESULT: FAIL ({len(errors)} scenarios with static metrics)")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("RESULT: PASS — metrics are dynamic")
        sys.exit(0)


if __name__ == "__main__":
    main()
