# CLAIM_MATRIX.md

Internal audit of scientific claims made by HSAP. Every claim in the manuscript must trace to a row in this table.

## Core Claims

| Claim | Evidence Type | Confidence | Reviewer Attack | Status | Manuscript location |
|---|---|---|---|---|---|
| Model produces population stabilization under reduced threat | Simulation (1,970 seeds) | High | Parameter dependence | Supported | Results 4.1 |
| Model produces crowding pathology despite resource abundance | Simulation (B vs C) | High | Parameter dependence | Supported | Results 4.2 |
| Behavioral sink produces recovery or partial collapse | Simulation (E, F) | High | Threshold sensitivity | Supported | Results 4.3 |
| Null models cannot distinguish HSAP on population data alone | Null comparison (11 models) | High | Threshold choice (1.5x) | Supported | Results 4.4 |
| Male T downshift and female aggression are minimal mechanisms | Ablation analysis | High | Ablation completeness | Supported | Results 4.5 |
| Space constraint is dominant population regulator | 54-factorial sweep | High | Parameter range selection | Supported | Results 4.6 |

## Biological Claims

| Claim | Evidence Type | Confidence | Reviewer Attack | Status | Manuscript location |
|---|---|---|---|---|---|
| Hormonal pathway exists biologically | Literature (testosterone-aggression link) | Medium | Species generalization | Supported by literature | Introduction 1.2 |
| Endocrine-mediated behavioral sinks occur in nature | Literature (Calhoun, Christian) | Medium | Laboratory vs field | Supported by literature | Introduction 1.3 |
| HSAP mechanism operates in real populations | None | None | **Not claimed** | Excluded | Limitations |
| Human populations follow this pathway | None | None | **Excluded** | Excluded | Scope and boundaries |
| Null model identifiability is meaningful | Statistical comparison | High | Threshold justification | Supported | Results 4.4 |

## Model-Specific Claims

| Claim | Evidence Type | Confidence | Reviewer Attack | Status | Manuscript location |
|---|---|---|---|---|---|
| HSAP is falsifiable | Model design + null comparison | High | Falsification criteria | Supported | Introduction 1.5 |
| Population data alone are insufficient for mechanism ID | Null model non-identifiability | High | Null model selection | Supported | Results 4.4 |
| Behavioral/endocrine observables are required for testing | Ablation + null comparison | High | Observable specificity | Supported | Results 4.4–4.5 |
| B_hsap_abundance does not substantially reduce fertility | Comparison with A: 0.568 vs 0.560 | Low | Effect size interpretation | **Limitation** | Results 4.1 |
| Cohen d=3.29 is inflated by simulation precision | Low variance across seeds | Low | Biological relevance | **Caveat needed** | Results 4.1 |
| Parameters are model assumptions, not empirical estimates | None (by design) | N/A | "Where is training data?" | **Explicitly stated** | Methods 2.12 |
| HSAP composite indicator is an analytical summary | Weighted composite | N/A | "What do weights mean?" | **Explicitly stated** | Methods 2.9 |
| No spatial geography (well-mixed) | Design choice | N/A | "Where is spatial structure?" | **Explicitly stated** | Methods 2.13 |
| Anonymous pairwise interactions | Design choice | N/A | "Where is social network?" | **Explicitly stated** | Methods 2.14 |

## Excluded Claims

| Claim | Why excluded | Reviewer Attack if claimed |
|---|---|---|
| HSAP proves endocrine regulation drives real populations | Simulation only; no empirical validation | Overclaim |
| This model explains modern human behavior | Out of scope; mammalian model only | Scope creep |
| Endocrine feedbacks are the primary population regulator | Not claimed; candidate mechanism only | Exclusivity |
| The behavioral sink mechanism is universal | Not claimed; tested under specific assumptions | Generalization |

## Key Guardrails

- Use "simulation-consistent" not "proves/validates/confirms"
- Use "under model assumptions" not "biological law"
- Use "candidate mechanism" not "the mechanism"
- Use "consistent with" not "demonstrates that"
- Use "suggests / raises the possibility" not "shows / establishes"
- B_hsap_abundance: explicitly note fertility limitation
- Cohen d: explicitly note simulation precision caveat
- Parameters: explicitly state "model assumptions, not empirical estimates"
- HSAP composite indicator: explicitly state "analytical summary metric, not directly measurable"
- Spatial representation: explicitly state "well-mixed, no spatial coordinates"
- Interactions: explicitly state "pairwise anonymous, no persistent network"

## Reviewer Attack Patterns

| Pattern | Description | Defense |
|---|---|---|
| Parameter dependence | Results change under different parameters | Report sensitivity analysis; acknowledge parameter range |
| Threshold choice | Classification thresholds are arbitrary | Justify thresholds in methods; report sensitivity |
| Species generalization | Model applies to one species, not general | Explicit scope limitations |
| Overclaim | Model behavior claimed as biological mechanism | Claim discipline; "simulation-consistent" |
| Scope creep | Model extended beyond original domain | Scope and boundaries paragraph |
| Laboratory vs field | Calhoun-style sinks don't occur in nature | Acknowledge; cite field evidence where available |
| Ablation completeness | Other components might also be minimal | Report full ablation suite |
| Observable specificity | Which observables are sufficient? | Acknowledge; report null model non-identifiability |
| Training data | "Where is your empirical calibration?" | Parameters are assumptions, not estimates; Methods 2.12 |
| Spatial abstraction | "Where is spatial structure?" | Well-mixed by design; Methods 2.13 |
| Social network | "Where is the network?" | Anonymous pairwise; Methods 2.14 |
| Composite indicator | "What do the weights mean?" | Not fit to data; chosen to reflect hypothesized causal chain |
| Refugee injection | "Are you artificially preventing extinction?" | Disabled in collapse scenarios; documented in assumptions |
| Seasonality | "Why no seasonal variation?" | Explicitly stated as absent; normalized conditions |
