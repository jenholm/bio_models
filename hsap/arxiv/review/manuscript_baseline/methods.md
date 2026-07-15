# 2. Methods

We follow the ODD (Overview, Design concepts, Details) protocol for describing individual-based models [@grimm2006].

## 2.1 Purpose

HSAP tests whether endocrine-linked behavioral feedbacks can generate population stabilization under reduced external threat. The model proposes that low predator pressure triggers a male testosterone downshift, reducing male aggression and reproductive effort, while female aggression increases under reduced male competition. These behavioral changes, combined with density-dependent reproductive restraint, can stabilize populations below carrying capacity through endocrine-mediated pathways rather than resource limitation alone.

## 2.2 Agent Architecture

Each agent is characterized by sex (assigned 50/50 at birth), age (in model time steps; 10 steps = 1 model-year), and a suite of physiological and behavioral state variables. Agents are initialized with age drawn uniformly from $[5, 40)$ and energy, health, and rank set to 1.0, 1.0, and 0.5 respectively.

**Hormonal state.** Each agent carries three hormonal axes: testosterone, estrogen, and cortisol. Male testosterone is initialized near 1.0 (`base_male_testosterone`) with Gaussian noise (SD=0.15); female testosterone near 0.3 (SD=0.05). Estrogen is initialized near 1.0 for females and 0.3 for males. Cortisol is initialized near 0.5 for both sexes (SD=0.1). All hormonal values are clamped to $[0, 1]$ at each time step.

**Behavioral state.** Derived from hormones and environment at each step: `aggression_tendency`, `maternal_defense_tendency` (females), `mating_drive`, `fertility`, and `offspring_survival_probability`. These are recomputed every time step; agents do not carry fixed behavioral types.

**Social state.** Each agent has a dominance rank (clamped $[0, 1]$), territory quality, `cooperation_bonus` (accumulated from cooperative actions, capped at 0.3), and a pregnancy flag with gestation countdown (`gestation_time` = 5 steps).

## 2.3 Environment

The environment provides five static parameters and several dynamic state variables.

**Static parameters** (set per scenario):
- `resource_abundance` (0 to 1): baseline resource availability
- `predator_pressure` (0 to 1): external threat level
- `disease_pressure` (0 to 1): disease prevalence
- `space_constraint` (0 to 1): controls how quickly territory availability declines with density
- `carrying_capacity` (integer): $K$ for density computation

**Dynamic state** (updated each step):
- `resource_abundance`: regenerates toward maximum, consumed by population; modulated by seasonality
- `territory_availability`: $\max(0, 1 - \rho \cdot S)$, where $\rho = N / K$
- `predation_risk`: $P \cdot (1 + 0.5 \cdot \rho)$
- `disease_risk`: $D \cdot (1 + 0.5 \cdot \rho)$

## 2.4 Endocrine Update

Hormones are recomputed for every agent at each time step, creating the causal feedback loop that defines HSAP.

**Male testosterone** is driven by five factors:

$$T_{m,t+1} = \min\left(T_{\max},\; T_{\text{base}} + 0.3 \cdot \text{rank} + 0.4 \cdot M_d - 0.3 \cdot \rho - 0.4 \cdot (1 - P) - 0.2 \cdot (1 - \text{health})\right)$$

The term $-0.4 \cdot (1 - P)$ is the critical endocrine feedback: when predator pressure is high, the term is near zero (testosterone is not reduced); when predator pressure is low, the term subtracts up to 0.4 (testosterone is downshifted). This is the mechanism through which threat reduction propagates to behavioral change.

**Female testosterone** responds to resource scarcity and density:

$$T_{f,t+1} = \min\left(T_{\max},\; 0.3 + 0.15 \cdot \text{rank} + 0.4 \cdot (1 - R) + 0.3 \cdot \rho\right)$$

**Cortisol** (both sexes) integrates density, rank, health, predation, and resource scarcity:

