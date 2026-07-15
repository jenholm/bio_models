# HSAP Reproducibility Package

## Goal

A stranger downloads the archive and can reproduce:
1. Baseline simulation
2. Null models
3. Sensitivity analysis
4. Figures

## Quick Start

```bash
# Option 1: Conda
conda env create -f environment.yml
conda activate hsap
bash run_all.sh

# Option 2: pip
pip install -r requirements.txt
bash run_all.sh

# Option 3: Manual
pip install -e ".[all]"
python scripts/run_baseline.py
python scripts/run_paper_experiments.py
python scripts/run_null_ablation_suite.py
python scripts/run_paper_sensitivity.py
python scripts/make_paper_figures.py --dpi 300
```

## What Gets Reproduced

| Step | Script | Output | Time |
|---|---|---|---|
| Baseline | `run_baseline.py` | Single run CSV | ~5s |
| Paper experiments | `run_paper_experiments.py` | 3,050 seed CSVs | ~30min |
| Null/ablation | `run_null_ablation_suite.py` | Null + ablation JSON | ~10min |
| Sensitivity | `run_paper_sensitivity.py` | Morris + Sobol tables | ~15min |
| Figures | `make_paper_figures.py` | 9 figures (PNG + PDF) | ~2min |

## Output Locations

- `results/paper/scenarios/` — Per-scenario seed CSVs
- `results/paper/null_ablation/` — Null model + ablation results
- `results/paper/ga/` — Genetic algorithm results
- `results/paper/figures/` — Generated figures
- `results/paper/scenario_summary.csv` — Summary table

## Data Freeze

All scenario definitions are frozen in `src/hsap/scenarios.py`. The result freeze is archived in `results/freezes/hsap_1970_seed_freeze_20260714/` with SHA-256 hashes for code tarballs.

## Verification

```bash
# Validate all seeds
python scripts/run_resumable_pipeline.py validate

# Check summary statistics
python scripts/run_resumable_pipeline.py summarize
```
