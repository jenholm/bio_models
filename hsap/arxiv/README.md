# HSAP arXiv Publication Tree

**Hormonal-Social Adaptation Population Model: A Computational Framework for Exploring Behavioral Stabilization Under Ecological Release**

## Structure

```
arxiv/
├── manuscript/          — Markdown manuscript sections
│   ├── main.md          — Full working manuscript
│   ├── abstract.md      — Abstract (extracted)
│   ├── introduction.md  — Introduction (extracted)
│   ├── methods.md       — Methods (extracted)
│   ├── results.md       — Results (extracted)
│   ├── discussion.md    — Discussion (extracted)
│   └── conclusion.md    — Conclusion (extracted)
│
├── latex/               — LaTeX submission package
│   ├── hsap.tex         — Main LaTeX document
│   ├── references.bib   — Bibliography
│   ├── figures/         — LaTeX figure imports
│   └── tables/          — LaTeX table imports
│
├── supplementary/       — Supplementary materials
│   ├── model_equations.md
│   ├── parameter_table.md
│   ├── sensitivity_methods.md
│   ├── GA_methods.md
│   └── null_models.md
│
├── figures/             — Publication figures
│   ├── final/           — Final publication figures
│   └── draft/           — Draft figures from paper_working
│
├── data/                — Data and results
│   ├── simulation_parameters/
│   └── generated_results/
│
├── code/                — Reproducible code snapshot
│   └── README.md
│
├── review/              — Internal review framework
│   ├── reviewer_attack_list.md
│   ├── claim_discipline.md
│   ├── PAPER_FREEZE.md
│   └── results_audit.md
│
├── reproducibility/     — Reproducibility package
│   ├── environment.yml
│   ├── requirements.txt
│   ├── run_all.sh
│   └── README.md
│
└── README.md            — This file
```

## Design Philosophy

The `arxiv/` tree is the publication cockpit. The model repository (`src/`, `scripts/`, `tests/`) is the laboratory. Different oxygen systems.

This separation ensures:
- Model history remains intact
- Paper can evolve aggressively
- Public code snapshot is frozen
- Reproducibility is self-contained

## Quick Start

```bash
# Install dependencies
pip install -e ".[all]"

# Run reproducibility package
cd arxiv/reproducibility
bash run_all.sh

# Compile LaTeX
cd arxiv/latex
pdflatex hsap.tex
bibtex hsap
pdflatex hsap.tex
pdflatex hsap.tex
```

## Submission Checklist

- [ ] Clean LaTeX compile
- [ ] No missing citations
- [ ] No missing figures
- [ ] No unsupported biological claims
- [ ] Reproducible figure generation
- [ ] All null models documented
- [ ] All ablation variants documented
- [ ] Claim discipline enforced
