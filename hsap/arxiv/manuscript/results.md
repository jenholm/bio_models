# 4. Results

All results are from the validated pipeline: 1,970 validated simulation runs across 61 scenarios (4 core × 50, 3 sink × 50, 54 factorial × 30), with null/ablation suite completed for 7 core scenarios. Scenario definitions are frozen in `src/hsap/scenarios.py`. Full traceability to source data is provided in `arxiv/review/RESULTS_TRACEABILITY.md`.

## 4.1 Experimental Scope

The computational experiment comprised:

- **4 core scenarios** (A–D): 50 runs each, testing baseline, abundance, crowding, and high-predation conditions
- **3 sink scenarios** (C_stable, E, F): 50 runs each, testing behavioral sink activation, recovery, and partial collapse
- **54-factorial sweep**: 30 runs each, varying predator pressure (0.1/0.4/0.8), disease pressure (0.05/0.3/0.7), resource abundance (0.4/1.0/1.5), and space constraint (0.2/0.8)
- **11 null models**: fit to each core scenario's population trajectory, evaluated by MSE
- **6 ablation variants**: removing one model component at a time
- **GA exploration**: fitness landscape mapping across parameter space

## 4.2 Core Scenario Outcomes

All four core scenarios produced distinct population outcomes (Table 1, Figure 2). Summary statistics are reported as mean (95% CI) across 50 runs.

| Scenario | Population | Male T | Male Aggression | Fertility | Extinction |
|---|---|---|---|---|---|
| A_normal_baseline | 94 (CI: 89–100) | 0.994 (CI: 0.993–0.995) | 0.895 (CI: 0.892–0.897) | 0.554 (CI: 0.552–0.557) | 0% |
| B_hsap_abundance | 141 (CI: 136–147) | 0.986 (CI: 0.985–0.987) | 0.847 (CI: 0.846–0.849) | 0.568 (CI: 0.566–0.571) | 0% |
| C_crowded_abundance | 44 (CI: 41–46) | 0.982 (CI: 0.980–0.984) | 0.848 (CI: 0.846–0.851) | 0.436 (CI: 0.433–0.440) | 0% |
| D_high_predation_survival | 77 (CI: 72–81) | 0.997 (CI: 0.997–0.998) | 0.933 (CI: 0.931–0.935) | 0.557 (CI: 0.555–0.560) | 0% |

**A_normal_baseline** (predator_pressure=0.25, disease_pressure=0.20, resource_abundance=0.60, space_constraint=0.40, K=500) served as the reference condition.

**B_hsap_abundance** (predator_pressure=0.10, disease_pressure=0.05, resource_abundance=1.50, space_constraint=0.20, K=500) produced 50% higher population than A. Male testosterone shifted from 0.994 to 0.986, directionally consistent with relaxed competitive endocrine signaling. The 95% confidence intervals for male testosterone do not overlap between A and B (Cohen $d=3.29$). Male aggression decreased from 0.895 to 0.847. The effect was statistically robust but modest in absolute magnitude (0.8 percentage points on a $[0,1]$ scale), indicating that the model's population-level separation is not driven by a large endocrine swing alone. Notably, B's mean fertility (0.568) is only marginally higher than A's (0.554), suggesting that the population increase in B is not primarily driven by increased reproductive output.

**C_crowded_abundance** (predator_pressure=0.10, disease_pressure=0.05, resource_abundance=1.50, space_constraint=0.90, K=200) stabilized at 44 agents, 47% below baseline despite identical resource availability to B. Fertility was reduced to 0.436 compared to 0.568 in B, indicating crowding pathology through fertility suppression rather than increased mortality.

**D_high_predation_survival** (predator_pressure=0.45, disease_pressure=0.15, resource_abundance=0.75, space_constraint=0.40, K=500) stabilized at 77 agents, 18% below baseline. Male testosterone (0.997) and aggression (0.933) were elevated above baseline, consistent with predator-mediated endocrine state.

## 4.3 Population Trajectories

The four core scenarios demonstrated that identical resource conditions (B and C share resource_abundance=1.50) can produce qualitatively different population outcomes depending on space constraint and predator/disease pressure. Population trajectories showed:

- **Stabilization** (A, B, D): populations reached steady state within 200–300 model-years
- **Partial collapse** (C): population declined to 31% of the resource-matched uncrowded condition (B)
- **No extinction** in core scenarios across all 200 runs

The comparison between B and C shows that, under model assumptions, space constraint alone can suppress population to 31% of the resource-matched uncrowded condition, with the crowding pathology manifesting through reduced fertility rather than increased mortality.

## 4.4 Sink, Recovery, and Collapse

The behavioral sink produced qualitatively distinct dynamics depending on scenario conditions (Table 2, Figure 6).

**C_crowded_stable** (control; same environment as C_crowded_abundance but with behavioral sink trigger raised to 0.92) produced outcomes identical to C_crowded_abundance (pop=44, male_T=0.982, 0% sink onset). This confirms that the behavioral sink requires its density-triggered mechanism; removing the trigger eliminates sink dynamics.

