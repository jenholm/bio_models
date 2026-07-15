# Figure Audit

Audit of all draft figures against manuscript references and data sources.

## Figure Inventory

| Figure | File(s) | Formats | Referenced in manuscript | Source data | Decision |
|---|---|---|---|---|---|
| fig1_causal_chain | fig1_causal_chain.pdf, .png | PDF, PNG | Introduction (conceptual) | None (schematic) | **Keep** — conceptual diagram, no data |
| fig2_population_trajectories | fig2_population_trajectories.pdf, .png | PDF, PNG | Results 4.2, 4.3 | results/paper/scenarios/ | **Keep** — core results figure |
| fig3_metrics_comparison | fig3_metrics_comparison.pdf, .png | PDF, PNG | Results 4.2 (table替代) | core_scenario_summary.csv | **Keep** — multi-panel comparison |
| fig4a_null_population | fig4a_null_population.pdf, .png | PDF, PNG | Results 4.5 | null_model_comparison.csv | **Keep** — null model results |
| fig4b_ablation_heatmap | fig4b_ablation_heatmap.pdf, .png | PDF, PNG | Results 4.6 | ablation_summary.csv | **Keep** — ablation results |
| fig5_sink_trajectories | fig5_sink_trajectories.pdf, .png | PDF, PNG | Results 4.4 | sink_scenario_summary.csv | **Keep** — sink dynamics |
| fig6_sensitivity_tornado | fig6_sensitivity_tornado.pdf, .png | PDF, PNG | Results 4.8 | sensitivity_summary.csv | **Keep** — sensitivity analysis |
| fig7_ga_convergence | fig7_ga_convergence.pdf, .png | PDF, PNG | Results 4.9 | results/paper/ga/ | **Keep** — GA exploration |
| fig8_phase_map | fig8_phase_map.pdf, .png | PDF, PNG | Results 4.7 | factorial_summary.csv | **Keep** — factorial sweep |
| fig9_external_proxy_observables | fig9_external_proxy_observables.pdf, .png | PDF, PNG | Not referenced in results.md | External proxy data | **Relegate to supplementary** — risks empirical-validation cosplay |
| null_ablation_heatmap | null_ablation_heatmap.png | PNG | Not referenced | null_ablation/ | **Remove** — redundant with fig4a/4b |

## Format Decision

**Canonical format: PDF** for arXiv submission (vector graphics, resolution-independent).

PNG copies retained for web visualization and review convenience.

## Promoted Figures

| Final name | Source | Section |
|---|---|---|
| figure_1_causal_chain.pdf | fig1_causal_chain.pdf | Introduction |
| figure_2_population_trajectories.pdf | fig2_population_trajectories.pdf | Results 4.2–4.3 |
| figure_3_core_metrics.pdf | fig3_metrics_comparison.pdf | Results 4.2 |
| figure_4_null_models.pdf | fig4a_null_population.pdf | Results 4.5 |
| figure_5_ablation_heatmap.pdf | fig4b_ablation_heatmap.pdf | Results 4.6 |
| figure_6_sink_trajectories.pdf | fig5_sink_trajectories.pdf | Results 4.4 |
| figure_7_sensitivity.pdf | fig6_sensitivity_tornado.pdf | Results 4.8 |
| figure_8_phase_map.pdf | fig8_phase_map.pdf | Results 4.7 |

## Not Promoted

| Figure | Reason |
|---|---|
| fig7_ga_convergence | Exploratory; supplementary only |
| fig9_external_proxy_observables | Risks empirical-validation cosplay; supplementary only |
| null_ablation_heatmap | Redundant with fig4a/4b |

## Figure Quality Notes

- All draft figures exist in both PDF and PNG formats
- PDF is preferred for LaTeX inclusion
- PNG retained for web and review
- No figure requires both formats for submission
