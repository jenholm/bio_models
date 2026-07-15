# HSAP: Hormonal-Social Adaptation Population Model

HSAP tests whether predator scarcity, low disease pressure, and resource abundance can produce endocrine-linked behavioral shifts in mammalian populations, including reduced male aggression, altered female competition/aggression, reproductive restraint, and population stabilization.

The model is designed to falsify the hypothesis. It compares HSAP mechanisms against simpler null models including logistic growth, predator/resource regulation, disease pressure, density-dependent fertility, and dominance hierarchy models.

**What HSAP does not claim:** This model does not model human sexual orientation. Where relevant, non-reproductive sexual or social behavior is treated only as species-specific ethological behavior and requires explicit supporting data.

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

## Quick smoke test

```bash
make test
python scripts/run_baseline.py
```

## Directory layout

```
HSAP/
├── src/hsap/         — core Python package
├── tests/            — unit/, integration/, smoke/
├── scripts/          — entry-point run scripts
├── configs/          — scenario YAML files
├── data/             — raw, processed, literature_matrix (empty; simulation-driven)
├── docs/             — hypothesis, model plan, falsification criteria
├── notebooks/        — exploration and analysis notebooks
├── results/          — figures, tables, scenario runs
├── web/              — interactive HTML visualization (unchanged)
├── archive/          — pre-reorg snapshots, old paper drafts
├── pyproject.toml    — package metadata and dependencies
├── Makefile          — common project commands
└── requirements.txt  — minimal runtime dependencies
```

## Running experiments

```bash
make smoke                    # quick baseline
python scripts/run_paper_experiments.py   # multi-seed paper experiments
python scripts/run_null_ablation_suite.py # null model + ablation comparisons
python scripts/run_paper_ga.py            # GA search
python scripts/run_paper_sensitivity.py   # Morris + Sobol sensitivity
python scripts/make_paper_figures.py      # generate figures
```

## Running tests

```bash
make test                     # all tests
make test-unit                # unit tests only
make test-integration         # integration tests only
```

## Where results go

Results are written to `results/paper/` (scenario runs, figures, GA results, sensitivity analysis).

## Paper status

Working notes only. Paper drafts and old arXiv packaging material are archived under `archive/old_paper_drafts/` until the model and results are stable.

## Falsification criteria

The HSAP model is considered weakened or rejected if:

1. Simpler density/resource models explain the same patterns with fewer assumptions.
2. Endocrine variables add no predictive power after density, food, predation, disease, and age structure are included.
3. The expected direction fails repeatedly (low predation/resource abundance does not reduce male aggression or testosterone proxy; female aggression does not rise under offspring/resource competition; population regulation does not improve).
4. The model only works with extreme, biologically implausible parameters.
5. It works in one species-style configuration but collapses across plausible mammalian life histories.
6. It cannot reproduce Calhoun-like outcomes under high density/crowding while separating them from predator-scarce abundance.

## Core question

> Under low predation, low disease, and abundant resources, can endocrine-linked behavioral shifts evolve or emerge that reduce male aggression, alter female competition/aggression, lower fertility, and stabilize population before ecological collapse?
