# ODD Compliance Audit

Audit of HSAP against the ODD (Overview, Design concepts, Details) protocol for individual-based models [@grimm2006].

## Overview

### Purpose

HSAP tests whether endocrine-linked behavioral feedbacks can generate population stabilization under reduced external threat. The model proposes that low predator pressure triggers a male testosterone downshift, reducing male aggression and reproductive effort, while female aggression increases under reduced male competition.

**Status:** Clearly stated. Falsifiable.

### Entities

**One entity type:** Agent (individual mammal).

**State variables:** 26 per agent (see METHODS_AUDIT.md).

**No group-level entities.** Population is an emergent property of agent interactions.

**Status:** Complete. Single entity type is appropriate for the question.

### Scales

- **Spatial:** None (well-mixed; no spatial explicit grid)
- **Temporal:** 1 step = 0.1 model-years; 10 steps = 1 model-year; max 500 steps = 50 model-years
- **Population:** Initial 50; no hard cap; carrying capacity K set per scenario

**Status:** Spatial abstraction is explicit. Temporal scale is documented.

## Design Concepts

### Adaptation

Agents do not learn or adapt behavior rules. Hormonal state is updated each step based on environmental conditions, creating plasticity without learning. This is a design choice: HSAP tests endocrine-mediated plasticity, not cognitive adaptation.

**Status:** Appropriate for the question. Not a limitation.

### Objectives

Agents do not have explicit fitness objectives. Behavior is stochastic, driven by hormonal state and environmental conditions. Mating is probabilistic, not strategic.

**Status:** Appropriate. No fitness optimization assumed.

### Learning

None. Hormonal state is reactive, not predictive. This is a simplification but appropriate for the model's scope.

**Status:** Explicitly absent. Documented.

### Prediction

None. Agents do not predict future states. All decisions are based on current state only.

**Status:** Explicitly absent. Documented.

### Emergence

Population-level patterns emerge from individual-level rules:
- Population stabilization emerges from endocrine-behavioral feedback
- Crowding pathology emerges from density-dependent reproductive restraint
- Behavioral sink dynamics emerge from hysteresis threshold mechanism
- Extinction risk emerges from sustained reproductive suppression

**Status:** Core claim. Results demonstrate emergent properties.

### Interaction

- Agent-agent: through dominance contests (fight outcomes depend on rank and testosterone)
- Agent-environment: through resource consumption, predation risk, disease risk
- No direct agent-agent communication or social network

**Status:** Interactions are documented in the methods.

### Stochasticity

- Initialization: random age, sex, hormone values (Gaussian noise)
- Action selection: probabilistic
- Mating: probabilistic
- Mortality: probabilistic
- Resource regeneration: stochastic flag
- Injury recovery: probabilistic

**Status:** Stochasticity is appropriate and documented.

## Details

### Initialization

- Population: 50 agents
- Sex: 50/50 male/female
- Age: uniform(5, 40)
- Energy: 1.0
- Health: 1.0
- Rank: 0.5
- Hormones: reset_dynamics() — sex-dependent Gaussian initialization
- All state variables clamped to [0, 1]

**Status:** Complete. Initialization is documented.

### Input Data

No external input data. All parameters are set in config.py and scenarios.py.

**Status:** Complete. No data dependencies.

### Submodels

12 submodels identified:

| Submodel | Module | Function |
|---|---|---|
| Endocrine update | endocrine.py | Hormone state update |
| Behavior selection | behavior.py | Action choice + execution |
| Reproduction | reproduction.py | Mating, pregnancy, birth |
| Mortality | mortality.py | Death probability computation |
| Population dynamics | population.py | Age structure, hormone means |
| Environment | environment.py | Resource, territory, sink state |
| Metrics | metrics.py | Per-step recording |
| Visual trace | visual_trace.py | Visualization data |
| HSAP index | visual_trace.py | Composite index computation |
| External threat index | visual_trace.py | Threat index computation |
| Sink state machine | environment.py | Sink activation/deactivation |
| Refugee injection | simulation.py | Recovery population supplement |

**Status:** Complete. All submodels are documented.

## Missing ODD Elements

1. **Spatial structure:** Not modeled. Agents are well-mixed. This is appropriate for the question but should be explicitly stated as a limitation.
2. **Social network:** No explicit social network. Rank is the only social variable. Interactions are pairwise and anonymous.
3. **Movement:** No spatial movement. Territory quality is assigned but not spatially explicit.
4. **Age-dependent behavior:** Age affects reproductive status (10-60) and mortality (old age > 50), but not behavioral rules directly (except dispersal threshold at age > 15).

## ODD Compliance Score

| Element | Status |
|---|---|
| Purpose | ✓ Complete |
| Entities | ✓ Complete |
| State variables | ✓ Complete |
| Scales | ✓ Complete |
| Process overview | ✓ Complete (simulation.py step function) |
| Design concepts | ✓ Appropriate |
| Initialization | ✓ Complete |
| Input data | ✓ Complete (no external data) |
| Submodels | ✓ Complete (12 submodels) |
| **Overall** | **Compliant** |

## Recommendations

1. Add explicit statement that spatial structure is absent (well-mixed assumption)
2. Document that social interactions are pairwise and anonymous (no network)
3. Consider adding a supplementary figure showing the simulation loop step order
4. The ODD protocol should be referenced in the methods section with a pointer to this document
