# CITATION_AUDIT.md

Audit of all citations in the HSAP manuscript LaTeX files.

## Citation Inventory

| Key | Used in | In references.bib? | Status | Action |
|-----|---------|-------------------|--------|--------|
| sinclair1989 | introduction.tex | Yes | Verified | OK |
| hixon2002population | introduction.tex | Yes | Verified | OK (replaces carton2008) |
| krebs1995impact | introduction.tex | Yes | Verified | OK (replaces getz1974) |
| krebs2001 | introduction.tex | Yes | Verified | OK |
| wingfield1990 | introduction.tex | Yes | Verified | OK |
| sapolsky2005 | introduction.tex | Yes | Verified | OK |
| creel2013 | introduction.tex | Yes | Verified | OK |
| ellison2003 | introduction.tex | Yes | Verified | OK |
| grimm2006 | methods.tex | Yes | Verified | OK |
| higham2013endocrinology | introduction.tex | Yes | Verified | OK (replaces van2014) |
| christian1964endocrines | introduction.tex | Yes | Verified | OK (replaces marine1971) |
| cluttonbrock1985population | (new, available) | Yes | Verified | Available for future use |
| boonstra2013reality | (new, available) | Yes | Verified | Available for future use |

## Removed References (Weak/Suspect)

These entries were in the old references.bib but have been removed due to verification issues:

| Key | Reason removed |
|-----|---------------|
| carton2008 | Unverifiable title/journal combination; replaced with hixon2002population |
| getz1974 | Vole ecology book carrying broad claims; replaced with krebs1995impact |
| van2014 | Author name garbled ("Van, Luyt"); replaced with higham2013endocrinology |
| marine1971 | Unverifiable title/journal combination; replaced with christian1964endocrines |

## Removed References (External Proxy)

These entries were in the old references.bib but are no longer cited in any manuscript section:

| Key | Reason removed |
|-----|---------------|
| travison2007 | External proxy section removed from discussion |
| andersson2007 | External proxy section removed from discussion |
| lokeshwar2020 | External proxy section removed from discussion |
| chodick2020 | External proxy section removed from discussion |
| fogliato2021 | External proxy section removed from discussion |
| fbiucr2024 | External proxy section removed from discussion |
| ojjdp2024 | External proxy section removed from discussion |
| bjsncvs2024 | External proxy section removed from discussion |
| ccj2025 | External proxy section removed from discussion |
| nhanes2024 | External proxy section removed from discussion |

## Unused Ecology References (retained for completeness)

| Key | Status | Notes |
|-----|--------|-------|
| beddington1975 | Not cited in current manuscript | Retained in bib |
| sinervo2000 | Not cited in current manuscript | Retained in bib |
| hau2014 | Not cited in current manuscript | Retained in bib |
| wilson1998 | Not cited in current manuscript | Retained in bib |
| may1976 | Not cited in current manuscript | Retained in bib |
| christian1975 | Not cited in current manuscript | Retained in bib |

## Verification Notes

- All 11 citation keys used in the manuscript are present in references.bib
- All entries have title, author, year, and journal/publisher
- No external proxy references remain in the active bibliography
- 6 unused ecology references retained in bib (benign — LaTeX natbib ignores uncited entries)
