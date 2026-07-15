# Genetic Algorithm Methods

## Overview

The genetic algorithm (GA) search is used as a falsification tool: it explores whether alternative parameter combinations within the HSAP framework produce equally strong or stronger HSAP-consistent patterns under low-threat conditions.

## Implementation

- **Tool**: DEAP (Distributed Evolutionary Algorithms in Python)
- **Algorithm**: NSGA-II (Non-dominated Sorting Genetic Algorithm II)
- **Population size**: 100
- **Generations**: 50
- **Crossover probability**: 0.7
- **Mutation probability**: 0.2
- **Selection**: Tournament selection (size 3)

## Objective Function

The GA maximizes the HSAP diagnostic index under B_hsap_abundance conditions (low predator pressure, low disease, high resources). The fitness function combines:

1. Population stability (crash ratio > 0.8)
2. Low male aggression (< 0.85)
3. High female aggression (> 0.6)
4. Population size > 100
5. Low fertility (< 0.55)

## Parameters Evolved

| Parameter | Range | Description |
|---|---|---|
| predator_pressure | [0.0, 0.5] | Predation intensity |
| disease_pressure | [0.0, 0.3] | Disease intensity |
| resource_abundance | [0.5, 1.5] | Resource level |
| space_constraint | [0.0, 0.6] | Territorial compression |
| base_male_testosterone | [0.5, 1.5] | Male T baseline |
| low_threat_T_downshift | [0.1, 0.8] | T downshift magnitude |
| reproductive_restraint_max | [0.1, 0.8] | Fertility suppression |
| endocrine_sensitivity_female | [0.2, 1.0] | Female sensitivity |

## Interpretation

The GA identifies the parameter regime producing the strongest HSAP signal. Failure to find alternative attractors suggests HSAP is a robust attractor within the hypothesized parameter space. This is a falsification search, not an optimization — the goal is to test whether HSAP is the only viable mechanism in its proposed regime.
