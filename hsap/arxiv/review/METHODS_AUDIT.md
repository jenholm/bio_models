# Methods Audit

Audit of HSAP model implementation extracted from source code. All equations are actual implementations, not manuscript approximations.

## Model Entities

**Single entity type:** `Agent` (src/hsap/entities.py)

- Sex: binary (male/female), assigned 50/50 at birth
- Age: continuous (model time steps; 10 steps = 1 model-year)
- All state variables clamped to [0, 1] at each step

## State Variables

### Agent State (26 variables)

| Variable | Type | Initial value | Range |
|---|---|---|---|
| agent_id | int | sequential | — |
| sex | str | "male"/"female" | — |
| age | float | uniform(5, 40) | [0, ∞) |
| energy | float | 1.0 | [0, 1] |
| rank | float | 0.5 | [0, 1] |
| territory_quality | float | 0.5 | [0, 1] |
| health | float | 1.0 | [0, 1] |
| stress | float | 0.0 | [0, 1] |
| testosterone | float | sex-dependent | [0, 1] |
| estrogen | float | sex-dependent | [0, 1] |
| cortisol | float | ~N(0.5, 0.1) | [0, 1] |
| aggression_tendency | float | computed | [0, 1] |
| maternal_defense_tendency | float | computed | [0, 1] |
| mating_drive | float | computed | [0, 1] |
| fertility | float | computed | [0, 1] |
| offspring_survival_probability | float | computed | [0, 1] |
| pregnant | bool | False | — |
| gestation_remaining | int | 0 | [0, 5] |
| offspring_ids | list[int] | [] | — |
| alive | bool | True | — |
| injury | bool | False | — |
| injury_timer | int | 0 | [0, 3] |
| dispersal_cooldown | int | 0 | — |
| cooperation_bonus | float | 0.0 | [0, 0.3] |
| guarding | bool | False | — |

### Environmental State (12 variables)

| Variable | Type | Initial | Updated |
|---|---|---|---|
| resource_abundance | float | scenario-dependent | each step |
| resource_abundance_max | float | 2.0 (default) | static |
| resource_regeneration_rate | float | 0.05 | static |
| predator_pressure | float | scenario-dependent | static |
| disease_pressure | float | scenario-dependent | static |
| carrying_capacity | int | scenario-dependent | static |
| space_constraint | float | scenario-dependent | static |
| seasonality | float | 0.0 | static |
| territory_availability | float | 1.0 | each step |
| sink_active | bool | False | each step |
| sink_factor | float | 0.0 | each step |
| post_sink_recovery | bool | False | each step |

## Equations

### Endocrine Update (src/hsap/endocrine.py)

**Male testosterone:**

```
T_m = base_male_testosterone
    + dominance_T_bonus * rank
    + mating_competition_T_bonus * mating_drive
    - crowding_T_penalty * density
    - low_threat_T_downshift * (1 - predator_pressure)
    - poor_condition_T_penalty * (1 - health)
```

**Female testosterone:**

```
T_f = base_female_testosterone
    + dominance_T_bonus * rank * 0.5
    + resource_competition_aggression_bonus * resource_scarcity
    + density_aggression_bonus * density
```

**Female estrogen:**

```
E = base_estrogen - fertility_cortisol_penalty * cortisol
```

**Cortisol (both sexes):**

```
C = base_cortisol
  + stress_cortisol_rise * density * 2.0
  - rank_stress_buffer * rank
  + health_stress_amplifier * (1 - health)
  + predator_pressure * 0.2
  + resource_scarcity * 0.3
```

**Aggression (male):**

```
A_m = testosterone * 0.5 + cortisol * 0.2 + dominance_T_bonus * rank
```

**Aggression (female):**

```
A_f = testosterone * 0.5 + cortisol * 0.2
    + offspring_aggression_bonus * n_offspring * 0.2
    + resource_competition_aggression_bonus * resource_scarcity
    + density_aggression_bonus * density
    + endocrine_sensitivity_female * testosterone
```

