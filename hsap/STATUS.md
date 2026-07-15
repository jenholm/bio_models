# HSAP Status

## What's built

- `src/hsap/` — core model: agents, endocrine, environment, config, simulation loop, I/O, metrics
- `scripts/` — paper experiments, null/ablation suite, figures, analysis, resumable pipeline
- `web/` — interactive visualization (JS)

## Infrastructure

| Component | Ready |
|---|---|
| Simulation loop | Done |
| Agent (hormones, behavior, glucose, hierarchy, infanticide, sink) | Done |
| Environment (predation, disease, resources, space constraint, carrying cap, water/food) | Done |
| Metrics (stability, extinction, sink onset, crash ratio, etc.) | Done |
| Config (full deserialization from JSON/dict) | Done |
| I/O (CSV save/load per seed) | Done |
| Script: `run_paper_experiments.py` (multi-seed per scenario, resumable) | Done |
| Script: `run_null_ablation_suite.py` (null models, ablation, heatmap, summary) | Done |
| Script: `run_analysis.py` (per-scenario plots, cross-scenario radar) | Done |
 | Script: `make_paper_figures.py` (Figure 1-8, including 4a/4b split) | Done |
| Script: `run_resumable_pipeline.py` (full pipeline end-to-end, resumable) | Done |
| Web visualization | Done |
| Quick-check pytest suite | Done |

## Pipeline status

```
run_resumable_pipeline.py:
  1. Run paper experiments (50 seeds × 61 scenarios)  ✓  3050 seeds all validated
  2. Null/ablation suite (7 core scenarios)            ✓  heatmap + results.json
  3. GA / sensitivity analysis                        ✓
  4. Figures (Fig 1-8, 4a/4b split)                    ✓  all regenerated from validated data
  5. Report (this doc)                                ✓
  Full pipeline: 3050 seeds validated OK
  Job ledger: results/paper/pipeline_state.sqlite
```

## Remaining bugs to fix

1. **space_constraint currently has no effect** — `territory_availability` is computed but never consumed. **Fix D**: wire into fertility (`fert *= max(0.2, env.territory_availability)`). ✅ Done
2. **Null model comparison reports MSE for all metrics** — null models only define population; MSE for other metrics is meaningless (currently compares against zeros). **Fix B**: only compute MSE for `population`. ✅ Done
3. **Heatmap only uses first scenario** — `results[list(results.keys())[0]]`. **Fix C**: aggregate MSE across all scenarios. ✅ Done
4. **time_to_stability fires on early quiet windows** — in collapse scenarios, CV<0.05 can match initial growth before the peak. **Fix E**: only search post-peak (start = max(peak_idx, n//2)). ✅ Done
5. **F_behavioral_sink_partial_collapse misnamed** — scenario rarely goes extinct; it shows partial collapse. **Fix F**: rename to `_partial_collapse`. ✅ Done
6. **run_paper_experiments.py not resumable** — no skip-if-exists. **Fix G**: skip seed if CSV exists, atomic writes. ✅ Done

## Next steps

- Write arXiv paper LaTeX (figures, methods, results sections)
- Optional: re-run Set3 factorial (54 scenarios × 50 seeds) if additional analysis needed

## Key scenario parameters

| Scenario | Predation | Disease | Resources | K | Space | Sink threshold |
|---|---|---|---|---|---|---|
| A_normal_baseline | 0.25 | 0.2 | 0.6 | 500 | 0.4 | 0.6 |
| B_hsap_abundance | 0.1 | 0.05 | 0.9 | 500 | 0.3 | 0.7 |
| C_crowded_abundance | 0.1 | 0.05 | 0.9 | 500 | 1.0 | 0.4 |
| D_high_predation_survival | 0.7 | 0.5 | 0.6 | 500 | 0.4 | 0.8 |
| E_behavioral_sink_recovery | 0.1 | 0.05 | 0.7 | 500 | 0.8 | 0.4 |
| F_behavioral_sink_partial_collapse | 0.1 | 0.05 | 0.4 | 200 | 0.8 | 0.4 |

## Output structure

```
results/
  paper/
    scenarios.json
    paper_manifest.json
    scenario_summary.csv
    scenarios/
      A_normal_baseline/
        seed_0.csv ... seed_49.csv
        summary_by_seed.csv
      B_hsap_abundance/
      ...
    null_ablation/
      null_results.json
      ablation_results.json
      null_comparison_heatmap.png
      ablation_heatmap.png
      null_comparison_summary.csv
      ablation_summary.csv
      null_ablation_results.json
      null_ablation_heatmap.png
    pipeline_state.sqlite
    ga/
      ga_results.json
      ga_sensitivity_table.csv
      ga_parallel_coords.png
      ga_top_nomadism_paths.png
      ga_feature_importance.png
    figures/
      figure1_paradigm.png
      figure2_hormone_profiles.png
      figure3_crowding_pathology.png
      figure4_stress_suppression.png
      figure5_sink_trajectories.png
      figure6_ablation_heatmap.png
    report.txt
```
