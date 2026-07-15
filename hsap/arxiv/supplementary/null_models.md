# Null Model Definitions

## Overview

HSAP is compared against 11 null models that lack endocrine feedbacks or behavioral mechanisms. Each null model is fit to HSAP's population trajectory and evaluated by mean squared error (MSE).

## Null Models

### N0: Logistic Growth
Standard logistic growth with density-dependent regulation:
$$dN/dt = rN(1 - N/K)$$
- Parameters: growth rate r, carrying capacity K
- Mechanism: Pure density-dependent regulation

### N1: Predator-Prey (Lotka-Volterra)
Classic predator-prey dynamics:
$$dN/dt = rN - aNP$$
$$dP/dt = baNP - mP$$
- Parameters: prey growth rate r, predation rate a, conversion efficiency b, predator mortality m
- Mechanism: External predator regulation

### N2: Density-Fertility
Density-dependent fertility only:
$$F = F_0(1 - N/K)$$
- Parameters: baseline fertility F0, carrying capacity K
- Mechanism: Reproductive suppression without endocrine coupling

### N3: Disease Pressure
Disease-mediated mortality:
$$M_{disease} = d \cdot (1 + N/K)$$
- Parameters: disease mortality d
- Mechanism: Density-dependent disease regulation

### N4: Dominance Hierarchy
Social rank-based resource allocation without endocrine coupling:
- Resources allocated proportionally to rank
- Rank assigned randomly at initialization
- Mechanism: Social hierarchy without hormonal mediation

### N5: Random Hormone
Random hormone levels with no environmental coupling:
- Hormones drawn from uniform [0, 1] each step
- No feedback from environment to endocrine state
- Mechanism: Stochastic endocrine noise

### N6: Resource-Limited Growth
Growth limited by resource availability only:
$$dN/dt = rN(R/R_{max}) - mN$$
- Parameters: growth rate r, resource scaling R/R_max, mortality m
- Mechanism: Pure resource limitation

### N7: Density with Recovery
Density dependence with post-disturbance recovery:
- Standard density regulation plus recovery dynamics after population drops below threshold
- Mechanism: Density regulation + resilience

### N8: Random Behavior
Random behavioral decisions without endocrine coupling:
- Action probabilities uniform across all options
- No influence of hormones on behavior
- Mechanism: Behavioral stochasticity

### N9: Social Behavior
Social interactions without endocrine coupling:
- Aggression, cooperation, dominance based on random initial conditions
- No hormonal feedback loop
- Mechanism: Social dynamics without endocrine mediation

### N10: Endocrine-No-Behavior
Endocrine changes without behavioral consequences:
- Hormones update based on environment
- But hormones do not influence behavior, fertility, or mortality
- Mechanism: Endocrine signaling without behavioral output

## Comparison Method

Each null model is simulated under the same environmental conditions as HSAP (scenarios A-F). The MSE between the null model's population trajectory and HSAP's trajectory is computed. Models with A/B MSE ratio < 1.5 cannot distinguish HSAP's two most different scenarios on population data alone.
