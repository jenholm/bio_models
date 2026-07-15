# Parameter Tables — HSAP v0.1

## Endocrine Parameters (default values)

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `base_male_testosterone` | 1.0 | [0.2, 2.0] | Baseline male T |
| `base_female_testosterone` | 0.3 | [0.05, 1.0] | Baseline female T |
| `base_estrogen` | 1.0 | [0.2, 2.0] | Baseline estrogen |
| `base_cortisol` | 0.5 | [0.0, 1.0] | Baseline cortisol |
| `low_threat_T_downshift` | 0.4 | [0.0, 0.8] | T reduction under low threat |
| `reproductive_restraint_max` | 0.5 | [0.0, 0.8] | Maximum fertility suppression |
| `fertility_cortisol_penalty` | 0.3 | [0.0, 0.6] | Cortisol effect on fertility |
| `endocrine_sensitivity_female` | 0.5 | [0.0, 1.0] | Female endocrine responsiveness |

## Environment Parameters (default values)

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `predator_pressure` | 0.5 | [0.0, 1.0] | Predation intensity |
| `disease_pressure` | 0.3 | [0.0, 1.0] | Disease intensity |
| `resource_abundance` | 1.0 | [0.3, 2.0] | Baseline resource level |
| `carrying_capacity` | 500 | [100, 1000] | Population carrying capacity |
| `space_constraint` | 0.5 | [0.0, 1.0] | Territorial compression |
| `behavioral_sink_on_threshold` | 0.75 | [0.0, 1.0] | Density to trigger sink |
| `behavioral_sink_off_threshold` | 0.50 | [0.0, 1.0] | Density to disengage sink |
| `behavioral_sink_recovery_duration` | 100 | [0, 500] | Steps in recovery phase |
| `behavioral_sink_min_duration` | 30 | [0, 100] | Minimum sink active steps |

## Behavioral Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `aggression_base_scaling` | 0.5 | [0.0, 1.0] | T-to-aggression scaling |
| `fertility_base` | 0.5 | [0.0, 1.0] | Baseline fertility |
| `fertility_gate` | 0.3 | [0.0, 0.5] | Minimum fertility for mating |
| `mating_drive_male` | 0.5 | [0.0, 1.0] | Male mating drive T-scaling |
| `mating_drive_female` | 0.4 | [0.0, 1.0] | Female mating drive E-scaling |
| `litter_mean` | 4.0 | [1.0, 8.0] | Mean litter size |
| `litter_sd` | 1.0 | [0.0, 2.0] | Litter size SD |

## Mortality Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `base_mortality` | 0.02 | [0.0, 0.1] | Baseline death probability |
| `predation_mortality` | 0.05 | [0.0, 0.2] | Predation death scaling |
| `disease_mortality` | 0.03 | [0.0, 0.1] | Disease death scaling |
| `starvation_threshold` | 0.2 | [0.0, 0.5] | Energy below which starvation |
| `starvation_mortality` | 0.3 | [0.0, 1.0] | Starvation death scaling |
| `injury_mortality` | 0.1 | [0.0, 0.5] | Injury death probability |
| `old_age_threshold` | 50 | [30, 80] | Age above which mortality rises |
| `crowding_mortality` | 0.05 | [0.0, 0.2] | Crowding death scaling |
| `age_increment` | 0.1 | [0.01, 0.2] | Time step age increment |

## Scenario Parameters (Set 1 — Core)

| Scenario | predator_pressure | disease_pressure | resource_abundance | space_constraint | carrying_capacity |
|---|---|---|---|---|---|
| A_normal_baseline | 0.25 | 0.20 | 0.60 | 0.40 | 500 |
| B_hsap_abundance | 0.10 | 0.20 | 0.60 | 0.40 | 500 |
| C_crowded_abundance | 0.10 | 0.20 | 0.60 | 0.80 | 200 |
| D_high_predation_survival | 0.40 | 0.20 | 0.60 | 0.40 | 500 |
