# Parameter Provenance Table

All parameters extracted from src/hsap/config.py. All values are model tuning constants; none are fit to empirical data.

## Endocrine Parameters

| Parameter | Symbol | Default | Meaning | Source |
|---|---|---|---|---|
| base_male_testosterone | $T_{\text{base}}$ | 1.0 | Male testosterone baseline | Model assumption |
| base_female_testosterone | $T_{\text{base,f}}$ | 0.3 | Female testosterone baseline | Model assumption |
| base_estrogen | $E_{\text{base}}$ | 1.0 | Estrogen baseline (females) | Model assumption |
| base_cortisol | $C_{\text{base}}$ | 0.5 | Cortisol baseline (both sexes) | Model assumption |
| dominance_T_bonus | $\beta_{\text{dom}}$ | 0.3 | Testosterone increase per rank unit | Model assumption |
| mating_competition_T_bonus | $\beta_{\text{mating}}$ | 0.4 | Testosterone increase per mating drive unit | Model assumption |
| crowding_T_penalty | $\beta_{\text{crowd}}$ | 0.3 | Testosterone decrease per density unit | Model assumption |
| low_threat_T_downshift | $\beta_{\text{threat}}$ | 0.4 | Testosterone decrease when predator pressure low | **Core mechanism** |
| poor_condition_T_penalty | $\beta_{\text{cond}}$ | 0.2 | Testosterone decrease per health deficit | Model assumption |
| offspring_aggression_bonus | $\beta_{\text{off}}$ | 0.5 | Female aggression per offspring | Model assumption |
| resource_competition_aggression_bonus | $\beta_{\text{res}}$ | 0.4 | Aggression per resource scarcity unit | Model assumption |
| density_aggression_bonus | $\beta_{\text{dens}}$ | 0.3 | Aggression per density unit | Model assumption |
| endocrine_sensitivity_female | $\beta_{\text{sens}}$ | 0.5 | Female aggression sensitivity to testosterone | Model assumption |
| stress_cortisol_rise | $\beta_{\text{stress}}$ | 0.05 | Cortisol increase per density unit | Model assumption |
| rank_stress_buffer | $\beta_{\text{rank}}$ | 0.3 | Cortisol decrease per rank unit | Model assumption |
| health_stress_amplifier | $\beta_{\text{health}}$ | 0.5 | Cortisol increase per health deficit | Model assumption |
| fertility_T_penalty | — | 0.2 | Female fertility decrease per testosterone | Model assumption |
| fertility_cortisol_penalty | — | 0.3 | Fertility decrease per cortisol | Model assumption |
| fertility_age_decline | — | 0.02 | Fertility decrease per year above 40 | Model assumption |
| reproductive_restraint_density_threshold | $\theta_{\text{rr}}$ | 0.7 | Density above which reproductive restraint activates | Model assumption |
| reproductive_restraint_max | — | 0.5 | Maximum fertility reduction from restraint | Model assumption |
| offspring_survival_T_effect | — | 0.1 | Offspring survival increase per testosterone | Model assumption |
| offspring_survival_cortisol_penalty | — | 0.2 | Offspring survival decrease per cortisol | Model assumption |

## Behavior Parameters

| Parameter | Symbol | Default | Meaning | Source |
|---|---|---|---|---|
| base_forage_success | — | 0.7 | Base probability of successful foraging | Model assumption |
| rank_forage_bonus | — | 0.15 | Foraging success increase per rank unit | Model assumption |
| energy_forage_threshold | — | 0.3 | Energy below which agent must forage | Model assumption |
| fight_win_rank_bonus | — | 0.2 | Fight win probability per rank unit | Model assumption |
| fight_win_T_bonus | — | 0.15 | Fight win probability per testosterone | Model assumption |
| fight_energy_cost | — | 0.15 | Energy cost of fighting | Model assumption |
| fight_injury_prob | — | 0.1 | Probability of injury on fight loss | Model assumption |
| dispersal_energy_cost | — | 0.3 | Energy cost of dispersal | Model assumption |
| dispersal_density_threshold | — | 0.6 | Density above which dispersal is possible | Model assumption |
| cooperation_energy_bonus | — | 0.05 | Energy gain from cooperation | Model assumption |
| withdrawal_energy_save | — | 0.05 | Energy saved by withdrawing | Model assumption |

