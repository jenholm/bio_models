#!/usr/bin/env python3
"""Resumable HSAP paper pipeline with SQLite job ledger.

Usage:
  python scripts/run_resumable_pipeline.py init --seeds 50 --sets Set1_HSAP_comparison
  python scripts/run_resumable_pipeline.py init --seeds 30 --sets Set3_factorial --append
  python scripts/run_resumable_pipeline.py run --workers 1
  python scripts/run_resumable_pipeline.py run --phase sim_set1 --workers 1
  python scripts/run_resumable_pipeline.py status
  python scripts/run_resumable_pipeline.py validate
  python scripts/run_resumable_pipeline.py retry-failed
  python scripts/run_resumable_pipeline.py summarize
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
from hsap.io import save_metrics_csv, save_summary_json
from hsap.null_models import NullModelSuite, compare_to_null
from hsap.ablation_models import ABLATION_REGISTRY

from hsap.scenarios import SCENARIO_SETS

OUT_ROOT = Path("results/resumable_paper")
DB_PATH = OUT_ROOT / "pipeline_state.sqlite"
STALE_MINUTES = 10
SLEEP_BETWEEN_JOBS = 1.0

REQUIRED_CSV_COLUMNS = [
    "step", "population", "births", "deaths", "mean_fertility",
    "male_aggression", "female_aggression", "mean_cortisol", "density",
]

# ── SQLite helpers ──

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            phase TEXT NOT NULL,
            scenario TEXT,
            seed INTEGER,
            task_type TEXT NOT NULL DEFAULT 'sim',
            status TEXT NOT NULL DEFAULT 'pending',
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            command TEXT,
            output_path TEXT,
            log_path TEXT,
            started_at TEXT,
            finished_at TEXT,
            heartbeat_at TEXT,
            elapsed_sec REAL,
            error TEXT,
            checksum TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_jobs_phase_status ON jobs(phase, status);
        CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
    """)
    conn.commit()


# ── Scenario helpers ──

def generate_scenarios():
    """Return dict of all scenario_name -> env_overrides across all sets."""
    scenarios = {}
    for set_info in SCENARIO_SETS.values():
        scenarios.update(set_info["scenarios"])
    return scenarios


def build_env_overrides_map(scenario_names=None):
    """Build {scenario_name: env_overrides} for quick lookup."""
    m = {}
    for set_info in SCENARIO_SETS.values():
        for sc_name, sc_params in set_info["scenarios"].items():
            if scenario_names is None or sc_name in scenario_names:
                m[sc_name] = sc_params.get("environment", {})
    return m


def phase_for_set(set_name):
    mapping = {
        "Set1_HSAP_comparison": "sim_set1",
        "Set2_behavioral_sink": "sim_set2",
        "Set3_factorial": "sim_set3",
    }
    return mapping.get(set_name, "sim_other")


def job_id_for_seed(phase, scenario, seed):
    return f"sim__{phase}__{scenario}__seed_{seed:04d}"


def scenario_job_id(phase, scenario):
    return f"null_ablation__{phase}__{scenario}"


# ── Validation ──

def checksum_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def validate_seed_output(scenario_dir, seed, expected_population, expected_carrying_capacity=500):
    """Validate a completed seed simulation output. Returns (ok, message)."""
    csv_path = scenario_dir / f"seed_{seed}.csv"
    sum_path = scenario_dir / f"seed_{seed}_summary.json"

    if not csv_path.exists():
        return False, "CSV missing"
    if not sum_path.exists():
        return False, "Summary JSON missing"

    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
    except Exception as e:
        return False, f"CSV parse error: {e}"

    if len(df) < 2:
        return False, f"CSV too short: {len(df)} rows"

    first_pop = int(df["population"].iloc[0])
    if first_pop != expected_population:
        return False, f"First pop {first_pop} != expected {expected_population}"

    for col in REQUIRED_CSV_COLUMNS:
        if col not in df.columns:
            return False, f"Missing required column: {col}"
        if df[col].isnull().any():
            return False, f"NaN in column: {col}"
        inf_mask = np.isinf(df[col].values) if col in ("step",) else df[col].apply(lambda x: isinstance(x, float) and (math.isinf(x) or math.isnan(x))).any()
        if isinstance(inf_mask, bool) and inf_mask:
            return False, f"Inf in column: {col}"

    steps = df["step"].values
    if not all(steps[i] < steps[i+1] for i in range(len(steps)-1)):
        return False, "Step column not monotonic"

    if "density" in df.columns and "population" in df.columns:
        expected_density = df["population"] / expected_carrying_capacity
        if not np.allclose(df["density"], expected_density, atol=1e-10):
            return False, "Density does not match population / carrying_capacity"

    try:
        summary = json.loads(sum_path.read_text())
    except Exception as e:
        return False, f"Summary parse error: {e}"

    final_csv_pop = int(df["population"].iloc[-1])
    final_sum_pop = int(summary.get("population_final", -1))
    if final_csv_pop != final_sum_pop:
        return False, f"CSV final pop {final_csv_pop} != summary {final_sum_pop}"

    return True, "valid"


