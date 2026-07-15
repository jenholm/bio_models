# 4. Results

All results reported here are from the validated pipeline: 3,050 simulation seeds across 61 scenarios, with null/ablation suite completed for 7 core scenarios. All scenario definitions are frozen in `src/hsap/scenarios.py`.

## 4.1 Core Scenario Separation

All four core scenarios produced distinct population outcomes (Table 1, Figure 2).

**A_normal_baseline** (predator_pressure=0.25, disease_pressure=0.20, resource_abundance=0.60, space_constraint=0.40, K=500) stabilized at a mean population of 94 agents (95% CI=$[89, 100]$) with zero extinctions across 50 seeds. Male testosterone averaged 0.994 (CI=$[0.993, 0.995]$).

**B_hsap_abundance** (predator_pressure=0.10, disease_pressure=0.05, resource_abundance=1.50, space_constraint=0.20, K=500) stabilized at 141 agents (CI=$[136, 147]$), a 50% increase over baseline. Male testosterone shifted to 0.986 (CI=$[0.985, 0.987]$), directionally consistent with relaxed competitive endocrine signaling. The 95% confidence intervals for male testosterone do not overlap between A and B (Cohen $d=3.29$). Male aggression similarly decreased from 0.895 (CI=$[0.892, 0.897]$) to 0.847 (CI=$[0.846, 0.849]$). The effect was statistically robust but modest in absolute magnitude (0.8 percentage points on a $[0,1]$ scale), indicating that the model's population-level separation is not driven by a large endocrine swing alone.

**C_crowded_abundance** (predator_pressure=0.10, disease_pressure=0.05, resource_abundance=1.50, space_constraint=0.90, K=200) stabilized at 44 agents (CI=$[41, 46]$), 47% below baseline despite identical resource availability. Fertility was reduced to 0.436 (CI=$[0.433, 0.440]$) compared to 0.568 in B, indicating crowding pathology. Male testosterone was 0.982 (CI=$[0.980, 0.984]$), slightly lower than B, consistent with density-mediated endocrine suppression.

**D_high_predation_survival** (predator_pressure=0.45, disease_pressure=0.15, resource_abundance=0.75, space_constraint=0.40, K=500) stabilized at 77 agents (CI=$[72, 81]$), 18% below baseline. Male testosterone (0.997, CI=$[0.997, 0.998]$) and aggression (0.933, CI=$[0.932, 0.935]$) were elevated above baseline, consistent with predator-mediated selection pressure on endocrine state.

## 4.2 Crowding Pathology

The comparison between B_hsap_abundance (pop=141, fertility=0.568) and C_crowded_abundance (pop=44, fertility=0.436) shows that space constraint alone, with identical resources, can suppress population to 31% of the resource-matched uncrowded condition. The crowding pathology manifests through reduced fertility, not increased mortality, consistent with density-dependent reproductive restraint rather than direct population control.

## 4.3 Sink, Recovery, and Collapse

The behavioral sink produced qualitatively distinct dynamics depending on scenario conditions (Table 2, Figure 5).

**C_crowded_stable** (control; same environment as C_crowded_abundance but with behavioral sink trigger raised to 0.92) produced outcomes identical to C_crowded_abundance: pop=44, male_T=0.982. This is consistent with the behavioral sink requiring its density-triggered mechanism; removing the trigger eliminates sink dynamics.

**E_behavioral_sink_recovery** (predator_pressure=0.20, disease_pressure=0.10, resource_abundance=1.00, space_constraint=0.80, K=200, sink_on_threshold=0.25) produced the characteristic sink-recovery pattern. The sink engaged in 62% of timesteps and disengaged in 36%. Population dipped from an initial transient to a minimum of $\sim$75 agents, then recovered to $\sim$98 agents. The behavioral sink is reversible under these conditions: the hysteresis mechanism allowed density to fall below the deactivation threshold, triggering recovery with fertility and mating drive boosts and mortality relief.

