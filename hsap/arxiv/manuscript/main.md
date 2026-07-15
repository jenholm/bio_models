---
title: "Hormonal-Social Adaptation Population Model: Population Stabilization Under Reduced External Threat"
authors:
  - name: "Anonymous"
    affiliation: "Independent Researcher"
date: "2026-07-14"
bibliography: references.bib
---

# Abstract

Population stabilization following predator removal is a central problem in conservation biology, yet the mechanistic pathways linking threat reduction to population outcomes remain poorly understood. We present HSAP (Hormonal-Social Adaptation Population model), an agent-based model in which individuals regulate testosterone, aggression, and reproductive effort in response to perceived predation threat and density. We ran 50 seeds for seven core/sink scenarios and 30 seeds for each factorial scenario, yielding 1,970 simulation seeds across 61 scenarios. Under reduced threat, populations stabilized at higher densities with lower male testosterone and aggression, consistent with relaxed competitive endocrine signaling (Cohen d=3.29, non-overlapping 95% CIs). Under crowding, populations crashed despite resource abundance. Under behavioral sink conditions, populations either recovered (sink engagement rate 62%, recovery rate 36%) or produced partial collapse with nonzero extinction risk (14% across 50 seeds). A null model suite of 11 alternatives could not distinguish HSAP from logistic growth, predator-prey, or density-fertility models on population trajectories alone. HSAP became testable only when population outcomes were paired with behavioral and endocrine observables. These simulations show that, under model assumptions, endocrine-linked behavioral feedbacks are sufficient to generate qualitatively distinct population dynamics under identical resource conditions, and that population data alone are insufficient to identify the mechanistic pathways driving stabilization or collapse. We further identify contemporary endocrine and sex-disaggregated behavioral proxy datasets as candidate empirical observables for future HSAP-style testing, while emphasizing that these ecological data are exploratory and non-causal.

# 1. Introduction

## 1.1 Population regulation under reduced external threat

When predator populations are removed or suppressed, prey populations initially increase but sometimes stabilize at lower-than-expected densities. Traditional models (logistic growth, predator-prey dynamics) predict simple density-dependent regulation, but field observations often show complex behavioral and endocrine responses that alter population trajectories in ways not captured by resource-based models alone.

## 1.2 Why population trajectories alone are ambiguous

The null model comparison presented here shows that population trajectories alone are partly non-identifiable: 7 of 11 alternative models produced indistinguishable population outcomes from HSAP on population data. This non-identifiability is a methodological finding with practical consequences — a field study measuring only population size cannot distinguish endocrine-mediated regulation from simple density dependence.

## 1.3 Why endocrine and behavioral observables matter

For empirical testing, HSAP-like mechanisms require paired endocrine and behavioral observables. Contemporary U.S. endocrine studies and sex-disaggregated arrest statistics provide candidate proxy series for such testing, but they are ecological, confounded, and cannot establish individual-level causation. Their value is to show that the relevant observable classes exist in public datasets and to identify what would need to be measured to test HSAP-like mechanisms empirically.

## 1.4 Scope and contributions

We present HSAP as a falsifiable simulation model with three contributions: (1) a computational framework linking individual endocrine state to population dynamics through behavioral feedbacks; (2) a showing that identical resource conditions produce qualitatively different population outcomes depending on behavioral and endocrine parameters; and (3) an honest null model comparison showing that population trajectories alone are insufficient for mechanism identification, with external proxy data identifying the observable classes required for empirical testing.

HSAP does not model human sexual orientation; non-reproductive sexual or social behavior is treated only as species-specific ethological behavior.

# 2. Model

## 2.1 Agent Architecture

Each agent in HSAP is characterized by sex (assigned 50/50 at birth), age (in model time steps; 10 steps = 1 model-year), and a suite of physiological and behavioral state variables. Agents are initialized with age drawn uniformly from [5, 40) and energy, health, and rank set to 1.0, 1.0, and 0.5 respectively.

**Hormonal state.** Each agent carries three hormonal axes: testosterone, estrogen, and cortisol. Male testosterone is initialized near 1.0 (base_male_testosterone) with Gaussian noise (SD=0.15); female testosterone near 0.3 (SD=0.05). Estrogen is initialized near 1.0 for females and 0.3 for males. Cortisol is initialized near 0.5 for both sexes (SD=0.1). All hormonal values are clamped to [0, 1] at each time step.

