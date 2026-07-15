# Results Audit — Internal Quality Check

## Validation Summary
- **3050/3050 seeds validated OK** (61 scenarios × 50 seeds)
- Ledger: `results/paper/pipeline_state.sqlite`
- All null/ablation runs completed for 7 core scenarios

## Key Numbers (pre-freeze)
| Metric | Value | Notes |
|--------|-------|-------|
| Scenarios | 61 factorial | 50 seeds each |
| Core scenarios | 7 | A, B, Cc, Cs, D, E, F |
| Null models | 11 | N0–N10 |
| Ablation models | 6 | 6 mechanism-removal variants |
| Figure count | 9 | 4a and 4b are separate |
| E sink seeds | 14/50 | seeds [0,2,5,10,11,12,14,15,20,27,33,34,39,44] |
| C/F sink seeds | 0/50 | never trigger sink |

## Claim Verification
- [x] No "proves", "validates", "confirmed", "biological law" in manuscript
- [x] Claim language uses "simulation-consistent", "under model assumptions", "candidate mechanism"
- [x] B_hsap_abundance fertility caveat explicitly stated in Results
- [x] Limitations section lists all model abstractions
- [x] Null model N3 (disease) fit acknowledged as indistinguishability limitation

## Data Integrity
- [x] CSV files have matching seed counts across groups
- [x] No partial or corrupted CSV files (validate_seed_output)
- [x] All figure scripts reference validated data files
- [x] Null/ablation data in standalone JSON, separate from pipeline state
