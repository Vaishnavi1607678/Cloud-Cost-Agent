# Calibration of P(problem) = P(Waste) + P(Compromise)

All decisions over 30 case sets (1200 cases).
Test mix: 40% of cases are real problems (Waste or Compromise).

## v1_C

| Predicted P(problem) | Cases | Mean predicted | Observed rate |
|---|---|---|---|
| 0.0–0.1 | 608 | 0.03 | 0.21 |
| 0.1–0.3 | 345 | 0.20 | 0.37 |
| 0.3–0.5 | 19 | 0.48 | 0.63 |
| 0.5–0.7 | 81 | 0.61 | 0.86 |
| 0.7–1.0 | 147 | 0.94 | 0.99 |

Expected calibration error (ECE): **0.163** (0 = perfect)

## v2_full

| Predicted P(problem) | Cases | Mean predicted | Observed rate |
|---|---|---|---|
| 0.0–0.1 | 422 | 0.04 | 0.16 |
| 0.1–0.3 | 463 | 0.16 | 0.29 |
| 0.3–0.5 | 49 | 0.40 | 0.69 |
| 0.5–0.7 | 64 | 0.60 | 0.83 |
| 0.7–1.0 | 202 | 0.90 | 0.95 |

Expected calibration error (ECE): **0.126** (0 = perfect)