$$C = 0.5 + 0.1 \cdot \rho - 0.3 \cdot \text{rank} + 0.5 \cdot (1 - \text{health}) + 0.2 \cdot P + 0.3 \cdot (1 - R)$$

**Estrogen** (females) is suppressed by cortisol:

$$E = 1.0 - 0.3 \cdot C$$

## 2.5 Behavioral Output

From hormones, agents derive:

- **Aggression**: base $= T \cdot 0.5 + C \cdot 0.2$, with sex-specific additions (females: offspring defense + resource competition; males: dominance bonus)
- **Fertility**: base $= 0.5$, modified by hormones, age, density-dependent reproductive restraint (activates above density 0.7), and territory availability
- **Mating drive**: males $= T \cdot 0.5 + 0.3$; females $= E \cdot 0.4 + 0.2$
- **Offspring survival probability**: affected by testosterone, cortisol, density, and resource scarcity

Agents select actions stochastically from: forage, dominate, disperse, withdraw, cooperate, guard_offspring. Action probabilities depend on current behavioral state and environmental conditions.

<!-- TODO: Specify action selection probability formulas -->

## 2.6 Reproduction

Mating occurs when a randomly selected male (probability proportional to `mating_drive`) encounters a fertile female above a fertility gate (default 0.3). Both must have energy above a threshold (0.4) and be in reproductive age (10–60 model-years). On successful mating, the female becomes pregnant with gestation time of 5 steps.

At birth, litter size is drawn from a normal distribution (mean=4.0, SD=1.0, floored to 1). Each pup survives with probability determined by the mother's `offspring_survival_probability`. The mother pays an energy cost of 0.3. Newborns face an additional mortality check.

**Infanticide** triggers when density exceeds 0.8, with probability proportional to agent aggression and density above threshold. **Offspring neglect** triggers when density exceeds 0.7 or cortisol exceeds 0.7, removing one offspring.

## 2.7 Mortality

Death probability per time step is computed as:

$$P_{\text{death}} = \min\left(1,\; (P_{\text{base}} + P_{\text{pred}} + P_{\text{disease}} + P_{\text{starvation}} + P_{\text{injury}} + P_{\text{old}} + P_{\text{crowd}}) \times \tau \times M\right)$$

where $\tau = 0.1$ (age increment per step) and $M$ is the mortality multiplier (1.0 normally, 0.4 during post-sink recovery).

| Component | Formula |
|---|---|
| Base | 0.02 (constant) |
| Predation | $0.05 \cdot P_{\text{risk}} \cdot (1 - 0.02 \cdot (1-R)) \cdot \text{modifiers}$ |
| Disease | $0.03 \cdot D_{\text{risk}} \cdot (1 + 0.5 \cdot (1 - \text{health})) \cdot (1 + 0.5 \cdot \rho)$ |
| Starvation | If energy $< 0.2$: $0.3 \cdot (1-R) \cdot (1 - \text{energy}/0.2)$ |
| Injury | 0.1 if injured |
| Old age | $0.01 \cdot (\text{age} - 50)$ if age $> 50$ |
| Crowding | $0.05 \cdot \max(0, \rho - 0.8) + \eta \cdot M_{\text{sink}}$ |

Here $\eta$ is the behavioral sink factor (Section 2.8) and $M_{\text{sink}}$ is a binary mortality modifier active during sink engagement.

## 2.8 Behavioral Sink and Recovery

The behavioral sink is a density-driven phase transition that suppresses reproductive output even after density falls below carrying capacity.

**Activation.** When density exceeds `behavioral_sink_on_threshold` (default 0.75), the sink engages. A `sink_factor` is computed as a continuous measure of sink severity:

$$\eta = \min\left(1,\; \frac{\rho - 0.75}{1 - 0.75}\right)$$

**Effects while active.** Fertility is multiplicatively suppressed: $F \times (1 - \eta \cdot 0.85)$. Mating drive is suppressed: $M_d \times (1 - \eta \cdot 0.4)$. Withdrawal behavior and offspring neglect probabilities are increased.

