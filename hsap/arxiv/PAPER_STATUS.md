# HSAP Paper Status

**Version:** 0.1.0  
**Date:** 2026-07-15  
**arXiv branch:** main

## Scientific Status

**Model:** HSAP v0.1.0 — validated simulation framework  
**Pipeline:** 1,970 seeds (4 core × 50, 3 sink × 50, 54 factorial × 30), 61 scenarios, null/ablation suite, sensitivity analysis, GA exploration

### Experiment Suite

| Suite | Scope | Status |
|---|---|---|
| Paper experiments | 61 scenarios (mixed-depth) | Validated |
| Null models | 7 core scenarios, population-only MSE | Complete |
| Ablation | Hormone removal conditions | Complete |
| Sensitivity | Parameter sweep | Complete |
| GA exploration | Fitness landscape mapping | Complete |
| Figures | Fig 1-8, 4a/4b split | Generated from validated data |

### Key Validated Numbers

- Baseline (A): ~94 agents at t=500
- Abundance (B): ~141 agents
- Crowded (C): ~44 agents (partial collapse)
- High predation (D): ~77 agents
- Cohen d (A vs D): 3.29
- Behavioral sink engagement: ~62%
- Sink recovery: ~36%
- Extinction rate: ~14% (50 seeds)
- Null models non-identifiable: 7/11
- Ablation MSE increase: 73 -> 565 (male T), 73 -> 397 (female aggression)

## Current Limitations

This is a computational model.
It does not establish biological causation.
Results are simulation-consistent, not proven.

## Pending Work

- [ ] Citation review (TODO markers in manuscript)
- [ ] Equation review (extract from code, verify against manuscript)
- [ ] Figure-to-text alignment audit
- [ ] External critique
- [ ] LaTeX compilation verification
- [ ] Supplementary materials alignment
