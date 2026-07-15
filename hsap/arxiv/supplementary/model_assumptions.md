# Model Assumptions — Internal Audit

Assumptions embedded in the HSAP implementation that are not explicitly documented in the manuscript. Identifying weak joints builds reviewer trust.

## Assumption Table

| Assumption | Current implementation | Impact on dynamics | Severity |
|---|---|---|---|
| Mating drive coupling | Set in simulation loop (`T*0.5+0.3` male, `E*0.4+0.2` female), not in endocrine module | Affects reproduction rate and sink recovery | Medium |
| Refugee injection | During post-sink recovery, up to 10 agents injected per step if pop < 30 | Prevents extinction in recovery scenarios; may mask true collapse dynamics | High |
| Offspring survival filtering | `random() < maternal.offspring_survival_probability` at birth | Pups filtered before entering population; survival probability is maternal, not environmental | Medium |
| Injury recovery | Fixed 30% probability per step (INJURY_RECOVERY_RATE = 0.3), independent of health or resources | Injuries resolve stochastically; no healing costs modeled | Low |
| Guarding blocks infanticide | 50% chance of blocking infanticide if agent is guarding | No resource cost for guarding beyond energy; single guard blocks all infanticide | Low |

## Detailed Descriptions

### 1. Mating Drive Coupling

**Implementation:** In `simulation.py`, mating drive is set after the endocrine update:

```python
if agent.sex == "male":
    agent.mating_drive = agent.testosterone * 0.5 + 0.3
else:
    agent.mating_drive = agent.estrogen * 0.4 + 0.2
```

**Issue:** This coupling is not part of the endocrine module (`endocrine.py`). It is an implicit assumption in the simulation loop that creates a direct testosterone-to-mating-drive link in males and estrogen-to-mating-drive link in females.

**Impact:** The male mating drive equation means testosterone downshift directly reduces mating effort, which is the mechanism through which low threat reduces reproduction. If this coupling were weaker (e.g., `T*0.3+0.5`), the HSAP mechanism would be less effective.

**Recommendation:** Document explicitly in methods. Consider sensitivity analysis on coupling strength.

### 2. Refugee Injection

**Implementation:** During post-sink recovery, if population drops below `behavioral_sink_recovery_min_population` (default 30), up to `behavioral_sink_recovery_refugee_count` (default 10) agents are injected per step.

**Issue:** Refugees are age-initialized uniformly from [10, 30] model-years and have default hormone values. They are not derived from the surviving population. This is a model convenience to prevent extinction during recovery, not a biological mechanism.

**Impact:** In scenario F (partial collapse), `behavioral_sink_recovery_min_population` is set to 0 and `behavioral_sink_recovery_refugee_count` is set to 0, so refugees are not injected. In scenario E (recovery), refugees supplement the recovering population, potentially inflating recovery speed.

**Recommendation:** Document explicitly. Note that refugee injection is disabled in collapse scenarios.

### 3. Offspring Survival Filtering

**Implementation:** In `reproduction.py`, each pup is filtered by:

```python
if self.rng.random() > female.offspring_survival_probability:
    continue
```

**Issue:** Survival probability is computed from maternal hormones and density, not from pup-specific conditions. Pups that survive the filter enter the population with fixed initial conditions (energy=0.5, health=uniform(0.7, 1.0)).

**Impact:** Litter sizes are variable but survival filtering is independent across pups. This creates stochastic variation in recruitment that is unrelated to environmental conditions at the time of birth.

**Recommendation:** Document as simplification. Pup survival is maternal-condition-dependent, not environmentally dependent.

### 4. Injury Recovery

**Implementation:** `INJURY_RECOVERY_RATE = 0.3` — each step, injured agents have a 30% chance of recovery, independent of health, resources, or treatment.

**Issue:** Injury recovery is a fixed rate. In reality, recovery would depend on health, nutrition, and social support. The fixed rate is a simplification.

**Impact:** Low. Injuries last an average of ~3 steps (geometric distribution with p=0.3). This is short enough that injuries primarily affect immediate behavior (dominance contests) rather than long-term survival.

**Recommendation:** Document as simplification. Injury duration is short relative to reproductive timescale.

### 5. Guarding Blocks Infanticide

**Implementation:** In `simulation.py`:

```python
if agent.guarding and infanticide_triggered:
    if self.rng.random() < 0.5:
        infanticide_triggered = False
```

**Issue:** A single guarding agent blocks infanticide with 50% probability for all offspring. There is no resource cost for guarding beyond the energy cost of the guard action (-0.1). No kin recognition is modeled.

**Impact:** Low. Guarding is only triggered when cortisol > 0.6 and the agent has offspring. The 50% block rate means infanticide still occurs in guarded litters.

**Recommendation:** Document as simplification. Guarding is a behavioral abstraction, not a detailed model of parental defense.