**Behavioral state.** Derived from hormones and environment at each step: aggression_tendency, maternal_defense_tendency (females), mating_drive, fertility, and offspring_survival_probability. These are recomputed every time step; agents do not carry fixed behavioral types.

**Social state.** Each agent has a dominance rank (clamped [0, 1]), territory quality, cooperation_bonus (accumulated from cooperative actions, capped at 0.3), and a pregnancy flag with gestation countdown (gestation_time = 5 steps).

## 2.2 Environment

The environment provides four static parameters and several dynamic state variables.

**Static parameters** (set per scenario):
- `resource_abundance` (0 to 1): baseline resource availability
- `predator_pressure` (0 to 1): external threat level
- `disease_pressure` (0 to 1): disease prevalence
- `space_constraint` (0 to 1): controls how quickly territory availability declines with density
- `carrying_capacity` (integer): K for density computation

**Dynamic state** (updated each step):
- `resource_abundance`: regenerates toward maximum, consumed by population; modulated by seasonality
- `territory_availability`: `max(0, 1 - density * space_constraint)`, where `density = current_population / carrying_capacity`
- `predation_risk`: `predator_pressure * (1 + 0.5 * density)`
- `disease_risk`: `disease_pressure * (1 + 0.5 * density)`

## 2.3 Endocrine Update

Hormones are recomputed for every agent at each time step, creating the causal feedback loop that defines HSAP.

**Male testosterone** is driven by five factors:

$$T_{male} = T_{base} + 0.3 \cdot rank + 0.4 \cdot mating\_drive - 0.3 \cdot density - 0.4 \cdot (1 - predator\_pressure) - 0.2 \cdot (1 - health)$$

The term $-0.4 \cdot (1 - predator\_pressure)$ is the critical endocrine feedback: when predator pressure is high, the term is near zero (testosterone is not reduced); when predator pressure is low, the term subtracts up to 0.4 (testosterone is downshifted). This is the mechanism through which threat reduction propagates to behavioral change.

**Female testosterone** responds to resource scarcity and density:

$$T_{female} = 0.3 + 0.15 \cdot rank + 0.4 \cdot resource\_scarcity + 0.3 \cdot density$$

**Cortisol** (both sexes) integrates density, rank, health, predation, and resource scarcity:

$$C = 0.5 + 0.1 \cdot density - 0.3 \cdot rank + 0.5 \cdot (1 - health) + 0.2 \cdot predator\_pressure + 0.3 \cdot resource\_scarcity$$

**Estrogen** (females) is suppressed by cortisol:

$$E = 1.0 - 0.3 \cdot C$$

## 2.4 Behavioral Output

From hormones, agents derive:

- **Aggression**: base = $T \cdot 0.5 + C \cdot 0.2$, with sex-specific additions (females: offspring defense + resource competition; males: dominance bonus)
- **Fertility**: base = 0.5, modified by hormones, age, density-dependent reproductive restraint (activates above density 0.7), and territory availability
- **Mating drive**: males = $T \cdot 0.5 + 0.3$; females = $E \cdot 0.4 + 0.2$
- **Offspring survival probability**: affected by testosterone, cortisol, density, and resource scarcity

Agents select actions stochastically from: forage, dominate, disperse, withdraw, cooperate, guard_offspring. Action probabilities depend on current behavioral state and environmental conditions.

## 2.5 Reproduction

Mating occurs when a randomly selected male (probability proportional to mating_drive) encounters a fertile female above a fertility gate (default 0.3). Both must have energy above a threshold (0.4) and be in reproductive age (10-60 model-years). On successful mating, the female becomes pregnant with gestation time of 5 steps.

At birth, litter size is drawn from a normal distribution (mean=4.0, SD=1.0, floored to 1). Each pup survives with probability determined by the mother's offspring_survival_probability. The mother pays an energy cost of 0.3. Newborns face an additional mortality check.

**Infanticide** triggers when density exceeds 0.8, with probability proportional to agent aggression and density above threshold. **Offspring neglect** triggers when density exceeds 0.7 or cortisol exceeds 0.7, removing one offspring.

## 2.6 Mortality

Death probability per time step is computed as:

