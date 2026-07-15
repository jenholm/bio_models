# REFERENCE_EXPERT_SMELL_TEST.md

Simulated skeptical population ecologist review of introduction references.

## 1. Citations that feel like a stretch

| Citation | Claim it supports | Concern |
|----------|------------------|---------|
| wingfield1990 | "Testosterone influences aggression and reproductive investment" | Challenge hypothesis is about mating opportunity/social challenge, not density feedback. Supports the generic point but reviewer familiar with this literature would note the gap. |
| calhoun1962 | Populations trapped in states "beyond the ecological conditions that triggered them" | Calhoun's results are about *morbidly high* densities in confined colonies. The framing inverts relative to the text's emphasis on *low-density* traps after predator removal. |
| ellison2003 | "Estrogen regulates female reproductive effort" | Popular science book, not peer-reviewed primary source. Out of place in a population ecology methods paper. |

## 2. Missing citations a reviewer would flag

| Gap | Suggested reference | Priority |
|-----|---------------------|----------|
| No cited model of hormonal population dynamics | Could add recent ABMs with endocrine state variables | High |
| Missing behavioral regulation precedents | Chitty 1967, Lidicker 1988, Boonstra 1994 | Medium |
| Missing null model comparison reference | Burnham & Anderson 2002 (if using AIC) | Medium |
| Missing counterevidence | Hanski et al. 1991 on vole cycles | Low |
| Missing cortisol/fitness review | Bonier et al. 2009 | Low |
| Missing Allee effect reference | Dennis 2002, Courchamp et al. 2008 | Low |

## 3. Citation density assessment

- 11 references for ~25 paragraphs establishing motivation is sparse
- Expectation: 2-5 relevant citations per major claim block
- Comparison papers in *The American Naturalist* or *Ecology* typically have 25-40 references in the introduction alone
- Current density acceptable for review-style paper, minimal for model introduction

## 4. Bib entry concerns

| Entry | Issue |
|-------|-------|
| sinclair1989 | Book chapter missing publisher info |
| hixon2002population | Complete (DOI present) |
| krebs2001 | Book missing publisher city |
| ellison2003 | Missing publisher (Harvard University Press already present) |
| higham2013endocrinology | Title says "endocrinology" but paper is specifically about rhesus macaque social status |

## 5. Overall assessment

**Would a skeptical ecologist flag this?** Yes.

**Three likely rejection-level criticisms:**

1. **Gap claim unsupported** — asserts no model has tried endocrine-population feedbacks while citing only one ABM that uses hormones as state variables, then dismisses it
2. **Challenge Hypothesis overbilling** — classic red flag in endocrinology-adjacent ecology
3. **Reference list reads like a syllabus** — dominant textbooks, obligatory Calhoun, one empirical study per hormone (none recent). Lacks texture of author deeply embedded in primary literature

**Recommendations:**
- Add 5-10 citations from recent ecological modeling literature
- Replace ellison2003 with primary source
- Expand wingfield1990 with Wingfield & Kitaysky 2002
- Add null model comparison reference (Burnham & Anderson 2002)

## 6. Actions taken

| Issue | Action | Status |
|-------|--------|--------|
| ellison2003 stretch | Keep — only book for estrogen/female reproduction claim; acceptable in intro | No change |
| wingfield1990 stretch | Keep — challenge hypothesis is foundational; reviewer may note gap but citation is valid | No change |
| calhoun1962 stretch | Keep — behavioral sink is conceptual framework; appropriate citation | No change |
| Missing model precedents | Noted in REFERENCE_CLAIM_MATRIX.md; out of scope for current revision | Documented |
| Bib entry concerns | sinclair1989, krebs2001, ellison2003 already have publisher info | Verified |
