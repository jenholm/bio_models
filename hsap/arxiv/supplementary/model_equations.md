# Model Equations — Formal Definition

All equations extracted from source code (src/hsap/). This is the authoritative reference.

## 1. Population Dynamics

$$N_{t+1} = N_t + B_t - D_t + R_t$$

where:
- $N_t$ = population size at time $t$
- $B_t$ = births at time $t$
- $D_t$ = deaths at time $t$
- $R_t$ = refugees injected during post-sink recovery

## 2. Environmental State

$$\mathbf{E}_t = (R_t, P_t, D_t, S_t, \tau_t)$$

where:
- $R_t$ = resource abundance
- $P_t$ = predator pressure (static per scenario)
- $D_t$ = disease pressure (static per scenario)
- $S_t$ = space constraint (static per scenario)
- $\tau_t$ = territory availability

### 2.1 Resource dynamics

$$R_{t+1} = \min\left(R_{\max},\; \left[R_t + r \cdot (1 - \rho_t) - 0.01 \cdot \rho_t \cdot \mathbb{1}_{\text{regen}}\right] \cdot \sigma_t\right)$$

where:
- $r$ = resource regeneration rate
- $\rho_t = N_t / K$ = density
- $\mathbb{1}_{\text{regen}}$ = Bernoulli($r$) — stochastic regeneration flag
- $\sigma_t = 1 + s \cdot \sin(2\pi t / 365)$ = seasonal modulation ($s$ = seasonality, default 0)
- $R_{\max}$ = maximum resource abundance

### 2.2 Territory availability

$$\tau_t = \max(0,\; 1 - \rho_t \cdot S)$$

### 2.3 Effective risks

$$P_t^{\text{risk}} = P_t \cdot (1 + 0.5 \cdot \rho_t)$$
$$D_t^{\text{risk}} = D_t \cdot (1 + 0.5 \cdot \rho_t)$$

## 3. Agent State

Each agent $i$ carries:
$$\mathbf{x}_i = (\text{sex}_i, \text{age}_i, e_i, r_i, h_i, T_i, E_i, C_i, A_i, F_i, M_{d,i}, \ldots)$$

All scalar state variables clamped to $[0, 1]$ at each step.

## 4. Endocrine Update

### 4.1 Male testosterone

$$T_{m,i} = T_{\text{base}} + \beta_{\text{dom}} \cdot r_i + \beta_{\text{mating}} \cdot M_{d,i} - \beta_{\text{crowd}} \cdot \rho_t - \beta_{\text{threat}} \cdot (1 - P_t) - \beta_{\text{cond}} \cdot (1 - h_i)$$

The critical feedback term is $-\beta_{\text{threat}} \cdot (1 - P_t)$: when predator pressure is high, the term is near zero; when predator pressure is low, testosterone is downshifted by up to $\beta_{\text{threat}}$.

### 4.2 Female testosterone

$$T_{f,i} = T_{\text{base,f}} + 0.5 \cdot \beta_{\text{dom}} \cdot r_i + \beta_{\text{res}} \cdot (1 - R_t) + \beta_{\text{dens}} \cdot \rho_t$$

### 4.3 Female estrogen

$$E_i = E_{\text{base}} - \beta_{\text{fert,C}} \cdot C_i$$

### 4.4 Cortisol (both sexes)

$$C_i = C_{\text{base}} + 2\beta_{\text{stress}} \cdot \rho_t - \beta_{\text{rank}} \cdot r_i + \beta_{\text{health}} \cdot (1 - h_i) + 0.2 \cdot P_t + 0.3 \cdot (1 - R_t)$$

### 4.5 Aggression

**Male:**
$$A_{m,i} = 0.5 \cdot T_i + 0.2 \cdot C_i + \beta_{\text{dom}} \cdot r_i$$

**Female:**
$$A_{f,i} = 0.5 \cdot T_i + 0.2 \cdot C_i + \beta_{\text{off}} \cdot n_{\text{off}} \cdot 0.2 + \beta_{\text{res}} \cdot (1-R_t) + \beta_{\text{dens}} \cdot \rho_t + \beta_{\text{sens}} \cdot T_i$$

### 4.6 Fertility

$$F_i = 0.5 + \begin{cases} 0.3 \cdot T_i & \text{if male} \\ 0.3 \cdot E_i - 0.2 \cdot T_i & \text{if female} \end{cases} - 0.3 \cdot C_i - 0.02 \cdot \max(0, \text{age}_i - 40)$$

Reproductive restraint (if $\rho_t > 0.7$):

$$F_i \mathrel{-}= 0.5 \cdot \frac{\rho_t - 0.7}{0.3}$$

Territory modulation:

$$F_i \mathrel{\times}= \max(0.2, \tau_t)$$

### 4.7 Offspring survival probability

