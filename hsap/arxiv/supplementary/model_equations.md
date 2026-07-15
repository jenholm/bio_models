# Model Equations — HSAP v0.1

## Variable Key

| Symbol | Meaning | Range | Code Variable |
|--------|---------|-------|---------------|
| $P$ | Predator pressure | [0, 1] | `env.predator_pressure` |
| $D$ | Disease pressure | [0, 1] | `env.disease_pressure` |
| $R$ | Resource abundance | [0, 2] | `env.resource_abundance` |
| $K$ | Carrying capacity | [100, 1000] | `env.carrying_capacity` |
| $S$ | Space constraint | [0, 1] | `env.space_constraint` |
| $N$ | Population size | $\mathbb{Z}^+$ | `len(alive_agents)` |
| $\rho$ | Density | [0, ~2] | `N / K` |
| $T_m$ | Male testosterone | [0, ~2] | `agent.testosterone` (male) |
| $T_f$ | Female testosterone | [0, ~1] | `agent.testosterone` (female) |
| $E$ | Estrogen | [0, ~2] | `agent.estrogen` |
| $C$ | Cortisol | [0, ~1.5] | `agent.cortisol` |
| $A$ | Aggression tendency | [0, 1] | `agent.aggression_tendency` |
| $F$ | Fertility | [0, 1] | `agent.fertility` |
| $M_d$ | Mating drive | [0, ~1] | `agent.mating_drive` |
| $\Phi$ | Territory availability | [0, 1] | `env.territory_availability` |
| $\theta$ | External threat index | [0, 1] | `compute_external_threat_index()` |
| $H$ | HSAP diagnostic index | [0, 1] | `compute_hsap_index()` |
| $\eta$ | Sink factor | [0, 1] | `env.sink_factor` |

---

## 1. External Threat Index

Combines predator pressure, disease pressure, and resource scarcity into a single threat metric:

$$\theta = 0.4 \cdot P + 0.3 \cdot D + 0.3 \cdot \max(0, 1 - R)$$

**Code**: `src/hsap/visual_trace.py:compute_external_threat_index()`

**Interpretation**: Weighted combination where predation is the strongest single contributor ($w = 0.4$), followed by disease and resource scarcity ($w = 0.3$ each).

---

## 2. Resource Dynamics

Resources regenerate toward a density-dependent maximum and are consumed by the population:

$$R_{t+1} = \max(0, R_t + r_R \cdot (1 - \rho) - 0.01 \cdot \rho \cdot \mathbf{1}_{\text{consuming}})$$

where $r_R$ is the regeneration rate (`env.resource_regeneration_rate`, default 0.05) and $\mathbf{1}_{\text{consuming}}$ is 1 when resources exceed the regeneration threshold.

Seasonal modulation:

$$R_{\text{final}} = R_{t+1} \cdot (1 + \sigma \cdot \sin(2\pi t / 365))$$

where $\sigma$ is seasonality (default 0.0).

**Code**: `src/hsap/environment.py:step()`

---

## 3. Density

$$\rho = \frac{N}{K}$$

**Code**: `env.density` (computed as `population_size / carrying_capacity`)

**Interpretation**: Dimensionless occupancy ratio. Values > 1 indicate overcrowding relative to carrying capacity.

---

## 4. Territory Availability

$$\Phi = \max(0, 1 - \rho \cdot S)$$

**Code**: `env.territory_availability`

**Interpretation**: Space constraint $S$ mediates how quickly territory becomes scarce as density increases.

---

## 5. Male Testosterone Update

$$T_{m,t+1} = \min(T_{\max}, T_{\text{base}} + \Delta T_{\text{dom}} + \Delta T_{\text{mating}} - \Delta T_{\text{crowding}} - \Delta T_{\text{threat}} - \Delta T_{\text{health}})$$

where:
- $T_{\text{base}}$: `base_male_testosterone` (default 1.0)
- $\Delta T_{\text{dom}} = 0.3 \cdot \text{rank}$: dominance bonus
- $\Delta T_{\text{mating}} = 0.4$ during mating: competition bonus
- $\Delta T_{\text{crowding}} = 0.3 \cdot \rho$: crowding penalty
- $\Delta T_{\text{threat}} = 0.4 \cdot (1 - \theta)$: low-threat downshift
- $\Delta T_{\text{health}} = 0.2 \cdot (1 - \text{health})$

