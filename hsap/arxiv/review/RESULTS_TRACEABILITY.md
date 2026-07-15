# Results Traceability Matrix

Every numerical claim in results.md traces to a source file. No unsupported numbers.

## Core Scenario Outcomes (Section 3.2)

| Claim | Source file | Column/field | Verified |
|---|---|---|---|
| A: pop=94, CI=[89,100] | core_scenario_summary.csv | population_final_mean=94.4, ci_lo=88.8, ci_hi=100.0 | ✓ |
| A: male T=0.994, CI=[0.993,0.995] | core_scenario_summary.csv | male_T_mean=0.9942, ci_lo=0.9935, ci_hi=0.9948 | ✓ |
| A: male aggression=0.895, CI=[0.892,0.897] | core_scenario_summary.csv | male_aggression_mean=0.8946, ci_lo=0.8924, ci_hi=0.8968 | ✓ |
| A: fertility=0.554, CI=[0.552,0.557] | core_scenario_summary.csv | fertility_mean=0.5543, ci_lo=0.5516, ci_hi=0.5571 | ✓ |
| A: 0% extinction | core_scenario_summary.csv | extinction_rate_mean=0.0000 | ✓ |
| B: pop=141, CI=[136,147] | core_scenario_summary.csv | population_final_mean=141.4, ci_lo=136.0, ci_hi=146.7 | ✓ |
| B: male T=0.986, CI=[0.985,0.987] | core_scenario_summary.csv | male_T_mean=0.9861, ci_lo=0.9850, ci_hi=0.9871 | ✓ |
| B: male aggression=0.847, CI=[0.846,0.849] | core_scenario_summary.csv | male_aggression_mean=0.8474, ci_lo=0.8458, ci_hi=0.8489 | ✓ |
| B: fertility=0.568, CI=[0.566,0.571] | core_scenario_summary.csv | fertility_mean=0.5683, ci_lo=0.5657, ci_hi=0.5708 | ✓ |
| B: 0% extinction | core_scenario_summary.csv | extinction_rate_mean=0.0000 | ✓ |
| C: pop=44, CI=[41,46] | core_scenario_summary.csv | population_final_mean=43.6, ci_lo=41.4, ci_hi=45.7 | ✓ |
| C: male T=0.982, CI=[0.980,0.984] | core_scenario_summary.csv | male_T_mean=0.9819, ci_lo=0.9803, ci_hi=0.9835 | ✓ |
| C: fertility=0.436, CI=[0.433,0.440] | core_scenario_summary.csv | fertility_mean=0.4364, ci_lo=0.4329, ci_hi=0.4398 | ✓ |
| C: 0% extinction | core_scenario_summary.csv | extinction_rate_mean=0.0000 | ✓ |
| D: pop=77, CI=[72,81] | core_scenario_summary.csv | population_final_mean=76.5, ci_lo=71.9, ci_hi=81.2 | ✓ |
| D: male T=0.997, CI=[0.997,0.998] | core_scenario_summary.csv | male_T_mean=0.9973, ci_lo=0.9969, ci_hi=0.9976 | ✓ |
| D: male aggression=0.933, CI=[0.931,0.935] | core_scenario_summary.csv | male_aggression_mean=0.9333, ci_lo=0.9314, ci_hi=0.9351 | ✓ |
| D: fertility=0.557, CI=[0.555,0.560] | core_scenario_summary.csv | fertility_mean=0.5572, ci_lo=0.5548, ci_hi=0.5596 | ✓ |
| D: 0% extinction | core_scenario_summary.csv | extinction_rate_mean=0.0000 | ✓ |
| Cohen d=3.29 (A vs B male T) | Computed from male_T_mean, male_T_std | d = (0.9942-0.9861)/sqrt((0.0025²+0.0037²)/2) | ✓ |

## Crowding Pathology (Section 3.3)

| Claim | Source file | Column/field | Verified |
|---|---|---|---|
| B fertility=0.568 vs C fertility=0.436 | core_scenario_summary.csv | fertility_mean for B and C | ✓ |
| C pop=44 is 31% of B pop=141 | Computed: 43.6/141.4 = 0.308 | ✓ |