## Reproduction Parameters

| Parameter | Symbol | Default | Meaning | Source |
|---|---|---|---|---|
| gestation_time | — | 5 | Steps from mating to birth | Model assumption |
| litter_size_mean | $\mu_L$ | 4.0 | Mean litter size | Model assumption |
| litter_size_std | $\sigma_L$ | 1.0 | Litter size standard deviation | Model assumption |
| mating_energy_threshold | — | 0.4 | Minimum energy for mating | Model assumption |
| post_partum_energy_cost | — | 0.3 | Energy cost of giving birth | Model assumption |
| weaning_age | — | 10 | Steps before offspring are weaned | Model assumption |
| infanticide_density_threshold | — | 0.8 | Density above which infanticide can occur | Model assumption |
| infanticide_rate | — | 0.05 | Base infanticide probability | Model assumption |
| offspring_neglect_density_threshold | — | 0.7 | Density above which neglect can occur | Model assumption |
| offspring_neglect_cortisol_threshold | — | 0.7 | Cortisol above which neglect can occur | Model assumption |

## Mortality Parameters

| Parameter | Symbol | Default | Meaning | Source |
|---|---|---|---|---|
| base_mortality | $P_{\text{base}}$ | 0.02 | Constant death probability per step | Model assumption |
| predation_mortality_base | — | 0.05 | Base predation death rate | Model assumption |
| disease_mortality_base | — | 0.03 | Base disease death rate | Model assumption |
| starvation_mortality_threshold | — | 0.2 | Energy below which starvation risk begins | Model assumption |
| starvation_mortality_max | — | 0.3 | Maximum starvation death rate | Model assumption |
| injury_mortality_bonus | — | 0.1 | Additional death probability if injured | Model assumption |
| old_age_mortality_start | — | 50 | Age above which senescence mortality begins | Model assumption |
| old_age_mortality_rise | — | 0.01 | Mortality increase per year above 50 | Model assumption |
| infanticide_mortality | — | 0.1 | Death probability from infanticide | Model assumption |
| crowding_mortality_bonus | — | 0.05 | Mortality increase per density above 0.8 | Model assumption |

## Environment Parameters

| Parameter | Symbol | Default | Meaning | Source |
|---|---|---|---|---|
| resource_abundance | $R_0$ | varies | Initial resource level | Scenario-dependent |
| resource_abundance_max | $R_{\max}$ | 2.0 | Maximum resource capacity | Scenario-dependent |
| resource_regeneration_rate | $r$ | 0.05 | Resource recovery rate | Scenario-dependent |
| predator_pressure | $P$ | varies | Static predation level | **Scenario driver** |
| disease_pressure | $D$ | varies | Static disease level | **Scenario driver** |
| carrying_capacity | $K$ | varies | Population carrying capacity | **Scenario driver** |
| space_constraint | $S$ | varies | Territory decline rate | **Scenario driver** |
| seasonality | $s$ | 0.0 | Amplitude of seasonal modulation | Model assumption |
| territory_availability | $\tau_0$ | 1.0 | Initial territory availability | Model assumption |
| behavioral_sink_on_threshold | $\theta_{\text{on}}$ | 0.75 | Density to activate sink | Model assumption |
| behavioral_sink_off_threshold | $\theta_{\text{off}}$ | 0.50 | Density to deactivate sink | Model assumption |
| behavioral_sink_min_duration | $d_{\text{min}}$ | 30 | Minimum steps in sink before exit | Model assumption |
| behavioral_sink_auto_recovery_duration | $d_{\text{auto}}$ | None | Auto-exit after N steps | Model assumption |
| behavioral_sink_fertility_penalty | — | 0.85 | Fertility multiplier in sink | Model assumption |
| behavioral_sink_neglect_bonus | — | 0.25 | Neglect probability increase in sink | Model assumption |
| behavioral_sink_withdrawal_bonus | — | 0.25 | Withdrawal probability increase in sink | Model assumption |
| behavioral_sink_mating_penalty | — | 0.4 | Mating drive multiplier in sink | Model assumption |
| behavioral_sink_mortality_bonus | — | 0.0 | Additional mortality in sink | Model assumption |
| behavioral_sink_recovery_duration | $d_{\text{rec}}$ | 100 | Recovery phase duration | Model assumption |
| behavioral_sink_recovery_fertility_boost | — | 0.3 | Fertility multiplier during recovery | Model assumption |
| behavioral_sink_recovery_mating_boost | — | 0.3 | Mating drive multiplier during recovery | Model assumption |
| behavioral_sink_recovery_female_fertility_gate | — | 0.15 | Lower fertility gate during recovery | Model assumption |
| behavioral_sink_recovery_mortality_relief | — | 0.4 | Mortality multiplier during recovery | Model assumption |
| behavioral_sink_recovery_min_population | — | 30 | Population below which refugees injected | Model assumption |
| behavioral_sink_recovery_refugee_count | — | 10 | Max refugees per step during recovery | Model assumption |