**Fertility:**

```
F = 0.5
  + (testosterone * 0.3) if male
  + (estrogen * 0.3 - fertility_T_penalty * testosterone) if female
  - fertility_cortisol_penalty * cortisol
  - fertility_age_decline * max(0, age - 40)
  - reproductive_restraint_max * (density - 0.7) / 0.3  [if density > 0.7]
  * max(0.2, territory_availability)
```

**Offspring survival probability:**

```
P_surv = 0.5
        + offspring_survival_T_effect * testosterone
        - offspring_survival_cortisol_penalty * cortisol
        - density * 0.3
        - resource_scarcity * 0.2
```

### Behavioral Decision Rules (src/hsap/behavior.py)

Action selection priority:

1. If energy < 0.3: **forage** (deterministic)
2. If female with offspring and cortisol > 0.6: **guard_offspring** (deterministic)
3. If random() < aggression_tendency * 0.3: **dominance_event**
4. If density > 0.6 and age > 15 and random() < 0.1: **disperse**
5. If cortisol > 0.7 and random() < withdraw_prob (0.3 + sink_factor * withdrawal_bonus): **withdraw**
6. If energy > 0.7 and random() < 0.1: **cooperate**
7. Default: **forage**

**Action effects:**

| Action | Energy | Rank | Other |
|---|---|---|---|
| forage (success) | +0.2 to +0.4 | — | success = 0.7 + 0.15*rank - 0.3*scarcity |
| forage (fail) | -0.05*(1+density) | — | — |
| dominance (win) | -0.15 | +0.05 | win_prob = 0.5 + 0.2*(rank-0.5) + 0.15*T |
| dominance (lose) | -0.225 | -0.05 | 10% injury chance |
| disperse | -0.3 | -0.1 | cooldown=10 |
| withdraw | +0.05 | -0.02 | — |
| cooperate | +0.05 | — | cooperation_bonus += 0.02 (cap 0.3) |
| guard_offspring | -0.1 | — | guarding=True |

### Reproduction (src/hsap/reproduction.py)

**Mating conditions:**
- Both not pregnant (female)
- Both energy > 0.4
- Both age in [10, 60]
- Mate probability: male.fertility * female.fertility * 0.5 * male.mating_drive * (1 - 0.2*resource_scarcity)

**Birth:**
- Gestation: 5 steps
- Litter size: round(N(litter_size_mean * female.fertility, litter_size_std)), min 1
- Post-partum energy cost: 0.3
- Offspring survival: random() < female.offspring_survival_probability
- Offspring initial: energy=0.5, health=uniform(0.7, 1.0)

**Infanticide:**
- Triggered if density > 0.8
- Probability: infanticide_rate * (density - 0.8) / 0.2 * aggression_tendency
- Guarding can block with 50% probability

**Offspring neglect:**
- Triggered if density > 0.7 or cortisol > 0.7
- Probability: 0.05 + 0.1*density + 0.1*(cortisol > 0.7)
- Removes one offspring

### Mortality (src/hsap/mortality.py)

**Death probability:**

```
P_death = (base + predation + disease + starvation + injury + old_age + crowding) * time_scale * mortality_multiplier
```

| Component | Formula |
|---|---|
| base | 0.02 |
| predation | 0.05 * predator_pressure * (1 - 0.02*(1-resource_scarcity)) * [1.5 if injured] * [2.0 if age<5] |
| disease | 0.03 * disease_pressure * (1 + 0.5*(1-health)) * (1 + 0.5*density) |
| starvation | if energy < 0.2: 0.3 * resource_scarcity * (1 - energy/0.2) |
| injury | 0.1 if injured |
| old_age | 0.01 * (age - 50) if age > 50 |
| crowding | 0.05 * max(0, density - 0.8) + sink_factor * behavioral_sink_mortality_bonus |

**time_scale** = 0.1 (age_increment per step)