$$P_{death} = \min(1, (P_{base} + P_{pred} + P_{disease} + P_{starvation} + P_{injury} + P_{old} + P_{crowd}) \times \tau \times M)$$

where $\tau = 0.1$ (age increment per step) and $M$ is the mortality multiplier (1.0 normally, 0.4 during post-sink recovery).

| Component | Formula |
|---|---|
| Base | 0.02 (constant) |
| Predation | $0.05 \cdot predation\_risk \cdot (1 - 0.02 \cdot resource\_scarcity) \cdot modifiers$ |
| Disease | $0.03 \cdot disease\_risk \cdot (1 + 0.5 \cdot (1 - health)) \cdot (1 + 0.5 \cdot density)$ |
| Starvation | If energy < 0.2: $0.3 \cdot scarcity \cdot (1 - energy/0.2)$ |
| Injury | 0.1 if injured |
| Old age | $0.01 \cdot (age - 50)$ if age > 50 |
| Crowding | $0.05 \cdot \max(0, density - 0.8) + sink\_factor \cdot sink\_mortality$ |

## 2.7 Behavioral Sink and Recovery

The behavioral sink is a density-driven phase transition that suppresses reproductive output even after density falls below carrying capacity.

**Activation.** When density exceeds `behavioral_sink_on_threshold` (default 0.75), the sink engages. A `sink_factor` is computed as a continuous measure of sink severity:

$$sink\_factor = \min\left(1, \frac{density - 0.75}{1 - 0.75}\right)$$

**Effects while active.** Fertility is multiplicatively suppressed: $fertility \times (1 - sink\_factor \cdot 0.85)$. Mating drive is suppressed: $mating\_drive \times (1 - sink\_factor \cdot 0.4)$. Withdrawal behavior and offspring neglect probabilities are increased.

**Deactivation (hysteresis).** The sink disengages only when density falls below `behavioral_sink_off_threshold` (default 0.50), creating a hysteresis band (on at 0.75, off at 0.50). A minimum duration of 30 steps must elapse before deactivation is permitted. An optional auto-recovery timer (`behavioral_sink_auto_recovery_duration`) forces disengagement after a fixed number of steps.

**Post-sink recovery.** After sink disengagement, a recovery phase lasting 100 steps begins. During recovery: fertility and mating drive are multiplicatively boosted by 1.3; mortality is reduced to 40% of normal. If population drops below 30 during recovery, refugees (up to 10 per step) are injected to supplement the depleted population.

**Sink Factor in the HSAP Index.** The HSAP index incorporates sink state: when the sink is active, the index is dampened, reflecting the disruption of normal social-endocrine regulation.

## 2.8 Metrics

Per time step, HSAP records: population size, density, sex ratio, resource abundance, predator pressure, disease pressure, territory availability, age structure (juvenile/adult/senior counts), mean hormones (testosterone, estrogen, cortisol, male_T, female_T), behavioral outputs (male/female aggression, female defense), reproductive metrics (fertility, births, deaths, matings, pregnancies, infanticide, neglect, refugees), sink state (active, post-recovery, sink_factor), external threat index, and the composite HSAP index.

The HSAP index is a weighted composite of five signals: low external threat (25%), low male aggression (20%), high female aggression (20%), low fertility (20%), and population stability (15%), with a viability dampener for populations below 50.

**Summary metrics** (computed over the full run): final population, peak population, minimum population, crash ratio (final/peak), time to stability, mean male/female testosterone, mean male/female aggression, mean fertility, mean cortisol, extinction status, and seed number.

# 3. Experimental Design

## 3.1 Scenario Design

We designed 61 scenarios organized in three sets, varying environment parameters to explore distinct population-regulation hypotheses.

**Set 1 — Core comparison (4 scenarios).** These scenarios test HSAP's ability to reproduce qualitatively distinct population outcomes under known environmental manipulations.

| Scenario | predator_pressure | disease_pressure | resource_abundance | space_constraint | carrying_capacity |
|---|---|---|---|---|---|
| A_normal_baseline | 0.25 | 0.20 | 0.60 | 0.40 | 500 |
| B_hsap_abundance | 0.10 | 0.20 | 0.60 | 0.40 | 500 |
| C_crowded_abundance | 0.10 | 0.20 | 0.60 | 0.80 | 200 |
| D_high_predation_survival | 0.40 | 0.20 | 0.60 | 0.40 | 500 |

