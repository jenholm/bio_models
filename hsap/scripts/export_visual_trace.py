#!/usr/bin/env python3
"""Export visual trace JSON files for HSAP worlds."""

import argparse
import json
from pathlib import Path

from hsap.config import HSAPConfig, load_config
from hsap.simulation import Simulation
from hsap.scenarios import get_all_scenarios


VISUAL_WORLDS = [
    "A_normal_baseline",
    "B_hsap_abundance",
    "C_crowded_abundance",
    "D_high_predation_survival",
    "E_behavioral_sink_recovery",
    "F_behavioral_sink_partial_collapse",
]

ALL_SCENARIOS = get_all_scenarios()
WORLD_DEFAULTS = {
    name: ALL_SCENARIOS[name]["environment"]
    for name in VISUAL_WORLDS
}


def export_world(
    world_name: str,
    env_overrides: dict,
    out_path: str,
    steps: int = 500,
    seed: int = 42,
    initial_population: int = 100,
):
    base = HSAPConfig(random_seed=seed, max_steps=steps, initial_population=initial_population)
    for k, v in env_overrides.items():
        setattr(base.environment, k, v)

    sim = Simulation(base)
    sim.visual_trace.world_name = world_name
    sim.run(steps=steps)

    data = sim.visual_trace.export()

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, indent=2)

    n_frames = len(data["frames"])
    final_pop = data["frames"][-1]["population"] if n_frames > 0 else 0
    print(f"  Exported {world_name}: {n_frames} frames, final_pop={final_pop} -> {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Export HSAP visual traces")
    parser.add_argument("--config", type=str, default=None, help="Path to YAML config")
    parser.add_argument("--world", type=str, default=None, help="World name")
    parser.add_argument("--steps", type=int, default=500, help="Number of steps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--initial-population", type=int, default=100, help="Initial population")
    parser.add_argument("--out", type=str, default=None, help="Output JSON path")
    parser.add_argument("--all-worlds", action="store_true", help="Export all four worlds")
    args = parser.parse_args()

    if args.all_worlds:
        base_out = Path("web/data")
        base_out.mkdir(parents=True, exist_ok=True)
        exported = []
        for name, env_params in WORLD_DEFAULTS.items():
            out_path = str(base_out / f"{name}.json")
            export_world(name, env_params, out_path, args.steps, args.seed, args.initial_population)
            exported.append(out_path)
        print(f"\nExported {len(exported)} worlds to {base_out}/")
        return

    if args.config:
        cfg = load_config(args.config)
        world_name = args.world or Path(args.config).stem
        out_path = args.out or f"web/data/{world_name}.json"
        base = cfg
        sim = Simulation(base)
        sim.visual_trace.world_name = world_name
        sim.run(steps=args.steps)
        data = sim.visual_trace.export()
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Exported {world_name}: {len(data['frames'])} frames -> {out_path}")
        return

    if args.world and args.world in WORLD_DEFAULTS:
        out_path = args.out or f"web/data/{args.world}.json"
        export_world(args.world, WORLD_DEFAULTS[args.world], out_path, args.steps, args.seed, args.initial_population)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
