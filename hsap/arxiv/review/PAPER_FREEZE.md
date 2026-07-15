# Paper Freeze Manifest

**Branch**: `paper/private-arxiv-draft-v1`  
**Commit**: $(git rev-parse HEAD)  
**Date**: 2026-06-26

## Freeze Rules
1. **No re-running simulations** — all 1,970 seeds validated, data frozen.
2. **No new null/ablation models** — existing 11 nulls + 6 ablations are final.
3. **Text changes only** — editing prose, labels, captions is fine.
4. **Figure tweaks allowed** — colors, layout, fonts, labels only; no new data.
5. **Supplementary files are frozen** — equations, parameter tables, scenario defs.

## What This Freeze Enables
- Drafting can proceed without fear of data invalidation.
- Internal review can check against stable figures and numbers.
- arXiv submission package can be assembled from frozen `paper/manuscript/` and `paper/supplementary/`.

## Post-Freeze Pipeline
1. Draft sections in order: Methods -> Results -> Limitations -> Discussion -> Introduction -> Abstract
2. Internal review against acceptance criteria
3. Clean branch for public repo
4. arXiv submission

## Acceptance Criteria
- [ ] No "proves", "validates", "confirmed", or "biological law" anywhere in manuscript
- [ ] B_hsap_abundance fertility caveat explicitly stated
- [ ] All 9 figures (fig1–fig8, fig4a, fig4b) appear in correct order
- [ ] Claim language uses "simulation-consistent", "under model assumptions", "candidate mechanism"
- [ ] Limitations section acknowledges model abstractions