**Code**: `src/hsap/endocrine.py:update()`

**Interpretation**: Male T rises with rank and mating competition, falls with crowding, low threat, and poor health.

---

## 6. Female Testosterone Update

$$T_{f,t+1} = \min(T_{\max}, T_{\text{base}} + \epsilon_f \cdot \Delta T_{\text{context}} - \Delta T_{\text{crowding}})$$

where:
- $T_{\text{base}}$: `base_female_testosterone` (default 0.3)
- $\epsilon_f = 0.5$: `endocrine_sensitivity_female`
- $\Delta T_{\text{context}}$: aggregated environmental/social cues
- $\Delta T_{\text{crowding}} = 0.3 \cdot \rho$

**Code**: `src/hsap/endocrine.py:update()`

**Interpretation**: Female T responds to environmental cues at reduced sensitivity ($\epsilon_f$) relative to male T.

---

## 7. Estrogen Update

$$E_{t+1} = \min(E_{\max}, E_{\text{base}} + \Delta E_{\text{context}} - \Delta E_{\text{stress}})$$

where:
- $E_{\text{base}}$: `base_estrogen` (default 1.0)
- $\Delta E_{\text{stress}} \propto C$: cortisol suppression

**Code**: `src/hsap/endocrine.py:update()`

---

## 8. Cortisol Update

$$C_{t+1} = C_{\text{base}} + \gamma_{\text{stress}} \cdot (1 - \text{rank\_buffer}) \cdot (1 - \text{health\_amp})$$

where:
- $C_{\text{base}}$: `base_cortisol` (default 0.5)
- $\gamma_{\text{stress}}$: `stress_cortisol_rise` (0.05 per stressor)
- $\text{rank\_buffer} = 0.3$: high rank reduces stress accumulation
- $\text{health\_amp} = 0.5$: poor health amplifies stress

**Code**: `src/hsap/endocrine.py:update()`

**Interpretation**: Cortisol reflects cumulative stress, buffered by rank and amplified by poor health.

---

## 9. Male Aggression

$$A_m = \min(1, \alpha_{\text{base}} \cdot T_m + \beta_{\text{offspring}} + \beta_{\text{resource}} \cdot (1 - R) + \beta_{\text{density}} \cdot \rho)$$

where:
- $\alpha_{\text{base}}$: scaling from T to aggression
- $\beta_{\text{offspring}} = 0.5$: offspring-defense bonus
- $\beta_{\text{resource}} = 0.4$: resource competition
- $\beta_{\text{density}} = 0.3$: crowding effect

**Code**: `src/hsap/behavior.py:compute_aggression()` and `agent.aggression_tendency`

---

## 10. Female Aggression

$$A_f = \min(1, \epsilon_f \cdot T_f + \beta_{\text{offspring}} \cdot \mathbf{1}_{\text{offspring}} + \beta_{\text{resource}} \cdot (1 - R) + \beta_{\text{density}} \cdot \rho)$$

Same structure as male aggression but with endocrine sensitivity scaling factor $\epsilon_f = 0.5$.

**Code**: `src/hsap/behavior.py:compute_aggression()`

---

## 11. Fertility

$$F = \max(0, F_{\text{base}} - \lambda_T \cdot T - \lambda_C \cdot C - \lambda_{\text{age}} \cdot \text{age})$$

where:
- $F_{\text{base}}$: baseline fertility
- $\lambda_T = 0.2$: testosterone penalty
- $\lambda_C = 0.3$: cortisol penalty
- $\lambda_{\text{age}} = 0.02$: age-related decline

Density-dependent reproductive restraint:

$$F_{\text{restrained}} = F \cdot (1 - \kappa \cdot \max(0, \rho - \rho_{\text{threshold}}))$$

where $\kappa = 0.5$ (`reproductive_restraint_max`) and $\rho_{\text{threshold}} = 0.7$.

**Code**: `src/hsap/endocrine.py:update_fertility()` and `agent.fertility`

---

