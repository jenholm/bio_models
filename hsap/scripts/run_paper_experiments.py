#!/usr/bin/env python3
"""Run multi-seed paper experiments across defined scenario sets.

Produces:
  results/paper/scenarios.json          — scenario parameter definitions
  results/paper/paper_manifest.json      — version metadata
  results/paper/scenarios/<name>/seed_<N>.csv  — per-seed step data
  results/paper/scenarios/<name>/summary_by_seed.csv  — per-seed outcomes
  results/paper/scenario_summary.csv     — aggregate across seeds
"""

import argparse
import csv
import hashlib
import json
import math
import sqlite3
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from hsap.config import HSAPConfig
from hsap.simulation import Simulation
from hsap.io import save_metrics_csv
from hsap.scenarios import SCENARIO_SETS


DB_PATH = Path("results/paper/pipeline_state.sqlite")
STALE_MINUTES = 10
MAX_ATTEMPTS = 3

REQUIRED_CSV_COLUMNS = [
    "step", "population", "births", "deaths", "mean_fertility",
    "male_aggression", "female_aggression", "mean_cortisol", "density",
]


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            scenario TEXT,
            seed INTEGER,
            status TEXT NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            output_path TEXT,
            started_at TEXT,
            finished_at TEXT,
            heartbeat_at TEXT,
            elapsed_sec REAL,
            error TEXT,
            checksum TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
        CREATE INDEX IF NOT EXISTS idx_jobs_scenario ON jobs(scenario);
    """)
    conn.commit()


def job_id_for(scenario, seed):
    return f"{scenario}__seed_{seed:04d}"


def checksum_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def validate_seed_output(scenario_dir, seed, expected_initial_pop, expected_carrying_capacity=500):
    csv_path = scenario_dir / f"seed_{seed}.csv"
    if not csv_path.exists():
        return False, "CSV missing"
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
    except Exception as e:
        return False, f"CSV parse error: {e}"
    if len(df) < 2:
        return False, f"CSV too short: {len(df)} rows"
    first_pop = int(df["population"].iloc[0])
    if first_pop != expected_initial_pop:
        return False, f"First pop {first_pop} != expected {expected_initial_pop}"
    for col in REQUIRED_CSV_COLUMNS:
        if col not in df.columns:
            return False, f"Missing required column: {col}"
        if df[col].isnull().any():
            return False, f"NaN in column: {col}"
    steps = df["step"].values
    if not all(steps[i] < steps[i+1] for i in range(len(steps)-1)):
        return False, "Step column not monotonic"
    if "density" in df.columns and "population" in df.columns:
        expected_density = df["population"] / expected_carrying_capacity
        if not np.allclose(df["density"], expected_density, atol=1e-10):
            return False, "Density does not match population / carrying_capacity"
    return True, "valid"


def recover_stale_jobs(conn):
    now = datetime.now(timezone.utc)
    for r in conn.execute(
        "SELECT job_id, heartbeat_at, attempts, max_attempts FROM jobs WHERE status='running'"
    ).fetchall():
        if not r["heartbeat_at"]:
            conn.execute("UPDATE jobs SET status='pending', error=NULL WHERE job_id=?", (r["job_id"],))
            continue
        try:
            hb = datetime.fromisoformat(r["heartbeat_at"])
            if (now - hb).total_seconds() / 60 > STALE_MINUTES:
                jid = r["job_id"]
                attempts = r["attempts"]
                max_att = r["max_attempts"]
                if attempts < max_att:
                    conn.execute("UPDATE jobs SET status='pending', error=NULL WHERE job_id=?", (jid,))
                    print(f"  Stale {jid}: reset to pending (attempt {attempts}/{max_att})")
                else:
                    conn.execute("UPDATE jobs SET status='failed', error='Stale, max attempts exceeded' WHERE job_id=?", (jid,))
                    print(f"  Stale {jid}: max attempts exceeded, marking failed")
        except (ValueError, TypeError):
            conn.execute("UPDATE jobs SET status='pending', error=NULL WHERE job_id=?", (r["job_id"],))
    conn.commit()


# ═══════════════════════════════════════════════════════════════════
# Outcome computation
# ═══════════════════════════════════════════════════════════════════

def compute_outcomes(metrics_df):
    """Compute all paper outcome metrics from a simulation metrics dataframe."""
    df = metrics_df
    if df.empty:
        return {}

    pop = df["population"].values
    n = len(pop)
    peak_idx = int(np.argmax(pop)) if n > 0 else 0

    return {
        "population_final": int(pop[-1]) if n > 0 else 0,
        "population_peak": int(pop.max()) if n > 0 else 0,
        "population_min_after_peak": int(pop[peak_idx:].min()) if peak_idx < n and n > 0 else 0,
        "population_crash_ratio": float(
            pop[-1] / max(pop.max(), 1)
        ) if n > 0 and pop.max() > 0 else 0.0,
        "time_to_stability": _time_to_stability(pop),
        "time_to_extinction": _time_to_extinction(pop),
        "time_to_sink_onset": _time_to_event(df, "sink_active", prompt=True),
        "time_to_recovery": _time_to_event(df, "post_sink_recovery", prompt=True),
        "mean_male_T": float(df["male_T"].mean()) if n > 0 else 0.0,
        "mean_female_T": float(df["female_T"].mean()) if n > 0 else 0.0,
        "mean_male_aggression": float(df["male_aggression"].mean()) if n > 0 else 0.0,
        "mean_female_aggression": float(df["female_aggression"].mean()) if n > 0 else 0.0,
        "mean_fertility": float(df["mean_fertility"].mean()) if n > 0 else 0.0,
        "mean_cortisol": float(df["mean_cortisol"].mean()) if n > 0 else 0.0,
        "mean_neglect": float(df["neglect"].mean()) if n > 0 and "neglect" in df.columns else 0.0,
        "mean_infanticide": float(df["infanticide"].mean()) if n > 0 and "infanticide" in df.columns else 0.0,
        "extinct": int(pop[-1] <= 0) if n > 0 else 1,
    }


def _time_to_stability(pop, window=20, cv_thresh=0.05):
    n = len(pop)
    if n < window:
        return float(n)
    peak_idx = int(np.argmax(pop))
    start = max(peak_idx, n // 2)
    for i in range(start, n - window):
        seg = pop[i : i + window]
        cv = seg.std() / max(seg.mean(), 1)
        if cv < cv_thresh:
            return float(i)
    return float(n)


def _time_to_extinction(pop):
    for i, p in enumerate(pop):
        if p <= 0:
            return float(i)
    return float(len(pop))


def _time_to_event(df, col, prompt=True):
    if col not in df.columns:
        return float("nan")
    vals = df[col].values
    if prompt:
        idx = np.where(vals > 0)[0]
    else:
        idx = np.where(vals)[0]
    return float(idx[0]) if len(idx) > 0 else float("nan")


# ═══════════════════════════════════════════════════════════════════
# Aggregation helpers
# ═══════════════════════════════════════════════════════════════════

def aggregate_outcomes(seed_outcomes: list[dict]) -> dict:
    """Compute mean, SD, SE, CI, median, IQR across seeds."""
    if not seed_outcomes:
        return {}
    keys = seed_outcomes[0].keys()
    agg = {}
    for k in keys:
        raw = [s[k] for s in seed_outcomes if k in s]
        nums = []
        for v in raw:
            try:
                fv = float(v)
                if not np.isnan(fv):
                    nums.append(fv)
            except (ValueError, TypeError):
                pass
        if not nums:
            continue
        vals = np.array(nums)
        n = len(vals)
        agg[f"{k}_mean"] = float(vals.mean())
        agg[f"{k}_std"] = float(vals.std())
        agg[f"{k}_se"] = float(vals.std() / max(n ** 0.5, 1))
        agg[f"{k}_ci95"] = float(1.96 * vals.std() / max(n ** 0.5, 1))
        agg[f"{k}_median"] = float(np.median(vals))
        agg[f"{k}_iqr"] = float(np.percentile(vals, 75) - np.percentile(vals, 25))
        if k == "extinct" or k.endswith("_probability"):
            agg[k] = float(vals.mean())
    return agg


# ═══════════════════════════════════════════════════════════════════
# Main runner
# ═══════════════════════════════════════════════════════════════════

def atomic_write_csv(df, path):
    tmp = path.with_suffix(".csv.tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)


def atomic_write_json(data, path):
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


def run_scenario(name, env_overrides, n_seeds, n_steps, base_config, out_dir, conn):
    """Run one scenario across n_seeds with ledger, validation, and atomic writes."""
    scenario_dir = out_dir / "scenarios" / name
    scenario_dir.mkdir(parents=True, exist_ok=True)
    seed_outcomes = []
    cc = env_overrides.get("carrying_capacity", 500)

    # Register pending jobs
    for seed in range(n_seeds):
        jid = job_id_for(name, seed)
        conn.execute(
            "INSERT OR IGNORE INTO jobs (job_id, scenario, seed, status, max_attempts) VALUES (?, ?, ?, 'pending', ?)",
            (jid, name, seed, MAX_ATTEMPTS),
        )
    conn.commit()

    for seed in range(n_seeds):
        jid = job_id_for(name, seed)
        seed_path = scenario_dir / f"seed_{seed}.csv"
        sum_path = scenario_dir / f"seed_{seed}_summary.json"

        # Check if already completed and valid
        row = conn.execute("SELECT status, checksum FROM jobs WHERE job_id=?", (jid,)).fetchone()
        if row and row["status"] == "complete" and seed_path.exists():
            ok, msg = validate_seed_output(scenario_dir, seed, base_config.initial_population, cc)
            if ok:
                try:
                    outcomes = json.loads(sum_path.read_text())
                    outcomes["seed"] = seed
                    seed_outcomes.append(outcomes)
                    if (seed + 1) % 10 == 0:
                        print(f"    seed {seed + 1}/{n_seeds} (cached, pop={outcomes['population_final']})")
                    continue
                except Exception:
                    pass

        # If CSV exists and validates, import as complete (no ledger entry yet)
        if seed_path.exists():
            ok, msg = validate_seed_output(scenario_dir, seed, base_config.initial_population, cc)
            if ok:
                try:
                    import pandas as pd
                    df = pd.read_csv(seed_path)
                    outcomes = compute_outcomes(df)
                    outcomes["seed"] = seed
                    outcomes["initial_population"] = base_config.initial_population
                    atomic_write_json(outcomes, sum_path)
                    cs = checksum_file(seed_path)
                    conn.execute(
                        "INSERT OR REPLACE INTO jobs (job_id, scenario, seed, status, checksum, max_attempts) VALUES (?, ?, ?, 'complete', ?, ?)",
                        (jid, name, seed, cs, MAX_ATTEMPTS),
                    )
                    conn.commit()
                    seed_outcomes.append(outcomes)
                    if (seed + 1) % 10 == 0:
                        print(f"    seed {seed + 1}/{n_seeds} (imported existing, pop={outcomes['population_final']})")
                    continue
                except Exception:
                    pass

        # Mark running
        conn.execute(
            "UPDATE jobs SET status='running', attempts=attempts+1, started_at=?, heartbeat_at=? WHERE job_id=?",
            (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), jid),
        )
        conn.commit()

        start = time.time()
        error = None
        try:
            cfg = base_config.model_copy(deep=True)
            cfg.random_seed = seed
            cfg.max_steps = n_steps
            for k, v in env_overrides.items():
                setattr(cfg.environment, k, v)

            sim = Simulation(cfg)
            metrics = sim.run()
            df = metrics.to_dataframe()

            atomic_write_csv(df, seed_path)

            outcomes = compute_outcomes(df)
            outcomes["seed"] = seed
            outcomes["initial_population"] = base_config.initial_population
            atomic_write_json(outcomes, sum_path)

            ok, msg = validate_seed_output(scenario_dir, seed, base_config.initial_population, cc)
            if not ok:
                raise RuntimeError(f"Validation failed: {msg}")

            cs = checksum_file(seed_path)
            elapsed = time.time() - start
            conn.execute(
                "UPDATE jobs SET status='complete', finished_at=?, elapsed_sec=?, checksum=?, heartbeat_at=? WHERE job_id=?",
                (datetime.now(timezone.utc).isoformat(), elapsed, cs, datetime.now(timezone.utc).isoformat(), jid),
            )
            conn.commit()
            seed_outcomes.append(outcomes)

            if (seed + 1) % 10 == 0:
                print(f"    seed {seed + 1}/{n_seeds} done (pop={outcomes['population_final']})")

        except Exception as e:
            elapsed = time.time() - start
            error = str(e)
            print(f"    seed {seed + 1}/{n_seeds} FAILED after {elapsed:.1f}s: {error}")

            row2 = conn.execute("SELECT attempts, max_attempts FROM jobs WHERE job_id=?", (jid,)).fetchone()
            if row2 and row2["attempts"] >= row2["max_attempts"]:
                conn.execute(
                    "UPDATE jobs SET status='failed', finished_at=?, elapsed_sec=?, error=? WHERE job_id=?",
                    (datetime.now(timezone.utc).isoformat(), elapsed, error[:1000], jid),
                )
            else:
                conn.execute(
                    "UPDATE jobs SET status='pending', error=?, elapsed_sec=? WHERE job_id=?",
                    (error[:1000], elapsed, jid),
                )
            conn.commit()

    # Save per-seed summary CSV (only from completed outcomes)
    if seed_outcomes:
        fieldnames = list(seed_outcomes[0].keys())
        with open(scenario_dir / "summary_by_seed.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(seed_outcomes)

    return seed_outcomes


def write_manifest(out_dir, all_seed_outcomes, N_SEEDS, N_STEPS):
    import subprocess
    import platform
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        commit = "unknown"
    n_completed = sum(len(v) for v in all_seed_outcomes.values())
    manifest = {
        "model_version": "hsap-paper-v0.1",
        "git_commit": commit,
        "python_version": platform.python_version(),
        "n_completed_seeds": n_completed,
        "n_scenarios": len(all_seed_outcomes),
        "scenarios": sorted(all_seed_outcomes.keys()),
    }
    with open(out_dir / "paper_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written: {n_completed} seeds across {len(all_seed_outcomes)} scenarios")


def report_pipeline_status(conn):
    rows = conn.execute(
        "SELECT status, COUNT(*) as cnt FROM jobs GROUP BY status ORDER BY status"
    ).fetchall()
    print("\nPipeline status:")
    for r in rows:
        print(f"  {r['status']}: {r['cnt']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Run paper experiments")
    parser.add_argument("--seeds", type=int, default=50, help="Number of seeds per scenario")
    parser.add_argument("--steps", type=int, default=500, help="Max steps per simulation")
    parser.add_argument("--sets", nargs="+", default=None,
                        help="Scenario sets to run (default: all). Options: Set1_HSAP_comparison, Set2_behavioral_sink, Set3_factorial")
    parser.add_argument("--status", action="store_true", help="Show pipeline status and exit")
    parser.add_argument("--retry-failed", action="store_true", help="Reset failed jobs to pending")
    parser.add_argument("--validate", action="store_true", help="Re-validate completed jobs")
    parser.add_argument("--recover", action="store_true", help="Recover stale running jobs")
    args = parser.parse_args()

    out_dir = Path("results/paper")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Init ledger
    conn = get_db()
    init_db(conn)
    recover_stale_jobs(conn)

    if args.status:
        report_pipeline_status(conn)
        return

    if args.retry_failed:
        rows = conn.execute("SELECT job_id FROM jobs WHERE status='failed'").fetchall()
        for r in rows:
            row = conn.execute("SELECT attempts, max_attempts FROM jobs WHERE job_id=?", (r["job_id"],)).fetchone()
            if row and row["attempts"] < row["max_attempts"]:
                conn.execute("UPDATE jobs SET status='pending', error=NULL WHERE job_id=?", (r["job_id"],))
                print(f"  Reset {r['job_id']} to pending")
            else:
                print(f"  Skipped {r['job_id']}: max attempts ({row['max_attempts']}) reached" if row else f"  Skipped {r['job_id']}")
        conn.commit()
        report_pipeline_status(conn)
        return

    if args.validate:
        base_config = HSAPConfig()
        scenarios_path = out_dir / "scenarios.json"
        cc_map = {}
        if scenarios_path.exists():
            sc_defs = json.loads(scenarios_path.read_text())
            cc_map = {k: v.get("environment", {}).get("carrying_capacity", 500) for k, v in sc_defs.items()}
        rows = conn.execute("SELECT job_id, scenario, seed FROM jobs WHERE status='complete'").fetchall()
        n_ok = 0
        n_fail = 0
        for r in rows:
            sc_dir = out_dir / "scenarios" / r["scenario"]
            cc = cc_map.get(r["scenario"], 500)
            ok, msg = validate_seed_output(sc_dir, r["seed"], base_config.initial_population, cc)
            if ok:
                n_ok += 1
            else:
                n_fail += 1
                print(f"  VALIDATION FAIL: {r['job_id']}: {msg}")
                conn.execute("UPDATE jobs SET status='failed', error=? WHERE job_id=?", (f"re-validation: {msg}", r["job_id"]))
        conn.commit()
        print(f"\nValidated: {n_ok + n_fail} jobs, {n_ok} OK, {n_fail} FAILED")
        return

    if args.recover:
        recover_stale_jobs(conn)
        report_pipeline_status(conn)
        return

    N_SEEDS = args.seeds
    N_STEPS = args.steps

    base_config = HSAPConfig()

    # Save scenario definitions
    all_scenarios = {}
    for set_name, set_info in SCENARIO_SETS.items():
        for sc_name, sc_params in set_info["scenarios"].items():
            all_scenarios[sc_name] = sc_params

    with open(out_dir / "scenarios.json", "w") as f:
        json.dump(all_scenarios, f, indent=2)
    print(f"Saved scenario definitions ({len(all_scenarios)} scenarios)")

    # Determine which sets to run
    set_names = args.sets or list(SCENARIO_SETS.keys())
    sets_to_run = {k: v for k, v in SCENARIO_SETS.items() if k in set_names}

    all_seed_outcomes = {}
    total_start = time.time()

    for set_name, set_info in sets_to_run.items():
        scenarios = set_info["scenarios"]
        print(f"\n{'=' * 60}")
        print(f"Running {set_name}: {set_info['description']}")
        print(f"{'=' * 60}")

        for sc_name, sc_params in scenarios.items():
            print(f"\n  Scenario: {sc_name}")
            start = time.time()
            env_overrides = sc_params.get("environment", {})
            outcomes = run_scenario(sc_name, env_overrides, N_SEEDS, N_STEPS, base_config, out_dir, conn)
            all_seed_outcomes[sc_name] = outcomes
            elapsed = time.time() - start
            pop_mean = np.mean([o["population_final"] for o in outcomes]) if outcomes else 0
            print(f"  Done: {elapsed:.1f}s, mean final pop={pop_mean:.0f}")

    # Aggregate and save scenario summary
    summary_rows = []
    for sc_name, outcomes in all_seed_outcomes.items():
        agg = aggregate_outcomes(outcomes)
        agg["scenario"] = sc_name
        summary_rows.append(agg)

    if summary_rows:
        fieldnames = sorted(set().union(*(r.keys() for r in summary_rows)))
        with open(out_dir / "scenario_summary.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in summary_rows:
                w.writerow({k: r.get(k, "") for k in fieldnames})

    total_elapsed = time.time() - total_start
    print(f"\n{'=' * 60}")
    print(f"Total: {total_elapsed:.1f}s ({total_elapsed / 60:.1f} min)")
    print(f"Results in: {out_dir.resolve()}")

    write_manifest(out_dir, all_seed_outcomes, N_SEEDS, N_STEPS)
    report_pipeline_status(conn)


if __name__ == "__main__":
    main()