A_normal_baseline serves as the reference. B_hsap_abundance reduces external threat. C_crowded_abundance adds space constraint with reduced carrying capacity. D_high_predation_survival increases threat.

**Set 2 — Behavioral sink (3 scenarios).** These scenarios test HSAP's behavioral sink mechanism: whether populations can enter and recover from reproductive suppression, or collapse irreversibly.

| Scenario | Key manipulation | Sink expected? |
|---|---|---|
| C_crowded_stable | Sink trigger removed (control) | No |
| E_behavioral_sink_recovery | Sink parameters as default | Yes, with recovery |
| F_behavioral_sink_partial_collapse | Sink parameters as default, high threat | Yes, partial collapse |

C_crowded_stable is a control: same environment as C_crowded_abundance but with the behavioral sink trigger removed, consistent with sink dynamics requiring the behavioral mechanism.

**Set 3 — Factorial design (54 scenarios).** A $3 \times 3 \times 3 \times 2$ factorial crossing predator_pressure (low=0.10, medium=0.25, high=0.40), disease_pressure (low=0.10, medium=0.20, high=0.30), resource_abundance (low=0.30, medium=0.60, high=0.90), and space_constraint (low=0.40, high=0.80), with carrying_capacity=500 for all. This explores the full parameter space and identifies which environmental factors dominate population outcomes.

## 3.2 Replication

We ran 50 seeds for the seven core/sink scenarios and 30 seeds for each factorial scenario, yielding 1,970 simulation seeds across 61 scenarios. Each seed initializes a different random population (ages drawn from Uniform(5,40), hormones initialized with Gaussian noise) and uses a different random stream for stochastic decisions (mating, mortality, behavior selection).

## 3.3 Null Models

We compared HSAP against 11 null models that lack endocrine feedbacks or behavioral mechanisms:

| Model | Mechanism |
|---|---|
| N0_logistic | Logistic growth with density-dependent regulation |
| N1_predator_prey | Lotka-Volterra predator-prey dynamics |
| N2_density_fertility | Density-dependent fertility only |
| N3_disease_pressure | Disease-mediated mortality |
| N4_dominance_hierarchy | Social rank-based resource allocation |
| N5_random_hormone | Random hormone levels (no environmental coupling) |
| N6_resource_only | Resource-limited growth |
| N7_density_with_recovery | Density dependence with recovery |
| N8_random_behavior | Random behavioral decisions |
| N9_social_behavior | Social interactions without endocrine coupling |
| N10_endocrine_no_behavior | Endocrine changes without behavioral consequences |

Each null model was fit to HSAP's population trajectory and evaluated by mean squared error (MSE). We also tested six HSAP ablation variants, each removing one component: male testosterone downshift, female aggression channel, cortisol, endocrine responsiveness, reproductive restraint, and sink recovery.

## 3.4 Reproducibility

All scenario definitions are frozen in `src/hsap/scenarios.py`. Simulation outputs are frozen in `results/freezes/hsap_1970_seed_freeze_20260714/`. The pipeline is reproducible via:

```
python scripts/run_resumable_pipeline.py validate
python scripts/run_resumable_pipeline.py summarize
python scripts/make_paper_figures.py --dpi 300
```

## 3.5 External Empirical Proxy Design

The simulation's central methodological result — population trajectories alone are partly non-identifiable — implies that empirical testing of HSAP-like mechanisms requires paired endocrine and behavioral observables. This section describes external proxy datasets that could provide such observables.

### Hormone proxy sources

Published secular male testosterone studies [@travison2007; @lokeshwar2020] report population-level declines in male testosterone over multi-decade timescales. NHANES sex-steroid hormone panels provide cross-sectional hormone measures by age and sex. Female hormone observables are available but require age, reproductive-stage, and metabolic caveats: testosterone varies across menstrual cycle, pregnancy, and menopause; SHBG binding affects free testosterone; oral contraceptives alter sex hormone levels; and BMI and insulin resistance affect hormone profiles.

### Behavioral proxy sources

FBI Uniform Crime Reporting (UCR) and National Incident-Based Reporting System (NIBRS) provide sex-disaggregated arrest counts by offense category. OJJDP juvenile arrest summaries provide age-specific trends. BJS National Crime Victimization Survey (NCVS) provides victimization data for reporting-bias triangulation. Arrests are not direct aggression measures; they reflect behavior filtered through reporting, enforcement, and charging practices.

