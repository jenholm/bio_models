# 5. Discussion

## 5.1 Summary of Findings

Under the model's assumptions, HSAP demonstrates that coupled endocrine-behavioral feedbacks can generate population-level dynamics that differ from simpler null formulations. Four core scenarios produced distinct population outcomes under identical resource conditions: the same resource abundance (1.50) produced populations of 141 (B_hsap_abundance) and 44 (C_crowded_abundance), depending on space constraint and threat level. The behavioral sink mechanism produced two distinct outcomes — recovery (E) or partial collapse (F) — depending on environmental context, not mechanism design.

These results are simulation-consistent, not proven. They demonstrate that the class of feedback structures described by HSAP is sufficient to produce qualitatively distinct population dynamics under defined assumptions. They do not demonstrate that these mechanisms operate in natural populations.

## 5.2 What This Paper Is Not

This paper is not:

1. **An empirical claim.** HSAP is a computational model. It does not establish that endocrine feedbacks drive population dynamics in any species. The parameter values are illustrative, not empirically calibrated.

2. **A predictive model.** HSAP does not predict population sizes, trajectories, or outcomes for specific ecosystems. It explores a class of feedback structures, not a specific parameterization.

3. **A universal explanation.** HSAP does not claim that endocrine-behavioral feedbacks are the primary mechanism of population regulation. It claims they are a candidate mechanism worth testing.

4. **A human behavioral model.** HSAP is a mammalian population model. It does not model human sexual orientation, human social dynamics, or human population regulation. Non-reproductive behavior is treated only as species-specific ethological behavior.

5. **An optimization result.** The genetic algorithm exploration maps fitness landscapes; it does not identify optimal parameter values for biological populations.

The paper's contribution is narrower: it identifies a family of coupled ecological-behavioral feedback mechanisms that can produce population-level dynamics distinguishable from simpler alternatives — but only when behavioral and endocrine observables are included alongside population data.

## 5.3 The Non-Identifiability Result

The null model comparison is the paper's most important result for empirical science. Seven of 11 null models could not distinguish HSAP from simpler alternatives (logistic growth, predator-prey, density-fertility) on population trajectories alone. Population data alone are insufficient to identify the mechanistic pathways driving stabilization or collapse.

This non-identifiability has two implications:

**For modelers:** Population trajectories alone cannot discriminate between endocrine-mediated regulation and simpler ecological mechanisms. Any model producing reasonable population dynamics should be tested against null alternatives before claiming mechanistic specificity.

**For empiricists:** Field studies measuring population size alone cannot reject HSAP in favor of logistic growth, or vice versa. HSAP becomes testable only when population outcomes are paired with behavioral and endocrine observables — specifically, male testosterone and aggression measurements that null models cannot reproduce.

This is a call for richer data in conservation biology, not a dismissal of population monitoring. Population data remain essential, but they are insufficient for mechanism identification.

## 5.4 Testable Predictions

HSAP generates three predictions for post-predator-removal populations, each falsifiable with paired endocrine-behavioral data:

1. **Endocrine signature.** Male testosterone should decrease following predator removal, with magnitude proportional to the reduction in perceived threat. This is the most direct test of the endocrine feedback loop.

2. **Crowding pathology.** Populations in space-constrained environments should show higher cortisol and lower fertility than resource-matched populations in unconstrained environments, even when resource availability is identical.

3. **Behavioral sink persistence.** Populations under high combined stressors (predation + disease + crowding) should show persistent reproductive suppression despite below-capacity density, consistent with the behavioral sink mechanism.

These predictions require paired endocrine and behavioral field measurements. They cannot be tested using population data alone — a direct consequence of the non-identifiability result.

## 5.5 Model Limitations

Several limitations constrain the interpretation of HSAP results:

**No empirical calibration.** All 71 parameters are model assumptions. The endocrine update equations, behavioral output functions, and sink mechanism are hypothesized, not empirically derived. Species-specific calibration is future work.

**No spatial geography.** The model uses a well-mixed population approximation. Agents are not assigned spatial coordinates. This excludes spatial processes such as habitat fragmentation, metapopulation dynamics, and localized resource depletion.

**Anonymous social interactions.** Social interactions are pairwise and anonymous. There is no kin recognition, no persistent social network, no reciprocal altruism, and no reputation system. This excludes network-mediated effects such as kin selection and social learning.

**No seasonality.** Seasonal variation was not modeled. Simulations represent normalized ecological conditions.

**B_hsap_abundance fertility limitation.** In scenario B (abundance), mean fertility (0.568) is only marginally higher than in scenario A (baseline, 0.554). The HSAP mechanism reduces male testosterone and aggression but does not substantially reduce female fertility under the tested parameterization. This is a limitation, not a feature.

**Cohen d inflation.** The reported Cohen d = 3.29 for male testosterone between A and B is inflated by the low variance across simulation runs. Simulation precision is not biological variance. Effect sizes should be interpreted with caution.

**Mixed-depth factorial.** Core scenarios use 50 runs; factorial scenarios use 30 runs. This reflects a deliberate trade-off between statistical power and parameter-space exploration.

## 5.6 Implications for Conservation Biology

The behavioral sink concept has practical implications for conservation. If populations can enter self-reinforcing states of reproductive failure that persist beyond the ecological conditions that triggered them, then:

1. **Population recovery may require active intervention** beyond predator control or habitat restoration. Behavioral and endocrine recovery may lag ecological recovery.

2. **Population monitoring should include behavioral and endocrine metrics.** Population size alone cannot distinguish between resource-limited regulation and endocrine-mediated behavioral sink dynamics.

3. **Multiple stressors may create irreversible states.** Under model assumptions, the partial collapse scenario (F) shows that combinations of predation, disease, and crowding can produce persistent reproductive suppression that does not resolve when individual stressors are reduced.

These implications are simulation-consistent, not proven. They suggest that conservation biology should consider endocrine and behavioral monitoring alongside population monitoring — a recommendation that requires empirical validation.

## 5.7 Future Work

HSAP provides a foundation for several extensions:

1. **Species-specific calibration.** Parameterize HSAP for a specific mammalian species with empirical endocrine and behavioral data.

2. **Spatial extension.** Add explicit spatial structure to test whether habitat fragmentation interacts with behavioral sink dynamics.

3. **Network extension.** Replace anonymous interactions with social network structure to test whether network topology affects endocrine-mediated regulation.

4. **Empirical validation.** Design field studies that pair population monitoring with endocrine sampling to test HSAP's predictions in post-predator-removal systems.

5. **Mechanism decomposition.** Identify which components of the endocrine-behavioral feedback loop are necessary and sufficient for population-level effects under field-relevant conditions.