**E_behavioral_sink_recovery** (predator_pressure=0.20, disease_pressure=0.10, resource_abundance=1.00, space_constraint=0.80, K=200, sink_on_threshold=0.25) produced the characteristic sink-recovery pattern. The sink engaged in 62% of timesteps and disengaged in 36%. Population dipped from an initial transient to a minimum of $\sim$75 agents, then recovered to $\sim$98 agents. The behavioral sink is reversible under these conditions: the hysteresis mechanism allowed density to fall below the deactivation threshold, triggering recovery with fertility and mating drive boosts and mortality relief.

**F_behavioral_sink_partial_collapse** (predator_pressure=0.10, disease_pressure=0.05, resource_abundance=0.40, space_constraint=0.80, K=200, sink_on_threshold=0.15) produced severe partial collapse. Population was reduced to $\sim$4 agents (CI=[3, 5]). Sink engagement rate was 55%, but recovery rate was 0% — the behavioral sink never disengaged. Extinction occurred in 14% of runs (95% CI=[6%, 24%]). This is partial collapse with nonzero extinction risk.

## 4.5 Null Model Non-Identifiability

The null model comparison reveals that population trajectories alone are partly non-identifiable across the null model suite (Table 3, Figure 4).

Of 11 null models tested, 7 (logistic growth, predator-prey, density-fertility, dominance hierarchy, random hormone, density with recovery, random behavior) could not distinguish A from B using population trajectories alone (A/B MSE ratio $< 1.5$). The 1.5x threshold is a practical classification boundary: below this ratio, the null model fits both scenarios comparably well, indicating that population data alone cannot discriminate the endocrine mechanism from simpler alternatives.

Two models showed partial separation: disease pressure (N3: A MSE=25,637, B MSE=74,023) and endocrine-no-behavior (N10: A MSE=56,787, B MSE=86,016). One model (resource-only, N6) distinguished A from B but with poor overall fit (A MSE=23,850).

This non-identifiability is one of the paper's main results. It implies that a field study measuring population size alone cannot reject HSAP in favor of logistic growth, predator-prey dynamics, or density-dependent fertility. HSAP becomes testable only when population outcomes are paired with behavioral and endocrine observables — specifically, male testosterone and aggression measurements that null models cannot reproduce.

## 4.6 Ablation Analysis

The ablation analysis quantifies the contribution of each model component (Table 4, Figure 5).

| Ablation | B MSE | Fold increase | Interpretation |
|---|---|---|---|
| Full model | 73 | 1.0x | Reference |
| No male T downshift | 565 | 7.8x | Core mechanism |
| No female aggression | 397 | 5.4x | Core mechanism |
| No cortisol | 898 | 12.3x | Broad effect |
| No endocrine responsiveness | 2,458 | 33.7x | Coupling critical |
| No reproductive restraint | 2,293 | 31.4x | Density feedback |
| No sink recovery | 0 | — | Sink not activated |

Removing the male testosterone downshift channel increased B's population MSE from 73 (full model) to 565 — a 7.8-fold increase. Removing the female aggression channel increased it to 397 (5.4-fold). These two components are the minimal endocrine mechanisms required for HSAP's distinguishing power.

Removing endocrine responsiveness (the coupling between hormones and behavior) produced the largest MSE increase on B (2,458) compared to A (913), indicating that the endocrine-behavioral coupling is more consequential under reduced threat.

Removing sink recovery produced MSE=0 across all scenarios, because without the sink mechanism, the behavioral sink never engages. This is consistent with the internal consistency of the model.

## 4.7 Factorial Sweep

The 54-factorial analysis identifies space constraint as the dominant population regulator (Figure 7).

Under low space constraint (0.20), populations ranged from 99–143 agents regardless of predation, disease, or resource levels. Under high space constraint (0.80), populations ranged from 7.7–99 agents, showing that crowding pathology can override resource abundance.

The factorial analysis also reveals interaction effects: high predator pressure combined with high disease pressure produced population collapse only under high space constraint, suggesting that multiple stressors are necessary for collapse when space is abundant. Extinction was rare (only 2 of 54 conditions showed nonzero extinction, both at 3.3%).

## 4.8 Sensitivity Analysis

The factorial sweep suggests that space constraint had the strongest apparent association with final population size in the explored grid. A formal global sensitivity analysis was not included in the release package and should be treated as future work.

## 4.9 Genetic Algorithm Exploration

The GA exploration mapped the fitness landscape across endocrine and behavioral parameter space. Results are presented as exploratory search, not optimization proof. The GA identified parameter regions where population stabilization is maximized, but these results should be interpreted as demonstrating the existence of favorable parameter regions, not as evidence that biological populations operate in those regions.

## 4.10 Negative Results and Boundaries

These results demonstrate behavior of the HSAP computational model under specified parameterizations. They do not establish:

1. That the modeled mechanisms operate in natural populations
2. That the parameter values are empirically calibrated
3. That the observed trajectories are unique to endocrine-linked behavioral regulation
4. That HSAP is the correct or only model capable of producing these dynamics
5. That the HSAP composite indicator weights are biologically meaningful

The results support the narrower claim that this class of coupled ecological-behavioral feedback model can generate population-level dynamics that differ from simpler null formulations under controlled simulation conditions. The non-identifiability result (Section 4.5) shows that population data alone are insufficient to distinguish HSAP from simpler alternatives — a finding that strengthens the case for empirical testing while simultaneously limiting the conclusions that can be drawn from simulation alone.
