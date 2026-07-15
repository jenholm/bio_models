# CLAIM_MATRIX.md

Internal audit of scientific claims made by HSAP. Every claim in the manuscript must trace to a row in this table.

## Core Claims

| Claim | Evidence | Status | Manuscript location |
|---|---|---|---|
| Model produces population stabilization under reduced threat | Simulation (3,050 seeds) | Supported | Results 4.1 |
| Model produces crowding pathology despite resource abundance | Simulation (B vs C comparison) | Supported | Results 4.2 |
| Behavioral sink produces recovery or partial collapse | Simulation (E, F scenarios) | Supported | Results 4.3 |
| Null models cannot distinguish HSAP on population data alone | Null comparison (11 models) | Supported | Results 4.4 |
| Male T downshift and female aggression are minimal mechanisms | Ablation analysis | Supported | Results 4.5 |
| Space constraint is dominant population regulator | 54-factorial sweep | Supported | Results 4.6 |

## Biological Claims

| Claim | Evidence | Status | Manuscript location |
|---|---|---|---|
| Hormonal pathway exists biologically | Literature (testosterone-aggression link) | Supported by literature | Introduction 1.2 |
| Endocrine-mediated behavioral sinks occur in nature | Literature (Calhoun, Christian) | Supported by literature | Introduction 1.3 |
| HSAP mechanism operates in real populations | None | **Not claimed** | Limitations |
| Human populations follow this pathway | None | **Excluded** | Scope and boundaries |
| Null model identifiability is meaningful | Statistical comparison | Supported | Results 4.4 |

## Model-Specific Claims

| Claim | Evidence | Status | Manuscript location |
|---|---|---|---|
| HSAP is falsifiable | Model design + null comparison | Supported | Introduction 1.5 |
| Population data alone are insufficient for mechanism ID | Null model non-identifiability | Supported | Results 4.4 |
| Behavioral/endocrine observables are required for testing | Ablation + null comparison | Supported | Results 4.4–4.5 |
| B_hsap_abundance does not substantially reduce fertility | Comparison with A: 0.568 vs 0.560 | **Limitation** | Results 4.1 |
| Cohen d=3.29 is inflated by simulation precision | Low variance across seeds | **Caveat needed** | Results 4.1 |

## Excluded Claims

| Claim | Why excluded |
|---|---|
| HSAP proves endocrine regulation drives real populations | Simulation only; no empirical validation |
| This model explains modern human behavior | Out of scope; mammalian model only |
| Endocrine feedbacks are the primary population regulator | Not claimed; claimed as candidate mechanism |
| The behavioral sink mechanism is universal | Not claimed; tested under specific assumptions |

## Key Guardrails

- Use "simulation-consistent" not "proves/validates/confirms"
- Use "under model assumptions" not "biological law"
- Use "candidate mechanism" not "the mechanism"
- Use "consistent with" not "demonstrates that"
- Use "suggests / raises the possibility" not "shows / establishes"
- B_hsap_abundance: explicitly note fertility limitation
- Cohen d: explicitly note simulation precision caveat