$$P_{\text{surv},i} = 0.5 + 0.1 \cdot T_i - 0.2 \cdot C_i - 0.3 \cdot \rho_t - 0.2 \cdot (1-R_t)$$

## 5. Behavioral Sink

### 5.1 Activation

When $\rho_t > \theta_{\text{on}}$ (default 0.75):

$$\eta_t = \min\left(1,\; \frac{\rho_t - \theta_{\text{on}}}{1 - \theta_{\text{on}}}\right)$$

### 5.2 Effects while active

- Fertility: $F_i \mathrel{\times}= (1 - \eta_t \cdot 0.85)$
- Mating drive: $M_{d,i} \mathrel{\times}= (1 - \eta_t \cdot 0.4)$
- Withdrawal probability increases by $\eta_t \cdot \beta_{\text{withdraw}}$
- Neglect probability increases by $\eta_t \cdot \beta_{\text{neglect}}$

### 5.3 Deactivation (hysteresis)

Sink disengages when:
- $\rho_t < \theta_{\text{off}}$ (default 0.50), AND
- $\text{sink\_active\_steps} \geq d_{\text{min}}$ (default 30), OR
- $\text{sink\_active\_steps} \geq d_{\text{auto}}$ (auto-recovery, optional)

### 5.4 Post-sink recovery

Duration: $d_{\text{rec}}$ steps (default 100)

During recovery:
- Fertility boost: $F_i \mathrel{\times}= 1.3$
- Mating drive boost: $M_{d,i} \mathrel{\times}= 1.3$
- Mortality multiplier: $\mu = 0.4$
- Refugee injection if $N_t < 30$: add up to 10 agents per step

## 6. Mating

Mate probability:

$$p_{\text{mate}} = F_{\text{male}} \cdot F_{\text{female}} \cdot 0.5 \cdot M_{d,\text{male}} \cdot (1 - 0.2 \cdot (1-R_t))$$

Conditions: both energy > 0.4, both age in [10, 60], female not pregnant.

## 7. Birth

Gestation: 5 steps.

Litter size:

$$L = \max(1,\; \text{round}(N(\mu_L \cdot F_{\text{female}}, \sigma_L)))$$

where $\mu_L = 4.0$, $\sigma_L = 1.0$.

Offspring survive with probability $P_{\text{surv},\text{mother}}$.

## 8. Mortality

$$P_{\text{death},i} = \min\left(1,\; \left[P_{\text{base}} + P_{\text{pred}} + P_{\text{dis}} + P_{\text{starv}} + P_{\text{inj}} + P_{\text{old}} + P_{\text{crowd}}\right] \cdot \tau_{\text{age}} \cdot \mu\right)$$

where $\tau_{\text{age}} = 0.1$ and $\mu = 1.0$ (normal) or $0.4$ (recovery).

| Component | Formula |
|---|---|
| $P_{\text{base}}$ | 0.02 |
| $P_{\text{pred}}$ | $0.05 \cdot P_t^{\text{risk}} \cdot (1 - 0.02(1-R_t)) \cdot \mathbb{1}_{\text{inj}}^{1.5} \cdot \mathbb{1}_{\text{juv}}^{2.0}$ |
| $P_{\text{dis}}$ | $0.03 \cdot D_t^{\text{risk}} \cdot (1 + 0.5(1-h_i)) \cdot (1 + 0.5\rho_t)$ |
| $P_{\text{starv}}$ | $0.3 \cdot (1-R_t) \cdot (1 - e_i/0.2)$ if $e_i < 0.2$ |
| $P_{\text{inj}}$ | 0.1 if injured |
| $P_{\text{old}}$ | $0.01 \cdot (\text{age}_i - 50)$ if age > 50 |
| $P_{\text{crowd}}$ | $0.05 \cdot \max(0, \rho_t - 0.8) + \eta_t \cdot \beta_{\text{sink,mort}}$ |

## 9. Composite Indices

### 9.1 External threat index

$$I_{\text{threat}} = \text{clamp}\left(0.4 \cdot P_t + 0.3 \cdot D_t + 0.3 \cdot \max(0, 1-R_t)\right)$$

### 9.2 HSAP index

$$I_{\text{HSAP}} = \text{clamp}\left(0.25 \cdot (1-I_{\text{threat}}) + 0.20 \cdot (1-A_m) + 0.20 \cdot A_f + 0.20 \cdot (1-F) + 0.15 \cdot S_{\text{pop}}\right)$$

where $S_{\text{pop}} = \text{clamp}(1 - 5|g_t|)$ is population stability ($g_t$ = growth rate).

Viability dampener: if $N_t < 50$, multiply $I_{\text{HSAP}}$ by $N_t / 50$.

### 9.3 Phase classification

| HSAP index | Phase |
|---|---|
| < 0.35 | external-control |
| 0.35–0.60 | transition |
| 0.60–0.80 | hsap-active |
| > 0.80 | strong-social-regulation |