**Deactivation (hysteresis).** The sink disengages only when density falls below `behavioral_sink_off_threshold` (default 0.50), creating a hysteresis band (on at 0.75, off at 0.50). A minimum duration of 30 steps must elapse before deactivation is permitted. An optional auto-recovery timer (`behavioral_sink_auto_recovery_duration`) forces disengagement after a fixed number of steps.

**Post-sink recovery.** After sink disengagement, a recovery phase lasting 100 steps begins. During recovery: fertility and mating drive are multiplicatively boosted by 1.3; mortality is reduced to 40% of normal. If population drops below 30 during recovery, refugees (up to 10 per step) are injected to supplement the depleted population.

**Sink Factor in the HSAP Index.** The HSAP index incorporates sink state: when the sink is active, the index is dampened, reflecting the disruption of normal social-endocrine regulation.

## 2.9 Metrics

Per time step, HSAP records: population size, density, sex ratio, resource abundance, predator pressure, disease pressure, territory availability, age structure (juvenile/adult/senior counts), mean hormones (testosterone, estrogen, cortisol, male_T, female_T), behavioral outputs (male/female aggression, female defense), reproductive metrics (fertility, births, deaths, matings, pregnancies, infanticide, neglect, refugees), sink state (active, post-recovery, sink_factor), external threat index, and the composite HSAP index.

The HSAP index is a weighted composite of five signals: low external threat (25%), low male aggression (20%), high female aggression (20%), low fertility (20%), and population stability (15%), with a viability dampener for populations below 50.

**Summary metrics** (computed over the full run): final population, peak population, minimum population, crash ratio (final/peak), time to stability, mean male/female testosterone, mean male/female aggression, mean fertility, mean cortisol, extinction status, and seed number.

## 2.10 Null Models

We compared HSAP against 11 null models that lack endocrine feedbacks or behavioral mechanisms. Each null model was fit to HSAP's population trajectory and evaluated by mean squared error (MSE). Full equations are provided in the supplementary materials.

| Model | Mechanism | Key equation |
|---|---|---|
| N0_logistic | Logistic growth | $dN/dt = rN(1-N/K)$ |
| N1_predator_prey | Lotka-Volterra | $dN/dt = \alpha N - \beta NP$; $dP/dt = \delta NP - \gamma P$ |
| N2_density_fertility | Density-dependent fertility | $F = F_0 \cdot (1 - N/K)$ |
| N3_disease_pressure | Disease mortality | $M_d = D \cdot (1 + 0.5 \cdot N/K)$ |
| N4_dominance_hierarchy | Rank-based allocation | Resources allocated by rank; no endocrine feedback |
| N5_random_hormone | Random hormones | Hormones drawn from $U(0,1)$; no environmental coupling |
| N6_resource_only | Resource-limited growth | Growth limited by $R$ only; no behavioral feedback |
| N7_density_with recovery | Density + recovery | Density dependence with Allee-effect recovery term |
| N8_random_behavior | Random actions | Action selection uniformly random; no state dependence |
| N9_social_behavior | Social only | Social interactions without endocrine coupling |
| N10_endocrine_no_behavior | Endocrine only | Hormones update but do not affect behavior |

We also tested six HSAP ablation variants, each removing one component: male testosterone downshift, female aggression channel, cortisol, endocrine responsiveness, reproductive restraint, and sink recovery.

## 2.11 Software and Reproducibility

The model is implemented in Python 3.10+ using NumPy, pandas, Matplotlib, and tqdm. Sensitivity analysis uses SALib. Genetic algorithm search uses DEAP. The model code is available in `src/hsap/` with full test coverage in `tests/`.

All scenario definitions are frozen in `src/hsap/scenarios.py`. Simulation outputs are frozen in `results/freezes/`. The pipeline is reproducible via:

```
python scripts/run_resumable_pipeline.py validate
python scripts/run_resumable_pipeline.py summarize
python scripts/make_paper_figures.py --dpi 300
```
