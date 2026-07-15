# Model Limitations

Explicit statement of HSAP's limitations. This document prevents reviewers from discovering limitations the authors have not acknowledged.

## Structural Limitations

### No empirical calibration

HSAP parameters were not estimated against empirical population data. All parameter values are model assumptions. The model is a computational exploration, not a predictive statistical model. Results demonstrate qualitative system behavior under defined assumptions, not quantitative fit to observed populations.

### No spatial geography

The model uses a well-mixed population approximation. Agents are not assigned spatial coordinates. Territory availability is a scalar function of density, not a spatially explicit landscape. This abstraction excludes spatial processes such as habitat fragmentation, metapopulation dynamics, and localized resource depletion.

### Anonymous social interactions

Social interactions are pairwise and anonymous. There is no kin recognition, no persistent social network, no reciprocal altruism, and no reputation system. Cooperation accumulates a bounded bonus but does not create social bonds. This abstraction excludes network-mediated effects such as kin selection, social learning, and coalition formation.

### No seasonality

Seasonal variation was not modeled in the default parameterization. Simulations represent normalized ecological conditions. Seasonal resource fluctuations, breeding seasons, and seasonal hormone cycles are not included. The environment module supports seasonality (sinusoidal resource modulation), but it is set to zero in all reported scenarios.

### No learning or adaptation

Agents do not learn. Hormonal state is reactive, not predictive. Behavioral rules are fixed; agents do not modify their decision rules based on experience. This excludes cultural transmission, behavioral innovation, and adaptive management.

### No genetic variation

All agents share identical parameter values. There is no genetic variation in hormone sensitivity, behavioral thresholds, or life history traits. Evolutionary dynamics are not modeled (the GA module explores parameter space, not agent evolution).

## Parameter Limitations

### 71 free parameters

The model contains 71 free parameters across six parameter classes. None are fit to data. The large parameter space raises concerns about overfitting to qualitative behavior, but since no empirical data is used for fitting, this concern is mitigated. The model explores a class of feedback structures, not a specific parameterization.

### Parameter sensitivity unknown for most parameters

Sensitivity analysis was performed on the core scenario parameters (predator pressure, disease pressure, resource abundance, space constraint, carrying capacity). Sensitivity of endocrine and behavioral parameters to population outcomes has not been systematically explored.

### B_hsap_abundance fertility limitation

In scenario B (abundance), mean fertility (0.568) is only marginally higher than in scenario A (baseline, 0.560). The HSAP mechanism reduces male testosterone and aggression but does not substantially reduce female fertility. This is a limitation of the model's parameterization, not a feature of the mechanism.

## Methodological Limitations

### Cohen d inflation

The reported Cohen d = 3.29 for male testosterone between scenarios A and B is inflated by the low variance across simulation seeds. Simulation precision is not biological variance. Effect sizes should be interpreted with caution.

### Null model threshold

The 1.5x MSE threshold used to classify null model non-identifiability is a practical boundary, not a statistical significance criterion. Different thresholds would produce different classifications.

### HSAP composite indicator weights

The composite indicator weights (0.25, 0.20, 0.20, 0.20, 0.15) are not fit to data and not empirically justified. They reflect the model's hypothesized causal chain. Different weights would produce different phase classifications.

### Recovery refugees

During post-sink recovery, refugee injection supplements depleted populations. This prevents extinction in recovery scenarios but may mask true collapse dynamics. Refugee injection is disabled in collapse scenarios (F).

## Scope Limitations

### Mammalian model only

HSAP is a mammalian population model. It does not model insects, plants, or non-mammalian vertebrates. Endocrine mechanisms are mammalian-specific.

### No human applications

HSAP does not model human sexual orientation, human social dynamics, or human population regulation. Non-reproductive sexual or social behavior is treated only as species-specific ethological behavior requiring explicit supporting data.

### No empirical validation

The model has not been validated against any empirical dataset. Empirical validation requires paired endocrine and behavioral field measurements across population conditions. This validation is left to future work.