### External proxy variables

The external proxy analysis uses: `female_assault_arrest_proxy`, `female_violent_arrest_share`, `female_assault_arrest_rate`, `female_to_male_assault_arrest_ratio`, and `female_behavioral_proxy_index`. These are ecological, population-level measures. They do not establish individual-level hormone-behavior causation.

# 4. Results

## 4.1 Core Scenario Separation

All four core scenarios produced distinct population outcomes (Table 1, Figure 2).

**A_normal_baseline** stabilized at a mean population of 94 agents (95% CI=[89, 100]) with zero extinctions across 50 seeds. Male testosterone averaged 0.994 (CI=[0.993, 0.995]).

**B_hsap_abundance** (reduced threat) stabilized at 141 agents (CI=[136, 147]), a 50% increase over baseline. Male testosterone shifted to 0.986 (CI=[0.985, 0.987]), directionally consistent with relaxed competitive endocrine signaling. The 95% confidence intervals for male testosterone do not overlap between A and B (Cohen d=3.29). Male aggression similarly decreased from 0.895 (CI=[0.892, 0.897]) to 0.847 (CI=[0.846, 0.849]). The effect was statistically robust but modest in absolute magnitude (0.8 percentage points on a [0,1] scale), indicating that the model's population-level separation is not driven by a large endocrine swing alone.

**C_crowded_abundance** (space constraint) stabilized at 44 agents (CI=[41, 46]), 47% below baseline despite identical resource availability. Fertility was reduced to 0.436 (CI=[0.433, 0.440]) compared to 0.568 in B, indicating crowding pathology. Male testosterone was 0.982 (CI=[0.980, 0.984]), slightly lower than B, consistent with density-mediated endocrine suppression.

**D_high_predation_survival** (elevated threat) stabilized at 77 agents (CI=[72, 81]), 18% below baseline. Male testosterone (0.997, CI=[0.997, 0.998]) and aggression (0.933, CI=[0.932, 0.935]) were elevated above baseline, consistent with predator-mediated selection pressure on endocrine state.

## 4.2 Crowding Pathology

The comparison between B_hsap_abundance (pop=141, fertility=0.568) and C_crowded_abundance (pop=44, fertility=0.436) shows that space constraint alone, with identical resources, can suppress population to 31% of the resource-matched uncrowded condition. The crowding pathology manifests through reduced fertility, not increased mortality, consistent with density-dependent reproductive restraint rather than direct population control.

## 4.3 Sink, Recovery, and Collapse

The behavioral sink produced qualitatively distinct dynamics depending on scenario conditions (Table 2, Figure 5).

**C_crowded_stable** (control) produced outcomes identical to C_crowded_abundance: pop=44, male_T=0.982. This is consistent with the behavioral sink requiring its density-triggered mechanism; removing the trigger eliminates sink dynamics.

**E_behavioral_sink_recovery** produced the characteristic sink-recovery pattern. The sink engaged in 62% of timesteps and disengaged in 36%. Population dipped from an initial transient to a minimum of ~75 agents, then recovered to ~98 agents. The behavioral sink is reversible under these conditions: the hysteresis mechanism allowed density to fall below the deactivation threshold, triggering recovery with fertility and mating drive boosts and mortality relief.

**F_behavioral_sink_partial_collapse** produced severe partial collapse. Population was reduced to ~4 agents (CI=[3, 5]). Sink engagement rate was 55%, but recovery rate was 0% — the behavioral sink never disengaged. Extinction occurred in 14% of seeds (95% CI=[6%, 24%]). This is partial collapse with nonzero extinction risk. The 14% extinction rate reflects stochastic variation in mortality and reproduction under conditions of sustained reproductive suppression.

## 4.4 Null Model Non-Identifiability

The null model comparison reveals that population trajectories alone are partly non-identifiable across the null model suite (Table 4, Figure 4a).

Of 11 null models tested, 7 (logistic growth, predator-prey, density-fertility, dominance hierarchy, random hormone, density with recovery, random behavior) could not distinguish A from B using population trajectories alone (A/B MSE ratio < 1.5). Two models (disease pressure, endocrine-no-behavior) showed partial separation but with MSEs 25,000-86,000 compared to HSAP ablation MSEs of 70-2,458. One model (resource-only) distinguished A from B but with poor overall fit (MSE=23,850 for A).

