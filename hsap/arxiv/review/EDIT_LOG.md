# HSAP Manuscript Edit Log

## Baseline

**Date:** 2026-07-15  
**Git commit:** no commits yet (pre-initial)

Starting manuscript:
- abstract.md
- introduction.md
- methods.md
- results.md
- discussion.md

Editing policy:
- Preserve scientific claims
- Do not increase certainty
- Maintain falsification framing
- All numerical results must trace to simulation outputs

## Editing Order

1. Abstract
2. Introduction
3. Methods
4. Results
5. Discussion
6. References
7. Figures
8. LaTeX packaging

## Edits

| Date | File | Change | Rationale |
|---|---|---|---|
| 2026-07-15 | — | Baseline snapshot created | Pre-edit reference point |
| 2026-07-15 | abstract.md | Full rewrite (257 words) | Five-question structure: problem → hypothesis → model → methods → results → limitations |
| 2026-07-15 | introduction.md | Full rewrite | Stronger scientific spine: ecological pathways → behavioral regulation → sink theory → integration gap → HSAP contribution. Removed Wrangham/Boehm (human-focused). Added Christian, Marine & Schneider. |
| 2026-07-15 | CLAIM_MATRIX.md | Created | Internal claim audit with evidence status and guardrails |
| 2026-07-15 | CLAIM_MATRIX.md | Expanded | Added Confidence, Reviewer Attack columns; added Reviewer Attack Patterns table |
| 2026-07-15 | METHODS_AUDIT.md | Created | Full audit of model implementation from source code |
| 2026-07-15 | model_equations.md | Created | Formal model definition extracted from code |
| 2026-07-15 | ODD_AUDIT.md | Created | ODD compliance review (100% compliant) |
| 2026-07-15 | parameter_table.md | Created | Parameter provenance with biological vs tuning classification |
| 2026-07-15 | methods.md | Methods hardening | Added: behavioral decision process (2.5), parameterization (2.12), spatial representation (2.13), interaction model (2.14), resource scarcity definition (2.15). Renamed HSAP index → composite indicator. |
| 2026-07-15 | MASTER_DRAFT.md | HSAP index rename | Updated to match methods.md |
| 2026-07-15 | main.md | HSAP index rename | Updated to match methods.md |
| 2026-07-15 | model_assumptions.md | Created | 5 unknown assumptions documented with severity and impact |
| 2026-07-15 | model_limitations.md | Created | Structural, parameter, methodological, and scope limitations |
| 2026-07-15 | CLAIM_MATRIX.md | Updated | Added 4 new model-specific claims, 6 new reviewer attack patterns, 5 new guardrails |
| 2026-07-15 | RESULTS_TRACEABILITY.md | Created | Every numerical claim traced to source CSV files |
| 2026-07-15 | results.md | Full rewrite | 9-section disciplined structure with negative results section (4.10) |
| 2026-07-15 | FIGURE_AUDIT.md | Created | 10 figures audited, 8 promoted, 2 relegated |
| 2026-07-15 | figures/final/ | 8 figures promoted | PDF format, stable names |
| 2026-07-15 | discussion.md | Full rewrite | 7-section disciplined structure: summary, what-this-is-not, non-identifiability, predictions, limitations, implications, future work. Removed external proxy section (5.6). |