## 12. Mortality

Per-step mortality probability:

$$P(\text{death}) = \min(1, M_{\text{base}} + M_{\text{pred}} + M_{\text{disease}} + M_{\text{starv}} + M_{\text{injury}} + M_{\text{age}} + M_{\text{crowding}})$$

where:
- $M_{\text{base}} = 0.02$: baseline
- $M_{\text{pred}} = 0.05 \cdot P$: predation
- $M_{\text{disease}} = 0.03 \cdot D \cdot (1 + \rho)$: disease
- $M_{\text{starv}} = 0.3 \cdot \max(0, 1 - R/0.2)$: starvation
- $M_{\text{injury}} = 0.1$ if injured
- $M_{\text{age}}$: age-dependent (rises after 50)
- $M_{\text{crowding}} = 0.05 \cdot \rho + \eta \cdot M_{\text{sink}}$: crowding + sink bonus

All probabilities multiplied by `age_increment` (0.1) per step.

**Code**: `src/hsap/mortality.py:check_death()`

---

## 13. Mating Probability

$$P(\text{mate}) = M_d \cdot 0.8$$

where $M_d = 0.5 \cdot T + 0.3$ for males and $M_d = 0.4 \cdot E + 0.2$ for females.

Fertility gate: females must have $F > 0.3$ (or $0.15$ during post-sink recovery).

**Code**: `src/hsap/simulation.py:step()`

---

## 14. Sink Factor

$$\eta = \begin{cases}
\min(1, (\rho - \theta_{\text{on}}) / (\theta_{\text{on}} - \theta_{\text{off}})) & \text{if } \rho > \theta_{\text{on}} \\
0 & \text{otherwise}
\end{cases}$$

where $\theta_{\text{on}} = 0.75$ (`behavioral_sink_on_threshold`) and $\theta_{\text{off}} = 0.50$.

The sink remains active for at least `behavioral_sink_min_duration` (default 30) steps before deactivation is possible. Recovery activates after sink duration exceeds recovery threshold.

**Code**: `src/hsap/environment.py:_update_sink_state()`

---

## 15. Post-Sink Recovery

When the sink exits after minimum duration:

1. Recovery lasts `recovery_duration` (default 100) steps
2. Fertility boost: $F' = F \cdot (1 + 0.3)$
3. Mating boost: $M_d' = M_d \cdot (1 + 0.3)$
4. Mortality relief: mortality multiplier reduced by 0.4
5. Refugee injection: 10 agents injected if population < 30

**Code**: `src/hsap/environment.py:_update_sink_state()` and `src/hsap/simulation.py:step()`

---

## 16. HSAP Diagnostic Index

$$H = 0.25 \cdot (1 - \theta) + 0.20 \cdot (1 - A_m) + 0.20 \cdot A_f + 0.20 \cdot (1 - F) + 0.15 \cdot S$$

where $S = N_{\text{final}} / \max(N)$ is population stability (crash ratio).

**Classification**:
- $H < 0.35$: External-control
- $0.35 \le H < 0.60$: Transition
- $0.60 \le H < 0.80$: HSAP-active
- $H \ge 0.80$: Strong social-regulation

**Code**: `src/hsap/visual_trace.py:compute_hsap_index()`

**Interpretation**: Weighted composite that increases when external threat is low, male aggression is low, female aggression is high, fertility is restrained, and the population is stable. Not a biological claim — a diagnostic index for model state classification.

---

## Parameter Tables

### Endocrine Parameters (default values)

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

### Environment Parameters (default values)

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `predator_pressure` | 0.5 | [0.0, 1.0] | Predation intensity |
| `disease_pressure` | 0.3 | [0.0, 1.0] | Disease intensity |
| `resource_abundance` | 1.0 | [0.3, 2.0] | Baseline resource level |
| `carrying_capacity` | 500 | [100, 1000] | Population carrying capacity |
| `space_constraint` | 0.5 | [0.0, 1.0] | Territorial compression |
| `behavioral_sink_on_threshold` | 0.75 | [0.0, 1.0] | Density to trigger sink |
| `behavioral_sink_recovery_duration` | 100 | [0, 500] | Steps in recovery phase |
