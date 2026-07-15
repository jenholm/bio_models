# HSAP File Manifest

**Source**: `/home/jenholm/workspace/hsap` (neighbor project)
**Destination**: `/home/jenholm/workspace/bio_models/hsap`

## Source Code

| Path | Description |
|---|---|
| `src/hsap/__init__.py` | Package init |
| `src/hsap/entities.py` | Agent and entity definitions |
| `src/hsap/endocrine.py` | Hormone update logic |
| `src/hsap/behavior.py` | Behavioral output computation |
| `src/hsap/environment.py` | Environment state and dynamics |
| `src/hsap/simulation.py` | Main simulation loop |
| `src/hsap/population.py` | Population management |
| `src/hsap/mortality.py` | Death probability computation |
| `src/hsap/reproduction.py` | Mating and birth logic |
| `src/hsap/metrics.py` | Summary metric computation |
| `src/hsap/config.py` | Configuration deserialization |
| `src/hsap/io.py` | CSV save/load |
| `src/hsap/scenarios.py` | Scenario definitions (frozen) |
| `src/hsap/null_models.py` | Null model implementations |
| `src/hsap/ablation_models.py` | Ablation variant implementations |
| `src/hsap/sensitivity.py` | Morris + Sobol sensitivity |
| `src/hsap/ga.py` | Genetic algorithm search |
| `src/hsap/visual_trace.py` | HSAP index computation |

## Scripts

| Path | Description |
|---|---|
| `scripts/run_paper_experiments.py` | Multi-seed paper experiments |
| `scripts/run_null_ablation_suite.py` | Null model + ablation comparisons |
| `scripts/run_paper_ga.py` | GA search for paper |
| `scripts/run_paper_sensitivity.py` | Morris + Sobol sensitivity |
| `scripts/make_paper_figures.py` | Figure generation (Fig 1-9) |
| `scripts/run_resumable_pipeline.py` | Full pipeline end-to-end |
| `scripts/run_baseline.py` | Quick baseline smoke test |
| `scripts/run_analysis.py` | Per-scenario analysis plots |
| `scripts/make_report.py` | Report generation |

## Paper Materials

| Path | Description |
|---|---|
| `paper_working/manuscript.md` | Working manuscript (377 lines) |
| `paper_working/references.bib` | Bibliography (41 entries) |
| `paper_working/figures/` | 9 figures (PNG + PDF) |
| `paper_working/tables/` | 6 CSV tables |
| `paper_working/tables_md/` | 6 Markdown tables |
| `paper_working/notes/` | Decision notes, claim register |
| `paper_working/empirical_proxy/` | External proxy analysis |
| `paper/internal/` | Review framework |
| `paper/supplementary/` | Model equations, parameters, scenarios |

## Configuration

| Path | Description |
|---|---|
| `pyproject.toml` | Package metadata, deps |
| `Makefile` | Common commands |
| `configs/*.yaml` | Scenario config files |
| `requirements.txt` | Runtime dependencies |

## Tests

| Path | Description |
|---|---|
| `tests/unit/` | Unit tests |
| `tests/integration/` | Integration tests |
| `tests/smoke/` | Smoke tests |

## Documentation

| Path | Description |
|---|---|
| `docs/hsap_hypothesis.md` | Core hypothesis |
| `docs/hsap_model_plan.md` | Model design |
| `docs/full_formulation.md` | Mathematical formulation |
| `docs/falsification_criteria.md` | Falsification criteria |
| `docs/literature_notes.md` | Literature context |
| `docs/model_time_units.md` | Time unit definitions |
| `docs/pipeline_checklist.md` | Pipeline checklist |
