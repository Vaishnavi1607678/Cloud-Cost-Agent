# Generalization (20 seeds x 500 cases, mean)

## Part 1: change one variable at a time

| Scenario | Policy | Total cost | Info cost | Questions/case | Human review | Missed compromises | Wrong Limits |
|---|---|---|---|---|---|---|---|
| baseline world | P0 baseline | $235,240 | $0 | 0.000 | 0.000 | 15.25 | 0.00 |
| baseline world | P2 threshold | $19,313 | $0 | 0.000 | 0.490 | 0.00 | 0.70 |
| baseline world | P3b VOI + stakes | $16,409 | $329 | 0.284 | 0.376 | 0.10 | 1.15 |
| (a) missed-problem cost x100 | P0 baseline | $23,523,987 | $0 | 0.000 | 0.000 | 15.25 | 0.00 |
| (a) missed-problem cost x100 | P2 threshold | $29,677 | $0 | 0.000 | 0.985 | 0.00 | 0.70 |
| (a) missed-problem cost x100 | P3b VOI + stakes | $28,085 | $37 | 0.073 | 0.956 | 0.00 | 1.25 |
| (b) paid checks cost x10 | P0 baseline | $235,240 | $0 | 0.000 | 0.000 | 15.25 | 0.00 |
| (b) paid checks cost x10 | P2 threshold | $19,313 | $0 | 0.000 | 0.490 | 0.00 | 0.70 |
| (b) paid checks cost x10 | P3b VOI + stakes | $16,876 | $636 | 0.117 | 0.383 | 0.15 | 1.25 |
| (c) enterprise world, startup model | P0 baseline | $422,683 | $0 | 0.000 | 0.000 | 30.80 | 0.00 |
| (c) enterprise world, startup model | P2 threshold | $25,351 | $0 | 0.000 | 0.490 | 0.10 | 0.25 |
| (c) enterprise world, startup model | P3b VOI + stakes | $21,578 | $445 | 0.298 | 0.400 | 0.30 | 1.65 |
| (c') enterprise world, re-fitted model | P0 baseline | $422,683 | $0 | 0.000 | 0.000 | 30.80 | 0.00 |
| (c') enterprise world, re-fitted model | P2 threshold | $21,454 | $0 | 0.000 | 0.454 | 0.10 | 2.45 |
| (c') enterprise world, re-fitted model | P3b VOI + stakes | $19,725 | $814 | 0.284 | 0.369 | 0.15 | 1.55 |

Threshold check for (a): Ignore/Report break-even P(Compromise) falls from 0.0112 to 50 / (50 + 499,400) = 0.000100.

## Part 2: Jensen-Shannon divergence alarm

Can the agent notice the move from startup to enterprise from the free evidence alone, before any labels arrive? Reference: 5,000 startup cases. For each window size, the alarm level is the 99th percentile of JSD between 100 startup windows and the reference (about 1 false alarm per 100 windows). Detection rate = share of 100 enterprise windows above the alarm level.

| Window size (cases) | Alarm level (bits) | Mean JSD, startup | Mean JSD, enterprise | False-alarm rate | Detection rate |
|---|---|---|---|---|---|
| 100 | 0.0596 | 0.0406 | 0.0483 | 0.01 | 0.11 |
| 200 | 0.0336 | 0.0217 | 0.0321 | 0.01 | 0.41 |
| 500 | 0.0148 | 0.0094 | 0.0230 | 0.01 | 0.98 |
| 1000 | 0.0088 | 0.0051 | 0.0199 | 0.01 | 1.00 |

Small windows are mostly noise: the shift only becomes reliably visible with enough cases. Which window size is enough is the honest answer to 'how would you even notice?'.