## Scenario Parameters

| Scenario | $P$ | $D$ | $R_0$ | $r$ | $K$ | $S$ | $\theta_{\text{on}}$ |
|---|---|---|---|---|---|---|---|
| A_normal_baseline | 0.25 | 0.20 | 0.60 | 0.03 | 500 | 0.40 | 0.75 |
| B_hsap_abundance | 0.10 | 0.05 | 1.50 | 0.08 | 500 | 0.20 | 0.75 |
| C_crowded_abundance | 0.10 | 0.05 | 1.50 | 0.08 | 200 | 0.90 | 0.75 |
| D_high_predation_survival | 0.45 | 0.15 | 0.75 | 0.05 | 500 | 0.40 | 0.75 |
| C_crowded_stable | 0.10 | 0.05 | 1.50 | 0.08 | 200 | 0.90 | 0.92 |
| E_behavioral_sink_recovery | 0.20 | 0.10 | 1.00 | 0.06 | 200 | 0.80 | 0.25 |
| F_behavioral_sink_partial_collapse | 0.10 | 0.05 | 0.40 | 0.03 | 200 | 0.80 | 0.15 |

## Parameter Classification

### Biological parameters (potentially measurable)

- $T_{\text{base}}$, $T_{\text{base,f}}$, $E_{\text{base}}$, $C_{\text{base}}$: Hormone baselines
- $\beta_{\text{threat}}$: Testosterone sensitivity to predation pressure
- $\beta_{\text{crowd}}$: Testosterone sensitivity to density
- Litter size parameters: reproductive output
- Age thresholds: reproductive maturity, senescence

### Model tuning parameters (not biologically measurable)

- $\beta_{\text{dom}}$, $\beta_{\text{mating}}$, $\beta_{\text{cond}}$: Testosterone coupling strengths
- $\beta_{\text{off}}$, $\beta_{\text{res}}$, $\beta_{\text{dens}}$, $\beta_{\text{sens}}$: Aggression coupling strengths
- $\beta_{\text{stress}}$, $\beta_{\text{rank}}$, $\beta_{\text{health}}$: Cortisol coupling strengths
- Behavioral thresholds and probabilities
- Mortality coefficients
- Sink thresholds and penalties

### Scenario drivers (varied across experiments)

- $P$: predator_pressure
- $D$: disease_pressure
- $R_0$: resource_abundance
- $r$: resource_regeneration_rate
- $K$: carrying_capacity
- $S$: space_constraint
- $\theta_{\text{on}}$: behavioral_sink_on_threshold
