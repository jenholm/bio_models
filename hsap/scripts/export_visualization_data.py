#!/usr/bin/env python3
"""Export visualization data from HSAP simulation results.

Generates web/data/*.json files with metadata blocks, suitable for
consumption by embed_hsap_data.py or direct browser loading.

Usage:
    python scripts/export_visualization_data.py --all-worlds
    python scripts/export_visualization_data.py --world A_normal_baseline
    python scripts/export_visualization_data.py --from-results results/paper/scenarios/

Output:
    web/data/<world>.json
"""

import argparse
import json
import subprocess
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
    "F_behavioral_sink_extinction",
]

ALL_SCENARIOS = get_all_scenarios()
WORLD_DEFAULTS = {
    name: ALL_SCENARIOS[name]["environment"]
    for name in VISUAL_WORLDS
    if name in ALL_SCENARIOS
}


def get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def build_meta(scenario_name: str, frame_count: int, seed: int = 42) -> dict:
    return {
        "model": "HSAP",
        "model_version": "1.0",
        "git_commit": get_git_commit(),
        "seed": seed,
        "scenario_name": scenario_name,
        "frame_count": frame_count,
    }


def export_world(
    world_name: str,
    env_overrides: dict,
    out_path: str,
    steps: int = 500,
    seed: int = 42,
    initial_population: int = 100,
) -> str:
    base = HSAPConfig(random_seed=seed, max_steps=steps, initial_population=initial_population)
    for k, v in env_overrides.items():
        setattr(base.environment, k, v)

    sim = Simulation(base)
    sim.visual_trace.world_name = world_name
    sim.run(steps=steps)

    data = sim.visual_trace.export()
    data["meta"] = build_meta(world_name, len(data["frames"]), seed)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, indent=2)

    n_frames = len(data["frames"])
    final_pop = data["frames"][-1]["population"] if n_frames > 0 else 0
    print(f"  Exported {world_name}: {n_frames} frames, final_pop={final_pop} -> {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Export HSAP visualization data")
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--initial-population", type=int, default=100)
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--all-worlds", action="store_true")
    parser.add_argument("--from-results", type=str, default=None,
                        help="Copy existing JSON from results dir and add meta block")
    args = parser.parse_args()

    if args.from_results:
        results_dir = Path(args.from_results)
        out_dir = Path("web/data")
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in VISUAL_WORLDS:
            src = results_dir / name / "trace.json"
            if not src.exists():
                src = results_dir / name / f"{name}.json"
            if not src.exists():
                print(f"  SKIP {name}: no trace found in {results_dir / name}")
                continue
            with open(src) as f:
                data = json.load(f)
            data["meta"] = build_meta(name, len(data.get("frames", [])))
            dst = out_dir / f"{name}.json"
            with open(dst, "w") as f:
                json.dump(data, f, indent=2)
            print(f"  Copied {name}: {len(data.get('frames', []))} frames -> {dst}")
        return

    if args.all_worlds:
        base_out = Path("web/data")
        base_out.mkdir(parents=True, exist_ok=True)
        for name, env_params in WORLD_DEFAULTS.items():
            out_path = str(base_out / f"{name}.json")
            export_world(name, env_params, out_path, args.steps, args.seed, args.initial_population)
        return

    if args.config:
        cfg = load_config(args.config)
        world_name = args.world or Path(args.config).stem
        out_path = args.out or f"web/data/{world_name}.json"
        sim = Simulation(cfg)
        sim.visual_trace.world_name = world_name
        sim.run(steps=args.steps)
        data = sim.visual_trace.export()
        data["meta"] = build_meta(world_name, len(data["frames"]), args.seed)
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
