# HSAP Code — arXiv Reproducibility Snapshot

## Python Version

Python >= 3.10

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
```

## Dependencies

### Core
- numpy
- pandas
- matplotlib
- pyyaml
- tqdm

### Optional
- SALib (sensitivity analysis)
- deap (genetic algorithm)
- scipy (paper experiments)
- pytest, pytest-cov (testing)

## Reproducing Paper Figures

### Full pipeline (end-to-end)
```bash
python scripts/run_resumable_pipeline.py
```

### Individual steps
```bash
# 1. Run paper experiments (1,970 seeds across 61 scenarios)
python scripts/run_paper_experiments.py

# 2. Run null model + ablation suite
python scripts/run_null_ablation_suite.py

# 3. Run GA search
python scripts/run_paper_ga.py

# 4. Run sensitivity analysis
python scripts/run_paper_sensitivity.py

# 5. Generate figures
python scripts/make_paper_figures.py --dpi 300
```

### Quick smoke test
```bash
make test           # all tests
make smoke          # baseline scenario
python scripts/run_baseline.py
```

## Output Structure

```
results/paper/
├── scenarios.json
├── paper_manifest.json
├── scenario_summary.csv
├── scenarios/
│   ├── A_normal_baseline/
│   │   ├── seed_0.csv ... seed_49.csv
│   │   └── summary_by_seed.csv
│   ├── B_hsap_abundance/
│   └── ...
├── null_ablation/
│   ├── null_results.json
│   ├── ablation_results.json
│   ├── null_comparison_heatmap.png
│   └── ablation_heatmap.png
├── ga/
│   ├── ga_results.json
│   └── ga_parallel_coords.png
├── figures/
│   ├── figure1_paradigm.png
│   ├── figure2_hormone_profiles.png
│   ├── figure3_crowding_pathology.png
│   ├── figure4_stress_suppression.png
│   ├── figure5_sink_trajectories.png
│   └── figure6_ablation_heatmap.png
└── pipeline_state.sqlite
```

## Data Freeze

All scenario definitions are frozen in `src/hsap/scenarios.py`. Simulation outputs are frozen in `results/freezes/hsap_1970_seed_freeze_20260714/`.
