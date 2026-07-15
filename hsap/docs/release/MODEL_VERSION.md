# HSAP Model Version

**Version**: 0.1.0
**Codename**: Initial public release
**Date**: 2026-07-15

## Version History

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-07-15 | Initial public release with arXiv packaging |

## Component Versions

| Component | Version | Status |
|---|---|---|
| Core model | 0.1.0 | Stable |
| Null models | 0.1.0 | Stable (11 models) |
| Ablation variants | 0.1.0 | Stable (6 variants) |
| Sensitivity analysis | 0.1.0 | Stable (Morris + Sobol) |
| GA search | 0.1.0 | Stable |
| Figure generation | 0.1.0 | Stable (9 figures) |

## Scenario Freeze

All 61 scenarios are defined in `src/hsap/scenarios.py` with frozen parameter values.
Result freeze archived in `results/freezes/hsap_1970_seed_freeze_20260714/`.

## Data Freeze

- 3,050 simulation seeds validated
- 50 seeds per core/sink scenario (7 scenarios)
- 30 seeds per factorial scenario (54 scenarios)
- All null/ablation runs completed for 7 core scenarios

## Code Provenance

- Source commit: b02892b28c417fbcbc1bf163308ecbd6402adc7b
- Python: >=3.10
- Key dependencies: numpy, pandas, matplotlib, pyyaml, tqdm
- Optional: SALib (sensitivity), deap (GA), scipy (paper experiments)