# ── Job status ──

def report_status(conn):
    phases = ["sim_set1", "sim_set2", "sim_set3", "null_ablation"]
    rows = conn.execute(
        "SELECT phase, status, COUNT(*) as cnt FROM jobs GROUP BY phase, status ORDER BY phase, status"
    ).fetchall()

    phase_data = defaultdict(lambda: defaultdict(int))
    for r in rows:
        phase_data[r["phase"]][r["status"]] = r["cnt"]

    print(f"\n{'Phase':<25} {'Complete':>10} {'Pending':>10} {'Running':>10} {'Failed':>10} {'Stale':>10}")
    print("-" * 75)
    for ph in phases:
        d = phase_data[ph]
        print(f"{ph:<25} {d.get('complete', 0):>10} {d.get('pending', 0):>10} {d.get('running', 0):>10} {d.get('failed', 0):>10} {d.get('stale', 0):>10}")

    total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    complete = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='complete'").fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='failed'").fetchone()[0]
    print("-" * 75)
    print(f"{'TOTAL':<25} {complete:>10} {total - complete - failed:>10} {0:>10} {failed:>10} {0:>10}")
    print()

    # Write status markdown
    status_md = OUT_ROOT / "pipeline_status.md"
    lines = ["# HSAP Pipeline Status\n", f"_(updated {datetime.now(timezone.utc).isoformat()})_\n\n"]
    lines.append(f"| Phase | Complete | Pending | Running | Failed | Stale |\n")
    lines.append(f"|-------|----------|---------|---------|--------|-------|\n")
    for ph in phases:
        d = phase_data[ph]
        lines.append(f"| {ph} | {d.get('complete',0)} | {d.get('pending',0)} | {d.get('running',0)} | {d.get('failed',0)} | {d.get('stale',0)} |\n")
    lines.append(f"| **Total** | **{complete}** | **{total - complete - failed}** | **0** | **{failed}** | **0** |\n")
    status_md.write_text("".join(lines))

    return total, complete, failed


# ── Stale job recovery ──

def recover_stale_jobs(conn, stale_minutes=STALE_MINUTES):
    """Reset any 'running' jobs with stale heartbeats back to 'pending'."""
    now = datetime.now(timezone.utc)
    for r in conn.execute("SELECT job_id, heartbeat_at, attempts, max_attempts FROM jobs WHERE status='running'").fetchall():
        if not r["heartbeat_at"]:
            conn.execute("UPDATE jobs SET status='pending', error=NULL WHERE job_id=?", (r["job_id"],))
            continue
        try:
            hb = datetime.fromisoformat(r["heartbeat_at"])
            if (now - hb).total_seconds() / 60 > stale_minutes:
                jid = r["job_id"]
                attempts = r["attempts"]
                max_att = r["max_attempts"]
                if attempts < max_att:
                    conn.execute("UPDATE jobs SET status='pending', error=NULL WHERE job_id=?", (jid,))
                    print(f"  Stale {jid}: reset to pending (attempt {attempts}/{max_att})")
                else:
                    conn.execute("UPDATE jobs SET status='failed', error='Stale, max attempts exceeded' WHERE job_id=?", (jid,))
                    print(f"  Stale {jid}: max attempts ({max_att}) exceeded, marking failed")
        except (ValueError, TypeError):
            conn.execute("UPDATE jobs SET status='pending', error=NULL WHERE job_id=?", (r["job_id"],))
    conn.commit()


