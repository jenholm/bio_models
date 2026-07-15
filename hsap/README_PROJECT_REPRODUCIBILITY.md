# HSAP Project Reproducibility

## Requirements

- Python 3.10+
- ~500 MB disk for results (full paper runs need ~2 GB)

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optional extras:

```bash
pip install -e ".[sensitivity]"   # SALib for sensitivity analysis
pip install -e ".[ga]"            # deap for genetic algorithm search
pip install -e ".[paper]"         # scipy for paper experiments
pip install -e ".[all]"           # everything
```

## Quick verification

```bash
make test           # runs all tests
make smoke          # runs baseline scenario
```

## Small scenario smoke test

```bash
python scripts/run_paper_experiments.py --seeds 3 --steps 100 --sets Set1_HSAP_comparison
```

## Where results go

- `results/runs/` -- single-run outputs
- `results/paper/` -- paper experiment outputs (scenarios, figures, GA, sensitivity)
- `results/resumable_paper/` -- resumable pipeline outputs

## What is archived

Paper drafts, old arXiv packaging material, and pre-reorganization snapshots are under `archive/`. The active project is the Python model and reproducibility code.