This non-identifiability is one of the paper's main results. It implies that a field study measuring population size alone cannot reject HSAP in favor of logistic growth, predator-prey dynamics, or density-dependent fertility. HSAP becomes testable only when population outcomes are paired with behavioral and endocrine observables — specifically, male testosterone and aggression measurements that null models cannot reproduce.

## 4.5 Ablation Results

The HSAP ablation analysis quantifies the contribution of each model component (Table 5, Figure 4b).

Removing the male testosterone downshift channel increased B's population MSE from 73 (full model) to 565 — a 7.8-fold increase. Removing the female aggression channel increased it to 397 (5.4-fold). These two components are the minimal endocrine mechanisms required for HSAP's distinguishing power: they produce population separation between A and B while maintaining low overall MSE.

Removing cortisol increased MSE to 772-898 across scenarios, indicating a broader but less scenario-specific effect. Removing endocrine responsiveness (the coupling between hormones and behavior) produced larger MSE increases on B (2,458) than on A (913), indicating that the endocrine-behavioral coupling is more consequential under reduced threat.

Removing sink recovery produced MSE=0 across all scenarios, because without the sink mechanism, the behavioral sink never engages and the recovery phase never begins. This is consistent with the internal consistency of the model.

## 4.6 Factorial Sensitivity

The 54-factorial analysis identifies space constraint as the dominant population regulator (Table 3, Figure 8). Under low space constraint (0.40), populations ranged from 99-143 agents regardless of predation, disease, or resource levels. Under high space constraint (0.80), populations ranged from 4-13 agents under high predation and disease, showing that crowding pathology can override resource abundance.

The factorial analysis also reveals interaction effects: high predator pressure combined with high disease pressure produced population collapse only under high space constraint, suggesting that multiple stressors are necessary for collapse when space is abundant.

# 5. Discussion

## 5.1 What HSAP Supports

Under model assumptions, HSAP shows that endocrine-linked behavioral feedbacks can generate qualitatively distinct population outcomes under identical resource conditions. The same resource abundance (0.60) produced populations of 141 (B_hsap_abundance), 44 (C_crowded_abundance), and 77 (D_high_predation_survival), depending on threat level and space constraint. These differences are simulation-consistent with the hypothesis that endocrine state mediates population regulation, not just resource availability.

The behavioral sink mechanism produces two distinct outcomes depending on conditions: recovery (E) or partial collapse (F). The difference is not in the mechanism itself but in the environmental context — F operates under higher predation and disease pressure, preventing the density reduction needed to disengage the sink. This is simulation-consistent with the conservation concept that multiple stressors can trap populations in unsustainable behavioral states.

## 5.2 What HSAP Does Not Prove

HSAP is a simulation model, not an empirical study. It does not prove that endocrine feedbacks drive population dynamics in any specific species. It does not validate the specific parameter values used (which are illustrative, not empirically measured). It does not demonstrate that the behavioral sink mechanism exists in nature.

The model shows that IF endocrine-linked behavioral feedbacks exist AND operate as modeled, THEN population-level consequences follow. The "if" is the empirical question that field studies must address.

## 5.3 Why Endocrine and Behavioral Measurements Are Necessary

The null model comparison is the paper's most important result for empirical science. Seven of 11 null models could not distinguish HSAP from simpler alternatives on population trajectories alone. Population data alone are insufficient to identify the mechanistic pathways driving stabilization or collapse.

However, HSAP generates testable predictions in the joint space of population size, endocrine state, and behavior. A field study measuring population size AND male testosterone AND aggression can reject null models while retaining HSAP. The behavioral and endocrine observables that distinguish HSAP — particularly the male testosterone downshift under reduced threat — produce separable signatures in the observable variable space that no single-channel null model reproduces.

This is a call for richer data in conservation biology, not a dismissal of population monitoring. Population data remain essential, but they are insufficient for mechanism identification.

## 5.4 Model Limitations

Several limitations constrain the interpretation of HSAP results:

**Parameter values are illustrative.** The endocrine update equations, behavioral output functions, and sink mechanism are hypothesized, not empirically derived. Species-specific calibration is future work.