# ── Atomic file write ──

def atomic_write_csv(df, path):
    tmp = path.with_suffix(".csv.tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(path)


def atomic_write_json(data, path):
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)


# ── Simulation runner ──

def run_simulation_seed(cfg, env_overrides, seed, n_steps, scenario_dir):
    """Run one seed, save CSV + summary atomically, return (outcomes, metrics_df)."""
    cfg = cfg.model_copy(deep=True)
    cfg.random_seed = seed
    cfg.max_steps = n_steps
    for k, v in env_overrides.items():
        setattr(cfg.environment, k, v)

    sim = Simulation(cfg)
    metrics = sim.run()
    df = metrics.to_dataframe()

    csv_path = scenario_dir / f"seed_{seed}.csv"
    atomic_write_csv(df, csv_path)

    outcomes = compute_outcomes(df)
    outcomes["seed"] = seed
    outcomes["initial_population"] = cfg.initial_population

    sum_path = scenario_dir / f"seed_{seed}_summary.json"
    atomic_write_json(outcomes, sum_path)

    return outcomes, df


def compute_outcomes(df):
    """Compute summary outcomes from a metrics DataFrame."""
    if df.empty:
        return {}
    pop = df["population"].values
    n = len(pop)
    peak_idx = int(np.argmax(pop)) if n > 0 else 0
    return {
        "population_final": int(pop[-1]) if n > 0 else 0,
        "population_peak": int(pop.max()) if n > 0 else 0,
        "population_min_after_peak": int(pop[peak_idx:].min()) if peak_idx < n and n > 0 else 0,
        "population_crash_ratio": float(pop[-1] / max(pop.max(), 1)) if n > 0 and pop.max() > 0 else 0.0,
        "time_to_stability": _time_to_stability(pop),
        "time_to_extinction": _time_to_extinction(pop),
        "mean_male_T": float(df["male_T"].mean()) if n > 0 else 0.0,
        "mean_female_T": float(df["female_T"].mean()) if n > 0 else 0.0,
        "mean_male_aggression": float(df["male_aggression"].mean()) if n > 0 else 0.0,
        "mean_female_aggression": float(df["female_aggression"].mean()) if n > 0 else 0.0,
        "mean_fertility": float(df["mean_fertility"].mean()) if n > 0 else 0.0,
        "mean_cortisol": float(df["mean_cortisol"].mean()) if n > 0 else 0.0,
        "extinct": int(pop[-1] <= 0) if n > 0 else 1,
    }


