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