**mortality_multiplier** = 0.4 during post-sink recovery, 1.0 otherwise

### Environment Dynamics (src/hsap/environment.py)

**Resource update:**

```
R_t+1 = R_t + regeneration_rate * (1 - density) - 0.01 * density * (not regenerating)
R_t+1 *= seasonal_factor
R_t+1 = min(R_max, R_t+1)
```

**Territory:**

```
territory = max(0, 1 - density * space_constraint)
```

**Predation risk:**

```
P_risk = predator_pressure * (1 + 0.5 * density)
```

**Disease risk:**

```
D_risk = disease_pressure * (1 + 0.5 * density)
```

**Sink state machine:**

```
if post_sink_recovery:
    sink_factor = 0
    recovery_steps -= 1
    if recovery_steps <= 0: post_sink_recovery = False
elif sink_active:
    sink_active_steps += 1
    if (sink_active_steps >= min_duration and density < off_threshold) or auto_recovery:
        sink_active = False
        if recovery_duration > 0: post_sink_recovery = True
    else:
        sink_factor = min(1, (density - on_threshold) / (1 - on_threshold))
else:
    if density > on_threshold:
        sink_active = True
        sink_factor = min(1, (density - on_threshold) / (1 - on_threshold))
    else:
        sink_factor = 0
```

### Simulation Loop (src/hsap/simulation.py)

Each step:

1. Increment age (0.1 per step)
2. Set stress = cortisol
3. Update endocrine state
4. Apply sink fertility penalty: `F *= (1 - sink_factor * 0.85)`
5. Apply recovery fertility boost: `F *= (1 + 0.3)`
6. Execute behavior (choose + apply action)
7. Update mating drive: male `T*0.5+0.3`, female `E*0.4+0.2`
8. Apply sink mating penalty: `M_d *= (1 - sink_factor * 0.4)`
9. Apply recovery mating boost: `M_d *= (1 + 0.3)`
10. Process pregnancies (birth if gestation complete)
11. Mate: males attempt with probability proportional to mating_drive
12. Check infanticide and neglect
13. Apply mortality
14. Add offspring to population
15. Inject refugees during recovery if population < 30
16. Sync environment (density, territory)
17. Update all agents' endocrine state
18. Record metrics

## Parameter Sources

All parameters are model tuning constants. No parameters are fit to empirical data.

| Parameter class | Count | Source |
|---|---|---|
| EndocrineParams | 15 | Model assumption |
| BehaviorParams | 10 | Model assumption |
| ReproductionParams | 10 | Model assumption |
| MortalityParams | 10 | Model assumption |
| EnvironmentParams | 20 | Model assumption (varied per scenario) |
| GAParams | 6 | Algorithm tuning |
| **Total** | **71** | |

## Unknown Assumptions

1. **Mating drive coupling**: Male mating drive is set to `T*0.5+0.3` in the simulation loop, not in the endocrine module. This is an implicit assumption not documented in the methods.
2. **Refugee injection**: During post-sink recovery, refugees are injected if population < 30. This is a model convenience, not a biological mechanism.
3. **Offspring survival filtering**: Offspring are filtered by `random() < maternal.offspring_survival_probability` at birth, not by environmental conditions.
4. **Injury recovery**: 30% chance per step of injury recovery (INJURY_RECOVERY_RATE = 0.3), independent of health or resources.
5. **Guarding blocking infanticide**: 50% chance of blocking infanticide if agent is guarding. No resource cost for guarding beyond energy.

## Missing Documentation

1. Action selection probabilities are not explicitly parameterized — they are hardcoded thresholds in `behavior.py`
2. The HSAP index weights (0.25, 0.20, 0.20, 0.20, 0.15) are not justified in the manuscript
3. The viability dampener (pop < 50) threshold is not justified
4. Seasonality implementation (sin wave with period 365) is not described in the manuscript
5. The `resource_scarcity` = `max(0, 1 - R)` definition is not explicit in the manuscript