def _time_to_stability(pop, window=20, cv_thresh=0.05):
    n = len(pop)
    if n < window:
        return float(n)
    peak_idx = int(np.argmax(pop))
    start = max(peak_idx, n // 2)
    for i in range(start, n - window):
        seg = pop[i: i + window]
        cv = seg.std() / max(seg.mean(), 1)
        if cv < cv_thresh:
            return float(i)
    return float(n)


def _time_to_extinction(pop):
    for i, p in enumerate(pop):
        if p <= 0:
            return float(i)
    return float(len(pop))


# ── Null/ablation runner ──

def run_null_ablation_scenario(scenario_name, env_overrides, n_steps, base_config, rng_seed, out_dir):
    """Run HSAP + null + ablation for one scenario. Returns comparison dict."""
    cfg = base_config.model_copy(deep=True)
    cfg.random_seed = rng_seed
    cfg.max_steps = n_steps
    for k, v in env_overrides.items():
        setattr(cfg.environment, k, v)

    sim = Simulation(cfg)
    metrics = sim.run()
    hsap_df = metrics.to_dataframe()

    null_suite = NullModelSuite(cfg.environment, cfg.initial_population, np.random.default_rng(rng_seed))
    null_results = null_suite.run_all(steps=n_steps)

    comparisons = {}
    for name, null_res in null_results.items():
        null_ts = null_res.population_ts
        comp = {"population_mse": float(np.mean((hsap_df["population"].values[:len(null_ts)] - null_ts) ** 2))}
        comparisons[name] = comp

    for ab_name, ab_fn in ABLATION_REGISTRY.items():
        if ab_name == "HSAP_full":
            continue
        ab_cfg = ab_fn(cfg)
        ab_cfg.random_seed = rng_seed
        ab_cfg.max_steps = n_steps
        for k, v in env_overrides.items():
            setattr(ab_cfg.environment, k, v)
        try:
            sim2 = Simulation(ab_cfg)
            ab_df = sim2.run().to_dataframe()
            min_len = min(len(hsap_df), len(ab_df))
            comp = {"population_mse": float(np.mean((hsap_df["population"].values[:min_len] - ab_df["population"].values[:min_len]) ** 2))}
            comparisons[ab_name] = comp
        except Exception as e:
            comparisons[ab_name] = {"error": str(e)}

    return comparisons


# ── Command handlers ──

def cmd_init(args):
    """Initialize the database and register all jobs."""
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    init_db(conn)
    recover_stale_jobs(conn)

    sets_to_run = args.sets or list(SCENARIO_SETS.keys())
    n_seeds = args.seeds
    n_steps = args.steps
    append = args.append

    all_scenarios = {}
    for set_name in sets_to_run:
        if set_name not in SCENARIO_SETS:
            print(f"Unknown set: {set_name}. Available: {list(SCENARIO_SETS.keys())}")
            continue
        set_info = SCENARIO_SETS[set_name]
        phase = phase_for_set(set_name)
        for sc_name, sc_params in set_info["scenarios"].items():
            all_scenarios[sc_name] = sc_params
            env_overrides = sc_params.get("environment", {})
            for seed in range(n_seeds):
                jid = job_id_for_seed(phase, sc_name, seed)
                if not append:
                    conn.execute(
                        "INSERT OR REPLACE INTO jobs (job_id, phase, scenario, seed, task_type, status) VALUES (?, ?, ?, ?, 'sim', 'pending')",
                        (jid, phase, sc_name, seed),
                    )
                else:
                    conn.execute(
                        "INSERT OR IGNORE INTO jobs (job_id, phase, scenario, seed, task_type, status) VALUES (?, ?, ?, ?, 'sim', 'pending')",
                        (jid, phase, sc_name, seed),
                    )

    conn.commit()

    n_jobs = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    print(f"Initialized {n_jobs} jobs across {len(all_scenarios)} scenarios in {len(sets_to_run)} sets")
    report_status(conn)


def cmd_run(args):
    """Run pending jobs with periodic heartbeat and stale recovery."""
    conn = get_db()
    recover_stale_jobs(conn)

    phase_filter = args.phase
    max_jobs = args.max_jobs or 0
    max_attempts_config = args.max_attempts
    n_steps = args.steps
    base_config = HSAPConfig()
    workers = max(1, args.workers)

    # Precompute env_overrides for all relevant scenarios
    all_scenario_names = set()
    if phase_filter:
        for set_name in SCENARIO_SETS:
            if phase_for_set(set_name) == phase_filter:
                all_scenario_names.update(SCENARIO_SETS[set_name]["scenarios"].keys())
    env_overrides_map = build_env_overrides_map(all_scenario_names if phase_filter else None)

    completed = 0
    while True:
        recover_stale_jobs(conn)

        query = "SELECT * FROM jobs WHERE status='pending'"
        params = []
        if phase_filter:
            query += " AND phase=?"
            params.append(phase_filter)

        pending = conn.execute(query + " ORDER BY job_id LIMIT ?", params + [workers]).fetchall()
        if not pending:
            recover_stale_jobs(conn)
            pending = conn.execute(query + " ORDER BY job_id LIMIT ?", params + [workers]).fetchall()
            if not pending:
                print("No pending jobs.")
                break

        for job in pending:
            jid = job["job_id"]
            phase = job["phase"]
            scenario = job["scenario"]
            seed = job["seed"]

            if max_jobs > 0 and completed >= max_jobs:
                break

            print(f"\n[{completed+1}] Running: {jid}")
            conn.execute(
                "UPDATE jobs SET status='running', attempts=attempts+1, started_at=?, heartbeat_at=? WHERE job_id=?",
                (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), jid),
            )
            conn.commit()

            start = time.time()
            error = None
            try:
                scenario_dir = OUT_ROOT / "scenarios" / scenario
                scenario_dir.mkdir(parents=True, exist_ok=True)

                env_overrides = env_overrides_map.get(scenario, {})
                cc = env_overrides.get("carrying_capacity", 500)

                outcomes, df = run_simulation_seed(base_config, env_overrides, seed, n_steps, scenario_dir)

                ok, msg = validate_seed_output(scenario_dir, seed, base_config.initial_population, cc)
                if not ok:
                    raise RuntimeError(f"Validation failed: {msg}")

                # Compute checksum
                csv_path = scenario_dir / f"seed_{seed}.csv"
                cs = checksum_file(csv_path)

                elapsed = time.time() - start
                conn.execute(
                    "UPDATE jobs SET status='complete', finished_at=?, elapsed_sec=?, checksum=?, heartbeat_at=? WHERE job_id=?",
                    (datetime.now(timezone.utc).isoformat(), elapsed, cs, datetime.now(timezone.utc).isoformat(), jid),
                )
                conn.commit()
                completed += 1
                print(f"  OK ({elapsed:.1f}s, pop={outcomes.get('population_final','?')})")

            except Exception as e:
                elapsed = time.time() - start
                error = str(e)
                print(f"  FAILED after {elapsed:.1f}s: {error}")

                # Check if max attempts exceeded
                row = conn.execute("SELECT attempts, max_attempts FROM jobs WHERE job_id=?", (jid,)).fetchone()
                if row and row["attempts"] >= row["max_attempts"]:
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

            # Heartbeat for loop
            conn.execute("UPDATE jobs SET heartbeat_at=? WHERE job_id=?", (datetime.now(timezone.utc).isoformat(), jid))
            conn.commit()

        if max_jobs > 0 and completed >= max_jobs:
            print(f"Reached --max-jobs={max_jobs}")
            break

        time.sleep(SLEEP_BETWEEN_JOBS)

    report_status(conn)