**F_behavioral_sink_partial_collapse** (predator_pressure=0.10, disease_pressure=0.05, resource_abundance=0.40, space_constraint=0.80, K=200, sink_on_threshold=0.15) produced severe partial collapse. Population was reduced to $\sim$4 agents (CI=$[3, 5]$). Sink engagement rate was 55%, but recovery rate was 0% — the behavioral sink never disengaged. Extinction occurred in 14% of seeds (95% CI=$[6\%, 24\%]$). This is partial collapse with nonzero extinction risk. The 14% extinction rate reflects stochastic variation in mortality and reproduction under conditions of sustained reproductive suppression.

## 4.4 Null Model Non-Identifiability

The null model comparison reveals that population trajectories alone are partly non-identifiable across the null model suite (Table 4, Figure 4a).

Of 11 null models tested, 7 (logistic growth, predator-prey, density-fertility, dominance hierarchy, random hormone, density with recovery, random behavior) could not distinguish A from B using population trajectories alone (A/B MSE ratio $< 1.5$). The 1.5x threshold is a practical classification boundary: below this ratio, the null model fits both scenarios comparably well, indicating that population data alone cannot discriminate the endocrine mechanism from simpler alternatives. Two models (disease pressure, endocrine-no-behavior) showed partial separation but with MSEs 25,000–86,000 compared to HSAP ablation MSEs of 70–2,458. One model (resource-only) distinguished A from B but with poor overall fit (MSE=23,850 for A).

This non-identifiability is one of the paper's main results. It implies that a field study measuring population size alone cannot reject HSAP in favor of logistic growth, predator-prey dynamics, or density-dependent fertility. HSAP becomes testable only when population outcomes are paired with behavioral and endocrine observables — specifically, male testosterone and aggression measurements that null models cannot reproduce.

## 4.5 Ablation Results

The HSAP ablation analysis quantifies the contribution of each model component (Table 5, Figure 4b).

Removing the male testosterone downshift channel increased B's population MSE from 73 (full model) to 565 — a 7.8-fold increase. Removing the female aggression channel increased it to 397 (5.4-fold). These two components are the minimal endocrine mechanisms required for HSAP's distinguishing power: they produce population separation between A and B while maintaining low overall MSE.

Removing cortisol increased MSE to 772–898 across scenarios, indicating a broader but less scenario-specific effect. Removing endocrine responsiveness (the coupling between hormones and behavior) produced larger MSE increases on B (2,458) than on A (913), indicating that the endocrine-behavioral coupling is more consequential under reduced threat.

Removing sink recovery produced MSE=0 across all scenarios, because without the sink mechanism, the behavioral sink never engages and the recovery phase never begins. This is consistent with the internal consistency of the model.

## 4.6 Factorial Sensitivity

The 54-factorial analysis (predator_pressure: 0.1/0.4/0.8; disease_pressure: 0.05/0.3/0.7; resource_abundance: 0.4/1.0/1.5; space_constraint: 0.2/0.8; K=500) identifies space constraint as the dominant population regulator (Table 3, Figure 8). Under low space constraint (0.20), populations ranged from 99–143 agents regardless of predation, disease, or resource levels. Under high space constraint (0.80), populations ranged from 4–13 agents under high predation and disease, showing that crowding pathology can override resource abundance.

The factorial analysis also reveals interaction effects: high predator pressure combined with high disease pressure produced population collapse only under high space constraint, suggesting that multiple stressors are necessary for collapse when space is abundant.

## 4.7 Summary

The validated pipeline (3,050 seeds, 61 scenarios) produced the following key findings:

1. Four core scenarios generated distinct population outcomes: pop=94 (A), 141 (B), 44 (C), 77 (D)
2. The behavioral sink mechanism produced recovery (E) or partial collapse (F) depending on environmental context
3. 7 of 11 null models could not distinguish HSAP from simpler alternatives on population data alone
4. Male testosterone downshift and female aggression are the two minimal endocrine mechanisms for population separation
5. Space constraint is the dominant population regulator in the factorial analysis
