# Sensitivity Analysis Methods

## Morris Screening

The Morris one-at-a-time (OAT) screening method identifies which parameters have negligible effects, linear additive effects, or nonlinear/interactive effects on model outputs.

### Implementation

- **Tool**: SALib (`saltelli` sample, `morris` analyze)
- **Parameters sampled**: 10 parameters across endocrine, environmental, and behavioral spaces
- **Number of trajectories**: 100
- **Number of grid levels**: 4
- **Output metric**: Final population size

### Parameters Screened

| Parameter | Range | Distribution |
|---|---|---|
| predator_pressure | [0.0, 1.0] | Uniform |
| disease_pressure | [0.0, 1.0] | Uniform |
| resource_abundance | [0.3, 2.0] | Uniform |
| space_constraint | [0.0, 1.0] | Uniform |
| carrying_capacity | [100, 1000] | Uniform |
| base_male_testosterone | [0.2, 2.0] | Uniform |
| low_threat_T_downshift | [0.0, 0.8] | Uniform |
| reproductive_restraint_max | [0.0, 0.8] | Uniform |
| fertility_cortisol_penalty | [0.0, 0.6] | Uniform |
| endocrine_sensitivity_female | [0.0, 1.0] | Uniform |

### Morris Indices

- **μ***: Modified mean of absolute elementary effects (overall importance)
- **σ**: Standard deviation of elementary effects (nonlinearity/interaction)
- **μ**: Raw mean (direction of effect)

## Sobol Global Sensitivity

The Sobol variance-based method decomposes output variance into contributions from individual parameters and their interactions.

### Implementation

- **Tool**: SALib (`saltelli` sample, `sobol` analyze)
- **Parameters**: Same 10 parameters as Morris
- **Number of samples**: 1024 (N × (2D + 2) = 1024 × 22 = 22,528 model evaluations)
- **Output metric**: Final population size

### Sobol Indices

- **S1**: First-order sensitivity index (individual contribution)
- **ST**: Total-order sensitivity index (individual + all interactions)
- **S2**: Second-order sensitivity index (pairwise interactions)

### Interpretation

Parameters with ST > 0.1 are considered dominant regulators of population output. The tornado plot (Figure 6) displays ST values for all parameters.