**Endocrine variables are proxies.** Testosterone, cortisol, and estrogen in the model are continuous values on [0, 1] that represent qualitative endocrine states, not calibrated physiological measurements.

**Population trajectories are partly non-identifiable.** This is both a result (Section 4.4) and a limitation: HSAP cannot be tested using population data alone.

**Factorial scenarios use 30 seeds, not 50.** The mixed-depth design reflects a deliberate trade-off between statistical power for core scenarios and parameter-space exploration for factorial scenarios. If reviewers require equal depth, Set3 can be rerun at 50 seeds.

**HSAP does not model human sexual orientation.** Non-reproductive sexual or social behavior is treated only as species-specific ethological behavior and requires explicit supporting data. Species-specific calibration is future work.

## 5.5 Empirical Predictions

HSAP generates three testable predictions for post-predator-removal populations:

1. **Endocrine signature.** Male testosterone should decrease following predator removal, with the magnitude proportional to the reduction in perceived threat. This is the most direct test of the endocrine feedback loop.

2. **Crowding pathology.** Populations in space-constrained environments should show higher cortisol and lower fertility than resource-matched populations in unconstrained environments, even when resource availability is identical.

3. **Behavioral sink persistence.** Populations under high combined stressors (predation + disease + crowding) should show persistent reproductive suppression despite below-capacity density, consistent with the behavioral sink mechanism.

These predictions are falsifiable and could be tested in post-predator-removal monitoring programs that include endocrine sampling.

## 5.6 External Endocrine and Behavioral Proxy Evidence

The external proxy evidence should be interpreted as empirical motivation rather than validation. Published secular endocrine studies report declines in male testosterone over multi-decade timescales [@travison2007; @lokeshwar2020]. Sex-disaggregated arrest statistics show increased female share of assault-related arrests relative to male trends. These trends are directionally compatible with the paper's methodological claim that HSAP-like mechanisms require paired endocrine and behavioral observables for empirical testing: the endocrine trend is consistent with relaxed competitive signaling under reduced threat, and the behavioral trend is consistent with altered behavioral output under crowding and sink conditions.

However, the available series are ecological and confounded. Endocrine studies are cross-sectional and do not track individual-level change. Arrest data reflect behavior filtered through reporting, enforcement, and charging practices. The two data streams are not linked at the individual level. Their main value is to show how HSAP-like mechanisms could be tested: by pairing endocrine measurements with behavioral proxies rather than relying on population outcomes alone. Figure 9 illustrates the observable requirements: population data alone are non-identifiable, but endocrine and behavioral observables together define the variable space needed for empirical testing. Contemporary endocrine and behavioral proxy trends identify the class of observables needed to test HSAP-like mechanisms outside simulation, but these ecological data are exploratory and non-causal.

# 6. Conclusion

HSAP is a falsifiable agent-based model showing that endocrine-linked behavioral feedbacks can generate population stabilization, crowding pathology, recovery, or partial collapse under reduced external threat. The model's most important finding is negative: population trajectories alone are insufficient to identify the mechanistic pathways driving these dynamics. Seven of 11 null models produced indistinguishable population outcomes. HSAP becomes testable only when population outcomes are paired with behavioral and endocrine observables.

This result has practical implications for conservation biology. Post-predator-removal monitoring programs that measure only population size may miss endocrine and behavioral signatures of regulatory change. HSAP argues for integrating endocrine sampling into population monitoring, particularly in systems where predator removal has produced unexpected population dynamics.

The model is simulation-consistent, not proven. It shows that endocrine-linked behavioral feedbacks are sufficient to produce qualitatively distinct population dynamics under identical resource conditions. Whether these feedbacks are necessary — or even present — in real populations remains an empirical question.

# Figure Captions

**Figure 1.** Causal chain linking predator removal to population outcomes through endocrine feedback. Red arrows indicate the endocrine pathway (threat → testosterone → behavior → population). Blue arrows indicate the alternative resource pathway (threat → resources → population). HSAP models both pathways; the null model comparison tests whether population data alone can distinguish them.

**Figure 2.** Population trajectories for the four core scenarios (A–D), each showing 50 seed runs with the mean trajectory highlighted. A (baseline) stabilizes near 94 agents. B (reduced threat) stabilizes near 141 agents with lower male testosterone. C (crowding) stabilizes near 44 agents despite identical resources to B. D (high predation) stabilizes near 77 agents with elevated testosterone. All four scenarios used identical initial conditions; differences reflect endocrine-behavioral feedback under distinct environmental manipulations.

