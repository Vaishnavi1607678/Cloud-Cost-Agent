# Sensitivity analysis (mean over 30 case sets of 40)

Each cell: total decision cost $ / false alarms / missed compromises / human-review rate

| Scenario | Baseline | v1_C | v2_full | v2 cheapest? |
|---|---|---|---|---|
| Default (Report $50, ignore-compromise $5,000, prior 4%) | $17,781 / 5.8 / 2.47 / 0.34 | $6,656 / 8.7 / 0.57 / 0.38 | $4,038 / 14.2 / 0.10 / 0.57 | yes |
| Alert fatigue: Report on Normal/Planned = $150 | $18,364 / 5.8 / 2.47 / 0.34 | $8,284 / 1.8 / 0.77 / 0.14 | $5,262 / 3.2 / 0.13 / 0.21 | yes |
| Strong alert fatigue: Report on Normal/Planned = $400 | $19,823 / 5.8 / 2.47 / 0.34 | $8,631 / 0.9 / 0.80 / 0.07 | $7,008 / 1.4 / 0.40 / 0.13 | yes |
| Cheaper compromise: Ignore-compromise = $2,000 | $10,381 / 5.8 / 2.47 / 0.34 | $6,656 / 8.4 / 1.50 / 0.37 | $4,018 / 11.5 / 0.17 / 0.47 | yes |
| Worse compromise: Ignore-compromise = $20,000 | $54,781 / 5.8 / 2.47 / 0.34 | $15,253 / 12.0 / 0.57 / 0.47 | $4,214 / 16.1 / 0.03 / 0.62 | yes |
| Rarer compromise: prior 1% | $17,781 / 5.8 / 2.47 / 0.34 | $11,531 / 11.3 / 1.50 / 0.48 | $5,697 / 11.0 / 0.20 / 0.53 | yes |
| More common compromise: prior 10% | $17,781 / 5.8 / 2.47 / 0.34 | $6,586 / 9.0 / 0.57 / 0.38 | $3,566 / 15.6 / 0.03 / 0.59 | yes |