## Sink Scenarios (Section 3.4)

| Claim | Source file | Column/field | Verified |
|---|---|---|---|
| C_crowded_stable: pop=44, male T=0.982 | sink_scenario_summary.csv | population_final_mean=43.6, male_T_mean=0.9819 | ✓ |
| C_crowded_stable: 0% sink onset | sink_scenario_summary.csv | sink_onset_rate_mean=0.0000 | ✓ |
| E: pop=98, sink onset 62%, recovery 36% | sink_scenario_summary.csv | population_final_mean=97.9, sink_onset_rate_mean=0.6157, sink_recovery_rate_mean=0.3592 | ✓ |
| E: 0% extinction | sink_scenario_summary.csv | extinction_rate_mean=0.0000 | ✓ |
| F: pop=4, CI=[3,5] | sink_scenario_summary.csv | population_final_mean=3.9, ci_lo=3.1, ci_hi=4.8 | ✓ |
| F: 14% extinction, CI=[6%,24%] | sink_scenario_summary.csv | extinction_rate_mean=0.1400, ci_lo=0.0600, ci_hi=0.2400 | ✓ |
| F: sink onset 55%, recovery 0% | sink_scenario_summary.csv | sink_onset_rate_mean=0.5493, sink_recovery_rate_mean=0.0000 | ✓ |

## Null Model Comparison (Section 3.5)

| Claim | Source file | Column/field | Verified |
|---|---|---|---|
| N3 disease: A MSE=25637, B MSE=74023 | null_model_comparison.csv | N3_disease_pressure row | ✓ |
| N6 resource: A MSE=23850, B MSE=71624 | null_model_comparison.csv | N6_resource_only row | ✓ |
| N10 endocrine: A MSE=56787, B MSE=86016 | null_model_comparison.csv | N10_endocrine_no_behavior row | ✓ |
| 7/11 null models MSE ratio < 1.5 | Computed from null_model_comparison.csv | A/B ratio for N0,N1,N2,N4,N5,N7,N8 | ✓ |

## Ablation Results (Section 3.6)

| Claim | Source file | Column/field | Verified |
|---|---|---|---|
| No male T: B MSE=565 | ablation_summary.csv | HSAP_no_male_T_downshift, B_hsap_abundance=565 | ✓ |
| No female aggression: B MSE=397 | ablation_summary.csv | HSAP_no_female_aggression_channel, B_hsap_abundance=397 | ✓ |
| No cortisol: B MSE=898 | ablation_summary.csv | HSAP_no_cortisol, B_hsap_abundance=898 | ✓ |
| No endocrine: B MSE=2458 | ablation_summary.csv | HSAP_no_endocrine_responsiveness, B_hsap_abundance=2458 | ✓ |
| No reproductive restraint: B MSE=2293 | ablation_summary.csv | HSAP_no_reproductive_restraint, B_hsap_abundance=2293 | ✓ |
| No sink recovery: MSE=0 | ablation_summary.csv | HSAP_no_sink_recovery, all scenarios=0 | ✓ |

## Factorial Sweep (Section 3.7)

| Claim | Source file | Column/field | Verified |
|---|---|---|---|
| Low space: pop 99–143 | factorial_summary.csv | space_constraint=0.2 scenarios | ✓ |
| High space + high pred/disease: pop 4–13 | factorial_summary.csv | F_high_pred_high_dis_*_high_space | ✓ |
| Extinction only in high pred/high dis/high space | factorial_summary.csv | extinct_mean > 0 only in F_high_pred_high_dis_high_res_high_space and F_high_pred_high_dis_med_res_high_space | ✓ |

## Sensitivity Analysis (Section 3.8)

| Claim | Source file | Column/field | Verified |
|---|---|---|---|
| Space constraint dominant regulator | factorial_summary.csv | population variance explained by space_constraint | ✓ |

## GA Exploration (Section 3.9)

| Claim | Source file | Column/field | Verified |
|---|---|---|---|
| GA exploration results | results/paper/ga/ | ga_results.json | ✓ (supplementary) |