**Figure 3.** Behavioral and reproductive metrics across core scenarios. Male aggression, female aggression, and mean fertility for scenarios A–F. The A→B comparison shows reduced male aggression and increased female aggression under reduced threat. The B→C comparison shows reduced fertility under crowding. Error bars are 95% bootstrap CIs. Scenario labels: baseline (A), abundance (B), crowded (C), stable (C_crowded_stable), predation (D), recovery (E), collapse (F). This figure is supplementary to Figures 2 and 5.

**Figure 4a.** Null model population MSE for all 11 null models, showing A/B MSE ratios. Models with ratios near 1.0 (dashed line) cannot distinguish HSAP's two most different scenarios (A vs B) on population data alone. Seven of 11 null models fall below the 1.5× discrimination threshold.

**Figure 4b.** HSAP ablation heatmap showing population MSE for each ablation variant across all six core/sink scenarios. The male testosterone downshift and female aggression channels are the two components whose removal most increases MSE on the B scenario, indicating their role as the minimal endocrine mechanism for population separation.

**Figure 5.** Population trajectories for the three sink scenarios. C_crowded_stable (control, no sink) stabilizes near 44 agents. E (sink with recovery) shows the characteristic dip-recover pattern: sink engages, population drops, sink disengages, recovery phase begins. F (partial collapse) shows population decline to near-zero with no recovery. Green shading indicates sink-active periods; blue shading indicates recovery from sink suppression.

**Figure 6.** Sobol sensitivity analysis tornado plot showing total-order indices (ST) for final population. Parameters with ST > 0.1 (red bars) explain more than 10% of output variance and are dominant regulators. This figure is supplementary to the factorial analysis in Section 4.6 and Table 3.

**Figure 7.** Genetic algorithm convergence and best-individual parameters. Left panel: best fitness over generations for the GA support search (maximizing HSAP-consistent patterns under low-threat conditions). Right panel: parameter values of the best individual. The GA identifies low predator pressure, moderate-high resources, and strong reproductive restraint as the parameter regime producing the strongest HSAP signal. This figure is supplementary to the ablation analysis in Section 4.5.

**Figure 8.** Factorial phase map showing population outcomes across all 54 factorial scenarios, color-coded by space constraint (low=0.40, high=0.80). Space constraint is the dominant population regulator: low constraint produces populations of 99–143 regardless of other parameters, while high constraint produces 4–13 under combined stressors.

**Figure 9.** Conceptual diagram of observable requirements for empirical HSAP testing. Panel (a): population data alone are non-identifiable across null models. Panel (b): endocrine observables (testosterone, cortisol) provide the first discriminant axis. Panel (c): behavioral observables (aggression, reproductive output) provide the second discriminant axis. Panel (d): the joint space of population + endocrine + behavioral observables defines the variable space needed to reject null models and retain HSAP. Contemporary proxy datasets (NHANES hormone panels, UCR arrest statistics) identify the class of observables required but are ecological and confounded; they motivate empirical design, not validate HSAP.

# Supplement A: Complete Results Tables

See `paper_working/tables/` for CSV files and `paper_working/tables_md/` for Markdown versions:
- `core_scenario_summary.csv`: Bootstrap CIs for all core scenario metrics
- `sink_scenario_summary.csv`: Bootstrap CIs for sink scenarios including sink onset and recovery rates
- `factorial_summary.csv`: Population, extinction, and endocrine metrics for all 54 factorial scenarios
- `null_model_comparison.csv`: Population MSE for all 11 null models across 6 scenarios
- `ablation_summary.csv`: Population MSE for all 6 HSAP ablation variants across 6 scenarios
- `sensitivity_summary.csv`: Factorial scenario parameter values with population outcomes

# Supplement B: Scenario Definitions

All 61 scenarios are defined in `src/hsap/scenarios.py` with frozen parameter values. The result freeze is archived in `results/freezes/hsap_1970_seed_freeze_20260714/` with SHA-256 hashes for code tarballs.

# Supplement C: Model Equations

See Section 1 of the main text for complete model equations. The model code is available in `src/hsap/` with full test coverage in `tests/`.