def cmd_retry_failed(args):
    """Reset failed jobs to pending if under max_attempts."""
    conn = get_db()
    if args.job_id:
        rows = conn.execute("SELECT * FROM jobs WHERE job_id=? AND status='failed'", (args.job_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM jobs WHERE status='failed'").fetchall()

    if not rows:
        print("No failed jobs to retry.")
        return

    for r in rows:
        if r["attempts"] < r["max_attempts"]:
            conn.execute(
                "UPDATE jobs SET status='pending', error=NULL, started_at=NULL, finished_at=NULL, elapsed_sec=NULL WHERE job_id=?",
                (r["job_id"],),
            )
            print(f"  Reset {r['job_id']} to pending (attempt {r['attempts']}/{r['max_attempts']})")
        else:
            print(f"  Skipped {r['job_id']}: max attempts ({r['max_attempts']}) reached")
    conn.commit()


def cmd_validate(args):
    """Re-validate all completed jobs."""
    conn = get_db()
    if args.job_id:
        rows = conn.execute("SELECT * FROM jobs WHERE job_id=? AND status='complete'", (args.job_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM jobs WHERE status='complete'").fetchall()

    if not rows:
        print("No completed jobs to validate.")
        return

    base_config = HSAPConfig()
    env_overrides_map = build_env_overrides_map()
    n_ok = 0
    n_fail = 0
    for r in rows:
        jid = r["job_id"]
        scenario = r["scenario"]
        seed = r["seed"]
        scenario_dir = OUT_ROOT / "scenarios" / scenario
        cc = env_overrides_map.get(scenario, {}).get("carrying_capacity", 500)
        ok, msg = validate_seed_output(scenario_dir, seed, base_config.initial_population, cc)
        if ok:
            n_ok += 1
        else:
            n_fail += 1
            print(f"  VALIDATION FAIL: {jid}: {msg}")
            conn.execute("UPDATE jobs SET status='failed', error=? WHERE job_id=?", (f"re-validation: {msg}", jid))

    conn.commit()
    print(f"\nValidated: {n_ok + n_fail} jobs, {n_ok} OK, {n_fail} FAILED")
    report_status(conn)


def cmd_summarize(args):
    """Build aggregate summary from completed seed results."""
    conn = get_db()
    rows = conn.execute(
        "SELECT scenario, seed, job_id FROM jobs WHERE status='complete' AND task_type='sim' ORDER BY scenario, seed"
    ).fetchall()

    if not rows:
        print("No completed sim jobs to summarize.")
        return

    by_scenario = defaultdict(list)
    for r in rows:
        by_scenario[r["scenario"]].append(r["seed"])

    # Per-scenario aggregation
    summary_rows = []
    for scenario, seeds in sorted(by_scenario.items()):
        seed_outcomes = []
        for seed in seeds:
            sum_path = OUT_ROOT / "scenarios" / scenario / f"seed_{seed}_summary.json"
            if sum_path.exists():
                try:
                    seed_outcomes.append(json.loads(sum_path.read_text()))
                except Exception:
                    pass

        if not seed_outcomes:
            continue

        agg = aggregate_outcomes(seed_outcomes)
        agg["scenario"] = scenario
        agg["n_seeds"] = len(seed_outcomes)
        summary_rows.append(agg)

        # Per-seed CSV
        csv_path = OUT_ROOT / "scenarios" / scenario / "summary_by_seed.csv"
        if seed_outcomes:
            fieldnames = list(seed_outcomes[0].keys())
            with open(csv_path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(seed_outcomes)

    # Write combined scenario summary
    if summary_rows:
        fieldnames = sorted(set().union(*(r.keys() for r in summary_rows)))
        csv_path = OUT_ROOT / "scenario_summary_all.csv"
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in summary_rows:
                w.writerow({k: r.get(k, "") for k in fieldnames})
        print(f"  Wrote {csv_path} ({len(summary_rows)} scenarios)")

    # Write manifest
    import subprocess
    import platform
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        commit = "unknown"
    manifest = {
        "model_version": "hsap-paper-v0.1",
        "git_commit": commit,
        "python_version": platform.python_version(),
        "n_completed_seeds": sum(len(s) for s in by_scenario.values()),
        "n_scenarios": len(by_scenario),
        "scenarios": sorted(by_scenario.keys()),
    }
    manifest_path = OUT_ROOT / "paper_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Wrote {manifest_path}")

    # Phase-specific summaries (avoid sharing)
    for set_name in SCENARIO_SETS:
        phase = phase_for_set(set_name)
        phase_scenarios = list(SCENARIO_SETS[set_name]["scenarios"].keys())
        phase_rows = [r for r in summary_rows if r["scenario"] in phase_scenarios]
        if phase_rows:
            pf = sorted(set().union(*(r.keys() for r in phase_rows)))
            p_path = OUT_ROOT / f"{phase}_summary.csv"
            with open(p_path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=pf)
                w.writeheader()
                for r in phase_rows:
                    w.writerow({k: r.get(k, "") for k in pf})
            print(f"  Wrote {p_path} ({len(phase_rows)} scenarios)")

    print(f"\nSummary complete: {len(summary_rows)} scenarios, {sum(len(s) for s in by_scenario.values())} seeds")


def aggregate_outcomes(seed_outcomes):
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


# ── Main ──

def main():
    parser = argparse.ArgumentParser(description="Resumable HSAP paper pipeline")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize database and register jobs")
    p_init.add_argument("--seeds", type=int, default=50)
    p_init.add_argument("--steps", type=int, default=500)
    p_init.add_argument("--sets", nargs="+", default=None)
    p_init.add_argument("--append", action="store_true", help="Add new jobs without clearing existing")

    p_run = sub.add_parser("run", help="Run pending jobs")
    p_run.add_argument("--phase", default=None, help="Phase filter (sim_set1, sim_set2, etc.)")
    p_run.add_argument("--workers", type=int, default=1)
    p_run.add_argument("--max-jobs", type=int, default=0)
    p_run.add_argument("--max-attempts", type=int, default=3)
    p_run.add_argument("--steps", type=int, default=500)

    p_status = sub.add_parser("status", help="Show pipeline status")
    p_validate = sub.add_parser("validate", help="Re-validate completed jobs")
    p_validate.add_argument("--job-id", default=None)
    p_summarize = sub.add_parser("summarize", help="Build aggregate summaries")

    p_retry = sub.add_parser("retry-failed", help="Reset failed jobs to pending")
    p_retry.add_argument("--job-id", default=None, help="Specific job to retry (default: all failed)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if args.command == "init":
        cmd_init(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "status":
        conn = get_db()
        report_status(conn)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "summarize":
        cmd_summarize(args)
    elif args.command == "retry-failed":
        cmd_retry_failed(args)


if __name__ == "__main__":
    main()
